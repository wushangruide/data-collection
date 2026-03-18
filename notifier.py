"""
Server酱 push notification to WeChat.
"""
import logging
import requests
import config

logger = logging.getLogger(__name__)

SERVERCHAN_URL = "https://sctapi.ftqq.com/{key}.send"


def push_jobs(jobs: list[dict]):
    """Push a batch of new jobs via Server酱."""
    if not jobs:
        return
    if config.SERVERCHAN_KEY == "YOUR_SERVERCHAN_KEY_HERE":
        logger.warning("Server酱 key not configured, skipping push.")
        _print_jobs(jobs)
        return

    title = f"📢 博后职位更新：{len(jobs)} 条新职位"
    lines = []
    for j in jobs:
        lines.append(f"**[{j['title']}]({j['url']})**")
        if j.get("location"):
            lines.append(f"📍 {j['location']}")
        lines.append(f"来源: {j['source']}")
        lines.append("---")

    content = "\n".join(lines)
    _send(title, content)


def _send(title: str, content: str):
    url = SERVERCHAN_URL.format(key=config.SERVERCHAN_KEY)
    try:
        resp = requests.post(url, data={"title": title, "desp": content}, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if data.get("code") == 0:
            logger.info(f"Server酱推送成功: {title}")
        else:
            logger.error(f"Server酱推送失败: {data}")
    except Exception as e:
        logger.error(f"Server酱推送异常: {e}")


def _print_jobs(jobs: list[dict]):
    """Fallback: print to console when key not configured."""
    print(f"\n{'='*60}")
    print(f"[预览] 发现 {len(jobs)} 条新博后职位:")
    for j in jobs:
        print(f"  [{j['source']}] {j['title']}")
        print(f"    {j['url']}")
        if j.get("location"):
            print(f"    📍 {j['location']}")
    print('='*60)
