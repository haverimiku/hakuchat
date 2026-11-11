# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project state

Early-stage prototype: a single script, `weather.py`, that tests LLM tool/function calling. No dependency manifest, tests, linter config, or README exists yet.

## Environment

- Python 3.14 virtualenv at `.venv/` (created with `python3 -m venv .venv`). It currently contains only `pip`; the `openai` package must be installed before the script will run:
  ```bash
  source .venv/bin/activate
  pip install openai
  ```
- Requires the `OPENROUTER_API_KEY` environment variable.

## Git workflow

- Push to git after changes: commit the finished changes and push them to the remote.

## Running

```bash
.venv/bin/python weather.py
```

## Architecture

- Uses the `openai` Python SDK pointed at OpenRouter (`base_url="https://openrouter.ai/api/v1"`), not the OpenAI API directly. Model IDs are OpenRouter slugs (currently `nvidia/nemotron-3.5-super-vl:free`).
- Tools are declared in OpenAI Chat Completions function-calling format (`{"type": "function", "function": {...}}`) and passed via `tools=`.
- The script only prints the tool calls the model requests; it does not yet execute the tool or send a `tool` role result message back to the model for a final answer.

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