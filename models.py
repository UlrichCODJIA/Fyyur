#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import datetime
from email.policy import default
from sqlalchemy.dialects import postgresql
from app import db


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    genres = db.Column(postgresql.ARRAY(db.Text))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.Text)
    shows = db.relationship('Show', backref='venue', cascade="all, delete", passive_deletes=True, lazy=True)

    def __repr__(self) -> str:
       return f'{self.name}'

    # TODO: implement any missing fields, as a database migration using Flask-Migrate OK--#

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(postgresql.ARRAY(db.Text))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.Text)
    shows = db.relationship('Show', backref='artist', cascade="all, delete", passive_deletes=True, lazy=True)
    albums = db.relationship('Album', backref='artist', cascade="all, delete", passive_deletes=True, lazy=True)
    website = db.Column(db.String(120))
    available_from = db.Column(db.Time(), default=datetime.time(0, 0 ,0))
    available_to = db.Column(db.Time(), default=datetime.time(23, 59, 59))

    def __repr__(self) -> str:
       return f'{self.name}'

    # TODO: implement any missing fields, as a database migration using Flask-Migrate OK--#

# TODO: Implement Show and Artist models, and complete all model relationships and properties, as a database migration OK--#
class Show(db.Model):
    __tablename__= 'Show'
    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id', ondelete="CASCADE"), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id', ondelete="CASCADE"), nullable=False)
    start_time = db.Column(db.DateTime)

    def __repr__(self) -> str:
       return f"{self.artist_id}'s show"

class Album(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    year = db.Column(db.Integer)
    genres = db.Column(postgresql.ARRAY(db.Text))
    image_link = db.Column(db.String(500))
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id', ondelete="CASCADE"), nullable=False)

    def __repr__(self) -> str:
       return f"{self.artist_id}'s album"    