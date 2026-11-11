"""Verkkohaku curlilla: DuckDuckGon HTML-versio, varalla Wikipedian haku-API."""

import json
import subprocess
import sys
from html.parser import HTMLParser
from urllib.parse import parse_qs, quote, quote_plus, urlparse

SEARCH_URL = "https://html.duckduckgo.com/html/?q={query}"
WIKI_URL = (
    "https://{lang}.wikipedia.org/w/api.php"
    "?action=query&list=search&srsearch={query}&srlimit={limit}&srprop=&format=json"
)
# Wikimedia edellyttää kuvaavaa User-Agentia botti-kyselyille.
WIKI_USER_AGENT = "hakuchat/0.1 (opetusprojekti; python-subprocess-curl)"
USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)
CURL_TIMEOUT = 10  # sekuntia, curlin oma aikaraja
MAX_RESULTS_LIMIT = 10  # tulosten enimmäismäärä
MAX_QUERY_LEN = 200  # merkkiä
MAX_TITLE_LEN = 150  # merkkiä
MAX_URL_LEN = 500  # merkkiä


class _DDGParser(HTMLParser):
    """Poimii hakutulosten <a class="result__a">-linkit."""

    def __init__(self):
        super().__init__()
        self.results = []
        self._href = None
        self._text = []

    def handle_starttag(self, tag, attrs):
        if tag != "a":
            return
        attrs = dict(attrs)
        if "result__a" in (attrs.get("class") or "").split():
            self._href = attrs.get("href", "")
            self._text = []

    def handle_data(self, data):
        if self._href is not None:
            self._text.append(data)

    def handle_endtag(self, tag):
        if tag == "a" and self._href is not None:
            title = " ".join("".join(self._text).split())
            self.results.append({"title": title, "url": _clean_url(self._href)})
            self._href = None


def _clean_url(href: str) -> str:
    """Purkaa DDG:n uudelleenohjauslinkin (//duckduckgo.com/l/?uddg=...) oikeaksi URL:ksi."""
    parsed = urlparse(href)
    if parsed.path == "/l/":
        target = parse_qs(parsed.query).get("uddg")
        if target:
            return target[0]
    if href.startswith("//"):
        return "https:" + href
    return href


def _is_ad(url: str) -> bool:
    return "duckduckgo.com/y.js" in url or "ad_domain=" in url


def _curl(url: str, user_agent: str = USER_AGENT) -> str | None:
    """Hakee URL:n curlilla (listamuoto, ei shell=True). Virheessä None."""
    cmd = ["curl", "-s", "-L", "--max-time", str(CURL_TIMEOUT), "-A", user_agent, url]
    try:
        proc = subprocess.run(
            cmd, capture_output=True, text=True, timeout=CURL_TIMEOUT + 5, check=False
        )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None
    if proc.returncode != 0:
        return None
    return proc.stdout


def search_ddg(query: str, max_results: int) -> list[dict]:
    """DuckDuckGon HTML-haku. Tyhjä lista, jos DDG estää kyselyn (bottitarkistus)."""
    html = _curl(SEARCH_URL.format(query=quote_plus(query)))
    if not html:
        return []
    parser = _DDGParser()
    parser.feed(html)
    results = [r for r in parser.results if r["title"] and r["url"] and not _is_ad(r["url"])]
    return results[:max_results]


def search_wikipedia(query: str, max_results: int, lang: str = "fi") -> list[dict]:
    """Wikipedian kokotekstihaku (list=search). Tyhjä lista virheessä."""
    url = WIKI_URL.format(lang=lang, query=quote_plus(query), limit=max_results)
    body = _curl(url, user_agent=WIKI_USER_AGENT)
    if not body:
        return []
    try:
        hits = json.loads(body)["query"]["search"]
    except (json.JSONDecodeError, KeyError, TypeError):
        return []
    return [
        {
            "title": h["title"],
            "url": f"https://{lang}.wikipedia.org/wiki/{quote(h['title'].replace(' ', '_'))}",
        }
        for h in hits
    ]


def web_search(query: str, max_results: int = 5) -> list[dict]:
    """Hakee verkosta ja palauttaa listan {"title", "url"}.

    Järjestys: DuckDuckGo -> suomenkielinen Wikipedia -> englanninkielinen Wikipedia.
    Virhetilanteessa tyhjä lista.
    """
    try:
        max_results = int(max_results)
    except (TypeError, ValueError):
        max_results = 5
    max_results = max(1, min(max_results, MAX_RESULTS_LIMIT))
    query = query[:MAX_QUERY_LEN]
    results = (
        search_ddg(query, max_results)
        or search_wikipedia(query, max_results, "fi")
        or search_wikipedia(query, max_results, "en")
    )
    # Rajataan pituudet, ettei yksittäinen tulos täytä mallin kontekstia.
    return [
        {"title": _truncate(r["title"], MAX_TITLE_LEN), "url": r["url"][:MAX_URL_LEN]}
        for r in results[:max_results]
    ]


def _truncate(text: str, limit: int) -> str:
    return text if len(text) <= limit else text[: limit - 1] + "…"


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Käyttö: python search.py "hakusana" [max_results]', file=sys.stderr)
        sys.exit(1)
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    print(json.dumps(web_search(sys.argv[1], n), ensure_ascii=False, indent=2))
