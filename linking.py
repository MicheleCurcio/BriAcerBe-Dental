from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from werkzeug.security import check_password_hash
from datetime import date
from flask import jsonify
from sqlalchemy.orm import validates
from sqlalchemy.exc import IntegrityError
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
    #from models import Dottore
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

@app.route("/logout")
def logout():
    # Rimuove il username dalla sessione, se esiste
    session.pop("username", None)

    # Reindirizza alla pagina di login
    return redirect(url_for("login"))

@app.route('/home')
def home():
    username = session.get('username', 'Ospite')  # se non loggato mostra "Ospite"
    return render_template('home.html', username=username)

@app.route("/prenotazioni")
def prenotazioni():
    username = session.get("username")

    from models import Prenotazione

    # tutte le prenotazioni di legate a quell'utente
    prenotazioni = Prenotazione.query.filter_by(
        username=username
    ).all()

    return render_template("prenotazioni.html", prenotazioni=prenotazioni)

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

            try:
                db.session.add(nuovo_paziente)
                db.session.commit()
                #flash("Registrazione avvenuta con successo")
                return render_template('index.html')
            except ValueError as e:       # intercetta l'errore lanciato dal model
                db.session.rollback()     # molto importante, altrimenti sessione sporca
                #flash(str(e))
                return redirect(url_for("register"))
            except Exception as e:        # intercetta eventuali altri errori di DB
                db.session.rollback()
                #flash("Errore nel database: " + str(e))
                return redirect(url_for("register"))


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

@app.route("/sceltadentist")
def sceltadentist():
    deninput = request.args.get("deninput")
    username = session.get("username")
    return render_template("sceltadentist.html", deninput=deninput, username=username)

@app.route("/sceltahygienist")
def sceltahygienist():
    hyginput = request.args.get("hyginput")
    username = session.get("username")
    return render_template("sceltahygienist.html", hyginput=hyginput, username=username)

@app.route("/sceltasurgeon")
def sceltasurgeon():
    surinput = request.args.get("surinput")
    username = session.get("username")
    return render_template("sceltasurgeon.html", surinput=surinput, username=username)

@app.route("/conferma")
def conferma():
    scopo = request.args.get("scopo")

    ora_visita = request.args.get("ore", type=int)

    matricola = request.args.get("matricola")

    giorno_str = request.args.get("giorno")  # "2026-02-09" || "2026-02-10" || "2026-02-11"
    giorno = datetime.strptime(giorno_str, "%Y-%m-%d").date() # lo adatta al tipo di dato date per il database

    oggi = date.today()

    username = session.get("username")

    from models import Prenotazione
    nuova_prenotazione = Prenotazione(
        scopo = scopo,
        data_richiesta_pren = oggi,
        data_visita = giorno,
        ora_visita = ora_visita,
        matricola = matricola,
        username = username
    )
    try:
        db.session.add(nuova_prenotazione)
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        errore = "Errore di prenotazione"  # fallback
        msg = str(e.orig) # messaggio del DB
        # print(msg)

        if all(k in msg for k in ["username", "data_visita", "ora_visita"]):
            errore = "Una persona non deve fare due visite contemporaneamente"
        elif all(k in msg for k in ["matricola", "data_visita", "ora_visita"]):
            errore = "Un medico non deve fare due visite contemporaneamente"
        else:
            errore = "Errore nella prenotazione"
        return render_template("conferma.html", errore=errore, msg=msg)

    return render_template("conferma.html")


from flask import jsonify

@app.route("/api/disponibilita-orari")
def disponibilita_orari():
    from models import Prenotazione

    matricola = request.args.get("matricola")
    giorno_str = request.args.get("giorno")

    if not matricola or not giorno_str:
        return jsonify({"ok": False}), 400

    giorno = datetime.strptime(giorno_str, "%Y-%m-%d").date()

    # tutte le prenotazioni di quell'igienista in quel giorno
    prenotazioni = Prenotazione.query.filter_by(
        matricola=matricola,
        data_visita=giorno
    ).all()

    # ore già occupate
    ore_occupate = [p.ora_visita for p in prenotazioni]

    # ore possibili
    ore_possibili = [16, 17, 18]

    # ore disponibili
    ore_disponibili = [o for o in ore_possibili if o not in ore_occupate]

    return jsonify({
        "ok": True,
        "ore_disponibili": ore_disponibili
    })





if __name__ == "__main__":
    app.run(debug=True)



