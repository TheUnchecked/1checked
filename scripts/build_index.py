import os
import re
from datetime import datetime
from bs4 import BeautifulSoup

ARTICLES_DIR = "articoli"
OUTPUT_FILE = "index.html"
FEED_FILE = "feed.xml"
BASE_URL = "https://theblacksheepblog.github.io/the.black.sheep"

TAG_COLORS = {
    "ai": "green", "exchange": "green", "certificazioni": "green",
    "security": "warm", "lavoro": "warm",
    "agent": "blue", "active directory": "blue", "it career": "blue",
    "shared permissions model": "orange", "formazione": "orange",
    "strategia": "purple", "rbac": "purple", "mindset": "purple",
}

def get_tag_color(tag_text):
    return TAG_COLORS.get(tag_text.lower(), "blue")

def extract_article_data(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    title = ""
    t = soup.find(class_="article-page-title")
    if t:
        title = t.get_text(separator=" ", strip=True)

    subtitle = ""
    content = soup.find(class_="article-content")
    if content:
        first_p = content.find("p")
        if first_p:
            text = first_p.get_text(strip=True)
            subtitle = text[:160] + ("..." if len(text) > 160 else "")

    date = ""
    m = soup.find(class_="article-meta")
    if m:
        match = re.search(r"\d{4}-\d{2}-\d{2}", m.get_text())
        if match:
            date = match.group()

    tags = []
    for tag in soup.find_all(class_="tag"):
        tags.append(tag.get_text(strip=True))

    read_time = 1
    if content:
        words = len(content.get_text().split())
        read_time = max(1, round(words / 200))

    filename = os.path.basename(filepath)
    return {"title": title, "subtitle": subtitle, "date": date, "tags": tags, "file": filename, "read_time": read_time}

def build_card(article):
    tags_html = "".join(
        f'<span class="tag {get_tag_color(t)}">{t}</span>'
        for t in article["tags"]
    )
    return f"""
      <a class="card" href="articoli/{article['file']}">
        <span class="card-date">{article['date']} &nbsp;·&nbsp; {article['read_time']} min</span>
        <h3>{article['title']}</h3>
        <p>{article['subtitle']}</p>
        <div class="tags">{tags_html}</div>
      </a>"""

def date_to_rfc822(date_str):
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return dt.strftime("%a, %d %b %Y 00:00:00 +0000")
    except:
        return ""

def build_feed(articles):
    now = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S +0000")
    items = ""
    for a in articles:
        url = f"{BASE_URL}/articoli/{a['file']}"
        pub_date = date_to_rfc822(a["date"])
        # Escape XML special chars in title and subtitle
        title = a["title"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        desc = a["subtitle"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        items += f"""
    <item>
      <title>{title}</title>
      <link>{url}</link>
      <guid>{url}</guid>
      <pubDate>{pub_date}</pubDate>
      <description>{desc}</description>
    </item>"""

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>The Black Sheep</title>
    <link>{BASE_URL}/</link>
    <description>Scrivo quello che penso. Fuori dal gregge.</description>
    <language>it</language>
    <lastBuildDate>{now}</lastBuildDate>
    <atom:link href="{BASE_URL}/feed.xml" rel="self" type="application/rss+xml"/>{items}
  </channel>
</rss>"""

def build_index(articles):
    articles.sort(key=lambda a: a["date"], reverse=True)
    cards_html = "".join(build_card(a) for a in articles)

    return f"""<!DOCTYPE html>
<html lang="it" data-theme="dark">
<head>
  <script>(function(){{var t;try{{t=localStorage.getItem('theme')}}catch(e){{}}document.documentElement.dataset.theme=t||'dark'}})()</script>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>The Black Sheep</title>
  <meta name="description" content="Scrivo quello che penso. Fuori dal gregge. IT, sicurezza, AI, lavoro.">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="The Black Sheep">
  <meta property="og:title" content="The Black Sheep">
  <meta property="og:description" content="Scrivo quello che penso. Fuori dal gregge. IT, sicurezza, AI, lavoro.">
  <meta property="og:image" content="{BASE_URL}/assets/favicon.png">
  <meta property="og:url" content="{BASE_URL}/">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="The Black Sheep">
  <meta name="twitter:description" content="Scrivo quello che penso. Fuori dal gregge.">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700;900&family=Inter:wght@400;500&display=swap" rel="stylesheet">
  <link rel="icon" type="image/png" href="assets/favicon.png">
  <link rel="stylesheet" href="style.css">
  <link rel="alternate" type="application/rss+xml" title="The Black Sheep" href="{BASE_URL}/feed.xml">
</head>
<body>

  <nav>
    <a href="index.html" class="logo">THE BLACK SHEEP</a>
    <div class="nav-right">
      <ul class="nav-links">
        <li><a href="index.html">Home</a></li>
        <li><a href="#articoli">Articoli</a></li>
        <li><a href="https://github.com/TheBlackSheepBlog/the.black.sheep" target="_blank">GitHub</a></li>
      </ul>
      <button id="theme-toggle" aria-label="Toggle theme">
        <svg id="theme-icon-dark" viewBox="0 0 24 24"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
        <svg id="theme-icon-light" viewBox="0 0 24 24"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>
      </button>
    </div>
  </nav>

  <section class="hero">
    <h1 class="hero-title">THE BLACK SHEEP</h1>
    <p class="hero-sub"><svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" style="width:16px;height:16px;vertical-align:middle;margin-right:7px;stroke:var(--text-secondary);fill:none;stroke-width:2;stroke-linecap:round;stroke-linejoin:round"><rect x="3" y="3" width="18" height="18" rx="2"/><line x1="7" y1="7" x2="17" y2="7"/><line x1="7" y1="15" x2="13" y2="15"/></svg>TheBlackSheepBlog</p>
    <p class="hero-desc">Scrivo quello che penso. Fuori dal gregge.</p>
    <a class="scroll-hint" href="#articoli">&#x2193; &nbsp; articoli</a>
  </section>

  <section class="section" id="articoli">
    <h2 class="section-title"><svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" style="width:20px;height:20px;vertical-align:middle;margin-right:8px;stroke:var(--accent);fill:none;stroke-width:2;stroke-linecap:round;stroke-linejoin:round"><rect x="3" y="3" width="18" height="18" rx="2"/><line x1="7" y1="7" x2="17" y2="7"/><line x1="7" y1="11" x2="17" y2="11"/><line x1="7" y1="15" x2="13" y2="15"/></svg>Articoli</h2>
    <p class="section-subtitle">Pensieri, analisi e osservazioni fuori dal gregge.</p>
    <div class="grid">{cards_html}
    </div>
  </section>

  <footer>
    the.black.sheep &mdash; <a href="https://github.com/TheBlackSheepBlog/the.black.sheep">github</a>
  </footer>

  <script>
    const toggle = document.getElementById('theme-toggle');
    const html = document.documentElement;
    toggle.addEventListener('click', () => {{
      const next = html.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      html.setAttribute('data-theme', next);
      localStorage.setItem('theme', next);
    }});
    window.addEventListener('scroll', () => {{
      document.querySelector('nav').style.borderBottomColor = window.scrollY > 50 ? 'var(--border-subtle)' : 'transparent';
    }});
    const observer = new IntersectionObserver((entries) => {{
      entries.forEach((e, i) => {{
        if (e.isIntersecting) setTimeout(() => e.target.classList.add('visible'), i * 100);
      }});
    }}, {{ threshold: 0.1 }});
    document.querySelectorAll('.card').forEach(c => observer.observe(c));
  </script>

</body>
</html>"""

def main():
    if not os.path.exists(ARTICLES_DIR):
        print(f"Cartella '{ARTICLES_DIR}' non trovata.")
        return

    articles = []
    for fname in sorted(os.listdir(ARTICLES_DIR)):
        if fname.endswith(".html"):
            fpath = os.path.join(ARTICLES_DIR, fname)
            data = extract_article_data(fpath)
            if data["title"]:
                articles.append(data)
                print(f"  + {fname} — {data['date']} — {data['title'][:50]}")

    articles.sort(key=lambda a: a["date"], reverse=True)

    html = build_index(articles)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"\nindex.html aggiornato con {len(articles)} articoli.")

    feed = build_feed(articles)
    with open(FEED_FILE, "w", encoding="utf-8") as f:
        f.write(feed)
    print(f"feed.xml aggiornato con {len(articles)} articoli.")

if __name__ == "__main__":
    main()
