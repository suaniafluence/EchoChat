"""Automated scheduler for periodic scraping and reindexing."""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
import asyncio

from app.config import settings
from app.models.database import SessionLocal
from app.scraper.scraper import run_scraper
from app.rag.rag_engine import get_rag_engine
from app.utils.logger import logger


scheduler = AsyncIOScheduler()


async def scheduled_scrape_and_index():
    """
    Scheduled task to scrape and reindex.
    This runs at the configured frequency.
    """
    logger.info("Starting scheduled scrape and index task")
    
    db = SessionLocal()
    
    try:
        # Run scraper
        logger.info(f"Scraping {settings.target_url}...")
        pages_scraped = await run_scraper(db, settings.target_url)
        logger.info(f"Scraped {pages_scraped} pages")
        
        # Reindex all pages
        logger.info("Starting reindexing...")
        rag_engine = get_rag_engine()
        chunks_indexed = rag_engine.index_all_pages(db)
        logger.info(f"Indexed {chunks_indexed} chunks")
        
        logger.info("Scheduled scrape and index completed successfully")
        
    except Exception as e:
        logger.error(f"Scheduled task failed: {e}")
    finally:
        db.close()


def setup_scheduler():
    """
    Configure the scheduler with the scraping task.
    """
    # Add job with interval trigger
    scheduler.add_job(
        scheduled_scrape_and_index,
        trigger=IntervalTrigger(hours=settings.scrape_frequency_hours),
        id='scrape_and_index',
        name='Scrape and index website',
        replace_existing=True,
        next_run_time=None  # Don't run immediately on startup
    )
    
    logger.info(f"Scheduler configured: scraping every {settings.scrape_frequency_hours} hours")


def start_scheduler():
    """Start the scheduler."""
    if not scheduler.running:
        scheduler.start()
        logger.info("Scheduler started")
    else:
        logger.warning("Scheduler is already running")


def stop_scheduler():
    """Stop the scheduler."""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler stopped")
