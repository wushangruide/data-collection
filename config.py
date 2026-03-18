"""
Configuration for postdoc job alerts.
Edit KEYWORDS, REGIONS, and SERVERCHAN_KEY before running.
"""

# Server酱推送 Key（在 https://sct.ftqq.com/ 获取）
SERVERCHAN_KEY = "YOUR_SERVERCHAN_KEY_HERE"

# 关键词过滤（职位标题/描述中含任意一个即匹配）
KEYWORDS = [
    # CS / 计算机科学
    "computer science", "machine learning", "deep learning", "artificial intelligence",
    "data science", "natural language processing", "NLP", "computer vision",
    "software engineering", "algorithm", "HCI", "human-computer interaction",
    "cybersecurity", "distributed systems", "cloud computing",

    # 心理学
    "psychology", "cognitive science", "neuroscience", "behavioral science",
    "clinical psychology", "social psychology", "developmental psychology",
    "psychotherapy", "mental health", "cognitive psychology",

    # 社会学
    "sociology", "social science", "social work", "anthropology",
    "political science", "public policy", "demography",
    "criminology", "urban studies", "social inequality",
]

# 地区过滤（留空表示不过滤地区）
# 示例: ["USA", "UK", "Canada", "Europe", "China"]
REGIONS = []

# 爬取间隔（小时）
INTERVAL_HOURS = 12

# 数据库路径
DB_PATH = "postdoc_jobs.db"
