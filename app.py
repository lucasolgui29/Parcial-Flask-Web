from flask import Flask
from config.config import DATABASE_CONNECTION_URI
from db import db
from models.song import Song

app = Flask(__name__)
app.secret_key = 'clave_secreta'

app.config["SQLALCHEMY_DATABASE_URI"]= DATABASE_CONNECTION_URI 
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    try:
        from models.song import Song
        db.create_all()
        print ("Base de datos inicializada")
    except Exception as e:
        print(f"Error al inicializar la base de datos: {e}")

if __name__ == '__main__':
    app.run(debug=True)