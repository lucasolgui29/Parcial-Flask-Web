from db import db

class Song(db.Model):
    __tablename__ = 'musica'

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column('cancion', db.String(255), nullable=False)
    artista = db.Column('artista', db.String(255), nullable=False)
    
    duracion = db.Column('duracion', db.Integer, nullable=False)
    
    album = db.Column('album', db.String(255), nullable=True)
    
    anio = db.Column('anio', db.Integer, nullable=True)

    fecha_lanzamiento = db.Column('fecha_lanzamiento', db.Date, nullable=True)
    hora_estreno = db.Column('hora_estreno', db.Time, nullable=True)
    descripcion = db.Column('descripcion', db.Text, nullable=True)
    email_contacto = db.Column('email_contacto', db.String(255), nullable=True)
    
    activo = db.Column('activo', db.Boolean, default=True, nullable=False)

    def __repr__(self):
        return f"<Cancion {self.id}: {self.titulo} por {self.artista}>"

    def __init__ (self):
        data = {
            'id': self.id,
            'titulo': self.titulo,
            'artista': self.artista,
            'duracion': self.duracion * 1000 if self.duracion is not None else None,
            'album': self.album,
            'anio': self.anio,
            'activo': bool(self.activo),
            'categoria_duracion': self.obtener_categoria_duracion(), 
            'fecha_lanzamiento': str(self.fecha_lanzamiento) if self.fecha_lanzamiento else None,
            'hora_estreno': str(self.hora_estreno) if self.hora_estreno else None,
            'descripcion': self.descripcion,
            'email_contacto': self.email_contacto
        }
        return data