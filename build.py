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
<header>
  <a class="sitelink" href="{root}index.html">{site_title}</a>
  <p class="tagline">{tagline}</p>
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
    return re.sub("<[^<]+?>", "", html)

def build():
    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir()
    (OUT_DIR / "posts").mkdir()
    shutil.copy(ROOT / "style.css", OUT_DIR / "style.css")

    posts = [parse_post(p) for p in POSTS_DIR.glob("*.md")]
    posts.sort(key=lambda p: p["date"], reverse=True)

    for post in posts:
        content = f"""<article>
  <h1>{post['title']}</h1>
  <p class="meta">{post['date']}</p>
  {post['html']}
</article>
<p class="back"><a href="../index.html">&larr; back to all posts</a></p>"""
        page = PAGE.format(
            title=f"{post['title']} — {SITE_TITLE}",
            description=post['excerpt'],
            root="../",
            site_title=SITE_TITLE,
            tagline=SITE_TAGLINE,
            content=content,
            footer=f"{SITE_TITLE}, built with plain files"
        )
        (OUT_DIR / "posts" / f"{post['slug']}.html").write_text(page, encoding="utf-8")

    if posts:
        list_items = "\n".join(
            f"""<div class="entry">
  <a class="entry-title" href="posts/{p['slug']}.html">{p['title']}</a>
  <p class="meta">{p['date']}</p>
  <p class="excerpt">{p['excerpt']}</p>
</div>"""
            for p in posts
        )
    else:
        list_items = '<p class="meta">nothing posted yet.</p>'

    index_content = f"<div class=\"entries\">\n{list_items}\n</div>"
    index_page = PAGE.format(
        title=SITE_TITLE,
        description=SITE_TAGLINE,
        root="",
        site_title=SITE_TITLE,
        tagline=SITE_TAGLINE,
        content=index_content,
        footer=f"{SITE_TITLE}, built with plain files"
    )
    (OUT_DIR / "index.html").write_text(index_page, encoding="utf-8")

    (OUT_DIR / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n", encoding="utf-8"
    )

    urls = [f"{SITE_URL}/"] + [f"{SITE_URL}/posts/{p['slug']}.html" for p in posts]
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    sitemap += "\n".join(f"  <url><loc>{u}</loc></url>" for u in urls)
    sitemap += "\n</urlset>\n"
    (OUT_DIR / "sitemap.xml").write_text(sitemap, encoding="utf-8")

    print(f"Built {len(posts)} post(s) into {OUT_DIR}")

if __name__ == "__main__":
    build()
