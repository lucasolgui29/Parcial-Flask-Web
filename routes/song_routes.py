import os
from flask import Blueprint, request, jsonify
from db import db
from models.song import Song 
from sqlalchemy.exc import IntegrityError, SQLAlchemyError 

canciones_bp = Blueprint('canciones_bp', __name__, url_prefix='/canciones') 

@canciones_bp.route('/', methods=['GET'])
def obtener_canciones(): 
    
    try:
        # Inicia la consulta filtrando solo las canciones activas por defecto
        consulta = Song.query.filter_by(activo=True) 
        canciones = consulta.all() 
        return jsonify([cancion.a_diccionario() for cancion in canciones]), 200 
    except SQLAlchemyError as e:
        return jsonify({"mensaje": f"Error de base de datos al obtener canciones: {str(e)}"}), 500 
    except Exception as e:
        return jsonify({"mensaje": f"Error interno del servidor: {str(e)}"}), 500 


@canciones_bp.route('/<int:id_cancion>', methods=['GET'])
def obtener_cancion(id_cancion): 
    cancion = Song.query.filter_by(id=id_cancion, activo=True).first() 
    if cancion: 
        return jsonify(cancion.a_diccionario()), 200 
    return jsonify({"mensaje": "Canción no encontrada o no activa."}), 404 

@canciones_bp.route('/', methods=['POST'])
def crear_cancion(): 
    datos = request.get_json() 
    if not datos: 
        return jsonify({"mensaje": "Datos JSON inválidos o ausentes."}), 400 

    titulo_req = datos.get('titulo') 
    artista_req = datos.get('artista') 
    duracion_req = datos.get('duracion') # Duración en segundos, tal como en la DB

    if not titulo_req or not artista_req or not isinstance(duracion_req, (int, float)) or duracion_req <= 0: 
        return jsonify({"mensaje": "Faltan campos obligatorios (titulo, artista, duracion válido)."}), 400 

    try:
        nueva_cancion = Song( 
            titulo=titulo_req, 
            artista=artista_req, 
            duracion=int(duracion_req), # Directamente en segundos
            album=datos.get('album'), 
            # genero ya no se recibe ni se asigna
            anio=datos.get('anio'), 
            fecha_lanzamiento=datos.get('fecha_lanzamiento'), 
            hora_estreno=datos.get('hora_estreno'),         
            descripcion=datos.get('descripcion'), 
            email_contacto=datos.get('email_contacto') 
        )
        db.session.add(nueva_cancion) 
        db.session.commit() 
        return jsonify(nueva_cancion.a_diccionario()), 201 
    except IntegrityError:
        db.session.rollback() 
        return jsonify({"mensaje": "Error de integridad de datos. Posiblemente un campo UNIQUE duplicado o dato inválido."}), 409 
    except SQLAlchemyError as e:
        db.session.rollback() 
        return jsonify({"mensaje": f"Error de base de datos al crear canción: {str(e)}"}), 500 
    except Exception as e:
        db.session.rollback() 
        return jsonify({"mensaje": f"Error interno del servidor: {str(e)}"}), 500 

@canciones_bp.route('/<int:id_cancion>', methods=['PUT'])
def actualizar_cancion(id_cancion):
    cancion = Song.query.filter_by(id=id_cancion, activo=True).first() 
    if not cancion: 
        return jsonify({"mensaje": "Canción no encontrada o no activa para actualizar."}), 404 

    datos = request.get_json() 
    if not datos: 
        return jsonify({"mensaje": "Datos JSON inválidos o ausentes."}), 400 

    if 'titulo' in datos: 
        cancion.titulo = datos['titulo'] 
    if 'artista' in datos: 
        cancion.artista = datos['artista'] 
    if 'duracion' in datos: 
        if isinstance(datos['duracion'], (int, float)) and datos['duracion'] > 0: 
            cancion.duracion = int(datos['duracion']) # Directamente en segundos
        else:
            return jsonify({"mensaje": "duracion debe ser un número entero positivo."}), 400 
    if 'album' in datos: 
        cancion.album = datos['album'] 
    # genero ya no se espera para actualizar
    if 'anio' in datos: 
        cancion.anio = datos['anio'] 

    if 'activo' in datos: 
        if isinstance(datos['activo'], bool): 
            cancion.activo = datos['activo'] 
        else:
            return jsonify({"mensaje": "activo debe ser un valor booleano (true/false)."}), 400 
    
    if 'fecha_lanzamiento' in datos: 
        cancion.fecha_lanzamiento = datos['fecha_lanzamiento'] 
    if 'hora_estreno' in datos: 
        cancion.hora_estreno = datos['hora_estreno'] 
    if 'descripcion' in datos: 
        cancion.descripcion = datos['descripcion'] 
    if 'email_contacto' in datos: 
        cancion.email_contacto = datos['email_contacto'] 

    try:
        db.session.commit() 
        return jsonify(cancion.a_diccionario()), 200 
    except IntegrityError:
        db.session.rollback() 
        return jsonify({"mensaje": "Error de integridad de datos al actualizar. Posiblemente un campo UNIQUE duplicado o dato inválido."}), 409 
    except SQLAlchemyError as e:
        db.session.rollback() 
        return jsonify({"mensaje": f"Error de base de datos al actualizar canción: {str(e)}"}), 500 
    except Exception as e:
        db.session.rollback() 
        return jsonify({"mensaje": f"Error interno del servidor: {str(e)}"}), 500 

@canciones_bp.route('/<int:id_cancion>', methods=['DELETE'])
def baja_logica_cancion(id_cancion):
    cancion = Song.query.filter_by(id=id_cancion, activo=True).first() 
    if not cancion: 
        return jsonify({"mensaje": "Canción no encontrada o ya dada de baja."}), 404 
    
    cancion.activo = False 
    try:
        db.session.commit() 
        return jsonify({"mensaje": f"Canción '{cancion.titulo}' (ID: {cancion.id}) dada de baja exitosamente."}), 200 
    except SQLAlchemyError as e:
        db.session.rollback() 
        return jsonify({"mensaje": f"Error de base de datos al dar de baja la canción: {str(e)}"}), 500 
    except Exception as e:
        db.session.rollback() 
        return jsonify({"mensaje": f"Error interno del servidor: {str(e)}"}), 500 

@canciones_bp.route('/<int:id_cancion>/restaurar', methods=['PATCH'])
def restaurar_cancion(id_cancion):
    cancion = Song.query.filter_by(id=id_cancion, activo=False).first() 
    if not cancion: 
        return jsonify({"mensaje": "Canción no encontrada o ya está activa."}), 404 
    
    cancion.activo = True 
    try:
        db.session.commit() 
        return jsonify({"mensaje": f"Canción '{cancion.titulo}' (ID: {cancion.id}) restaurada exitosamente."}), 200 
    except SQLAlchemyError as e:
        db.session.rollback() 
        return jsonify({"mensaje": f"Error de base de datos al restaurar la canción: {str(e)}"}), 500 
    except Exception as e:
        db.session.rollback() 
        return jsonify({"mensaje": f"Error interno del servidor: {str(e)}"}), 500