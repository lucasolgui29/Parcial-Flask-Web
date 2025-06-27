import os
from flask import Blueprint, flash, redirect, render_template, request, url_for
from werkzeug.utils import secure_filename
from db import db

from flask import Blueprint, request, jsonify
from db import db
from models.song import Song
from sqlalchemy.exc import IntegrityError # Para manejar errores de unicidad, etc.

song_bp = Blueprint('song_bp', __name__, url_prefix='/api/v1/songs')
def get_duration_category(duration_ms):
    if duration_ms < 120000: # Menos de 2 minutos
        return 'short'
    elif 120000 <= duration_ms < 300000: # Entre 2 y 5 minutos
        return 'medium'
    else: # Más de 5 minutos
        return 'long'

@song_bp.route('/', methods=['GET'])
def get_songs():
    # Obtener query parameters para filtrado
    duration_filter = request.args.get('duration', '').lower() # 'short', 'medium', 'long'
    
    query = Song.query.filter_by(is_active=True)

    if duration_filter:
        if duration_filter == 'short':
            query = query.filter(Song.duration_ms < 120000)
        elif duration_filter == 'medium':
            query = query.filter(Song.duration_ms >= 120000, Song.duration_ms < 300000)
        elif duration_filter == 'long':
            query = query.filter(Song.duration_ms >= 300000)
        else:
            return jsonify({"message": "Filtro de duración no válido. Use 'short', 'medium' o 'long'."}), 400

    songs = query.all()
    return jsonify([song.to_dict() for song in songs]), 200

@song_bp.route('/<int:song_id>', methods=['GET'])
def get_song(song_id):
    song = Song.query.get(song_id)
    if song:
        return jsonify(song.to_dict()), 200
    return jsonify({"message": "Canción no encontrada."}), 404

@song_bp.route('/', methods=['POST'])
def create_song():
    data = request.get_json()
    if not data:
        return jsonify({"message": "Datos JSON inválidos."}), 400

    title = data.get('title')
    artist = data.get('artist')
    duration_ms = data.get('duration_ms') # Debe ser un entero en milisegundos

    # Validaciones básicas
    if not title or not artist or not isinstance(duration_ms, int) or duration_ms <= 0:
        return jsonify({"message": "Faltan campos obligatorios (title, artist, duration_ms válido)."}), 400

    try:
        new_song = Song(
            title=title,
            artist=artist,
            duration_ms=duration_ms,
            album=data.get('album'),
            genre=data.get('genre'),
            release_year=data.get('release_year')
        )
        db.session.add(new_song)
        db.session.commit()
        return jsonify(new_song.to_dict()), 201 # 201 Created
    except IntegrityError:
        db.session.rollback()
        return jsonify({"message": "Error de integridad de datos. Posiblemente un campo UNIQUE duplicado."}), 409 # Conflict
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error interno del servidor: {e}"}), 500

@song_bp.route('/<int:song_id>', methods=['PUT'])
def update_song(song_id):
    song = Song.query.get(song_id)
    if not song:
        return jsonify({"message": "Canción no encontrada."}), 404

    data = request.get_json()
    if not data:
        return jsonify({"message": "Datos JSON inválidos."}), 400

    # Actualizar campos si están presentes en la solicitud
    song.title = data.get('title', song.title)
    song.artist = data.get('artist', song.artist)
    song.duration_ms = data.get('duration_ms', song.duration_ms)
    song.album = data.get('album', song.album)
    song.genre = data.get('genre', song.genre)
    song.release_year = data.get('release_year', song.release_year)

    # Opcional: permitir cambiar is_active con PUT
    if 'is_active' in data:
        song.is_active = bool(data['is_active'])

    try:
        db.session.commit()
        return jsonify(song.to_dict()), 200 # OK
    except IntegrityError:
        db.session.rollback()
        return jsonify({"message": "Error de integridad de datos al actualizar."}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error interno del servidor: {e}"}), 500

@song_bp.route('/<int:song_id>', methods=['DELETE'])
def soft_delete_song(song_id):
    song = Song.query.get(song_id)
    if not song:
        return jsonify({"message": "Canción no encontrada."}), 404
    
    if not song.is_active:
        return jsonify({"message": "La canción ya está dada de baja."}), 400

    song.is_active = False # Marca como inactiva
    try:
        db.session.commit()
        return jsonify({"message": f"Canción '{song.title}' dada de baja exitosamente."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error al dar de baja la canción: {e}"}), 500

@song_bp.route('/<int:song_id>/restore', methods=['PATCH'])
def restore_song(song_id):
    song = Song.query.get(song_id)
    if not song:
        return jsonify({"message": "Canción no encontrada."}), 404
    
    if song.is_active:
        return jsonify({"message": "La canción ya está activa."}), 400

    song.is_active = True 
    try:
        db.session.commit()
        return jsonify({"message": f"Canción '{song.title}' restaurada exitosamente."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error al restaurar la canción: {e}"}), 500
