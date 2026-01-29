from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from werkzeug.security import check_password_hash
from datetime import date
#import os

app = Flask(__name__)

# CONFIG DATABASE
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#app.secret_key = os.urandom(24)  # genera attraverso import os una chiave casuale ad ogni avvio

app.secret_key = "chiavesegretissima_per_prenotazioni"

from models import db  # importa qui dopo aver creato l'app
db.init_app(app)       # ⚡ importantissimo: lega l'istanza db all'app

migrate = Migrate(app, db)

import models  # ora sicuro, senza ciclo


@app.route("/", methods=["GET", "POST"])
# @app.route("/login",methods=["GET", "POST"])
def login():
    from models import Paziente
    from models import Dottore
    from models import Prenotazione

    #if request.method == "POST":
    #nome = request.form.get("chir_uno")

    #return render_template(
    #"index.html",
    #nome=nome,
    #)
    #return render_template("index.html")
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # 1. Cerca l'utente
        paziente = Paziente.query.get(username)

        # 2. Controlla password
        if paziente and check_password_hash(paziente.password_hash, password):
            # LOGIN OK
            session["username"] = paziente.username
            return redirect(url_for("home"))

        # LOGIN FALLITO
        return render_template("index.html", errore="Credenziali non valide")

    return render_template("index.html")


@app.route('/home')
def home():
    username = session.get('username', 'Ospite')  # se non loggato mostra "Ospite"
    return render_template('home.html', username=username)

@app.route("/prenotazioni")
def prenotazioni():
    return render_template("prenotazioni.html")

@app.route("/info")
def info():
    return render_template("info.html")


@app.route("/appuntamento")
def appuntamento():
    return render_template("appuntamento.html")


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Qui prenderemo i dati dal form
        username = request.form['username']
        nome = request.form['nome']
        cognome = request.form['cognome']
        data_di_nascita = datetime.strptime(request.form['datanascita'], "%Y-%m-%d").date() # perché SQLAlchemy accetta
                                                                                            # oggetti datetime.date, non stringhe tipo "2004-08-31"
        sesso = request.form['sesso']
        n_telefono = request.form['numerotelefono']
        password = request.form['password']
        confermapassword = request.form['confermapassword']

        if password == confermapassword and data_di_nascita <= date.today():
            # Inserisci hash della password (consigliato)
            from werkzeug.security import generate_password_hash
            password_hash = generate_password_hash(password)

            # Crea oggetto Paziente
            from models import Paziente
            nuovo_paziente = Paziente(
                username=username,
                nome=nome,
                cognome=cognome,
                data_di_nascita=data_di_nascita,
                sesso=sesso,
                n_telefono=n_telefono,
                password_hash=password_hash
            )
            db.session.add(nuovo_paziente)
            db.session.commit()

            return render_template('index.html')
        else:
            # le password non coincidono oppure ha messo una data > a quella di oggi (deve ancora nascere)
            return render_template("register.html", errore="Password non identiche")


    return render_template('register.html')

@app.route("/dentist")
def dentist():
    return render_template("dentist.html")

@app.route("/surgeon")
def surgeon():
    return render_template("surgeon.html")

@app.route("/hygienist")
def hygienist():
    return render_template("hygienist.html")

if __name__ == "__main__":
    app.run(debug=True)



