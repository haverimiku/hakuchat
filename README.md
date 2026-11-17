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

Silmukka on `chat_core.py`:n funktiossa `chat()` (rivit 83–111). Funktio `run_tool()` (rivit 59–80) suorittaa yksittäisen työkalukutsun.

Malli ei itse hae mitään. Se voi vain *pyytää*, että työkalua kutsutaan tietyillä argumenteilla. Ohjelma suorittaa haun ja lähettää tuloksen takaisin mallille. Sitten malli päättää, haluaako se tehdä uuden haun vai vastata tekstillä.

Silmukka kiertää enintään 5 kertaa. Jokainen kierros on yksi kutsu. Raja estää tilanteen, jossa malli pyytäisi hakuja loputtomasti.

## Reflektio

### Missä kohdassa agentti teki virheen tai huonon ratkaisun, ja miten huomasit sen?

Ensimmäisessä versiossa oli tietoturvapuutteita. System-prompt ei kertonut mallille, että hakutulokset ovat dataa eivätkä ohjeita. Otsikoiden pituutta ei rajattu, mallikutsulla ei ollut aikarajaa ja .gitignore puuttui. Huomasin puutteet vasta, kun lisäsin tietoturvataulukon CLAUDE.md:hen ja pyysin agenttia tarkistamaan koodin sitä vasten. Opin, että vaatimukset kannattaa antaa agentille heti alussa eikä vasta jälkikäteen.

### Minkä osan koodista ymmärrän heikoimmin? Mitä tekisin asialle?

Heikoimmin ymmärrän search.py: miten html.parser käy sivun läpi ja miten uudelleenohjauslinkit puretaan. Ajaisin search.py:tä ja tulostaisin välivaiheita. Voisin myös pyytää agenttia selittämään koodin rivi riviltä.

### Miten agentin käyttö vaikutti oppimiseeni verrattuna siihen, että olisin kirjoittanut koodin itse?

Sain toimivan sovelluksen paljon nopeammin, mutta riskinä on, että koodi toimii ilman että ymmärrän sitä. Eniten opin silloin, kun pyysin selityksiä ohjelman toiminnasta. Jos olisin kirjoittanut kaiken itse, olisin luultavasti oppinut virheiden kautta syvemmin, mutta tekeminen olisi ollut huomattavasti hitaampaa.

### Milloin malli päätti hakea ja milloin ei? Toimiko päätös järkevästi?

Kun pyysin "Etsi linkkejä aiheesta WSL2 ja Docker", malli kutsui web_search-työkalua ja vastasi linkkilistalla. Kysymykseen "Mikä on rekursio?" se vastasi suoraan ilman hakua, mikä oli järkevää, koska kyse on yleistiedosta. Myös jatkokysymys "Etsi vielä suomenkielisiä" toimi, koska historia säilyi.
