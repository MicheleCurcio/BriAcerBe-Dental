from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()  # solo istanza, NON legata all'app qui

class Dottore(db.Model):
    matricola = db.Column(db.String(10), primary_key=True)
    nome = db.Column(db.String(16), nullable=False)
    ruolo = db.Column(db.String(20))  # dentista / chirurgo / igienista

    #def __repr__(self):
        #return f"<Dottore matricola={self.matricola} nome={self.nome}>"

class Paziente(db.Model):
    username = db.Column(db.String(32), primary_key=True)
    nome = db.Column(db.String(16), nullable=False)
    cognome = db.Column(db.String(16), nullable=False)
    data_di_nascita = db.Column(db.Date, nullable=False)
    n_telefono = db.Column(db.String(10), nullable=False)
    sesso = db.Column(db.String(1), nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    def __repr__(self):
        return f"<Paziente username={self.username}>"

class Prenotazione(db.Model):
    scopo = db.Column(db.String(80), primary_key=True)
    data_richiesta_pren = db.Column(db.Date, primary_key=True)
    data_visita = db.Column(db.Date, primary_key=True)
    matricola = db.Column(
        db.String(10),
        db.ForeignKey("dottore.matricola"),
        primary_key=True
    )
    username = db.Column(
        db.String(32),
        db.ForeignKey("paziente.username"),
        primary_key=True
    )

    #def __repr__(self):
        #return (
            #f"<Prenotazione username={self.username} "
            #f"matricola={self.matricola} "
            #f"data={self.data_visita}>"
        #)
