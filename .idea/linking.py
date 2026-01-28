from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from werkzeug.security import check_password_hash
#from models import Paziente

app = Flask(__name__)

# CONFIG DATABASE
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

import models

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/prenotazioni")
def prenotazioni():
    return render_template("prenotazioni.html")

@app.route("/servizi")
def servizi():
    return render_template("servizi.html")

@app.route("/info")
def info():
    return render_template("info.html")


@app.route("/login",methods=["GET", "POST"])
def login():
    #if request.method == "POST":
        #nome = request.form.get("chir_uno")

        #return render_template(
            #"login.html",
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
        return render_template("login.html", errore="Credenziali non valide")

    return render_template("login.html")

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

        return "Registrazione completata!"

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



