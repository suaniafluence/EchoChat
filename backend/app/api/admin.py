"""Admin API endpoints for configuration and scraping."""
import subprocess
import sys
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel, HttpUrl
from typing import Optional, List, Dict
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.database import get_db
from app.models.scrape_job import ScrapeJob, JobStatus
from app.models.scraped_page import ScrapedPage
from app.config import settings
from app.utils.logger import logger
from app.utils.log_buffer import get_logs
from app.rag.rag_engine import get_rag_engine


router = APIRouter()


class ScrapeRequest(BaseModel):
    """Request to start a scrape job."""
    target_url: HttpUrl
    reindex: bool = True


class ConfigUpdate(BaseModel):
    """Configuration update request."""
    target_url: Optional[HttpUrl] = None
    scrape_frequency_hours: Optional[int] = None


class ScrapeJobResponse(BaseModel):
    """Scrape job response."""
    id: int
    target_url: str
    status: str
    pages_scraped: int
    error_message: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime
    rag_indexed: int = 0  # Number of chunks indexed in RAG


class StatsResponse(BaseModel):
    """System statistics response."""
    total_pages: int
    total_chunks: int
    last_scrape: Optional[datetime]
    target_url: str
    scrape_frequency_hours: int


def _run_scrape_job(job_id: int, target_url: str, reindex: bool):
    """Background task to run scraping job in a separate process."""
    try:
        logger.info(f"Starting scrape worker process for job {job_id}")

        # Run scraper in a separate Python process to avoid event loop issues on Windows
        python_executable = sys.executable
        module_path = "app.scraper.scrape_worker"
        reindex_str = "true" if reindex else "false"

        logger.info(f"Worker command: {python_executable} -m {module_path} {job_id} {target_url} {reindex_str}")

        result = subprocess.run(
            [python_executable, "-m", module_path, str(job_id), target_url, reindex_str],
            capture_output=True,
            text=True,
            timeout=3600  # 1 hour timeout
        )

        logger.info(f"Scrape worker completed with return code: {result.returncode}")
        if result.stdout:
            logger.info(f"Worker STDOUT:\n{result.stdout}")
        if result.stderr:
            logger.error(f"Worker STDERR:\n{result.stderr}")

        if result.returncode != 0:
            logger.error(f"Scrape worker failed with code {result.returncode}")

    except subprocess.TimeoutExpired:
        logger.error(f"Scrape worker for job {job_id} timed out")
    except Exception as e:
        logger.error(f"Failed to start scrape worker: {e}", exc_info=True)


@router.post("/scrape", response_model=ScrapeJobResponse)
async def start_scrape(
    scrape_request: ScrapeRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Start a new scraping job.
    
    Args:
        scrape_request: Scrape request with target URL
        background_tasks: FastAPI background tasks
        db: Database session
        
    Returns:
        Created scrape job
    """
    try:
        # Create new job
        job = ScrapeJob(
            target_url=str(scrape_request.target_url),
            status=JobStatus.PENDING
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        
        # Start scraping in background
        background_tasks.add_task(
            _run_scrape_job,
            job.id,
            str(scrape_request.target_url),
            scrape_request.reindex
        )
        
        logger.info(f"Started scrape job {job.id} for {scrape_request.target_url}")
        
        return ScrapeJobResponse(
            id=job.id,
            target_url=job.target_url,
            status=job.status.value,
            pages_scraped=job.pages_scraped,
            error_message=job.error_message,
            started_at=job.started_at,
            completed_at=job.completed_at,
            created_at=job.created_at,
            rag_indexed=job.rag_indexed or 0
        )
        
    except Exception as e:
        logger.error(f"Failed to start scrape job: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/jobs", response_model=List[ScrapeJobResponse])
async def get_jobs(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Get recent scrape jobs.
    
    Args:
        limit: Maximum number of jobs to return
        db: Database session
        
    Returns:
        List of recent scrape jobs
    """
    jobs = db.query(ScrapeJob).order_by(desc(ScrapeJob.created_at)).limit(limit).all()
    
    return [
        ScrapeJobResponse(
            id=job.id,
            target_url=job.target_url,
            status=job.status.value,
            pages_scraped=job.pages_scraped,
            error_message=job.error_message,
            started_at=job.started_at,
            completed_at=job.completed_at,
            created_at=job.created_at,
            rag_indexed=job.rag_indexed or 0
        )
        for job in jobs
    ]


@router.get("/jobs/{job_id}", response_model=ScrapeJobResponse)
async def get_job(
    job_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific scrape job by ID.
    
    Args:
        job_id: Job ID
        db: Database session
        
    Returns:
        Scrape job details
    """
    job = db.query(ScrapeJob).filter(ScrapeJob.id == job_id).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return ScrapeJobResponse(
        id=job.id,
        target_url=job.target_url,
        status=job.status.value,
        pages_scraped=job.pages_scraped,
        error_message=job.error_message,
        started_at=job.started_at,
        completed_at=job.completed_at,
        created_at=job.created_at,
        rag_indexed=job.rag_indexed or 0
    )


@router.get("/stats", response_model=StatsResponse)
async def get_stats(db: Session = Depends(get_db)):
    """
    Get system statistics.
    Always uses the last successfully indexed RAG data, even if recent scraping jobs failed.

    Args:
        db: Database session

    Returns:
        System statistics
    """
    total_pages = db.query(ScrapedPage).count()

    rag_engine = get_rag_engine()
    rag_stats = rag_engine.get_collection_stats()

    # Get the last job that successfully indexed RAG (has rag_indexed > 0)
    last_indexed_job = db.query(ScrapeJob).filter(
        ScrapeJob.rag_indexed > 0
    ).order_by(desc(ScrapeJob.completed_at)).first()

    # Fallback to last completed job if no indexed job found
    if not last_indexed_job:
        last_indexed_job = db.query(ScrapeJob).filter(
            ScrapeJob.status == JobStatus.COMPLETED
        ).order_by(desc(ScrapeJob.completed_at)).first()

    return StatsResponse(
        total_pages=total_pages,
        total_chunks=rag_stats.get('total_chunks', 0),
        last_scrape=last_indexed_job.completed_at if last_indexed_job else None,
        target_url=settings.target_url,
        scrape_frequency_hours=settings.scrape_frequency_hours
    )


@router.get("/config")
async def get_config():
    """
    Get current configuration.

    Returns:
        Current configuration
    """
    return {
        "target_url": settings.target_url,
        "scrape_frequency_hours": settings.scrape_frequency_hours
    }


@router.put("/config")
async def update_config(config_update: ConfigUpdate):
    """
    Update configuration (target URL and scrape frequency).

    Args:
        config_update: Configuration update request

    Returns:
        Updated configuration
    """
    try:
        if config_update.target_url:
            settings.target_url = str(config_update.target_url)
            logger.info(f"Updated target URL to: {settings.target_url}")

        if config_update.scrape_frequency_hours:
            settings.scrape_frequency_hours = config_update.scrape_frequency_hours
            logger.info(f"Updated scrape frequency to: {settings.scrape_frequency_hours} hours")

        return {
            "target_url": settings.target_url,
            "scrape_frequency_hours": settings.scrape_frequency_hours,
            "message": "Configuration updated successfully"
        }

    except Exception as e:
        logger.error(f"Failed to update configuration: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/logs")
async def get_system_logs(limit: int = 100):
    """
    Get recent system logs from log file for display in Admin Panel.

    Args:
        limit: Maximum number of logs to return (default 100)

    Returns:
        List of recent log entries
    """
    import os
    import re
    from datetime import datetime

    log_file = "./logs/app.log"
    logs = []

    if os.path.exists(log_file):
        try:
            with open(log_file, "r", encoding="utf-8") as f:
                lines = f.readlines()

            # Parse log lines: format is "timestamp - logger - LEVEL - func:line - message"
            log_pattern = re.compile(
                r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) - (\S+) - (\w+) - (.+)$'
            )

            for line in lines[-limit:]:
                line = line.strip()
                if not line:
                    continue
                match = log_pattern.match(line)
                if match:
                    timestamp_str, logger, level, message = match.groups()
                    logs.append({
                        "timestamp": timestamp_str.replace(",", "."),
                        "level": level,
                        "logger": logger,
                        "message": message
                    })
                else:
                    # Handle continuation lines or non-standard format
                    if logs:
                        logs[-1]["message"] += "\n" + line
        except Exception as e:
            logs.append({
                "timestamp": datetime.now().isoformat(),
                "level": "ERROR",
                "logger": "admin",
                "message": f"Failed to read log file: {str(e)}"
            })

    return {
        "logs": logs,
        "total": len(logs)
    }


@router.get("/homepage")
async def get_homepage(db: Session = Depends(get_db)):
    """
    Get the homepage HTML for pixel-perfect display.

    Args:
        db: Database session

    Returns:
        Homepage HTML and metadata
    """
    homepage = db.query(ScrapedPage).filter(
        ScrapedPage.is_homepage == True
    ).first()

    if not homepage:
        raise HTTPException(status_code=404, detail="Homepage not found. Please run scraping first.")

    return {
        'url': homepage.url,
        'title': homepage.title,
        'html': homepage.html,
        'scraped_at': homepage.scraped_at
    }
