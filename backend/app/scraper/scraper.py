"""Deep web scraper using Playwright."""
import asyncio
import sys
from typing import Set, Dict, List, Optional
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, Browser, Page
from sqlalchemy.orm import Session

from app.models.scraped_page import ScrapedPage
from app.config import settings
from app.utils.logger import logger


# Fix for Windows: Use ProactorEventLoop for subprocess support
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


class WebScraper:
    """Deep web scraper that stays within the same domain."""

    def __init__(self, db: Session, target_url: str = None, single_page: bool = False, path_prefix: str = None):
        """
        Initialize the scraper.

        Args:
            db: Database session
            target_url: Target URL to scrape (defaults to settings)
            single_page: If True, only scrape the target URL without following links
            path_prefix: If set, only follow links that start with this path (e.g., "/sortir-bouger/")
        """
        self.db = db
        self.target_url = target_url or settings.target_url
        self.single_page = single_page
        self.path_prefix = path_prefix
        parsed_target = urlparse(self.target_url)
        self.base_domain = parsed_target.netloc
        # Store the base path to only crawl downward (not parent directories)
        self.base_path = parsed_target.path.rstrip('/')
        self.visited_urls: Set[str] = set()
        self.to_visit: Set[str] = {self.target_url}
        self.scraped_data: List[Dict] = []
        
    def _is_same_domain(self, url: str) -> bool:
        """Check if URL belongs to the same domain."""
        parsed = urlparse(url)
        return parsed.netloc == self.base_domain or parsed.netloc == ""
    
    def _normalize_url(self, url: str, base_url: str) -> Optional[str]:
        """
        Normalize and validate URL.
        
        Args:
            url: URL to normalize
            base_url: Base URL for relative links
            
        Returns:
            Normalized URL or None if invalid
        """
        # Handle relative URLs
        absolute_url = urljoin(base_url, url)
        
        # Parse URL
        parsed = urlparse(absolute_url)
        
        # Remove fragments
        url_without_fragment = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        if parsed.query:
            url_without_fragment += f"?{parsed.query}"
        
        # Check if same domain
        if not self._is_same_domain(url_without_fragment):
            return None

        # Check if URL is within or below the base path (no going up in hierarchy)
        url_path = parsed.path.rstrip('/')
        if self.base_path and not url_path.startswith(self.base_path):
            return None

        # If path_prefix is set, only include URLs that start with it
        if self.path_prefix and not url_path.startswith(self.path_prefix):
            return None
        
        # Skip common non-HTML extensions
        skip_extensions = ['.pdf', '.jpg', '.jpeg', '.png', '.gif', '.svg', '.ico', 
                          '.css', '.js', '.xml', '.zip', '.tar', '.gz', '.mp4', '.avi']
        if any(url_without_fragment.lower().endswith(ext) for ext in skip_extensions):
            return None
        
        return url_without_fragment
    
    async def _extract_links(self, page: Page, current_url: str) -> Set[str]:
        """
        Extract all internal links from the current page.
        
        Args:
            page: Playwright page
            current_url: Current page URL
            
        Returns:
            Set of normalized URLs
        """
        links = set()
        
        try:
            # Get all anchor tags
            anchors = await page.query_selector_all('a[href]')
            
            for anchor in anchors:
                href = await anchor.get_attribute('href')
                if href:
                    normalized = self._normalize_url(href, current_url)
                    if normalized and normalized not in self.visited_urls:
                        links.add(normalized)
        except Exception as e:
            logger.error(f"Error extracting links from {current_url}: {e}")
        
        return links
    
    async def _scrape_page(self, browser: Browser, url: str) -> Optional[Dict]:
        """
        Scrape a single page.

        Args:
            browser: Playwright browser instance
            url: URL to scrape

        Returns:
            Scraped page data or None on failure
        """
        page = None
        try:
            # Create page with user agent to avoid blocking
            page = await browser.new_page(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )

            # Set timeout
            page.set_default_timeout(settings.scraper_timeout)

            # Navigate to page
            try:
                await page.goto(url, wait_until='domcontentloaded', timeout=settings.scraper_timeout)
            except Exception as nav_error:
                logger.warning(f"Navigation timeout for {url}, proceeding with partial content: {nav_error}")

            # Get page content
            html = await page.content()

            # Parse with BeautifulSoup
            soup = BeautifulSoup(html, 'lxml')

            # Extract title
            title = soup.title.string if soup.title else ""

            # Remove script and style elements
            for script in soup(['script', 'style', 'meta', 'link']):
                script.decompose()

            # Extract text content
            text_content = soup.get_text(separator=' ', strip=True)

            # Clean up whitespace
            text_content = ' '.join(text_content.split())

            # Extract links for further crawling (unless single_page mode)
            new_links = set()
            if not self.single_page:
                new_links = await self._extract_links(page, url)
                self.to_visit.update(new_links)

            logger.info(f"Scraped: {url} (found {len(new_links)} new links)")

            return {
                'url': url,
                'title': title,
                'content': text_content,
                'html': html,
                'is_homepage': url == self.target_url
            }

        except Exception as e:
            logger.error(f"Failed to scrape {url}: {e}")
            return None
        finally:
            if page:
                try:
                    await page.close()
                except Exception as close_error:
                    logger.warning(f"Error closing page for {url}: {close_error}")
    
    def _save_to_db(self, page_data: Dict) -> None:
        """
        Save scraped page to database.
        
        Args:
            page_data: Page data dictionary
        """
        try:
            # Check if page already exists
            existing = self.db.query(ScrapedPage).filter(
                ScrapedPage.url == page_data['url']
            ).first()
            
            if existing:
                # Update existing page
                existing.title = page_data['title']
                existing.content = page_data['content']
                existing.html = page_data['html']
                existing.is_homepage = page_data['is_homepage']
            else:
                # Create new page
                page = ScrapedPage(**page_data)
                self.db.add(page)
            
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Failed to save page {page_data['url']}: {e}")
            self.db.rollback()
    
    async def scrape(self, max_pages: Optional[int] = None) -> int:
        """
        Start the scraping process.

        Args:
            max_pages: Maximum number of pages to scrape (None for unlimited)

        Returns:
            Number of pages scraped
        """
        logger.info(f"Starting scrape of {self.target_url}")

        pages_scraped = 0
        browser = None

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)

                try:
                    while self.to_visit and (max_pages is None or pages_scraped < max_pages):
                        # Get next URL
                        url = self.to_visit.pop()

                        # Skip if already visited
                        if url in self.visited_urls:
                            continue

                        # Mark as visited
                        self.visited_urls.add(url)

                        # Scrape the page
                        page_data = await self._scrape_page(browser, url)

                        if page_data:
                            self._save_to_db(page_data)
                            self.scraped_data.append(page_data)
                            pages_scraped += 1

                            # Add small delay to be polite
                            await asyncio.sleep(0.5)

                    logger.info(f"Scraping completed. Total pages scraped: {pages_scraped}")

                finally:
                    try:
                        if browser:
                            await browser.close()
                    except Exception as e:
                        logger.warning(f"Error closing browser: {e}")
        except Exception as e:
            logger.error(f"Scraping error: {e}", exc_info=True)
            raise

        return pages_scraped


async def run_scraper(db: Session, target_url: str = None, single_page: bool = False, path_prefix: str = None) -> int:
    """
    Convenience function to run the scraper.

    Args:
        db: Database session
        target_url: Target URL to scrape
        single_page: If True, only scrape the target URL without following links
        path_prefix: If set, only follow links that start with this path

    Returns:
        Number of pages scraped
    """
    scraper = WebScraper(db, target_url, single_page=single_page, path_prefix=path_prefix)
    return await scraper.scrape()
