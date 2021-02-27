#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from enum import unique
import json
from operator import contains
import dateutil.parser
import babel
import sys

from sqlalchemy.sql.elements import collate
import phonenumbers
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort,jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from sqlalchemy.orm import backref, query
from wtforms import ValidationError
from flask_wtf import FlaskForm
from forms import *
from Models import *
from flask_migrate import Migrate
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

def name_validator_unique(model_name,field_value):
  valueOfField=field_value.lower()
  print(valueOfField)
  all_rows=model_name.query.all()
  for row in all_rows:
    name_value=row.name.lower()
    if(name_value==valueOfField):
      raise ValidationError('This name already exists')

def phone_validator(num):
  phone= phonenumbers.parse(num, "US")
  if not phonenumbers.is_valid_number(phone):
    raise ValidationError('Must be a valid US phone number.')

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data = []
  
  # get all the venues and create a set from the cities
  venues = Venue.query.all()
  venue_cities = set()
  for venue in venues:
    # add city/state tuples
    venue_cities.add((venue.city, venue.state))

  # for each unique city/state, add venues
  for city in venue_cities:
    data.append({
      "city": city[0],
      "state": city[1],
      "venues": []
    })

  # get number of upcoming shows for each venue
  for venue in venues:
    no_upcoming_shows = 0

    shows = Show.query.filter_by(Venue_id=venue.id).all()

    # if the show start time is after now, add to upcoming
    for show in shows:
      if show.start_time > datetime.now():
        no_upcoming_shows += 1

    # for each entry, add venues to matching city/state
    for d in data:
      if venue.city == d['city'] and venue.state == d['state']:
        d['venues'].append({
          "id": venue.id,
          "name": venue.name,
          "no_upcoming_shows": no_upcoming_shows
        })

    # return venues page with data
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  # get the user search term
  search_term = request.form.get('search_term', '')
  venues = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()

  response = {
    "count": len(venues),
    "data": []
  }

  for venue in venues:
    num_upcoming_shows = 0

    shows = Show.query.filter_by(Venue_id=venue.id).all()

    # calculuate num of upcoming shows for each venue
    for show in shows:
      if show.start_time > datetime.now():
        num_upcoming_shows += 1

    # add venue data to response
    response['data'].append({
    "id": venue.id,
    "name": venue.name,
    "num_upcoming_shows": num_upcoming_shows,
    })

    # return response with search results
  return render_template('pages/search_venues.html', results=response, search_term= request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  # get all venues
  venue = Venue.query.filter_by(id=venue_id).first()

  # get all shows for given venue
  shows = Show.query.filter_by(Venue_id=venue_id).all()

  # returns upcoming shows
  def upcoming_shows():
    upcoming_shows = []
    upcoming_shows_query = db.session.query(Show,Artist).join(Artist).filter(Show.Venue_id==venue_id).filter(Show. start_time>datetime.now()).all()  
    
    # if show is in future, add show details to upcoming
    for show,artist in upcoming_shows_query:
      upcoming_shows.append({
        "venue_id":show.Venue_id,
        "venue_name":artist.name,
        "venue_image_link":artist.image_link,
        "start_time":format_datetime(str(show.start_time))

      })
    return upcoming_shows
  
  # returns past shows
  def past_shows():
    past_shows = []
    past_shows_query = db.session.query(Show,Artist).join(Artist).filter(Show.Venue_id==venue_id).filter(Show. start_time<datetime.now()).all()  
    
    # if show is in future, add show details to upcoming
    for show,artist in past_shows_query:
      past_shows.append({
        "venue_id":show.Venue_id,
        "venue_name":artist.name,
        "venue_image_link":artist.image_link,
        "start_time":format_datetime(str(show.start_time))

      })
    return past_shows
  
  data = {
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": past_shows(),
    "upcoming_shows": upcoming_shows(),
    "past_shows_count": len(past_shows()),
    "upcoming_shows_count": len(upcoming_shows())
  }

  # return template with venue data
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
    error= False
  #create_venue_form=VenueForm()
  #if create_venue_form.validate_on_submit():
    try:
      name= request.form.get('name')
      name_validator_unique(Venue,name)
      city= request.form.get('city')
      state= request.form.get('state')
      address= request.form.get('address')
      phone= request.form.get('phone')
      phone_validator(phone)
      genres= request.form.get('genres')
      facebook_link= request.form.get('facebook_link')
      website= request.form.get('website')
      image= request.form.get('image_link')
      seeking= request.form.get('seeking_talent')
      seekingDescription= request.form.get('seeking_description')
      venue = Venue(name=name,city=city,state=state,address=address,phone=phone,facebook_link=facebook_link,genres=genres, image_link=image, seeking_talent= bool(int(seeking)), seeking_description= seekingDescription, website= website)
      db.session.add(venue)
      db.session.commit()
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
    
    except ValidationError as e:
      db.session.rollback()
      flash('There is an error occurred in the name field ' +
      request.form.get('name') + ' could not be listed. ' + str(e))
    
    except ValidationError as e:
      db.session.rollback()
      flash('error. Venue ' +
      request.form.get('name') + ' could not be added, ' + str(e))

    except:
      db.session.rollback()
      error=True
      print(sys.exc_info())
    
    finally:
      db.session.close()
      
    # TODO: modify data to be the data object returned from db insertion
    # on successful db insert, flash success
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')

  #else:
    flash('Venue ' + request.form['name'] + "wasn't successfully listed!")
    return render_template('forms/new_venue.html')
@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data=[]
  all_artists= Artist.query.all()
  for artist in all_artists:
    data.append({
      "id": artist.id,
      "name": artist.name
    })
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term', '')
  artists = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()

  response = {
    "count": len(artists),
    "data": []
  }

  for artist in artists:
    num_upcoming_shows = 0

    shows = Show.query.filter_by(Artist_id=artist.id).all()

    # calculuate num of upcoming shows for each venue
    for show in shows:
      if show.start_time > datetime.now():
        num_upcoming_shows += 1

    # add venue data to response
    response['data'].append({
    "id": artist.id,
    "name": artist.name,
    "num_upcoming_shows": num_upcoming_shows,
    })

    # return response with search results
  return render_template('pages/search_venues.html', results=response, search_term= request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  # get all artists
  artist = Artist.query.filter_by(id=artist_id).first()

  # get all shows for given venue
  shows = Show.query.filter_by(Artist_id=artist_id).all()

  # returns upcoming shows
  def upcoming_shows():
    upcoming_shows = []
    upcoming_shows_query = db.session.query(Show,Venue).join(Venue).filter(Show.Artist_id==artist_id).filter(Show. start_time>datetime.now()).all()  
    
    # if show is in future, add show details to upcoming
    for show,venue in upcoming_shows_query:
      upcoming_shows.append({
        "venue_id":show.Venue_id,
        "venue_name":venue.name,
        "venue_image_link": venue.image_link,
        "start_time":format_datetime(str(show.start_time))

      })
    return upcoming_shows

  # returns past shows
  def past_shows():
    past_shows = []
    past_shows_query = db.session.query(Show,Venue).join(Venue).filter(Show.Artist_id==artist_id).filter(Show. start_time<datetime.now()).all()  
    
    # if show is in future, add show details to upcoming
    for show,venue in past_shows_query:
      past_shows.append({
        "venue_id":show.Venue_id,
        "venue_name":venue.name,
        "venue_image_link": venue.image_link,
        "start_time":format_datetime(str(show.start_time))

      })
    return past_shows
    # if show is in past, add show details to past
    for show in shows:
      if show.start_time < datetime.now():
        past.append({
          "venue_id": show.Venue_id,
          "venue_name": Venue.query.filter_by(id=show.Venue_id).first().name,
          "venue_image_link": Venue.query.filter_by(id=show.Venue_id).first().image_link,
          "start_time": format_datetime(str(show.start_time))
        })
    return past

  # data for given venue
  data = {
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "address": artist.address,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": past_shows(),
    "upcoming_shows": upcoming_shows(),
    "past_shows_count": len(past_shows()),
    "upcoming_shows_count": len(upcoming_shows())
  }

  # return template with venue data
  return render_template('pages/show_artist.html', artist=data)
  
#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
    error=False
  #create_artist_form=ArtistForm()
  #if create_artist_form.validate_on_submit():
    try:
      name = request.form.get('name')
      name_validator_unique(Artist,name)
      city = request.form.get('city')
      state = request.form.get('state')
      address = request.form.get('address')
      phone = request.form.get('phone')
      phone_validator(phone)
      genres = request.form.get('genres')
      image = request.form.get('image_link')
      facebook_link = request.form.get('facebook_link')
      website= request.form.get('website')
      seeking = request.form.get('seeking_venue')
      seekingDescription = request.form.get('seeking_description')
      artist=Artist(name=name,city=city,state=state,address=address,phone=phone,facebook_link=facebook_link,genres=genres,image_link=image,seeking_venue=bool(int(seeking)),seeking_description=seekingDescription, website= website)
      db.session.add(artist)
      db.session.commit()
      flash('Artist ' + request.form['name'] + ' was successfully listed!')

    except ValidationError as e:
      db.session.rollback()
      flash('There is an error occurred in the name field ' +
      request.form.get('name') + ' could not be listed. ' + str(e))

    except ValidationError as e:
      db.session.rollback()
      flash('error. Venue ' +
      request.form.get('name') + ' could not be added, ' + str(e))
    
    except:
      db.session.rollback()
      error=True
      print(sys.exc_info())
    finally:
      db.session.close()
  
    # TODO: modify data to be the data object returned from db insertion

    # on successful db insert, flash success
    return render_template('pages/home.html')

  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  #else:
    flash('Artist ' + request.form['name'] + ' does not successfully listed!')
    return render_template('forms/new_artist.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data=[]
  shows= Show.query.all()
  for show in shows:
    data.append({
      'venue_id': show.Venue_id,
      'venue_name': Venue.query.filter_by(id= show.Venue_id).first().name,
      'artist_id': show.Artist_id,
      'artist_name': Artist.query.filter_by(id= show.Artist_id).first().name,
      'artist_image_link': Artist.query.filter_by(id= show.Artist_id).first().image_link,
      'start_time': format_datetime(str(show.start_time))
    })
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  error= False
  #create_artist_form=ArtistForm()
  #if create_artist_form.validate_on_submit():
  artist_id = request.form.get('artist_id')
  venue_id = request.form.get('venue_id')
  start_time = request.form.get('start_time')

  try:
    show=Show(Artist_id=artist_id, Venue_id=venue_id,start_time=start_time)
    db.session.add(show)
    db.session.commit()
  except:
    db.session.rollback()
    error=True
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    print("Errooooooooooooooooooooor")
    abort (400)
  else:
    print("WOOOHOOO artist successfully added")
  
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  flash('show was successfully listed!')
  return render_template('pages/home.html')  
  # on successful db insert, flash success
  flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
