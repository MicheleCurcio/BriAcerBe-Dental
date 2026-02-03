from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime, date
from werkzeug.security import check_password_hash
from flask import jsonify
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)

# =========================
# 🔵 FILTRO DATA IN ITALIANO
# =========================
@app.template_filter('data_it')
def data_it(d):
    giorni = [
        "Lunedì", "Martedì", "Mercoledì",
        "Giovedì", "Venerdì", "Sabato", "Domenica"
    ]
    mesi = [
        "Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno",
        "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"
    ]
    return f"{giorni[d.weekday()]} {d.day} {mesi[d.month - 1]}"


# =========================
# CONFIG DATABASE
# =========================
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.secret_key = "chiavesegretissima_per_prenotazioni"

from models import db
db.init_app(app)

migrate = Migrate(app, db)

import models


@app.route("/", methods=["GET", "POST"])
def login():
    from models import Paziente

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        paziente = Paziente.query.get(username)

        if paziente and check_password_hash(paziente.password_hash, password):
            session["username"] = paziente.username
            return redirect(url_for("home"))

        return render_template("index.html", errore="Credenziali non valide")

    return render_template("index.html")


@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))


@app.route('/home',methods=["GET", "POST"])
def home():
    if request.method == "POST":

         username = session.get('username', 'Ospite')
         return render_template('home.html', username=username)
    username = session.get('username', 'Ospite')

    return render_template('home.html', username=username)



@app.route("/prenotazioni")
def prenotazioni():
    username = session.get("username")
    from models import Prenotazione

    prenotazioni = Prenotazione.query.filter_by(username=username).all()
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
        from models import Paziente
        from werkzeug.security import generate_password_hash

        username = request.form['username']
        nome = request.form['nome']
        cognome = request.form['cognome']
        data_di_nascita = datetime.strptime(
            request.form['datanascita'], "%Y-%m-%d"
        ).date()
        sesso = request.form['sesso']
        n_telefono = request.form['numerotelefono']
        password = request.form['password']
        confermapassword = request.form['confermapassword']

        if password == confermapassword and data_di_nascita <= date.today():
            password_hash = generate_password_hash(password)

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
                return render_template('index.html')
            except:
                db.session.rollback()
                return redirect(url_for("register"))

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
    from models import Prenotazione

    scopo = request.args.get("scopo")
    ora_visita = request.args.get("ore", type=int)
    matricola = request.args.get("matricola")

    giorno = datetime.strptime(
        request.args.get("giorno"), "%Y-%m-%d"
    ).date()

    nuova_prenotazione = Prenotazione(
        scopo=scopo,
        data_richiesta_pren=date.today(),
        data_visita=giorno,
        ora_visita=ora_visita,
        matricola=matricola,
        username=session.get("username")
    )

    try:
        db.session.add(nuova_prenotazione)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return render_template("conferma.html", errore="Occhio! Hai già un appuntamento in questa data a quest'ora.")

    return render_template("conferma.html")


@app.route("/api/disponibilita-orari")
def disponibilita_orari():
    from models import Prenotazione

    matricola = request.args.get("matricola")
    giorno = datetime.strptime(
        request.args.get("giorno"), "%Y-%m-%d"
    ).date()

    prenotazioni = Prenotazione.query.filter_by(
        matricola=matricola,
        data_visita=giorno
    ).all()

    ore_occupate = [p.ora_visita for p in prenotazioni]
    ore_disponibili = [o for o in [16, 17, 18] if o not in ore_occupate]

    return jsonify({"ok": True, "ore_disponibili": ore_disponibili})

@app.route('/cancella', methods=['POST'])
def cancella():
    from models import Prenotazione

    ora_visita =  request.form.get("ore", type=int)

    giorno = datetime.strptime(
        request.form.get("giorno"), "%Y-%m-%d"
    ).date()

    username = session.get("username")

    # cancella dal DB
    cestino = Prenotazione.query.filter_by(data_visita=giorno, ora_visita=ora_visita, username=username).all()

    for c in cestino:
        db.session.delete(c)
    db.session.commit()

    return redirect(url_for("prenotazioni"))



if __name__ == "__main__":
    app.run(debug=True)