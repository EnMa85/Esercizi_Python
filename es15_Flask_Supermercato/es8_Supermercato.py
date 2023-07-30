'''
Creare un programma supermarketFlask che rappresenta la gestione di un supermercato online.
Inizialmente creare l’interfaccia per l’utente: l’utente può: scegliere tra 4 select prodotti da banco,
prodotti freschi, prodotti da frigo, inoltre nell’ultima select  possiamo scegliere tra vari elettrodomestici.
In questo programma l’utente può anche scegliere di non selezionare alcuni prodotti (stringa vuota o null).
Inoltre una volta effettuato l’ordine il programma va a scrivere su una tabella mysql i dati.
ATTENZIONE: tra i dati sono presenti la mail e la password dell’utente, e quindi i relativi cookie dei dati di sessione.
'''

from flask import Flask, render_template, request
import mysql.connector
import datetime
from datetime import datetime
import matplotlib.pyplot as plt


mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="pyThon23@_",
  database="supermercato"
)

app = Flask(__name__)

class Prodotti:
    def __init__(self, prodotto, prezzo):
        self.prodotto = prodotto
        self.prezzo = prezzo
    def __str__(self):
        return f"€ {self.prezzo} - {self.prodotto}"


#dichiaro e inizializzo prodotti e prezzi
banco1 = Prodotti("Pasta", 2)
banco2 = Prodotti("Grissini", 3)
banco3 = Prodotti("Caffè", 5)
fresco1 = Prodotti("Pomodori", 5)
fresco2 = Prodotti("Melanzane", 3)
fresco3 = Prodotti("Pesche", 2)
frigo1 = Prodotti("Latte", 2)
frigo2 = Prodotti("Yogurt", 1)
frigo3 = Prodotti("Mozzarella", 3)
elettrodomestico1 = Prodotti("Ventilatore", 20)
elettrodomestico2 = Prodotti("Condizionatore", 400)
elettrodomestico3 = Prodotti("Refrigeratore", 200)
lista_banco = []
lista_freschi = []
lista_frigo = []
lista_elettrodomestici = []
lista_banco.append(banco1)
lista_banco.append(banco2)
lista_banco.append(banco3)
lista_freschi.append(fresco1)
lista_freschi.append(fresco2)
lista_freschi.append(fresco3)
lista_frigo.append(frigo1)
lista_frigo.append(frigo2)
lista_frigo.append(frigo3)
lista_elettrodomestici.append(elettrodomestico1)
lista_elettrodomestici.append(elettrodomestico2)
lista_elettrodomestici.append(elettrodomestico3)


def save_cookies_db(utente, last_access):
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='pyThon23@_',
            database='supermercato'
        )
        cursor = connection.cursor()
        query = "INSERT INTO accessi_cliente (mail_accessi, ultimo_accesso) VALUES (%s, %s)"
        values = (utente, last_access)
        cursor.execute(query, values)
        connection.commit()
        print("Dati salvati correttamente nel database.")
    except mysql.connector.Error as error:
        print("Errore durante il salvataggio dei dati:", error)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


@app.route('/')
def login_cliente():
    return render_template('es8_cliente_login.html')


@app.route('/login', methods=['POST'])
def index():
    mycursor = mydb.cursor()

    # prendo i dati dal form html
    mail = request.form['email']
    pw = request.form['password']
    access = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    accedi = request.form.get('accedi')
    registrati = request.form.get('registrati')
    #estrapolo il nome dell'utente
    nome = mail.rsplit("@")[0].capitalize()

    if accedi:  #se clicca su accedi
        reg = False
        # prendo la lista credenziali salvata
        mycursor.execute("SELECT mail_utente, pass_utente FROM utenti_registrati")
        dbLista_utenti = mycursor.fetchall()
        # verifico la corrispondenza delle credenziali
        for u in dbLista_utenti:
            if mail == u[0] and pw == u[1]:
                reg = True
                save_cookies_db(mail, access)
                return render_template('es8_cliente_index.html', mail=mail, nome=nome, lista_banco=lista_banco, lista_freschi=lista_freschi, lista_frigo=lista_frigo, lista_elettrodomestici=lista_elettrodomestici)
        if not reg:
            errore = "CREDENZIALI INVALIDE!!!"
            return render_template('es8_cliente_login.html', errore=errore)

    if registrati:  #se clicca su registrati
        gia_reg = False
        # prendo la lista mail salvata
        mycursor.execute("SELECT mail_utente FROM utenti_registrati")
        dbLista_mail = mycursor.fetchall()
        for m in dbLista_mail:
            if mail == m[0]:
                gia_reg == True
                errore = 'Utente già registrato! Clicca su ACCEDI'
                return render_template('es8_cliente_login.html', errore=errore)
        if not gia_reg:
            sql = "INSERT INTO utenti_registrati (mail_utente, pass_utente) VALUES (%s,%s)"
            val = (mail, pw)
            mycursor.execute(sql, val)
            mydb.commit()
            save_cookies_db(mail, access)
            return render_template('es8_cliente_index.html', mail=mail, nome=nome, lista_banco=lista_banco, lista_freschi=lista_freschi, lista_frigo=lista_frigo, lista_elettrodomestici=lista_elettrodomestici)


@app.route('/acquista', methods=['POST'])
def ordina():
    acquista = request.form.get('acquista')
    annulla = request.form.get('annulla')

    mycursor = mydb.cursor()

    if acquista:
        #prendo i dati dal form
        scelta_banco = request.form['banco']
        scelta_fresco = request.form['freschi']
        scelta_frigo = request.form['frigo']
        scelta_elettrodomestico = request.form['elettrodomestici']
        mail = request.form['mail']

        #associo i prezzi ai prodotti scelti
        scontrino = 0
        carrello = []
        for banco in lista_banco:
            if scelta_banco == banco.prodotto:
                scontrino += int(banco.prezzo)
                prezzo_ban = int(banco.prezzo)
                carrello.append(f"{scelta_banco} € {prezzo_ban}")
        for fresco in lista_freschi:
            if scelta_fresco == fresco.prodotto:
                scontrino += int(fresco.prezzo)
                prezzo_fre = int(fresco.prezzo)
                carrello.append(f"{scelta_fresco} € {prezzo_fre}")
        for frigo in lista_frigo:
            if scelta_frigo == frigo.prodotto:
                scontrino += int(frigo.prezzo)
                prezzo_fri = int(frigo.prezzo)
                carrello.append(f"{scelta_frigo} € {prezzo_fri}")
        for elettro in lista_elettrodomestici:
            if scelta_elettrodomestico == elettro.prodotto:
                scontrino += int(elettro.prezzo)
                prezzo_ele = int(elettro.prezzo)
                carrello.append(f"{scelta_elettrodomestico} € {prezzo_ele}")

        #salvo l'ordine sul database
        data_ordine = datetime.now()
        data = data_ordine.strftime('%d-%m-%Y %H:%M:%S')

        sql = "INSERT INTO vendite (mail_vendite, data_acquisto, banco, freschi, frigo, elettro, totale_acquisto) VALUES (%s,%s,%s,%s,%s,%s,%s)"
        val = (mail, data_ordine, scelta_banco, scelta_fresco, scelta_frigo, scelta_elettrodomestico, scontrino)
        mycursor.execute(sql, val)
        mydb.commit()
        return render_template('es8_cliente_acquista.html', carrello=carrello, scontrino=scontrino, data=data)

    if annulla:
        return render_template('es8_cliente_login.html')


@app.route('/gestore')
def gestore():
    return render_template('es8_gestore_login.html')


@app.route('/login_gestore', methods=['POST'])
def login_gestore():
    mycursor = mydb.cursor()
    reg = False

    # prendo i dati dal form html
    username = request.form['username']
    password = request.form['password']

    # prendo la lista credenziali salvata
    mycursor.execute("SELECT * FROM admin")
    dbLista_admin = mycursor.fetchall()

    # verifico la corrispondenza delle credenziali
    for u in dbLista_admin:
        if username == u[0] and password == u[1]:
            reg = True
            return render_template('es8_gestore_pagina.html')
    if not reg:
        return render_template('es8_gestore_login.html')


@app.route('/statistiche', methods=['POST'])
def statistiche():
    mycursor = mydb.cursor()
    tortaCli = request.form.get('tortaCli')
    istoCli = request.form.get('istoCli')
    tortaProd = request.form.get('tortaProd')
    istoProd = request.form.get('istoProd')
    tortaAccDay = request.form.get('tortaAccDay')
    istoAccDay = request.form.get('istoAccDay')
    tortaCliAcc = request.form.get('tortaCliAcc')
    istoCliAcc = request.form.get('istoCliAcc')
    tortaAccData = request.form.get('tortaAccData')
    istoAccData = request.form.get('istoAccData')


    totale_incassi = 0
    # prendo la lista ordini conclusi
    mycursor.execute("SELECT * FROM vendite")
    vendite = mycursor.fetchall()


    #DATI PER CLIENTE
    totale_cliente = []
    lista_clienti = []
    # compilo due liste contenenti clienti e spesa totale per cliente
    for ordine in vendite:
        cont = 0
        cliente_ins = False
        totale_incassi += int(ordine[7])
        for cliente in lista_clienti:
            if cliente == ordine[1]:
                totale_cliente[cont] += int(ordine[7])
                cliente_ins = True
                cont += 1
        if not cliente_ins:
            lista_clienti.append(ordine[1])
            totale_cliente.append(int(ordine[7]))

    # DATI PER PRODOTTO
    totale_prodotti = []
    lista_prodotti = []
    # compilo due liste contenenti prodotti e quantità venduta
    for banco in lista_banco:
        lista_prodotti.append(banco.prodotto)
        totale_prodotti.append(0)
    for fresco in lista_freschi:
        lista_prodotti.append(fresco.prodotto)
        totale_prodotti.append(0)
    for frigo in lista_frigo:
        lista_prodotti.append(frigo.prodotto)
        totale_prodotti.append(0)
    for elettro in lista_elettrodomestici:
        lista_prodotti.append(elettro.prodotto)
        totale_prodotti.append(0)
    # calcolo la quantità venduta
    cont = 0
    for prodotto in lista_prodotti:
        for ordine in vendite:
            if str(prodotto) == str(ordine[3]) or str(prodotto) == str(ordine[4]) or str(prodotto) == str(ordine[5]) or str(prodotto) == str(ordine[6]):
                totale_prodotti[cont] += 1
        cont += 1

    # DATI PER ACCESSI PER CLIENTE
    mycursor.execute("SELECT mail_utente FROM utenti_registrati")
    utenti_registrati = mycursor.fetchall()
    #trasferisco la lista in un'altra senza virgole
    nuova_lista = []
    for u in utenti_registrati:
        nuova_lista.append(u[0])
    mycursor.execute("SELECT mail_accessi FROM accessi_cliente")
    accessi = mycursor.fetchall()
    utente_accessi = []
    #inizializzo la lista accessi
    for utente in utenti_registrati:
        utente_accessi.append(0)
    for accesso in accessi:
        indice = 0
        for utente in utenti_registrati:
            if utente == accesso:
                utente_accessi[indice] += 1
            indice += 1

    # DATI PER ACCESSI PER DATA
    mycursor.execute("SELECT ultimo_accesso FROM accessi_cliente")
    lista_date = mycursor.fetchall()
    accessi = []
    # creo una nuova lista per contenere le date senza orario
    date = []
    for data in lista_date:
        if data[0].strftime('%d-%m-%Y') not in date:
            date.append(data[0].strftime('%d-%m-%Y'))
    #inizializzo la lista numero_accessi per averla della stessa dimensione
    indice = 0
    for data_pulita in date:
        accessi.append(0)
        for data in lista_date:
            if data[0].strftime('%d-%m-%Y') == data_pulita:
                accessi[indice] += 1
        indice += 1

    # DATI PER ACCESSI DEL GIORNO
    mycursor = mydb.cursor()
    lista_orari = []
    data_oggi = datetime.today()
    solo_data_oggi = data_oggi.strftime('%d-%m-%Y')
    mycursor.execute("SELECT ultimo_accesso FROM accessi_cliente")
    date_accessi = mycursor.fetchall()
    # per ogni accesso del giorno, salvo l'ora in una lista
    solo_ora = []
    for giorno in date_accessi:
        if giorno[0].strftime('%d-%m-%Y') == solo_data_oggi:
            lista_orari.append(giorno[0].hour)
    #creo lista che raccoglie le singole ore per non avere duplicati
    solo_ore = []
    for ora in lista_orari:
        if ora not in solo_ore:
            solo_ore.append(ora)
    #conto gli accessi per ora
    indice_ora = 0
    somma_ore = []
    for ora_grafico in solo_ore:
        somma_ore.append(0)
        for ora_accessi in lista_orari:
            if ora_grafico == ora_accessi:
                somma_ore[indice_ora] += 1
        indice_ora += 1


    # CREAZIONE GRAFICI
    if tortaCli:
        plt.pie(totale_cliente, labels=lista_clienti, autopct='%1.1f%%')
        plt.title("Vendite per cliente")
    if istoCli:
        plt.bar(lista_clienti, totale_cliente)
        plt.title("Vendite per cliente")
        plt.xlabel("Clienti")
        plt.ylabel("Incassi")
    if tortaProd:
        plt.pie(totale_prodotti, labels=lista_prodotti, autopct='%1.1f%%')
        plt.title("Vendite per prodotto")
    if istoProd:
        plt.bar(lista_prodotti, totale_prodotti)
        plt.title("Vendite per prodotto")
        plt.xlabel("Prodotti")
        plt.ylabel("Quantità")
    if tortaAccDay:
        plt.pie(somma_ore, labels=solo_ore, autopct='%1.1f%%')
        plt.title("Accessi del giorno")
    if istoAccDay:
        plt.bar(solo_ore, somma_ore)
        plt.title("Accessi del giorno")
        plt.xlabel("Acquisti")
        plt.ylabel("Numero")
    if tortaCliAcc:
        plt.pie(utente_accessi, labels=nuova_lista, autopct='%1.1f%%')
        plt.title("Accessi per cliente")
    if istoCliAcc:
        plt.bar(nuova_lista, utente_accessi)
        plt.title("Accessi per cliente")
        plt.xlabel("Accessi")
        plt.ylabel("Numero")
    if tortaAccData:
        plt.pie(accessi, labels=date, autopct='%1.1f%%')
        plt.title("Accessi per data")
    if istoAccData:
        plt.bar(date, accessi)
        plt.title("Accessi per data")
        plt.xlabel("Date")
        plt.ylabel("Numero")

    plt.show()

    return render_template('es8_gestore_pagina.html')


if __name__ == '__main__':
    app.run(debug=True)
