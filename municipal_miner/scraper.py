"""Web scraper for municipal meeting documents."""

import re
import time
from pathlib import Path
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse
from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup
from loguru import logger


class MunicipalScraper:
    """Scrapes PDFs from municipal websites."""

    def __init__(self, download_dir: Path, delay: float = 2.0):
        """
        Initialize scraper.

        Args:
            download_dir: Directory to save downloaded PDFs
            delay: Delay between requests in seconds (be polite)
        """
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(parents=True, exist_ok=True)
        self.delay = delay

        # Headers to look like a real browser
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        }

    def scrape_austin(self, max_pdfs: int = 10) -> List[Path]:
        """
        Scrape Austin City Council PDFs.

        Austin has a well-structured site with recent agendas/minutes.
        """
        logger.info("Scraping Austin City Council...")

        base_url = "https://www.austintexas.gov"
        # Austin's council meeting calendar
        calendar_url = f"{base_url}/department/city-council/council/council_meeting_info_center.htm"

        pdfs = []

        try:
            response = requests.get(calendar_url, headers=self.headers, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            # Find all PDF links
            pdf_links = []
            for link in soup.find_all('a', href=True):
                href = link['href']
                if href.endswith('.pdf'):
                    full_url = urljoin(base_url, href)
                    pdf_links.append({
                        'url': full_url,
                        'text': link.get_text(strip=True),
                    })

            logger.info(f"Found {len(pdf_links)} PDF links on Austin's site")

            # Download PDFs
            for idx, pdf_info in enumerate(pdf_links[:max_pdfs]):
                pdf_path = self._download_pdf(
                    pdf_info['url'],
                    f"Austin_{idx + 1}.pdf"
                )
                if pdf_path:
                    pdfs.append(pdf_path)

                time.sleep(self.delay)

        except Exception as e:
            logger.error(f"Failed to scrape Austin: {e}")

        return pdfs

    def scrape_dallas(self, max_pdfs: int = 10) -> List[Path]:
        """Scrape Dallas City Council PDFs."""
        logger.info("Scraping Dallas City Council...")

        # Dallas posts agendas and minutes publicly
        base_url = "https://dallascityhall.com"
        council_url = f"{base_url}/government/citycouncil/Pages/default.aspx"

        pdfs = []

        try:
            response = requests.get(council_url, headers=self.headers, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            pdf_links = []
            for link in soup.find_all('a', href=True):
                href = link['href']
                if '.pdf' in href.lower():
                    full_url = urljoin(base_url, href)
                    pdf_links.append({
                        'url': full_url,
                        'text': link.get_text(strip=True),
                    })

            logger.info(f"Found {len(pdf_links)} PDF links on Dallas's site")

            for idx, pdf_info in enumerate(pdf_links[:max_pdfs]):
                pdf_path = self._download_pdf(
                    pdf_info['url'],
                    f"Dallas_{idx + 1}.pdf"
                )
                if pdf_path:
                    pdfs.append(pdf_path)

                time.sleep(self.delay)

        except Exception as e:
            logger.error(f"Failed to scrape Dallas: {e}")

        return pdfs

    def scrape_houston(self, max_pdfs: int = 10) -> List[Path]:
        """Scrape Houston City Council PDFs."""
        logger.info("Scraping Houston City Council...")

        base_url = "https://www.houstontx.gov"
        council_url = f"{base_url}/council/"

        pdfs = []

        try:
            response = requests.get(council_url, headers=self.headers, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            pdf_links = []
            for link in soup.find_all('a', href=True):
                href = link['href']
                if href.endswith('.pdf'):
                    full_url = urljoin(base_url, href)
                    pdf_links.append({
                        'url': full_url,
                        'text': link.get_text(strip=True),
                    })

            logger.info(f"Found {len(pdf_links)} PDF links on Houston's site")

            for idx, pdf_info in enumerate(pdf_links[:max_pdfs]):
                pdf_path = self._download_pdf(
                    pdf_info['url'],
                    f"Houston_{idx + 1}.pdf"
                )
                if pdf_path:
                    pdfs.append(pdf_path)

                time.sleep(self.delay)

        except Exception as e:
            logger.error(f"Failed to scrape Houston: {e}")

        return pdfs

    def scrape_san_antonio(self, max_pdfs: int = 10) -> List[Path]:
        """Scrape San Antonio City Council PDFs."""
        logger.info("Scraping San Antonio City Clerk...")

        base_url = "https://www.sanantonio.gov"
        clerk_url = f"{base_url}/Clerk/Council"

        pdfs = []

        try:
            response = requests.get(clerk_url, headers=self.headers, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            pdf_links = []
            for link in soup.find_all('a', href=True):
                href = link['href']
                if '.pdf' in href.lower():
                    full_url = urljoin(base_url, href)
                    pdf_links.append({
                        'url': full_url,
                        'text': link.get_text(strip=True),
                    })

            logger.info(f"Found {len(pdf_links)} PDF links on San Antonio's site")

            for idx, pdf_info in enumerate(pdf_links[:max_pdfs]):
                pdf_path = self._download_pdf(
                    pdf_info['url'],
                    f"SanAntonio_{idx + 1}.pdf"
                )
                if pdf_path:
                    pdfs.append(pdf_path)

                time.sleep(self.delay)

        except Exception as e:
            logger.error(f"Failed to scrape San Antonio: {e}")

        return pdfs

    def scrape_fort_worth(self, max_pdfs: int = 10) -> List[Path]:
        """Scrape Fort Worth City Secretary PDFs."""
        logger.info("Scraping Fort Worth City Secretary...")

        base_url = "https://www.fortworthtexas.gov"
        secretary_url = f"{base_url}/departments/city-secretary/council-agendas-minutes"

        pdfs = []

        try:
            response = requests.get(secretary_url, headers=self.headers, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            pdf_links = []
            for link in soup.find_all('a', href=True):
                href = link['href']
                if href.endswith('.pdf'):
                    full_url = urljoin(base_url, href)
                    pdf_links.append({
                        'url': full_url,
                        'text': link.get_text(strip=True),
                    })

            logger.info(f"Found {len(pdf_links)} PDF links on Fort Worth's site")

            for idx, pdf_info in enumerate(pdf_links[:max_pdfs]):
                pdf_path = self._download_pdf(
                    pdf_info['url'],
                    f"FortWorth_{idx + 1}.pdf"
                )
                if pdf_path:
                    pdfs.append(pdf_path)

                time.sleep(self.delay)

        except Exception as e:
            logger.error(f"Failed to scrape Fort Worth: {e}")

        return pdfs

    def scrape_all_texas(self, pdfs_per_city: int = 5) -> Dict[str, List[Path]]:
        """
        Scrape all Texas cities.

        Returns:
            Dict mapping city name to list of downloaded PDF paths
        """
        results = {}

        cities = [
            ('Austin', self.scrape_austin),
            ('Dallas', self.scrape_dallas),
            ('Houston', self.scrape_houston),
            ('San Antonio', self.scrape_san_antonio),
            ('Fort Worth', self.scrape_fort_worth),
        ]

        for city_name, scraper_func in cities:
            logger.info(f"\n{'=' * 60}")
            logger.info(f"Scraping {city_name}")
            logger.info('=' * 60)

            try:
                pdfs = scraper_func(max_pdfs=pdfs_per_city)
                results[city_name] = pdfs
                logger.info(f"✓ {city_name}: Downloaded {len(pdfs)} PDFs")
            except Exception as e:
                logger.error(f"✗ {city_name}: {e}")
                results[city_name] = []

            # Delay between cities
            time.sleep(self.delay * 2)

        return results

    def _download_pdf(self, url: str, filename: str) -> Optional[Path]:
        """
        Download a single PDF.

        Args:
            url: PDF URL
            filename: Filename to save as

        Returns:
            Path to downloaded file, or None if failed
        """
        try:
            logger.info(f"Downloading: {url}")

            response = requests.get(url, headers=self.headers, timeout=60, stream=True)
            response.raise_for_status()

            # Verify it's actually a PDF
            content_type = response.headers.get('Content-Type', '').lower()
            if 'pdf' not in content_type and not url.endswith('.pdf'):
                logger.warning(f"Not a PDF: {content_type}")
                return None

            # Save to disk
            file_path = self.download_dir / filename

            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            file_size = file_path.stat().st_size
            logger.info(f"✓ Saved: {filename} ({file_size / 1024:.1f} KB)")

            return file_path

        except Exception as e:
            logger.error(f"Failed to download {url}: {e}")
            return None
