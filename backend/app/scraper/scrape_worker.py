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

        # Reindex if requested
        if reindex:
            logger.info("Starting reindexing...")
            rag_engine = get_rag_engine()
            rag_engine.index_all_pages(db)
            logger.info("Reindexing completed")

    except Exception as e:
        logger.error(f"Scrape job {job_id} failed: {str(e)}", exc_info=True)
        job = db.query(ScrapeJob).filter(ScrapeJob.id == job_id).first()
        if job:
            job.status = JobStatus.FAILED
            job.error_message = str(e)
            job.completed_at = datetime.now()
            db.commit()
            logger.error(f"Job {job_id} marked as FAILED")
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
