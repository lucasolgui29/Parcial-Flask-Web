from db import db

class Song(db.Model):
    __tablename__ = 'musica' # Nombre de la tabla en la base de datos

    id = db.Column(db.Integer, primary_key=True)
    # Mapeo de variables en español a nombres de columnas en la DB
    titulo = db.Column('cancion', db.String(255), nullable=False)
    artista = db.Column('artista', db.String(255), nullable=False)
    
    # 'duracion' se mapea a 'duracion' de la DB (asumiendo que 'duracion' en la DB son segundos)
    duracion = db.Column('duracion', db.Integer, nullable=False)
    
    album = db.Column('album', db.String(255), nullable=True)
    
    # 'anio' se mapea a 'anio' de la DB
    anio = db.Column('anio', db.Integer, nullable=True)

    # Columnas adicionales de tu DB que puedes mapear si las necesitas
    fecha_lanzamiento = db.Column('fecha_lanzamiento', db.Date, nullable=True)
    hora_estreno = db.Column('hora_estreno', db.Time, nullable=True)
    descripcion = db.Column('descripcion', db.Text, nullable=True)
    email_contacto = db.Column('email_contacto', db.String(255), nullable=True)
    
    # 'activo' se mapea a 'activo' de la DB
    activo = db.Column('activo', db.Boolean, default=True, nullable=False)

    def __repr__(self):
        return f"<Cancion {self.id}: {self.titulo} por {self.artista}>"

    # Método para serializar el objeto Cancion a un diccionario JSON
    def a_diccionario(self):
        # Aquí defines cómo quieres que se llamen las claves en tu respuesta JSON
        # Puedes mantener los nombres en inglés aquí si tu API está orientada a desarrolladores,
        # o cambiarlos también a español para total consistencia.
        # Por ahora, los mantendremos en español para las claves JSON.
        data = {
            'id': self.id,
            'titulo': self.titulo,
            'artista': self.artista,
            # Asumiendo que 'duracion' de la DB son segundos, lo convertimos a milisegundos para 'duration_ms' en el JSON
            'duracion': self.duracion * 1000 if self.duracion is not None else None,
            'album': self.album,
            'anio': self.anio,
            'activo': bool(self.activo),
            'categoria_duracion': self.obtener_categoria_duracion(), # Llama a la función con el nuevo nombre
            'fecha_lanzamiento': str(self.fecha_lanzamiento) if self.fecha_lanzamiento else None,
            'hora_estreno': str(self.hora_estreno) if self.hora_estreno else None,
            'descripcion': self.descripcion,
            'email_contacto': self.email_contacto
        }
        return data

    # Función auxiliar para la categoría de duración
    def obtener_categoria_duracion(self):
        # Usamos self.duracion que ya está mapeado a la columna 'duracion' de la DB (en segundos)
        # y lo multiplicamos por 1000 para la lógica de categorías en milisegundos.
        duracion_en_ms = self.duracion * 1000 if self.duracion is not None else 0

        if duracion_en_ms < 120000: # Menos de 2 minutos (120,000 ms)
            return 'corta'
        elif 120000 <= duracion_en_ms < 300000: # Entre 2 y 5 minutos (120,000 ms a 300,000 ms)
            return 'media'
        else: # Más de 5 minutos
            return 'larga'