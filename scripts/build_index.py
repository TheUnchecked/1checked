import os
import re
from datetime import datetime
from bs4 import BeautifulSoup

ARTICLES_DIR = "articoli"
OUTPUT_FILE = "index.html"
FEED_FILE = "feed.xml"
BASE_URL = "https://theunchecked.github.io/theunchecked"

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
    return {
        "title": title,
        "subtitle": subtitle,
        "date": date,
        "tags": tags,
        "file": filename,
        "read_time": read_time
    }

def format_date_short(date_str):
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        months = ["Gen","Feb","Mar","Apr","Mag","Giu","Lug","Ago","Set","Ott","Nov","Dic"]
        return f"{months[dt.month-1]} {dt.day:02d}"
    except:
        return date_str

def build_card(article, index):
    tags_html = "".join(f'<span class="tag">{t}</span>' for t in article["tags"])
    date_short = format_date_short(article["date"])
    num = str(index + 1).zfill(2)
    return f"""
      <a class="card" href="articoli/{article['file']}">
        <div class="card-num">{num}</div>
        <div class="card-date">{date_short} · {article['read_time']} min</div>
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
    <title>The Unchecked</title>
    <link>{BASE_URL}/</link>
    <description>Non dare niente per scontato. Mai.</description>
    <language>it</language>
    <lastBuildDate>{now}</lastBuildDate>
    <atom:link href="{BASE_URL}/feed.xml" rel="self" type="application/rss+xml"/>{items}
  </channel>
</rss>"""

def build_index(articles):
    articles.sort(key=lambda a: a["date"], reverse=True)
    count = len(articles)
    cards_html = "".join(build_card(a, i) for i, a in enumerate(articles))

    # Hero: prende il titolo dell'articolo più recente
    latest = articles[0] if articles else None
    hero_num = str(count).zfill(2)
    hero_title = latest["title"] if latest else "The Unchecked"
    # Mette in <mark> l'ultima parola del titolo
    words = hero_title.split()
    if len(words) > 1:
        hero_title_html = " ".join(words[:-1]) + f" <mark>{words[-1]}</mark>"
    else:
        hero_title_html = f"<mark>{hero_title}</mark>"

    return f"""<!DOCTYPE html>
<html lang="it" data-theme="dark">
<head>
  <script>(function(){{var t;try{{t=localStorage.getItem('theme')}}catch(e){{}}document.documentElement.dataset.theme=t||'dark'}})()</script>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>The Unchecked</title>
  <meta name="description" content="Non dare niente per scontato. Mai. IT, sicurezza, AI, lavoro.">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="The Unchecked">
  <meta property="og:title" content="The Unchecked">
  <meta property="og:description" content="Non dare niente per scontato. Mai. IT, sicurezza, AI, lavoro.">
  <meta property="og:image" content="{BASE_URL}/assets/favicon.png">
  <meta property="og:url" content="{BASE_URL}/">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="The Unchecked">
  <meta name="twitter:description" content="Non dare niente per scontato. Mai.">
  <link rel="icon" type="image/png" href="assets/favicon.png">
  <link rel="alternate" type="application/rss+xml" title="The Unchecked" href="{BASE_URL}/feed.xml">
  <link rel="stylesheet" href="style.css">
</head>
<body>

  <nav>
    <a href="index.html" class="logo"><span style="color:#c0392b">[</span> Unchecked <span style="color:#c0392b">]</span></a>
    <div class="nav-right">
      <ul class="nav-links">
        <li><a href="index.html">Home</a></li>
        <li><a href="#articoli">Articoli</a></li>
        <li><a href="https://github.com/theunchecked/theunchecked" target="_blank">GitHub</a></li>
      </ul>
      <button id="theme-toggle" aria-label="Toggle theme">
        <svg id="theme-icon-dark" viewBox="0 0 24 24"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
        <svg id="theme-icon-light" viewBox="0 0 24 24"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>
      </button>
    </div>
  </nav>

  <section class="hero">
    <div>
      <div class="hero-eyebrow">Ultimo articolo</div>
      <span class="hero-number">{hero_num}</span>
      <h1 class="hero-title">{hero_title_html}</h1>
      <p class="hero-desc">Non dare niente per scontato. Mai. dentro alla realtà.</p>
    </div>
    <div class="hero-right">
      <div class="hero-stat-label">Articoli</div>
      <div class="hero-stat-num">{count:02d}</div>
      <div class="hero-stat-sub">pubblicati</div>
    </div>
  </section>

  <div class="featured">
    <div class="featured-label">The Unchecked</div>
    <div class="featured-quote">"Non dare niente per scontato. Mai. dentro alla realtà."</div>
    <div class="featured-byline">theunchecked</div>
  </div>

  <section class="section" id="articoli">
    <div class="section-header">
      <div class="section-title">Articoli recenti</div>
      <div class="section-count">{count:02d}</div>
    </div>
    <div class="grid">{cards_html}
    </div>
  </section>

  <footer>
    <span>theunchecked</span>
    <span>pubblicato su <a href="https://github.com/theunchecked/theunchecked">github</a></span>
  </footer>

  <script>
    const toggle = document.getElementById('theme-toggle');
    const html = document.documentElement;
    toggle.addEventListener('click', () => {{
      const next = html.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      html.setAttribute('data-theme', next);
      localStorage.setItem('theme', next);
    }});
    const observer = new IntersectionObserver((entries) => {{
      entries.forEach((e, i) => {{
        if (e.isIntersecting) setTimeout(() => e.target.classList.add('visible'), i * 120);
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
