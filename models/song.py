from db import db
import uuid

class Song(db.Model):
    __tablename__ = 'songs'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(100), nullable=False)
    artist = db.Column(db.String(100), nullable=False)
    album = db.Column(db.String(100), nullable=True)
    duration = db.Column(db.Integer, nullable=False)
    genre = db.Column(db.String(50), nullable=True)

    def __repr__(self):
        return f"<Song {self.title} by {self.artist}>"