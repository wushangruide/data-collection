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


# ── PostdocJobs.com ──────────────────────────────────────────────────────────

def scrape_postdocjobs():
    jobs = []
    try:
        url = "https://www.postdocjobs.com/posting/list"
        soup = _get(url)
        for item in soup.select("div.job-listing, article.posting, div.listing-item"):
            a = item.find("a", href=True)
            if not a:
                continue
            title = a.get_text(strip=True)
            href = a.get("href", "")
            link = f"https://www.postdocjobs.com{href}" if href.startswith("/") else href
            loc_el = item.select_one(".location, .job-location, [class*='location']")
            location = loc_el.get_text(strip=True) if loc_el else ""
            if title:
                jobs.append({"title": title, "url": link, "location": location, "source": "PostdocJobs"})
    except Exception as e:
        logger.error(f"PostdocJobs scrape failed: {e}")
    return jobs


# ── Academic Positions ────────────────────────────────────────────────────────

def scrape_academic_positions():
    jobs = []
    try:
        # Fetch CS + social sciences postdoc listings separately and combine
        urls = [
            ("https://academicpositions.com/jobs/position/post-doc/field/computer-science-mf", "CS"),
            ("https://academicpositions.com/jobs/position/post-doc/field/social-science", "SocSci"),
            ("https://academicpositions.com/jobs/position/post-doc/field/psychology", "Psychology"),
        ]
        seen = set()
        for url, _ in urls:
            soup = _get(url)
            for item in soup.select("article.job, div.job-item, li.job-listing"):
                a = item.select_one("h2 a, h3 a, a.job-title, a[href*='/ad/']")
                if not a:
                    continue
                title = a.get_text(strip=True)
                href = a.get("href", "")
                link = f"https://academicpositions.com{href}" if href.startswith("/") else href
                if link in seen:
                    continue
                seen.add(link)
                loc_el = item.select_one(".location, .country, [class*='location']")
                location = loc_el.get_text(strip=True) if loc_el else ""
                if title:
                    jobs.append({"title": title, "url": link, "location": location, "source": "AcademicPositions"})
    except Exception as e:
        logger.error(f"AcademicPositions scrape failed: {e}")
    return jobs


# ── Chronicle of Higher Education ────────────────────────────────────────────

def scrape_chronicle():
    jobs = []
    try:
        urls = [
            "https://jobs.chronicle.com/jobs/social-and-behavioral-sciences/post-doc/",
            "https://jobs.chronicle.com/jobs/information-technology/post-doc/",
        ]
        seen = set()
        for url in urls:
            soup = _get(url)
            for item in soup.select("li.jlr, article.job, div.job-result, li[class*='result']"):
                a = item.select_one("h2 a, h3 a, a.job-link, a[href*='/job/']")
                if not a:
                    continue
                title = a.get_text(strip=True)
                href = a.get("href", "")
                link = f"https://jobs.chronicle.com{href}" if href.startswith("/") else href
                if link in seen:
                    continue
                seen.add(link)
                loc_el = item.select_one(".location, [class*='location']")
                location = loc_el.get_text(strip=True) if loc_el else ""
                if title:
                    jobs.append({"title": title, "url": link, "location": location, "source": "ChronicleJobs"})
    except Exception as e:
        logger.error(f"Chronicle scrape failed: {e}")
    return jobs


# ── Inside Higher Ed ──────────────────────────────────────────────────────────

def scrape_insidehighered():
    jobs = []
    try:
        urls = [
            "https://careers.insidehighered.com/jobs/social-sciences/postdoc/",
            "https://careers.insidehighered.com/jobs/computer-science/postdoc/",
        ]
        seen = set()
        for url in urls:
            soup = _get(url)
            for item in soup.select("li.jlr, article.job, div.job-result, div[class*='listing']"):
                a = item.select_one("h2 a, h3 a, a[href*='/job/']")
                if not a:
                    continue
                title = a.get_text(strip=True)
                href = a.get("href", "")
                link = f"https://careers.insidehighered.com{href}" if href.startswith("/") else href
                if link in seen:
                    continue
                seen.add(link)
                loc_el = item.select_one(".location, [class*='location']")
                location = loc_el.get_text(strip=True) if loc_el else ""
                if title:
                    jobs.append({"title": title, "url": link, "location": location, "source": "InsideHigherEd"})
    except Exception as e:
        logger.error(f"InsideHigherEd scrape failed: {e}")
    return jobs


# ── THE UniJobs ───────────────────────────────────────────────────────────────

def scrape_the_unijobs():
    jobs = []
    try:
        urls = [
            "https://www.timeshighereducation.com/unijobs/listings/computer-science/postdocs/",
            "https://www.timeshighereducation.com/unijobs/listings/social-sciences/postdocs/",
            "https://www.timeshighereducation.com/unijobs/listings/psychology/postdocs/",
        ]
        seen = set()
        for url in urls:
            soup = _get(url)
            for item in soup.select("article, li.job, div.job-item, div[class*='listing']"):
                a = item.select_one("h2 a, h3 a, a.job-title, a[href*='/unijobs/job/']")
                if not a:
                    continue
                title = a.get_text(strip=True)
                href = a.get("href", "")
                link = f"https://www.timeshighereducation.com{href}" if href.startswith("/") else href
                if link in seen:
                    continue
                seen.add(link)
                loc_el = item.select_one(".location, [class*='location']")
                location = loc_el.get_text(strip=True) if loc_el else ""
                if title:
                    jobs.append({"title": title, "url": link, "location": location, "source": "THEUniJobs"})
    except Exception as e:
        logger.error(f"THEUniJobs scrape failed: {e}")
    return jobs


def scrape_all():
    """Run all scrapers and return combined job list."""
    all_jobs = []
    for fn in [
        scrape_academicjobsonline,
        scrape_jobs_ac_uk,
        scrape_nature_careers,
        scrape_higheredjobs,
        scrape_postdocjobs,
        scrape_academic_positions,
        scrape_chronicle,
        scrape_insidehighered,
        scrape_the_unijobs,
    ]:
        results = fn()
        logger.info(f"{fn.__name__}: {len(results)} jobs fetched")
        all_jobs.extend(results)
    return all_jobs
