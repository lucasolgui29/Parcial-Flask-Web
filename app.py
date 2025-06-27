from flask import Flask
from config.config import DATABASE_CONNECTION_URI
from models.db import db

app = Flask(__name__)
app.secret_key = 'clave_secreta'

app.config["SQLALCHEMY_DATABASE_URI"]= DATABASE_CONNECTION_URI 
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    try:
        print ("Base de datos inicializada")
    except Exception as e:
        print(f"Error al inicializar la base de datos: {e}")

if __name__ == '__main__':
    app.run(debug=True)