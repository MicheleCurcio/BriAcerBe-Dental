from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)

# CONFIG DATABASE
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

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
    if request.method == "POST":
        nome = request.form.get("chir_uno")

        return render_template(
            "login.html",
            nome=nome,
        )
    return render_template("index.html")

@app.route("/appuntamento")
def appuntamento():
    return render_template("appuntamento.html")


@app.route('/register', methods=['GET'])
def register():
    return render_template("register.html")

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


import models
