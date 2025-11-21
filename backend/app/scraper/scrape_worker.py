"""Scraper worker script - runs scraping jobs in isolated subprocess."""
import sys
import os
import asyncio
import logging
from datetime import datetime

# Add backend directory to path so imports work
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Setup event loop policy for Windows BEFORE importing anything else
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.scrape_job import ScrapeJob, JobStatus
from app.models.scraped_page import ScrapedPage
from app.scraper.scraper import run_scraper
from app.rag.rag_engine import get_rag_engine
from app.config import settings

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("echochat")


async def run_scrape_job_worker(job_id: int, target_url: str, reindex: bool):
    """Run a scraping job as a worker process."""
    # Create database session
    engine = create_engine(settings.database_url)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    try:
        # Update job status
        job = db.query(ScrapeJob).filter(ScrapeJob.id == job_id).first()
        if not job:
            logger.error(f"Job {job_id} not found in database")
            return

        job.status = JobStatus.RUNNING
        job.started_at = datetime.now()
        db.commit()
        logger.info(f"Job {job_id} status set to RUNNING")

        # Clear existing scraped pages before scraping new site
        deleted_count = db.query(ScrapedPage).delete()
        db.commit()
        logger.info(f"Cleared {deleted_count} existing scraped pages from database")

        # Run scraper
        logger.info(f"Starting scraper for job {job_id}")
        pages_scraped = await run_scraper(db, target_url)
        logger.info(f"Scraper completed: {pages_scraped} pages scraped")

        # Update job with results
        job.pages_scraped = pages_scraped
        job.status = JobStatus.COMPLETED
        job.completed_at = datetime.now()
        db.commit()
        logger.info(f"Job {job_id} marked as COMPLETED")

        # Always reindex after successful scrape (ignore reindex parameter)
        if pages_scraped > 0:
            logger.info("Starting reindexing...")
            rag_engine = get_rag_engine()
            total_chunks = rag_engine.index_all_pages(db)

            # Update job with RAG stats
            job.rag_indexed = total_chunks
            job.last_successful_job_id = job.id
            db.commit()
            logger.info(f"Reindexing complete. Total chunks indexed: {total_chunks} from {pages_scraped} pages")

    except Exception as e:
        error_msg = str(e)
        logger.error(f"Scrape job {job_id} failed: {error_msg}", exc_info=True)
        try:
            job = db.query(ScrapeJob).filter(ScrapeJob.id == job_id).first()
            if job:
                job.status = JobStatus.FAILED
                job.error_message = error_msg[:500]  # Limit to 500 chars
                job.completed_at = datetime.now()
                db.commit()
                logger.info(f"Job {job_id} marked as FAILED with error: {error_msg[:200]}")
        except Exception as db_error:
            logger.error(f"Failed to update job {job_id} status in DB: {db_error}", exc_info=True)
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) < 4:
        logger.error("Usage: python -m app.scraper.scrape_worker <job_id> <target_url> <reindex>")
        sys.exit(1)

    job_id = int(sys.argv[1])
    target_url = sys.argv[2]
    reindex = sys.argv[3].lower() == "true"

    logger.info(f"Starting scrape worker for job {job_id}")
    asyncio.run(run_scrape_job_worker(job_id, target_url, reindex))
    logger.info(f"Scrape worker for job {job_id} completed")
