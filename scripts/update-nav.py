import os
import re

ARTICLES = [
    {"file": "la-matematica-degli-agent.html", "num": "10", "title": "La matematica degli agent non mente, ma siamo sicuri che basti questo?", "tags": ["AI", "Lavoro"]},
    {"file": "exchange-split-permissions.html", "num": "09", "title": "Exchange on-prem: il rischio che dorme nella tua configurazione di default", "tags": ["Exchange", "Security"]},
    {"file": "ho-fallito-la-certificazione.html", "num": "08", "title": "27 anni di IT. Bocciato per 20 centesimi.", "tags": ["IT Career"]},
    {"file": "zero-trust.html", "num": "07", "title": "Zero Trust non è un prodotto. È una mentalità.", "tags": ["Security"]},
    {"file": "domain-join-risks.html", "num": "06", "title": "La falla silenziosa: i rischi dell'account Domain Join.", "tags": ["Active Directory", "Security"]},
    {"file": "adminsdholder.html", "num": "05", "title": "AdminSDHolder: perché i tuoi permessi spariscono ogni 60 minuti.", "tags": ["Active Directory"]},
    {"file": "rc4-kerberos-2026.html", "num": "04", "title": "RC4 e Kerberos: hai tempo fino a luglio 2026.", "tags": ["Kerberos", "Security"]},
    {"file": "azure-storage.html", "num": "03", "title": "Azure Storage: scegli la ridondanza sbagliata e lo scopri nel momento peggiore.", "tags": ["Azure", "Cloud"]},
    {"file": "la-vita-và-così.html", "num": "02", "title": "Ovidio Marras: l'eroe che nessuno di noi sarebbe.", "tags": ["Società"]},
    {"file": "IA-Lavoro.html", "num": "01", "title": "L'IA ci ruberà il lavoro? Solo se lo meriti.", "tags": ["AI", "Lavoro"]},
]

HTML_NAV = """
<nav class="article-nav" id="article-nav"></nav>
<div style="text-align:center;">
  <a href="../index.html" class="nav-back-home" id="back-home-link">← Tutti gli articoli</a>
</div>"""

JS_ARTICLES = "const ARTICLES = " + str(ARTICLES).replace("'", '"').replace("True", "true").replace("False", "false") + ";"

JS_NAV = """
const ARTICLES = """ + str([
    {"file": a["file"], "num": a["num"], "title": a["title"], "tags": a["tags"]}
    for a in ARTICLES
]).replace("'", '"') + """;

(function() {
  const currentFile = window.location.pathname.split('/').pop();
  const idx = ARTICLES.findIndex(a => a.file === currentFile);
  if (idx === -1) return;

  const prev = idx > 0 ? ARTICLES[idx - 1] : null;
  const next = idx < ARTICLES.length - 1 ? ARTICLES[idx + 1] : null;

  function buildLink(article, direction) {
    if (!article) {
      return `<div class="article-nav-link nav-${direction} nav-placeholder">
        <span class="nav-direction">${direction === 'prev' ? '← Precedente' : 'Successivo →'}</span>
      </div>`;
    }
    const tags = article.tags.map(t => `<span class="nav-tag">${t}</span>`).join('');
    const label = direction === 'prev' ? '← Precedente' : 'Successivo →';
    return `<a class="article-nav-link nav-${direction}" href="${article.file}" data-href="${article.file}">
      <span class="nav-direction">${label}</span>
      <span class="nav-num">${article.num}</span>
      <span class="nav-title">${article.title}</span>
      <div style="display:flex;flex-wrap:wrap;gap:0.6rem;margin-top:0.2rem;">${tags}</div>
    </a>`;
  }

  const nav = document.getElementById('article-nav');
  if (nav) {
    nav.innerHTML = buildLink(prev, 'prev') + buildLink(next, 'next');
    nav.querySelectorAll('a[data-href]').forEach(link => {
      link.addEventListener('click', e => {
        e.preventDefault();
        document.body.classList.add('fade-out');
        setTimeout(() => { window.location.href = link.getAttribute('data-href'); }, 260);
      });
    });
  }

  const backHome = document.getElementById('back-home-link');
  if (backHome) {
    backHome.addEventListener('click', e => {
      e.preventDefault();
      document.body.classList.add('fade-out');
      setTimeout(() => { window.location.href = backHome.href; }, 260);
    });
  }
})();"""

OLD_BACKLINK = re.compile(
    r'<div[^>]*style="margin-top:3rem.*?</div>\s*\n?\s*</article>',
    re.DOTALL
)

OLD_JS = re.compile(
    r'const backLink = document\.getElementById\("back-link"\);.*?}\s*\n?\s*}',
    re.DOTALL
)

articles_dir = "articoli"

for article in ARTICLES:
    filepath = os.path.join(articles_dir, article["file"])
    if not os.path.exists(filepath):
        print(f"⚠️  Non trovato: {filepath}")
        continue

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Salta se già aggiornato
    if 'id="article-nav"' in content:
        print(f"✅ Già aggiornato: {article['file']}")
        continue

    # Sostituisce il vecchio div back-link
    content = re.sub(
        r'<div style="margin-top:3rem.*?</div>\s*(?=\s*</article>)',
        HTML_NAV + "\n\n  ",
        content,
        flags=re.DOTALL
    )

    # Sostituisce il vecchio JS backLink
    content = re.sub(
        r'const backLink = document\.getElementById\("back-link"\);.*?}\s*\n?\s*}',
        JS_NAV,
        content,
        flags=re.DOTALL
    )

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ Aggiornato: {article['file']}")

print("\\nDone!")
