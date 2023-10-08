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
import os
from werkzeug.utils import secure_filename


mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="agenziaImmobiliare"
)


app = Flask(__name__)


# Configura la cartella per il caricamento delle immagini
UPLOAD_FOLDER = 'static/uploads1'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Estensioni consentite per le immagini
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


class Appartamento:
    def __init__(self, proprietario, superficie, piano, stanze ):
        self.proprietario = proprietario
        self.superficie = superficie
        self.piano = piano
        self.stanze = stanze

    def __str__(self):
        return f"Recapito proprietario: {self.proprietario}\n{self.superficie} mq, {self.piano}° piano, {self.stanze} stanze."


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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

    # SALVA ELENCO APPARTAMENTI
    mycursor.execute("SELECT * FROM appartamenti")
    appartamenti = mycursor.fetchall()

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
    aggiungi = request.form['aggiungi']
    if aggiungi:
        return render_template('es9_cliente_aggiungi.html')


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    mycursor = mydb.cursor()
    carica = request.form.get('carica')
    inserisci = request.form.get('inserisci')

    if carica:
        if request.method == 'POST':
            # Controlla se è stato fornito un file
            if 'file' not in request.files:
                error = "Nessun file fornito"
                return render_template('es9_cliente_aggiungi.html', error=error)

            file = request.files['file']
            # Controlla se il file ha un nome
            if file.filename == '':
                error = "Nessun file selezionato"
                return render_template('es9_cliente_aggiungi.html', error=error)

            # Controlla se il file è un'immagine consentita
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

                #inserisco nel database il nome della foto ed inizializzo come vuote le altre colonne
                sql = "INSERT INTO checkAppartamenti (proprietario, superficie, piano, stanze, foto) VALUES (%s,%s,%s,%s,%s)"
                val = ('n', 'n', 'n', 'n', filename)
                mycursor.execute(sql, val)
                mydb.commit()
                return render_template('es9_cliente_aggiungi.html', filename=filename)

            error = "File non valido. Le estensioni consentite sono: " + ", ".join(ALLOWED_EXTENSIONS)
            return render_template('es9_cliente_aggiungi.html', error=error)

    if inserisci:
        proprietario = request.form['proprietario']
        superficie = request.form['superficie']
        piano = request.form['piano']
        stanze = request.form['stanze']
        appartamento = [proprietario, superficie, piano, stanze]


        #cambio il nome dell'immagine per omologarla
        mycursor.execute("SELECT foto FROM checkAppartamenti WHERE proprietario = 'n'")
        filename = mycursor.fetchone()[0]
        mycursor.execute(f"SELECT id_check FROM checkAppartamenti WHERE proprietario = 'n'")
        id = mycursor.fetchone()[0]
        image = f"id{id}_imageCheck.{filename.rsplit('.')[1]}"
        os.rename('static/uploads1/' + filename, 'static/uploads1/' + image)

        #aggiorno la riga che era stata inizializzata come vuota
        sql = f"UPDATE checkAppartamenti SET proprietario = '{proprietario}', superficie = '{superficie}', " \
              f"piano = '{piano}', stanze = '{stanze}', foto = '{image}' WHERE id_check = '{id}'"
        mycursor.execute(sql)
        mydb.commit()

        #estrapolo il nome della foto dalla tupla
        cursor = mydb.cursor(buffered=True, dictionary=True)
        cursor.execute(f"SELECT * FROM checkAppartamenti WHERE id_check = {id}")
        riga = cursor.fetchall()
        for a in riga:
            if a['foto']:
                foto = a['foto']
        return render_template('es9_cliente_aggiungi.html', appartamento=appartamento, foto=foto)


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
    idcheck = request.form['id']
    pubblica = request.form.get('pubblica')
    rifiuta = request.form.get('rifiuta')

    if pubblica:
        # copio l'appartamento sul database degli appartamenti pubblicati
        mycursor.execute(f"SELECT proprietario FROM checkAppartamenti WHERE id_check = '{idcheck}'")
        proprietario = mycursor.fetchone()[0]
        mycursor.execute(f"SELECT superficie FROM checkAppartamenti WHERE id_check = '{idcheck}'")
        superficie = mycursor.fetchone()[0]
        mycursor.execute(f"SELECT piano FROM checkAppartamenti WHERE id_check = '{idcheck}'")
        piano = mycursor.fetchone()[0]
        mycursor.execute(f"SELECT stanze FROM checkAppartamenti WHERE id_check = '{idcheck}'")
        stanze = mycursor.fetchone()[0]
        mycursor.execute(f"SELECT foto FROM checkAppartamenti WHERE id_check = '{idcheck}'")
        foto = mycursor.fetchone()[0]
        sql = "INSERT INTO appartamenti (proprietario, superficie, piano, stanze, foto) VALUES (%s,%s,%s,%s,%s)"
        val = (proprietario, superficie, piano, stanze, foto)
        mycursor.execute(sql, val)
        mydb.commit()
        # cambio il nome dell'immagine per omologarla
        id = mycursor.lastrowid
        mycursor.execute(f"SELECT foto FROM Appartamenti WHERE id_appartamento = '{id}'")
        filename = mycursor.fetchone()[0]
        image = f"id{id}_image.{filename.rsplit('.')[1]}"
        os.rename('static/uploads1/' + filename, 'static/uploads1/' + image)
        # aggiorno il nome dell'immagine nella lista definitiva
        sql = f"UPDATE Appartamenti SET foto = '{image}' WHERE id_appartamento = '{id}'"
        mycursor.execute(sql)
        mydb.commit()

    if rifiuta:
        # elimino l'immagine
        mycursor.execute(f"SELECT foto FROM checkAppartamenti WHERE id_check = '{idcheck}'")
        filename = mycursor.fetchone()[0]
        os.remove('static/uploads1/' + filename)

    # cancello l'appartamento dalla lista provvisoria
    sql = "DELETE FROM checkAppartamenti WHERE id_check = %s"
    val = (idcheck,)
    mycursor.execute(sql, val)
    mydb.commit()
    # aggiorno la lista provvisoria degli appartamenti
    mycursor.execute("SELECT * FROM checkAppartamenti")
    appartamentiXcheck = mycursor.fetchall()

    return render_template('es9_gestore_pagina.html', appartamentiXcheck=appartamentiXcheck)


if __name__ == '__main__':
    app.run(debug=True)
