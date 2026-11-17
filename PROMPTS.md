# Promptit

<!-- Viisi tärkeintä promptia, joilla sovellus rakennettiin agentin kanssa. Kopioi prompti sellaisenaan ja kirjoita lyhyt huomio siitä, miten agentti vastasi: mitä se teki hyvin, mitä piti korjata ja mitä opit. -->

## 1. Suunnitelma ennen koodia

**Prompti** (plan mode):

> Lue weather.py. Suunnittele Python-sovellus, jossa on Flask-palvelin, yksinkertainen index.html-chat ja tool use -työkalu web_search, joka hakee curlilla. Käytä samaa openai-kirjastoa, OpenRouteria ja mallia kuin weather.py:ssä. Älä kirjoita vielä koodia. Listaa tiedostot, funktiot ja toteutusjärjestys pieninä testattavina askelina.

**Miten agentti vastasi:**

Agentti luki `weather.py`:n ja `CLAUDE.md`:n ja kirjoitti suunnitelman, joka hyväksyttiin vasta kolmannella versiolla. Sen jälkeen se teki `search.py`:n ja `chat_core.py`:n ja testasi haun. Testissä selvisi, että DuckDuckGo palauttaa tältä koneelta bottitarkistussivun (HTTP 202), joten agentti lisäsi varalle Wikipedian kokotekstihaun. Tämän poikkeaman se kertoi itse. Työkalusilmukkaa se testasi valemallilla, koska API-avainta ei vielä ollut sen komentotulkissa.

## 2. Palvelin ja käyttöliittymä

**Prompti:**

> Tee app.py (Flask), joka tarjoaa index.html:n ja POST /api/chat -rajapinnan chat_core.chat-funktion päälle. Tee index.html ilman kirjastoja: viestilista, tekstikenttä, Lähetä-nappi, Enter lähettää. Näytä erillisenä rivinä, jos malli teki haun ja millä hakusanalla. Tee vastausten linkeistä klikattavia.

**Miten agentti vastasi:**

Agentti teki `app.py`:n ja `index.html`:n ja testasi rajapinnan Flaskin testiasiakkaalla ja valemallilla, myös istuntohistorian ja virhetilanteet. Se kertoi suoraan, ettei kokeillut sivua selaimessa eikä ajanut linkkien regexiä, koska koneella ei ole Nodea. Pyytämättä se lisäsi `/api/reset`-reitin ja "Uusi keskustelu" -napin, mutta mainitsi nekin.

## 3. API-avain ympäristömuuttujaan

**Prompti:**

> lisää api key bashrc

**Miten agentti vastasi:**

Agentti huomasi, että `~/.bashrc` yritti jo lukea avaimen Windowsista, mutta kutsui `from_windows`-funktiota, jota ei ollut määritelty. Se lisäsi puuttuvan funktion `.bashrc`:hen ja tarkisti avaimen pituuden tulostamatta itse avainta. Lopuksi se testasi oikeaa mallia: hakukysymys teki haun ja "Mikä on rekursio?" vastattiin suoraan. Kun `app.py` kaatui vanhassa terminaalissa `KeyError`iin, keskeytin agentin ja pyysin selkeät komennot. Vastaukseksi tuli vaiheittainen ohje (`nano`, `source ~/.bashrc`, `echo ${#OPENROUTER_API_KEY}`), jossa varoitettiin myös, että `echo >> ~/.bashrc` jättäisi avaimen komentohistoriaan.

## 4. Tietoturvatarkistus

**Prompti:**

> Lisää claude.md tiedostoon: *(liitteenä tietoturvavaatimusten taulukko: komentoinjektio, prompt injection, jumiutuminen, liian suuri vastaus, API-avaimen vuoto, avoin palvelin)*

ja heti perään:

> Korjaa puutteet

**Miten agentti vastasi:**

Agentti lisäsi taulukon `CLAUDE.md`:hen ja kävi koodin läpi sitä vasten. Puutteiksi se raportoi tiedostorivien tarkkuudella mm. system-promptista puuttuvan "tulokset ovat dataa" -ohjeen, otsikoiden rajaamattoman pituuden, mallikutsun aikarajan puuttumisen ja puuttuvan `.gitignore`:n. Toisella promptilla se korjasi kaikki kuusi puutetta (esim. `timeout=60`, pituusrajat vakioina, virheellinen `max_results` → oletus 5) ja testasi rajaukset valehaulla. Oikeaa hakua tai mallikutsua se ei korjausten jälkeen ajanut, ja sen se myös kertoi.

## 5. Tool use -silmukan selitys

**Prompti:**

> selitä tool use -silmukka rivi riviltä.

**Miten agentti vastasi:**

Agentti selitti `chat_core.py`:n funktiot `chat()` ja `run_tool()` rivinumeroiden kanssa. Se kertoi esimerkiksi, miksi `messages`-listaa muokataan paikallaan: siksi `app.py` voi säilyttää historian ja jatkokysymys toimii. Lisäksi se selitti, miten `MAX_ROUNDS` estää loputtoman silmukan. Myöhemmin pyysin saman selityksen erilliseksi tiedostoksi (`TOOL_USE.md`), joka pidetään vain omalla koneella README:n oman selityksen pohjaksi.
