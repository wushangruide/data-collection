# 博后职位实时监控 & 微信推送

自动爬取多个学术招聘网站的博后职位，按关键词/地区过滤后通过 **Server酱** 推送到微信。

## 功能

- 监控网站：AcademicJobsOnline、jobs.ac.uk、Nature Careers、HigherEdJobs
- 关键词过滤：CS / 心理学 / 社会学方向
- 去重：已推送职位不再重复推送
- 每 **12小时** 自动爬取一次

## 快速开始

### 1. 安装依赖

```bash
pip install requests beautifulsoup4 lxml schedule python-dotenv
```

### 2. 配置 Server酱

1. 访问 [https://sct.ftqq.com/](https://sct.ftqq.com/) 用微信扫码登录
2. 复制 **SendKey**
3. 编辑 `config.py`，将 `SERVERCHAN_KEY` 替换为你的 Key：

```python
SERVERCHAN_KEY = "SCT...你的key..."
```

### 3. 自定义关键词/地区（可选）

编辑 `config.py`：

```python
# 添加或删除关键词
KEYWORDS = ["machine learning", "psychology", ...]

# 指定地区（留空 = 不过滤地区）
REGIONS = ["USA", "UK", "Canada"]
```

### 4. 运行

```bash
# 持续运行（每12小时爬取一次）
python main.py

# 仅运行一次（测试用）
python main.py --once
```

## 文件结构

```
├── main.py        # 入口，调度逻辑
├── scrapers.py    # 各网站爬虫
├── filters.py     # 关键词/地区过滤
├── notifier.py    # Server酱推送
├── db.py          # SQLite去重数据库
├── config.py      # 配置文件（修改这里）
└── requirements.txt
```

## 后台运行

```bash
# Linux/Mac 后台运行并记录日志
nohup python main.py > /dev/null 2>&1 &

# 或使用 screen
screen -S postdoc-alerts
python main.py
# Ctrl+A D 退出 screen
```
