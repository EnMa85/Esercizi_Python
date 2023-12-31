'''
Creare un file html con 4 select che rappresentano le scelte degli utenti per un ristorante.
Le select rappresentano il primo il secondo il contorno e il dolce.
Ogni select avrà valori diversi per il primo es. “lasagna” “risotto” etc
per il secondo “cotoletta” “spigola” etc.
'''

from flask import Flask, render_template, request
import mysql.connector
import matplotlib.pyplot as plt
from datetime import datetime


mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="ristorante"
)

app = Flask(__name__)

class Piatti:
    def __init__(self, piatto, prezzo):
        self.piatto = piatto
        self.prezzo = prezzo
    def __str__(self):
        return f"€ {self.prezzo} - {self.piatto}"

#dichiaro e inizializzo piatti e prezzi
primo1 = Piatti("Lasagne", 10)
primo2 = Piatti("Risotto ai funghi", 12)
primo3 = Piatti("Gnocchi alla sorrentina", 8)
secondo1 = Piatti("Parmigiana di melanzane", 8)
secondo2 = Piatti("Involtini di zucchine", 10)
secondo3 = Piatti("Sformato di verdure", 9)
contorno1 = Piatti("Insalata mista", 4)
contorno2 = Piatti("Verdure grigliate", 6)
contorno3 = Piatti("Patate alla brace", 7)
dolce1 = Piatti("Tiramisù", 5)
dolce2 = Piatti("Semifreddo all'arancia", 6)
dolce3 = Piatti("Tartufo di pizzo", 7)
lista_primi = []
lista_secondi = []
lista_contorni = []
lista_dolci = []
lista_primi.append(primo1)
lista_primi.append(primo2)
lista_primi.append(primo3)
lista_secondi.append(secondo1)
lista_secondi.append(secondo2)
lista_secondi.append(secondo3)
lista_contorni.append(contorno1)
lista_contorni.append(contorno2)
lista_contorni.append(contorno3)
lista_dolci.append(dolce1)
lista_dolci.append(dolce2)
lista_dolci.append(dolce3)


def save_cookies_db(user, last_access):
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='ristorante'
        )
        cursor = connection.cursor()
        query = "INSERT INTO accessi (user, last_access) VALUES (%s, %s)"
        values = (user, last_access)
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
    return render_template('es7_cliente_login.html')


@app.route('/login', methods=['POST'])
def index():
    mycursor = mydb.cursor()
    reg = False

    # prendo i dati dal form html
    mail = request.form['email']
    pw = request.form['password']
    access = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    btn1 = request.form.get('accedi')
    btn2 = request.form.get('registrati')
    #estrapolo il nome dell'utente
    nome = mail.rsplit("@")[0].capitalize()

    if btn1:  #se clicca su accedi
        # prendo la lista credenziali salvata
        mycursor.execute("SELECT email, password FROM utenti")
        dbLista_utenti = mycursor.fetchall()
        # verifico la corrispondenza delle credenziali
        for u in dbLista_utenti:
            if mail == u[0] and pw == u[1]:
                reg = True
                save_cookies_db(mail, access)
                return render_template('es7_cliente_index.html', mail=mail, nome=nome, lista_primi=lista_primi, lista_secondi=lista_secondi, lista_contorni=lista_contorni, lista_dolci=lista_dolci)
        if not reg:
            errore = "CREDENZIALI INVALIDE!!!"
            return render_template('es7_cliente_login.html', errore=errore)

    gia_reg = False
    if btn2:  #se clicca su registrati
        # prendo la lista credenziali salvata
        mycursor.execute("SELECT email FROM utenti")
        dbLista_mail = mycursor.fetchall()
        for m in dbLista_mail:
            if mail == m[0]:
                gia_reg == True
                errore = 'Utente già registrato! Clicca su ACCEDI'
                return render_template('es7_cliente_login.html', errore=errore)
        if not gia_reg:
            sql = "INSERT INTO utenti (email, password) VALUES (%s,%s)"
            val = (mail, pw)
            mycursor.execute(sql, val)
            mydb.commit()
            save_cookies_db(mail, access)
            return render_template('es7_cliente_index.html', mail=mail, nome=nome, lista_primi=lista_primi, lista_secondi=lista_secondi, lista_contorni=lista_contorni, lista_dolci=lista_dolci)


@app.route('/ordina', methods=['POST'])
def ordina():
    btn1 = request.form.get('ordina')
    btn2 = request.form.get('annulla')

    mycursor = mydb.cursor()

    if btn1:
        #prendo i dati dal form
        scelta_primo = request.form['primi']
        scelta_secondo = request.form['secondi']
        scelta_contorno = request.form['contorni']
        scelta_dolce = request.form['dolci']
        mail = request.form['mail']

        #associo i prezzi ai piatti scelti
        prezzo_menu = 0
        for primo in lista_primi:
            if scelta_primo == primo.piatto:
                prezzo_menu += int(primo.prezzo)
        for secondo in lista_secondi:
            if scelta_secondo == secondo.piatto:
                prezzo_menu += int(secondo.prezzo)
        for contorno in lista_contorni:
            if scelta_contorno == contorno.piatto:
                prezzo_menu += int(contorno.prezzo)
        for dolce in lista_dolci:
            if scelta_dolce == dolce.piatto:
                prezzo_menu += int(dolce.prezzo)
        #restituisco la stringa con menù e prezzo
        iltuomenu = [scelta_primo, scelta_secondo, scelta_contorno, scelta_dolce]
        #salvo l'ordine sul database
        sql = "INSERT INTO ordinicorso (mail, primo, secondo, contorno, dolce, prezzo) VALUES (%s,%s,%s,%s,%s,%s)"
        val = (mail, scelta_primo, scelta_secondo, scelta_contorno, scelta_dolce, prezzo_menu)
        mycursor.execute(sql, val)
        mydb.commit()
        return render_template('es7_cliente_ordina.html', iltuomenu=iltuomenu, prezzo_menu=prezzo_menu)

    if btn2:
        return render_template('es7_cliente_login.html')


@app.route('/gestore')
def gestore():
    return render_template('es7_gestore_login.html')


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
            return render_template('es7_gestore_pagina.html')
    if not reg:
        return render_template('es7_gestore_login.html')


@app.route('/gestore_ordini')
def pagina_ordini():
    # prendo la lista ordini in corso
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM ordinicorso")
    ordiniCorso = mycursor.fetchall()
    return render_template('es7_gestore_ordini.html', ordiniCorso=ordiniCorso)


@app.route('/accetta_ordine', methods=['POST'])
def accetta_ordine():
    mycursor = mydb.cursor()
    ordine_id = request.form['id']

    # copio l'ordine sul database degli ordini accettati
    sql = f"INSERT INTO ordiniconclusi SELECT * FROM ordinicorso WHERE id = {ordine_id};"
    mycursor.execute(sql,)
    mydb.commit()

    # cancello l'ordine dagli ordini in corso
    sql = "DELETE FROM ordinicorso WHERE id = %s"
    val = (ordine_id,)
    mycursor.execute(sql, val)
    mydb.commit()

    # aggiorno la lista ordini in corso
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM ordinicorso")
    ordiniCorso = mycursor.fetchall()
    return render_template('es7_gestore_ordini.html', ordiniCorso=ordiniCorso)


@app.route('/rifiuta_ordine', methods=['POST'])
def rifiuta_ordine():
    mycursor = mydb.cursor()
    idordine = request.form['id']

    # cancello l'ordine dagli ordini in corso
    sql = "DELETE FROM ordinicorso WHERE id = %s"
    val = (idordine,)
    mycursor.execute(sql, val)
    mydb.commit()

    # aggiorno la lista ordini in corso
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM ordinicorso")
    ordiniCorso = mycursor.fetchall()
    return render_template('es7_gestore_ordini.html', ordiniCorso=ordiniCorso)


@app.route('/gestore_incassi')
def pagina_incassi():
    totale_incassi = 0

    # prendo lo storico ordini
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM ordiniconclusi")
    ordiniConclusi = mycursor.fetchall()

    for ordine in ordiniConclusi:
        totale_incassi += int(ordine[5])
    return render_template('es7_gestore_incassi.html', ordiniConclusi=ordiniConclusi, totale_incassi=totale_incassi)


@app.route('/gestore_statistiche')
def pagina_statistiche():
    return render_template('es7_gestore_statistiche.html')


@app.route('/tortaCli')
def tortaCli():
    mycursor = mydb.cursor()

    totale_incassi = 0
    totale_cliente = []
    lista_clienti = []

    # prendo la lista ordini conclusi
    mycursor.execute("SELECT * FROM ordiniconclusi")
    ordiniConclusi = mycursor.fetchall()

    for ordine in ordiniConclusi:
        cont = 0
        cliente_ins = False
        totale_incassi += int(ordine[5])
        for cliente in lista_clienti:
            if cliente == ordine[0]:
                totale_cliente[cont] += int(ordine[5])
                cliente_ins = True
                cont += 1
        if not cliente_ins:
            lista_clienti.append(ordine[0])
            totale_cliente.append(int(ordine[5]))

    plt.pie(totale_cliente, labels=lista_clienti, autopct='%1.1f%%')
    plt.title("Incassi per cliente")

    plt.show()
    return render_template('es7_gestore_statistiche.html')


@app.route('/istoCli')
def istoCli():
    mycursor = mydb.cursor()
    totale_cliente = []
    lista_clienti = []

    # prendo la lista ordini conclusi
    mycursor.execute("SELECT * FROM ordiniconclusi")
    ordiniConclusi = mycursor.fetchall()

    for ordine in ordiniConclusi:
        cont = 0
        cliente_ins = False
        for cliente in lista_clienti:
            if cliente == ordine[0]:
                totale_cliente[cont] += int(ordine[5])
                cliente_ins = True
                cont += 1
        if not cliente_ins:
            lista_clienti.append(ordine[0])
            totale_cliente.append(int(ordine[5]))

    plt.bar(lista_clienti, totale_cliente)
    plt.title("Incassi per cliente")
    plt.xlabel("Clienti")
    plt.ylabel("Incassi")

    plt.show()
    return render_template('es7_gestore_statistiche.html')


@app.route('/tortaPia')
def tortaPia():
    mycursor = mydb.cursor()

    totale_piatti = []
    lista_piatti = []

    # prendo la lista ordini conclusi
    mycursor.execute("SELECT primo, secondo, contorno, dolce FROM ordiniconclusi")
    piatti_venduti = mycursor.fetchall()

    for primo in lista_primi:
        lista_piatti.append(primo.piatto)
        totale_piatti.append(0)
    for secondo in lista_secondi:
        lista_piatti.append(secondo.piatto)
        totale_piatti.append(0)
    for contorno in lista_contorni:
        lista_piatti.append(contorno.piatto)
        totale_piatti.append(0)
    for dolce in lista_dolci:
        lista_piatti.append(dolce.piatto)
        totale_piatti.append(0)

    cont = 0
    for piatto in lista_piatti:
        for ordine in piatti_venduti:
            if str(piatto) == str(ordine[0]) or str(piatto) == str(ordine[1]) or str(piatto) == str(ordine[2]) or str(piatto) == str(ordine[3]):
                totale_piatti[cont] += 1
        cont += 1

    plt.pie(totale_piatti, labels=lista_piatti, autopct='%1.1f%%')
    plt.title("Piatti venduti")

    plt.show()
    return render_template('es7_gestore_statistiche.html')


@app.route('/istoPia')
def istoPia():
    mycursor = mydb.cursor()

    totale_piatti = []
    lista_piatti = []

    # prendo la lista ordini conclusi
    mycursor.execute("SELECT primo, secondo, contorno, dolce FROM ordiniconclusi")
    piatti_venduti = mycursor.fetchall()

    for primo in lista_primi:
        lista_piatti.append(primo.piatto)
        totale_piatti.append(0)
    for secondo in lista_secondi:
        lista_piatti.append(secondo.piatto)
        totale_piatti.append(0)
    for contorno in lista_contorni:
        lista_piatti.append(contorno.piatto)
        totale_piatti.append(0)
    for dolce in lista_dolci:
        lista_piatti.append(dolce.piatto)
        totale_piatti.append(0)

    cont = 0
    for piatto in lista_piatti:
        for ordine in piatti_venduti:
            if str(piatto) == str(ordine[0]) or str(piatto) == str(ordine[1]) or str(piatto) == str(ordine[2]) or str(piatto) == str(ordine[3]):
                totale_piatti[cont] += 1
        cont += 1

    plt.bar(lista_piatti, totale_piatti)
    plt.title("Incassi per piatto")
    plt.xlabel("Piatti")
    plt.ylabel("Incassi")

    plt.show()
    return render_template('es7_gestore_statistiche.html')


if __name__ == '__main__':
    app.run(debug=True)
