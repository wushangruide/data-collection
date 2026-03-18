"""
Postdoc job alert system - main entry point.
Scrapes academic job sites every 12 hours and pushes new matching jobs via Server酱.

Usage:
    python main.py          # run once immediately, then schedule
    python main.py --once   # run once and exit
"""
import argparse
import logging
import schedule
import time

from config import INTERVAL_HOURS
from db import get_conn, is_new, mark_seen
from filters import is_relevant
from scrapers import scrape_all
from notifier import push_jobs

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("postdoc_alerts.log", encoding="utf-8"),
    ]
)
logger = logging.getLogger(__name__)


def run_once():
    logger.info("开始爬取博后职位...")
    conn = get_conn()

    all_jobs = scrape_all()
    logger.info(f"共抓取 {len(all_jobs)} 条职位")

    new_relevant = []
    for job in all_jobs:
        if not is_relevant(job["title"], location=job.get("location", "")):
            continue
        if is_new(conn, job["title"], job["url"]):
            new_relevant.append(job)
            mark_seen(conn, job["title"], job["url"], job["source"])

    logger.info(f"过滤后新职位 {len(new_relevant)} 条，准备推送")
    push_jobs(new_relevant)

    conn.close()
    logger.info("本轮爬取完成")


def main():
    parser = argparse.ArgumentParser(description="Postdoc job alert system")
    parser.add_argument("--once", action="store_true", help="Run once and exit")
    args = parser.parse_args()

    if args.once:
        run_once()
        return

    # Run immediately on start, then schedule
    run_once()
    schedule.every(INTERVAL_HOURS).hours.do(run_once)
    logger.info(f"调度已启动，每 {INTERVAL_HOURS} 小时爬取一次")

    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    main()
