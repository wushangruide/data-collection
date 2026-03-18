"""
Scrapers for academic postdoc job sites.
Each scraper returns a list of dicts: {title, url, location, source}
"""
import logging
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}
TIMEOUT = 15


def _get(url):
    resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "lxml")


# ── AcademicJobsOnline ──────────────────────────────────────────────────────

def scrape_academicjobsonline():
    jobs = []
    try:
        # Search postdoc positions
        url = "https://academicjobsonline.org/ajo/jobs?field0=&type=2&country=&deadline=&limit=50"
        soup = _get(url)
        rows = soup.select("table.jobtable tr")
        for row in rows[1:]:  # skip header
            cols = row.find_all("td")
            if len(cols) < 3:
                continue
            a = cols[0].find("a")
            if not a:
                continue
            title = a.get_text(strip=True)
            href = a.get("href", "")
            link = f"https://academicjobsonline.org{href}" if href.startswith("/") else href
            location = cols[2].get_text(strip=True) if len(cols) > 2 else ""
            jobs.append({"title": title, "url": link, "location": location, "source": "AcademicJobsOnline"})
    except Exception as e:
        logger.error(f"AcademicJobsOnline scrape failed: {e}")
    return jobs


# ── jobs.ac.uk ──────────────────────────────────────────────────────────────

def scrape_jobs_ac_uk():
    jobs = []
    try:
        url = "https://www.jobs.ac.uk/search/?keywords=postdoc&sort=date"
        soup = _get(url)
        articles = soup.select("article.j-search-result")
        for art in articles:
            a = art.select_one("h2 a") or art.select_one("h3 a")
            if not a:
                continue
            title = a.get_text(strip=True)
            href = a.get("href", "")
            link = f"https://www.jobs.ac.uk{href}" if href.startswith("/") else href
            loc_el = art.select_one(".j-search-result__location")
            location = loc_el.get_text(strip=True) if loc_el else ""
            jobs.append({"title": title, "url": link, "location": location, "source": "jobs.ac.uk"})
    except Exception as e:
        logger.error(f"jobs.ac.uk scrape failed: {e}")
    return jobs


# ── Nature Careers ──────────────────────────────────────────────────────────

def scrape_nature_careers():
    jobs = []
    try:
        url = "https://www.nature.com/naturecareers/jobs/postdoc?sort=date"
        soup = _get(url)
        items = soup.select("li.js-result")
        for item in items:
            a = item.select_one("h3 a") or item.select_one("a.js-result-title")
            if not a:
                continue
            title = a.get_text(strip=True)
            href = a.get("href", "")
            link = f"https://www.nature.com{href}" if href.startswith("/") else href
            loc_el = item.select_one(".location") or item.select_one("[class*='location']")
            location = loc_el.get_text(strip=True) if loc_el else ""
            jobs.append({"title": title, "url": link, "location": location, "source": "NatureCareers"})
    except Exception as e:
        logger.error(f"NatureCareers scrape failed: {e}")
    return jobs


# ── HigherEdJobs (US academic) ───────────────────────────────────────────────

def scrape_higheredjobs():
    jobs = []
    try:
        url = "https://www.higheredjobs.com/faculty/search.cfm?JobCat=21&PosType=2&InstType=1&Keyword=postdoc&Remote=1&Remote=2&Remote=3&NumJobs=50"
        soup = _get(url)
        for row in soup.select("tr.result-row"):
            a = row.select_one("a.job-title")
            if not a:
                continue
            title = a.get_text(strip=True)
            href = a.get("href", "")
            link = f"https://www.higheredjobs.com{href}" if href.startswith("/") else href
            loc_el = row.select_one(".location")
            location = loc_el.get_text(strip=True) if loc_el else ""
            jobs.append({"title": title, "url": link, "location": location, "source": "HigherEdJobs"})
    except Exception as e:
        logger.error(f"HigherEdJobs scrape failed: {e}")
    return jobs


def scrape_all():
    """Run all scrapers and return combined job list."""
    all_jobs = []
    for fn in [scrape_academicjobsonline, scrape_jobs_ac_uk, scrape_nature_careers, scrape_higheredjobs]:
        results = fn()
        logger.info(f"{fn.__name__}: {len(results)} jobs fetched")
        all_jobs.extend(results)
    return all_jobs
