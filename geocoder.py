import urllib.request
import urllib.parse
import json
import pandas as pd

pliki = {
    "zero": "zero.txt",
    "jeden": "jeden.txt",
    "wiecej": 'wiecej.txt'
}
file_in = 'obwody_glosowania_utf8.csv'
auto_io = True # Ustawiamy na True do testów podczas tworzenia programu, po stworzeniu programu ustaw na False


def wyczysc_pliki_():
    for plik in pliki:
        open(pliki[plik], 'w').close()


wyczysc_pliki_()
zero = open(pliki['zero'], 'a')
jeden = open(pliki['jeden'], 'a')
wiecej = open(pliki['wiecej'], 'a')


def formatuj(x):#do zmiany
    if x == None:
        return ""
    else:
        return x.strip()


def geocode(miasto, ulica, numer):#dodac kod pocztowy
    miasto = formatuj(miasto)
    ulica = formatuj(ulica)
    numer = formatuj(numer)
    if miasto == "":
        how_many_results = -1
        print('Błąd: Nie podano miasta')
        return None, how_many_results
    service = "http://services.gugik.gov.pl/uug/?"
    if (ulica == '' or ulica == miasto) and (numer == ''):
        params = {"request": "GetAddress", "address": "%s" % (miasto)}
    elif ulica == '' or ulica == miasto:
        params = {"request": "GetAddress", "address": "%s %s" % (miasto, numer)}

    elif numer == '':
        params = {"request": "GetAddress", "address": "%s, %s" % (miasto, ulica)}
    else:
        params = {"request": "GetAddress", "address": "%s, %s %s" % (miasto, ulica, numer)}

    paramsUrl = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
    request = urllib.request.Request(service + paramsUrl)
    print(service + paramsUrl)

    try:
        response = urllib.request.urlopen(request).read()
        js = response.decode("utf-8")  # pobrany, zdekodowany plik json z odpowiedzia z serwera
        w = json.loads(js)

        results = w['results']
        if not results:
            how_many_results = 0
            return None, how_many_results
        else:
            how_many_results = len(w['results'].keys())
            if how_many_results == 1:
                geomWkt = w['results']["1"]['geometry_wkt']
                return geomWkt, how_many_results
            else:
                geomWkt = []
                for i in range(1, how_many_results + 1):
                    napis = str(i)
                    geomWkt.append(w['results'][napis]['geometry_wkt'])  # zwraca wszystkie wyniki
                return geomWkt, how_many_results
    except:#do zmiany
        how_many_results = -1
        print('Wystapil blad połączenia z serwerem')
        return None, how_many_results


def pisz_do_pliku(miasto, ulica, numer, numer_linii_pliku):#dodac wypisywanie adresu przed wspolrzednymi
    miasto = str(miasto)
    ulica = str(ulica)
    numer = str(numer)
    geomWkt, how_many_results = geocode(miasto, ulica, numer)
    if how_many_results == 0:
        with open(pliki['zero'], 'a') as zero:
            zero.write(str(numer_linii_pliku)+". "+ miasto + " " + ulica + " " + numer + "\n")
    elif how_many_results == 1:
        with open(pliki['jeden'], 'a') as jeden:
            jeden.write(str(numer_linii_pliku)+". "+geomWkt + "\n")
    else:
        geomWkt = str(geomWkt).rstrip("]")
        geomWkt = geomWkt.lstrip("[")
        geomWkt = geomWkt.replace("'", "")
        with open(pliki['wiecej'], 'a') as wiecej:
            wiecej.write(str(numer_linii_pliku)+". "+geomWkt + "\n")


def test_geocode():
    g = geocode(miasto='Słupno', ulica='Lipowa', numer='4')
    print(g)
    g = geocode(miasto='Słupno', ulica='Lipowa', numer='')
    print(g)
    g = geocode(miasto='Słupno', ulica='', numer='4')
    print(g)
    g = geocode(miasto='Słupno', ulica='', numer='')
    print(g)
    g = geocode(miasto='Opole', ulica='Opolska', numer='34')
    print(g)
    g = geocode(miasto='Opole', ulica='Edmunda Osmańczyka', numer='20')
    print(g)
    g = geocode(miasto='Knyszyn ', ulica='', numer='')
    print(g)
    g = geocode(miasto='Knyszyn', ulica='', numer='')
    print(g)


def test_pisz_do_pliku():
    pisz_do_pliku(miasto='Słupno', ulica='Lipowa', numer='4', numer_linii_pliku=1)
    pisz_do_pliku(miasto='Słupno', ulica='Lipowa', numer='',numer_linii_pliku=2)
    pisz_do_pliku(miasto='Słupno', ulica='', numer='4',numer_linii_pliku=3)
    pisz_do_pliku(miasto='Słupno', ulica='', numer='',numer_linii_pliku=4)
    pisz_do_pliku(miasto='Opole', ulica='Opolska', numer='34',numer_linii_pliku=5)
    pisz_do_pliku(miasto='Opole', ulica='Edmunda Osmańczyka', numer='20',numer_linii_pliku=6)
    pisz_do_pliku(miasto='Knyszyn ', ulica='', numer='',numer_linii_pliku=7)
    pisz_do_pliku(miasto='Knyszyn', ulica='', numer='',numer_linii_pliku=8)


if __name__ == '__main__':
    if auto_io ==False: # w przeciwnym wypadku ścieżki maja domyślne wartosci
        file_in = input("Podaj ścieżkę do pliku wejściowego")
        pliki['zero'] = input("Podaj ścieżkę do wyjsciowego (0 wynikow)")
        pliki['jeden'] = input("Podaj ścieżkę do wyjsciowego (1 wynik)")
        pliki['wiecej'] = input("Podaj ścieżkę do wyjsciowego (wiecej wynikow)")
    df_all = pd.read_csv(file_in, delimiter=';', header=[0], encoding='utf-8') #wczytywanie danych
    df = pd.DataFrame(df_all, columns=['Miejscowość', 'Ulica', 'Numer']) #wycinanie potrzebnych kolumn
    df = df.reset_index()
    for index, row in df.iterrows():
        pisz_do_pliku(miasto = row['Miejscowość'], ulica = row['Ulica'], numer = row['Numer'],numer_linii_pliku=index + 1)