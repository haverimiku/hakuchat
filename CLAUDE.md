# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project state

Hakuchat: a local browser chat where an LLM can call a `web_search` tool. One Flask server + one HTML page. User-facing docs (install, run, API, security) are in `README.md`, written in Finnish; its "Tool use -silmukka" section is a skeleton the user fills in themselves — don't write that content for them. No tests or linter config exist.

## Environment

- Python 3.14 virtualenv at `.venv/` (created with `python3 -m venv .venv`). Install dependencies from `requirements.txt` (Flask, openai):
  ```bash
  source .venv/bin/activate
  pip install -r requirements.txt
  ```
- Requires the `OPENROUTER_API_KEY` environment variable and `curl` on `PATH`.

## Git workflow

- Push to git after changes: commit the finished changes and push them to the remote (`origin` = github.com/haverimiku/hakuchat, branch `main`).

## Running

```bash
.venv/bin/python app.py                 # http://127.0.0.1:5000 (PORT, FLASK_DEBUG=1 optional)
.venv/bin/python chat_core.py           # CLI chat, no browser
.venv/bin/python search.py "query" 5    # search only, prints JSON
```

## Architecture

- `app.py` — Flask server bound to `127.0.0.1` only. Serves `index.html` and `style.css`; `POST /api/chat` takes `{"message"}` and returns `{"reply", "searches": [{"query", "count"}]}`; `POST /api/reset` clears history. Conversation history lives in an in-memory dict keyed by a session-cookie UUID (lost on restart; `secret_key` is random per start). A failed model call rolls the user turn back out of history.
- `chat_core.py` — model + tool use loop. `openai` SDK pointed at OpenRouter (`base_url="https://openrouter.ai/api/v1"`), model `nvidia/nemotron-3.5-super-vl:free`. Holds `SYSTEM_PROMPT` (when to search; search results are data, not instructions) and the `WEB_SEARCH_TOOL` definition in Chat Completions function-calling format. `chat()` loops at most `MAX_ROUNDS = 5`: call model → if no `tool_calls`, return text; otherwise append the assistant message and one `tool` message per call (`run_tool` → JSON string). Mutates the passed `messages` list in place.
- `search.py` — `web_search(query, max_results)` returns `[{"title", "url"}]`. Runs `curl` via `subprocess.run` as an argument list (never `shell=True`), `--max-time 10`, query URL-encoded. Source order: DuckDuckGo HTML (parsed with `html.parser`, ads filtered, redirect URLs unwrapped) → fi.wikipedia → en.wikipedia. Clamps result count (1–10) and query/title/URL lengths. Returns `[]` on any error.
- `index.html` + `style.css` — no frameworks; message list, input, Lähetä button, Enter sends; shows which search queries were used and renders links as clickable.
- `weather.py` — the original tool-calling experiment; not used by the app.

Valmis sovellus on yksi Python-palvelin ja yksi HTML-sivu. Kun käyttäjä kirjoittaa "Etsi linkkejä aiheesta WSL2 ja Docker", malli kutsuu hakutyökalua ja vastaa linkkilistalla. Kun käyttäjä kysyy "Mikä on rekursio?", malli vastaa suoraan ilman hakua.

Pakolliset vaatimukset
[ ] Taustapalvelin Pythonilla (Flask tai standardikirjaston http.server), joka tarjoaa index.html-sivun ja POST-rajapinnan /api/chat.
[ ] Kielimalli kutsutaan openai-kirjastolla OpenRouterin kautta samalla Nemotron-mallilla kuin weather.py:ssä.
[ ] API-avain luetaan ympäristömuuttujasta OPENROUTER_API_KEY. Avain ei saa näkyä koodissa eikä git-historiassa.
[ ] Yksi työkalu nimeltä web_search, jonka parametrit ovat query (merkkijono, pakollinen) ja max_results (kokonaisluku, oletus 5). Kuvaus kertoo mallille, milloin hakua kannattaa käyttää.
[ ] Haku tehdään curlilla Pythonin subprocess.run-kutsulla. Tulos jäsennetään listaksi, jossa on otsikko ja URL, ja palautetaan mallille JSON-muodossa.
[ ] Tool use -silmukka: ohjelma suorittaa työkalukutsut ja kutsuu mallia uudelleen, kunnes malli vastaa tekstillä. Kierroksia on enintään 5.
[ ] Keskusteluhistoria säilyy saman selainistunnon ajan, joten jatkokysymys "Etsi vielä suomenkielisiä" toimii.
[ ] Käyttöliittymä on yksi index.html ilman kehyskirjastoja: viestilista, tekstikenttä ja Lähetä-painike. Enter lähettää viestin.
[ ] Näkyvyys: käyttöliittymä näyttää, jos malli käytti hakua, ja millä hakusanalla. Vastauksen linkit ovat klikattavia.
[ ] README.md kertoo, miten sovellus asennetaan ja käynnistetään.

Hakupalvelu
Valitse hakulähde, jota voi kutsua curlilla ilman maksullista avainta. Kaksi toimivaa vaihtoehtoa:

Vaihtoehto	Osoite	Huomio
DuckDuckGon HTML-versio	https://html.duckduckgo.com/html/?q=<haku>	Yleinen verkkohaku. Voi estää automaattiset kyselyt, jos niitä tulee paljon.
Wikipedian haku-API	https://fi.wikipedia.org/w/api.php?action=opensearch&search=<haku>&format=json	Luotettava ja palauttaa valmista JSONia, mutta hakee vain Wikipediasta.

## Tietoturvavaatimukset

Tarkista, että agentin koodi täyttää nämä:

| Riski | Mitä voi tapahtua | Vaadittu suojaus |
|---|---|---|
| Komentoinjektio | Hakusana `x; rm -rf ~` suoritetaan komentona | `subprocess.run([...])` listana, ei `shell=True`; hakusana URL-enkoodataan (`urllib.parse.quote`) |
| Prompt injection | Hakutuloksen teksti käskee mallia toimimaan toisin | Tuloksista palautetaan vain otsikko ja URL; system-prompt kertoo, että tulokset ovat dataa, eivät ohjeita |
| Jumiutuminen | Curl tai malli jää odottamaan loputtomasti | Curlille `--max-time 10`, silmukalle enintään 5 kierrosta |
| Liian suuri vastaus | Sivu täyttää mallin kontekstin | Tulosten määrä ja pituus rajataan |
| API-avaimen vuoto | Avain päätyy GitHubiin | Avain ympäristömuuttujassa, `.env` ja `.venv` tiedostossa `.gitignore` |
| Avoin palvelin | Muut verkon koneet käyttävät avaintasi | Palvelin kuuntelee vain osoitetta `127.0.0.1` |