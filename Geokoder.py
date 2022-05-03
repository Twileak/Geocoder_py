import urllib.request
import urllib.parse
import json
import pandas as pd
import keyboard

pliki = {
    "zero": "zero.txt",
    "jeden": "jeden.txt",
    "wiecej": 'wiecej.txt'
}
file_in = 'obwody_glosowania_utf8.csv'
auto_io = True  # Ustawiamy na True do testów podczas tworzenia programu, po stworzeniu programu ustaw na False
nazwy_kolumn = {
    "miasto": "Miejscowość",
    "ulica": "Ulica",
    "numer": "Numer posesji",
    "kod": "Kod pocztowy"
}


def formatuj(x):
    if x == None:
        return ""
    else:
        return x.strip()


def geocode(kod, miasto, ulica, numer):#Funkcja zwraca adres, współrzedne jako POINT(x,y) oraz oddzielnie współrzedne x i y
    kod = formatuj(kod)
    miasto = formatuj(miasto)
    ulica = formatuj(ulica)
    numer = formatuj(numer)
    if miasto == "":
        how_many_results = -1
        print('Błąd: Nie podano miasta')
        return None, None, None, how_many_results
    service = "http://services.gugik.gov.pl/uug/?" 
    if (ulica == '' or ulica == miasto) and (numer == ''):
        params = {"request": "GetAddress", "address": "%s %s" % (kod, miasto)}
    elif ulica == '' or ulica == miasto:
        params = {"request": "GetAddress", "address": "%s %s %s" % (kod, miasto, numer)}

    elif numer == '': 
        params = {"request": "GetAddress", "address": "%s %s, %s" % (kod, miasto, ulica)}
    else:
        params = {"request": "GetAddress", "address": "%s %s, %s %s" % (kod, miasto, ulica, numer)}

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
            return None, None, None, how_many_results
        else:
            how_many_results = len(w['results'].keys())
            if how_many_results == 1:
                geomWkt = w['results']["1"]['geometry_wkt']
                x = w['results']['1']['x']
                y = w['results']['1']['y']
                return geomWkt, x, y, how_many_results
            else:
                geomWkt = []
                x = []
                y = []
                for i in range(1, how_many_results + 1):
                    napis = str(i)
                    geomWkt.append(w['results'][napis]['geometry_wkt'])  # zwraca wszystkie wyniki
                    x.append(w['results'][napis]['x'])
                    y.append(w['results'][napis]['y'])
                return geomWkt, x, y, how_many_results
    except:
        how_many_results = -1
        print('Wystapil blad połączenia z serwerem')
        return None, None, None, how_many_results


def str_with_nan(s):
    if pd.isna(s):
        return ""
    return str(s);


def pisz_do_pliku(kod, miasto, ulica, numer, numer_linii_pliku,plik1,plik2,plik3):
    miasto = str_with_nan(miasto)
    ulica = str_with_nan(ulica)
    numer = str_with_nan(numer)
    kod = str_with_nan(kod)
    geomWkt, x, y, how_many_results = geocode(kod, miasto, ulica, numer)
    if how_many_results == 0:
        plik1.write(str(numer_linii_pliku) + ". " + kod + " " + miasto + " " + ulica + " " + numer + "\n")
    elif how_many_results == 1:
        plik2.write(str(numer_linii_pliku) + ". " + kod + " " + miasto + " " + ulica + " " + numer + " " +str(x) + " "  + str(y) + " "+ geomWkt + "\n")
    elif how_many_results > 1:
        geomWkt = str(geomWkt).rstrip("]")
        geomWkt = geomWkt.lstrip("[")
        geomWkt = geomWkt.replace("'", "")
        plik3.write(str(numer_linii_pliku) + ". " + kod + " " + miasto + " " + ulica + " " + numer + " "+str(x) + " "  + str(y) + " " + geomWkt + "\n")
    # Jesli how_many_results == -1 program nic nie zapisuje do pliku
	# W przyszłości zmienimy na wypisywanie błędnych wartości do kolejnego pliku

def wyczysc_pliki_():
    try:
        for plik in pliki:
            open(pliki[plik], 'w').close()
        return True
    except IOError:
        print ("Problem z otwarciem pliku")
        return False


def otworz_pliki():
    try:
        zero = open(pliki['zero'], 'a')
        jeden = open(pliki['jeden'], 'a')
        wiecej = open(pliki['wiecej'], 'a')
        return zero, jeden, wiecej
    except IOError:
        print("Problem z otwarciem pliku")
        return None, None, None


def zamknij_pliki(zero, jeden, wiecej):
    try:
        zero.close()
        jeden.close()
        wiecej.close()
        return True
    except IOError:
        print("Problem z zamknieciem pliku")
        return False


def wczytaj_sciezki_do_plikow():
    global file_in
    file_in = input("Podaj ścieżkę do pliku wejściowego")
    pliki['zero'] = input("Podaj ścieżkę do wyjsciowego (0 wynikow)")
    pliki['jeden'] = input("Podaj ścieżkę do wyjsciowego (1 wynik)")
    pliki['wiecej'] = input("Podaj ścieżkę do wyjsciowego (wiecej wynikow)")


if __name__ == '__main__':
    df_all = pd.read_csv(file_in, delimiter=';', header=[0], encoding='utf-8')  # wczytywanie danych
    df = pd.DataFrame(df_all, columns=[nazwy_kolumn['miasto'], nazwy_kolumn['ulica'], nazwy_kolumn['numer'],
                                       nazwy_kolumn['kod']])  # wycinanie potrzebnych kolumn
    df = df.reset_index()
    generator = df.iterrows()  # pozwoli na zapamietanie pozycji przed zatrzymaniem petli
    if not auto_io:  # w przeciwnym wypadku ścieżki maja domyślne wartosci
        wczytaj_sciezki_do_plikow()
    wyczysc_pliki_()
    zero, jeden, wiecej = otworz_pliki()
    paused = False
    for index, row in generator:
        if keyboard.is_pressed("x"):  # wylaczy sie po nacisnieciu 'x'
            zamknij_pliki(zero,jeden,wiecej)
            exit()
        if (not paused) and keyboard.is_pressed('q'): # pauza po wcisnieciu q
            zamknij_pliki(zero,jeden,wiecej)
            paused = True
        while paused:
            if keyboard.is_pressed('a'): # po wcisnieciu a wznawia program
                zero, jeden, wiecej = otworz_pliki()
                paused = False
        pisz_do_pliku(kod=row[nazwy_kolumn['kod']], miasto=row[nazwy_kolumn['miasto']], ulica=row[nazwy_kolumn['ulica']], numer=row[nazwy_kolumn['numer']], numer_linii_pliku=index + 1,
                      plik1=zero, plik2=jeden, plik3=wiecej)
    zamknij_pliki(zero,jeden,wiecej)