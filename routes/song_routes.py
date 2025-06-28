import os
from flask import Blueprint, flash, redirect, render_template, request, url_for, jsonify
# werkzeug.utils.secure_filename no se usa en estas rutas, puedes quitarla si no la necesitas
# from werkzeug.utils import secure_filename 
from db import db
from models.song import Song # Importa tu modelo Song
from sqlalchemy.exc import IntegrityError, SQLAlchemyError # Importa SQLAlchemyError para un manejo más amplio

# Renombrar el Blueprint y su url_prefix para consistencia en español
canciones_bp = Blueprint('canciones_bp', __name__, url_prefix='/canciones') #

@canciones_bp.route('/', methods=['GET'])
def obtener_canciones(): # Función para obtener todas las canciones, con filtrado
    filtro_duracion = request.args.get('duracion', '').lower() #
    
    # Inicia la consulta filtrando solo las canciones activas por defecto
    consulta = Song.query.filter_by(activo=True) #

    if filtro_duracion: #
        if filtro_duracion == 'corta': #
            # Usamos el atributo 'duracion' del modelo que mapea a la columna 'duracion' de la DB (en segundos)
            consulta = consulta.filter(Song.duracion < 120) # Menos de 2 minutos (120 segundos)
        elif filtro_duracion == 'media': #
            consulta = consulta.filter(Song.duracion >= 120, Song.duracion < 300) # Entre 2 y 5 minutos (120-300 segundos)
        elif filtro_duracion == 'larga': #
            consulta = consulta.filter(Song.duracion >= 300) # Más de 5 minutos (300 segundos)
        else:
            return jsonify({"mensaje": "Filtro de duración no válido. Use 'corta', 'media' o 'larga'."}), 400

    try:
        canciones = consulta.all() #
        # Usa el método a_diccionario() del modelo Song
        return jsonify([cancion.a_diccionario() for cancion in canciones]), 200 #
    except SQLAlchemyError as e:
        # Captura errores específicos de la base de datos
        return jsonify({"mensaje": f"Error de base de datos al obtener canciones: {str(e)}"}), 500 #
    except Exception as e:
        # Captura cualquier otro error inesperado
        return jsonify({"mensaje": f"Error interno del servidor: {str(e)}"}), 500 #


@canciones_bp.route('/<int:id_cancion>', methods=['GET'])
def obtener_cancion(id_cancion): # Función para obtener una canción por ID
    # Solo se buscan canciones activas por defecto
    cancion = Song.query.filter_by(id=id_cancion, activo=True).first() #
    if cancion: #
        return jsonify(cancion.a_diccionario()), 200 #
    return jsonify({"mensaje": "Canción no encontrada o no activa."}), 404 #

@canciones_bp.route('/', methods=['POST'])
def crear_cancion(): # Función para crear una nueva canción
    datos = request.get_json() #
    if not datos: #
        return jsonify({"mensaje": "Datos JSON inválidos o ausentes."}), 400 #

    titulo_req = datos.get('titulo') #
    artista_req = datos.get('artista') #
    # Esperamos 'duracion' del cliente, que debe ser en segundos para coincidir con la DB
    duracion_req = datos.get('duracion') #

    # Validaciones básicas
    if not titulo_req or not artista_req or not isinstance(duracion_req, (int, float)) or duracion_req <= 0: #
        return jsonify({"mensaje": "Faltan campos obligatorios (titulo, artista, duracion válido)."}), 400 #

    try:
        nueva_cancion = Song( #
            titulo=titulo_req, #
            artista=artista_req, #
            duracion=int(duracion_req), # Mapea a la columna 'duracion' en segundos
            album=datos.get('album'), #
            genero=datos.get('genero'), #
            anio=datos.get('anio'), # Coincide con la columna 'anio' de la DB
            fecha_lanzamiento=datos.get('fecha_lanzamiento'), # Asegúrate que el formato sea 'YYYY-MM-DD'
            hora_estreno=datos.get('hora_estreno'),         # Asegúrate que el formato sea 'HH:MM:SS'
            descripcion=datos.get('descripcion'), #
            email_contacto=datos.get('email_contacto') #
        )
        db.session.add(nueva_cancion) #
        db.session.commit() #
        return jsonify(nueva_cancion.a_diccionario()), 201 # 201 Created
    except IntegrityError:
        db.session.rollback() #
        return jsonify({"mensaje": "Error de integridad de datos. Posiblemente un campo UNIQUE duplicado o dato inválido."}), 409 #
    except SQLAlchemyError as e:
        db.session.rollback() #
        return jsonify({"mensaje": f"Error de base de datos al crear canción: {str(e)}"}), 500 #
    except Exception as e:
        db.session.rollback() #
        return jsonify({"mensaje": f"Error interno del servidor: {str(e)}"}), 500 #

@canciones_bp.route('/<int:id_cancion>', methods=['PUT'])
def actualizar_cancion(id_cancion):
    # Solo permite actualizar canciones activas, a menos que se necesite restaurar con PUT (mejor con PATCH)
    cancion = Song.query.filter_by(id=id_cancion, activo=True).first() #
    if not cancion: #
        return jsonify({"mensaje": "Canción no encontrada o no activa para actualizar."}), 404 #

    datos = request.get_json() #
    if not datos: #
        return jsonify({"mensaje": "Datos JSON inválidos o ausentes."}), 400 #

    # Actualizar campos si están presentes en la solicitud y son válidos
    if 'titulo' in datos: #
        cancion.titulo = datos['titulo'] #
    if 'artista' in datos: #
        cancion.artista = datos['artista'] #
    if 'duracion' in datos: #
        if isinstance(datos['duracion'], (int, float)) and datos['duracion'] > 0: #
            cancion.duracion = int(datos['duracion']) # Mapea a la columna 'duracion' en segundos
        else:
            return jsonify({"mensaje": "duracion debe ser un número entero positivo."}), 400 #
    if 'album' in datos: #
        cancion.album = datos['album'] #
    if 'genero' in datos: #
        cancion.genero = datos['genero'] #
    if 'anio' in datos: #
        cancion.anio = datos['anio'] # Coincide con la columna 'anio' de la DB

    # Si se intenta cambiar 'activo' con PUT, asegúrate de que sea booleano.
    if 'activo' in datos: #
        if isinstance(datos['activo'], bool): #
            cancion.activo = datos['activo'] #
        else:
            return jsonify({"mensaje": "activo debe ser un valor booleano (true/false)."}), 400 #
    
    # Actualizar campos adicionales si se envían
    if 'fecha_lanzamiento' in datos: #
        cancion.fecha_lanzamiento = datos['fecha_lanzamiento'] #
    if 'hora_estreno' in datos: #
        cancion.hora_estreno = datos['hora_estreno'] #
    if 'descripcion' in datos: #
        cancion.descripcion = datos['descripcion'] #
    if 'email_contacto' in datos: #
        cancion.email_contacto = datos['email_contacto'] #

    try:
        db.session.commit() #
        return jsonify(cancion.a_diccionario()), 200 # OK
    except IntegrityError:
        db.session.rollback() #
        return jsonify({"mensaje": "Error de integridad de datos al actualizar. Posiblemente un campo UNIQUE duplicado o dato inválido."}), 409 #
    except SQLAlchemyError as e:
        db.session.rollback() #
        return jsonify({"mensaje": f"Error de base de datos al actualizar canción: {str(e)}"}), 500 #
    except Exception as e:
        db.session.rollback() #
        return jsonify({"mensaje": f"Error interno del servidor: {str(e)}"}), 500 #

@canciones_bp.route('/<int:id_cancion>', methods=['DELETE'])
def baja_logica_cancion(id_cancion):
    cancion = Song.query.filter_by(id=id_cancion, activo=True).first() # Solo se puede "eliminar" si está activa
    if not cancion: #
        return jsonify({"mensaje": "Canción no encontrada o ya dada de baja."}), 404 #
    
    cancion.activo = False # Marca como inactiva
    try:
        db.session.commit() #
        return jsonify({"mensaje": f"Canción '{cancion.titulo}' (ID: {cancion.id}) dada de baja exitosamente."}), 200 #
    except SQLAlchemyError as e:
        db.session.rollback() #
        return jsonify({"mensaje": f"Error de base de datos al dar de baja la canción: {str(e)}"}), 500 #
    except Exception as e:
        db.session.rollback() #
        return jsonify({"mensaje": f"Error interno del servidor: {str(e)}"}), 500 #

@canciones_bp.route('/<int:id_cancion>/restaurar', methods=['PATCH'])
def restaurar_cancion(id_cancion):
    cancion = Song.query.filter_by(id=id_cancion, activo=False).first() # Busca solo canciones inactivas
    if not cancion: #
        return jsonify({"mensaje": "Canción no encontrada o ya está activa."}), 404 #
    
    cancion.activo = True #
    try:
        db.session.commit() #
        return jsonify({"mensaje": f"Canción '{cancion.titulo}' (ID: {cancion.id}) restaurada exitosamente."}), 200 #
    except SQLAlchemyError as e:
        db.session.rollback() #
        return jsonify({"mensaje": f"Error de base de datos al restaurar la canción: {str(e)}"}), 500 #
    except Exception as e:
        db.session.rollback() #
        return jsonify({"mensaje": f"Error interno del servidor: {str(e)}"}), 500 #

# La ruta '/api' está comentada y no es necesaria si '/' ya devuelve JSON.
# Puedes eliminarla si no tiene un propósito distinto.