# hakuchat

Selaimessa toimiva chat, jossa kielimalli voi tarvittaessa hakea verkosta. Kun kirjoitat esimerkiksi *"Etsi linkkejä aiheesta WSL2 ja Docker"*, malli kutsuu `web_search`-työkalua ja vastaa linkkilistalla. Kysymykseen *"Mikä on rekursio?"* malli vastaa suoraan ilman hakua.

- **Taustapalvelin:** Python ja Flask (`app.py`)
- **Kielimalli:** `nvidia/nemotron-3.5-super-vl:free` OpenRouterin kautta `openai`-kirjastolla (`chat_core.py`)
- **Haku:** curl ajetaan `subprocess.run`-kutsulla. Hakulähde on DuckDuckGon HTML-versio, ja varalla ovat suomen- ja englanninkielinen Wikipedia (`search.py`).
- **Käyttöliittymä:** yksi `index.html` ilman kehyskirjastoja

## Vaatimukset

- Python 3.10 tai uudempi (kehitetty versiolla 3.14)
- `curl` asennettuna ja löydyttävä `PATH`:sta
- OpenRouter-API-avain (ilmainen tili riittää, koska malli on `:free`-versio)

## Asennus

```bash
git clone https://github.com/haverimiku/hakuchat.git
cd hakuchat
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## API-avain

Avain luetaan ympäristömuuttujasta `OPENROUTER_API_KEY`. Sitä ei kirjoiteta koodiin.

```bash
export OPENROUTER_API_KEY="sk-or-..."
```

Jos tallennat avaimen `.env`-tiedostoon, se ei päädy gitiin, koska `.env` on `.gitignore`ssa. Lataa se tällöin itse ennen käynnistystä, esimerkiksi `set -a; source .env; set +a`.

## Käynnistys

```bash
.venv/bin/python app.py
```

Avaa sitten selaimessa http://127.0.0.1:5000. Kirjoita viesti ja paina Enter tai Lähetä-painiketta.

Valinnaiset ympäristömuuttujat:

| Muuttuja | Oletus | Merkitys |
|---|---|---|
| `PORT` | `5000` | Portti, jota palvelin kuuntelee |
| `FLASK_DEBUG` | ei asetettu | Arvolla `1` Flaskin debug-tila on päällä. Käytä sitä vain kehityksessä. |

Palvelin kuuntelee vain osoitetta `127.0.0.1`, joten muut verkon koneet eivät pääse käyttämään avaintasi.

### Testaus ilman selainta

```bash
.venv/bin/python search.py "WSL2 Docker" 5   # pelkkä haku, tulostaa JSONin
.venv/bin/python chat_core.py                # chat komentorivillä
```

## Rajapinta

| Metodi ja polku | Runko | Vastaus |
|---|---|---|
| `POST /api/chat` | `{"message": "..."}` | `{"reply": "...", "searches": [{"query": "...", "count": 5}]}` |
| `POST /api/reset` | – | `{"ok": true}`. Tyhjentää istunnon keskusteluhistorian. |

Keskusteluhistoria pidetään palvelimen muistissa selainistunnon evästeen perusteella. Siksi jatkokysymykset, kuten *"Etsi vielä suomenkielisiä"*, toimivat. Historia häviää, kun palvelin käynnistetään uudelleen.

## Tietoturva

| Riski | Suojaus |
|---|---|
| Komentoinjektio | curl ajetaan `subprocess.run([...])`-listana ilman `shell=True`:ta, ja hakusana URL-enkoodataan. |
| Prompt injection | Hakutuloksista palautetaan vain otsikko ja URL. System-prompt kertoo mallille, että tulokset ovat dataa eivätkä ohjeita. |
| Jumiutuminen | curlilla on `--max-time 10`, mallikutsulla 60 sekunnin aikaraja ja tool use -silmukalla enintään 5 kierrosta. |
| Liian suuri vastaus | Tuloksia on enintään 10, ja otsikon, URL:n sekä hakusanan pituudet on rajattu. |
| API-avaimen vuoto | Avain on ympäristömuuttujassa, ja `.env` sekä `.venv` ovat `.gitignore`ssa. |
| Avoin palvelin | Palvelin kuuntelee vain osoitetta `127.0.0.1`. |

## Tool use -silmukka

<!-- Oma selitys tähän. Ehdotettu runko: -->

### Mitä tool use tarkoittaa

_TODO: Mitä tarkoittaa, että malli "kutsuu työkalua"? Kuka työkalun oikeasti suorittaa?_

### Työkalun määrittely

_TODO: Miten `web_search` kuvataan mallille (`WEB_SEARCH_TOOL` tiedostossa `chat_core.py`) ja miksi kuvausteksti vaikuttaa siihen, milloin malli hakee?_

### Silmukan kulku

_TODO: Käy läpi `chat()`-funktion vaiheet:_

1. _..._
2. _..._
3. _..._

### Viestihistorian rakenne

_TODO: Esimerkki `messages`-listasta yhden haun jälkeen (rollit `system`, `user`, `assistant` + `tool_calls`, `tool`). Miksi `tool_call_id` tarvitaan?_

```text
system    → ...
user      → ...
assistant → tool_calls: web_search(...)
tool      → [...]
assistant → ...
```

### Miksi kierrosraja (5)?

_TODO_

### Mitä opin

_TODO_

## Reflektio

<!-- Oma reflektio tähän, yhteensä 200–400 sanaa. Vastaa alla oleviin kysymyksiin. -->

### Missä kohdassa agentti teki virheen tai huonon ratkaisun, ja miten huomasit sen?

_TODO_

### Minkä osan koodista ymmärrän heikoimmin? Mitä tekisin asialle?

_TODO_

### Miten agentin käyttö vaikutti oppimiseeni verrattuna siihen, että olisin kirjoittanut koodin itse?

_TODO_

### Milloin malli päätti hakea ja milloin ei? Toimiko päätös järkevästi?

_TODO_
