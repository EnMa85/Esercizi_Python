'''
Scrivere un programma Agenzia i cui oggetti rappresentano appartamenti.
Le caratteristiche di un appartamento sono: mail del proprietario, superficie, piano e numero di stanze.
Queste informazioni devono essere rese disponibili alle altre classi tramite opportuni metodi.
Aggiungere un metodo visualizza (utilizzabile dalle altre classi) che stampa sullo schermo tutte le
caratteristiche dell’appartamento.
Per testare la classe, creare  tre appartamenti (oggetti della classe Appartamento), e stampare le
caratteristiche di tutti e tre gli appartamenti.
Successivamente creare una applicazione flask che consente all’utente di aggiungere un appartamento,
una volta aggiunto, questo viene inserito in una tabella mysql.
Quindi nella pagina home, oltre ad un bottone che porta all’inserimento di un nuovo appartamento,
vengono visualizzati gli appartamenti disponibili.
'''

from flask import Flask, render_template, request
import mysql.connector
import datetime
from datetime import datetime


mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="agenziaImmobiliare"
)


app = Flask(__name__)


class Appartamento:
    def __init__(self, proprietario, superficie, piano, stanze ):
        self.proprietario = proprietario
        self.superficie = superficie
        self.piano = piano
        self.stanze = stanze

    def __str__(self):
        return f"Recapito proprietario: {self.proprietario}\n{self.superficie} mq, {self.piano}° piano, {self.stanze} stanze."


def visualizza(appartamento):
    print(appartamento)


def save_cookies_db(utente, ultimo_accesso):
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='agenziaImmobiliare'
        )
        cursor = connection.cursor()
        query = "INSERT INTO accessi (utente, ultimo_accesso) VALUES (%s, %s)"
        values = (utente, ultimo_accesso)
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
def login():
    return render_template('es9_cliente_login.html')


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
        accesso = False
        # prendo la lista credenziali salvata
        mycursor.execute("SELECT email, password FROM utenti")
        dbLista_utenti = mycursor.fetchall()
        # verifico la corrispondenza delle credenziali
        for u in dbLista_utenti:
            if mail == u[0] and pw == u[1]:
                accesso = True
                save_cookies_db(mail, access)
                return render_template('es9_cliente_index.html', nome=nome, appartamenti=appartamenti)
        if not accesso:
            errore = "CREDENZIALI INVALIDE!!!"
            return render_template('es9_cliente_login.html', errore=errore)

    if registrati:  #se clicca su registrati
        gia_reg = False
        # prendo la lista mail salvata
        mycursor.execute("SELECT email FROM utenti")
        dbLista_mail = mycursor.fetchall()
        for m in dbLista_mail:
            if mail == m[0]:
                gia_reg == True
                errore = 'Utente già registrato! Clicca su ACCEDI'
                return render_template('es9_cliente_login.html', errore=errore)
        if not gia_reg:
            sql = "INSERT INTO utenti (email, password) VALUES (%s,%s)"
            val = (mail, pw)
            mycursor.execute(sql, val)
            mydb.commit()
            save_cookies_db(mail, access)
            return render_template('es9_cliente_index.html', nome=nome, appartamenti=appartamenti)


@app.route('/aggiungi', methods=['POST'])
def aggiungi():
    mycursor = mydb.cursor()
    aggiungi = request.form['aggiungi']
    if aggiungi:
        return render_template('es9_cliente_aggiungi.html')


@app.route('/aggiorna', methods=['POST'])
def aggiorna():
    mycursor = mydb.cursor()

    proprietario = request.form['proprietario']
    superficie = request.form['superficie']
    piano = request.form['piano']
    stanze = request.form['stanze']

    appartamento = [proprietario, superficie, piano, stanze]

    sql = "INSERT INTO checkAppartamenti (proprietario, superficie, piano, stanze) VALUES (%s,%s,%s,%s)"
    val = (proprietario, superficie, piano, stanze)
    mycursor.execute(sql, val)
    mydb.commit()

    return render_template('es9_cliente_aggiungi.html', appartamento=appartamento)


@app.route('/gestore')
def gestore():
    return render_template('es9_gestore_login.html')


@app.route('/login_gestore', methods=['POST'])
def login_gestore():
    mycursor = mydb.cursor()
    reg = False

    # SALVA ELENCO APPARTAMENTI PER CHECK
    mycursor.execute("SELECT * FROM checkAppartamenti")
    appartamentiXcheck = mycursor.fetchall()

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
            return render_template('es9_gestore_pagina.html', appartamentiXcheck=appartamentiXcheck)
    if not reg:
        errore = "CREDENZIALI INVALIDE!!!"
        return render_template('es9_gestore_login.html', errore=errore)


@app.route('/check', methods=['POST'])
def check():
    mycursor = mydb.cursor()
    id = request.form['id']
    pubblica = request.form.get('pubblica')
    rifiuta = request.form.get('rifiuta')

    if pubblica:
        # copio l'appartamento sul database degli appartamenti pubblicati
        sql = f"INSERT INTO appartamenti SELECT * FROM checkAppartamenti WHERE id_appartamento = {id};"
        mycursor.execute(sql,)
        mydb.commit()

    # cancello l'appartamento dalla lista provvisoria
    sql = "DELETE FROM checkAppartamenti WHERE id_appartamento = %s"
    val = (id,)
    mycursor.execute(sql, val)
    mydb.commit()
    # aggiorno la lista provvisoria degli appartamenti
    mycursor.execute("SELECT * FROM checkAppartamenti")
    appartamentiXcheck = mycursor.fetchall()

    return render_template('es9_gestore_pagina.html', appartamentiXcheck=appartamentiXcheck)


# SALVA ELENCO APPARTAMENTI
mycursor = mydb.cursor()
mycursor.execute("SELECT * FROM appartamenti")
appartamenti = mycursor.fetchall()


if __name__ == '__main__':
    app.run(debug=True)
