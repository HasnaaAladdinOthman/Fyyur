from flask import Flask
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_migrate import Migrate
from sqlalchemy.sql.elements import collate

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate= Migrate(app, db)

class Show(db.Model):
  __tablename__= 'Show'

  Artist_id= db.Column(db.Integer, db.ForeignKey('Artist.id'),primary_key= True)
  Venue_id= db.Column(db.Integer, db.ForeignKey('Venue.id'),primary_key= True)
  start_time= db.Column(db.DateTime)
  
  def __repr__(self):
    return f'<Show {self.Artist_id} {self.Venue_id} {self.start_time}>'

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable= False, unique= True)
    collate(name, 'SQL_Latin1_General_CP1_CS_AS')
    genres=db.Column(db.String, nullable= False)
    address = db.Column(db.String(120), nullable= False)
    city = db.Column(db.String(120), nullable= False)
    state = db.Column(db.String(120), nullable= False)
    phone = db.Column(db.String(120), nullable= False)
    website=db.Column(db.String)
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String)
    image_link = db.Column(db.String(500))


    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable= False, unique= True)
    collate(name, 'SQL_Latin1_General_CP1_CS_AS')
    genres=db.Column(db.String, nullable= False)
    address = db.Column(db.String(120), nullable= False)
    city = db.Column(db.String(120), nullable= False)
    state = db.Column(db.String(120),nullable= False)
    phone = db.Column(db.String(120), nullable= False)
    website=db.Column(db.String)
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String)
    image_link = db.Column(db.String(500))
    venues= db.relationship('Venue', secondary= lambda: Show.__table__, backref='Artist', lazy= True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    # TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
