#import delle librerie per il DB
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates

db = SQLAlchemy()  # solo istanza, NON legata all'app qui

# relazione Paziente
class Paziente(db.Model):
    username = db.Column(db.String(64), primary_key=True)
    nome = db.Column(db.String(16), nullable=False)
    cognome = db.Column(db.String(16), nullable=False)
    data_di_nascita = db.Column(db.Date, nullable=False)
    n_telefono = db.Column(db.String(10), nullable=False)
    sesso = db.Column(db.String(1), nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    # controllo per il numero di telefono
    @validates("n_telefono")
    def valida_telefono(self, key, numero):
        if not (numero.isdigit() and len(numero) == 10):
            raise ValueError("Numero di telefono non valido")
        return numero

# relazione Prenotazione
class Prenotazione(db.Model):
    scopo = db.Column(db.String(80), nullable=False)
    data_richiesta_pren = db.Column(db.Date, nullable=False)
    data_visita = db.Column(db.Date, primary_key=True)
    ora_visita = db.Column(db.Integer, primary_key=True)
    matricola = db.Column(db.String(10), primary_key=True)

    username = db.Column(
        db.String(64),
        db.ForeignKey("paziente.username")
    )

    __table_args__ = (
        db.UniqueConstraint(
            'username',
            'data_visita',
            'ora_visita',
            name='uq_prenotazione_user_data_ora'
        ),
    )