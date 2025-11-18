"""ScrapedPage model for storing scraped content."""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.sql import func
from .database import Base


class ScrapedPage(Base):
    """Model for scraped pages."""
    
    __tablename__ = "scraped_pages"
    
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, unique=True, index=True, nullable=False)
    title = Column(String, nullable=True)
    content = Column(Text, nullable=True)
    html = Column(Text, nullable=True)
    is_homepage = Column(Boolean, default=False)
    scraped_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<ScrapedPage(url='{self.url}', title='{self.title}')>"
