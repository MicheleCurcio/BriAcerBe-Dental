from flask import Flask, render_template,request

app = Flask(__name__)

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


@app.route("/pippo",methods=["GET", "POST"])
def pippo():
    if request.method == "POST":
        nome = request.form.get("chir_uno")

        return render_template(
            "dopo.html",
            nome=nome,
        )
    return render_template("index.html")

@app.route("/appuntamento")
def appuntamento():
    return render_template("appuntamento.html")

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
