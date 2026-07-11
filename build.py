#!/usr/bin/env python3
import re
import shutil
from pathlib import Path
from datetime import datetime
import markdown

ROOT = Path(__file__).parent
POSTS_DIR = ROOT / "posts"
OUT_DIR = ROOT / "docs"
SITE_TITLE = "diary of a dead man"
SITE_TAGLINE = "still updating"
SITE_URL = "https://hobbyprojs.github.io/diary"

PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{description}">
<link rel="stylesheet" href="{root}style.css">
</head>
<body>
<header class="hero">
  <div class="hero-inner">
    <a class="sitelink" href="{root}index.html">{site_title}</a>
    <p class="tagline">{tagline}</p>
  </div>
</header>
<main>
{content}
</main>
<footer>{footer}</footer>
</body>
</html>
"""

def parse_post(path):
    text = path.read_text(encoding="utf-8")
    meta = {}
    if text.startswith("---"):
        end = text.index("---", 3)
        header = text[3:end].strip()
        for line in header.splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip().lower()] = v.strip()
        body = text[end + 3:].strip()
    else:
        body = text.strip()

    stem = path.stem
    m = re.match(r"(\d{4}-\d{2}-\d{2})-(.+)", stem)
    if m:
        default_date, slug = m.group(1), m.group(2)
    else:
        default_date, slug = datetime.today().strftime("%Y-%m-%d"), stem

    meta.setdefault("date", default_date)
    meta.setdefault("title", slug.replace("-", " ").title())
    meta["slug"] = slug
    meta["html"] = markdown.markdown(body, extensions=["fenced_code", "tables"])
    meta["excerpt"] = strip_tags(meta["html"])[:220].rsplit(" ", 1)[0] + "..."
    return meta

def strip_tags(html):
    return
