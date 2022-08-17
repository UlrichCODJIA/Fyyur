#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import sys
import dateutil.parser
import babel
from flask import Flask, render_template, request, flash, redirect, url_for, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database OK----------------------------#


from models import *


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  if isinstance(value, str):
      date = dateutil.parser.parse(value)
  else:
      date = value
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

def time_in_range(start, end, current):
  return start <= current <= end

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  error = False
  try:
    latest_objects = {
      "last_venues" : Venue.query.order_by('id').all()[-10:],
      "last_venues_count": Venue.query.order_by('id').count(),
      "last_artists" : Artist.query.order_by('id').all()[-10:],
      "last_artists_count" : Artist.query.order_by('id').count(),
    }
  
  except Exception as e:
    error = True
    print(e)
  finally:
    db.session.close()    

  if not error:
    return render_template('pages/home.html', latest_objects=latest_objects)
  
  else:
    abort(500)


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  error = False
  Form = SearchForm()

  try:
    all_venues = Venue.query.order_by('id').all()
    city_state_list_beta = []
    for venue in all_venues:
      city_state_list_beta.append({
        "city": venue.city,
        "state": venue.state,
      })
    city_state_list = []
    for city_state in city_state_list_beta:
      if city_state not in city_state_list:
        city_state_list.append(city_state)

    data = [{
      "city": city_state["city"],
      "state": city_state["state"],
      "venues": Venue.query.filter_by(city=city_state["city"], state=city_state["state"]).order_by('id')
    } for city_state in city_state_list]

  except Exception as e:
    error = True
    print(e)
  finally:
    db.session.close()    

  if not error:
    return render_template('pages/venues.html', areas=data, form=Form)
  
  else:
    abort(500)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  error = False
  Form = SearchForm()

  try:
    venues = Venue.query.filter(
      Venue.name.like('%' + Form.search_term.data + '%')
    ).order_by(Venue.id)

    response = {
      "count": venues.count(),
      "data": [{
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows": Show.query.filter(
          db.and_(Show.start_time > datetime.datetime.now(), Show.venue_id == venue.id)
        ).count()
      } for venue in venues] 
    }

  except Exception as e:
    error = True
    print(e)
  finally:
    db.session.close()     

  if not error:
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''), form=Form)
  
  else:
    abort(500)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  error = False
  Form = SearchForm()

  try:
    venue=Venue.query.get(venue_id)

    venue={
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
      "past_shows": Show.query.filter(
          db.and_(Show.start_time <= datetime.datetime.now(), Show.venue_id == venue_id)), 
      "upcoming_shows": Show.query.filter(
          db.and_(Show.start_time > datetime.datetime.now(), Show.venue_id == venue_id)),
      "past_shows_count": Show.query.filter(
          db.and_(Show.start_time <= datetime.datetime.now(), Show.venue_id == venue_id)).count(),
      "upcoming_shows_count": Show.query.filter(
          db.and_(Show.start_time > datetime.datetime.now(), Show.venue_id == venue_id)).count(),
    }

  except Exception as e:
    error = True
    print(e)
  finally:
    db.session.close()     

  if not error:
    return render_template('pages/show_venue.html', venue=venue, form=Form)
  
  else:
    abort(500)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  error = False
  form = VenueForm()
  try:

    venue = Venue(
      name = form.name.data,
      city = form.city.data,
      state = form.state.data,
      address = form.address.data,
      phone = form.phone.data,
      image_link = form.image_link.data,
      genres = form.genres.data,
      facebook_link = form.facebook_link.data,
      website = form.website_link.data,
      seeking_talent = form.seeking_talent.data,
      seeking_description = form.seeking_description.data,
    )
    db.session.add(venue)
    db.session.commit()
  
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  
  finally:
    db.session.close()
  
  if not error:
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
    return redirect(url_for('venues'))
  
  else:
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    abort(500)

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage  
  error = False
  try:
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
  except Exception as e:
    error = True
    print(e)
    db.session.rollback()
  finally:
    db.session.close()
  if not error:
    flash('Venue ' + venue_id + ' was successfully deleted!')
    return redirect(url_for('index'))
  
  else:
    flash('An error occurred. Venue ' + venue_id + ' could not be deleted.')
    abort(500)

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():

  error = False
  Form = SearchForm()

  try:
    all_artists = Artist.query.order_by('id').all()
    data = [{
      "id": artist.id,
      "name": artist.name
    } for artist in all_artists]
  
  except Exception as e:
    error = True
    print(e)
  finally:
    db.session.close()     

  if not error:
    return render_template('pages/artists.html', artists=data, form=Form)
  
  else:
    abort(500)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  error = False
  Form = SearchForm()

  try:
    artists = Artist.query.filter(
      Artist.name.like('%' + Form.search_term.data + '%')
    ).order_by(Artist.id)

    response = {
      "count": artists.count(),
      "data": [{
        "id": artist.id,
        "name": artist.name,
        "num_upcoming_shows": Show.query.filter(
          db.and_(Show.start_time <= datetime.datetime.now(), Show.artist_id == artist.id)
        ).count()
      } for artist in artists] 
    }

  except Exception as e:
    error = True
    print(e)
  finally:
    db.session.close()     

  if not error:
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))
  
  else:
    abort(500)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  error = False
  Form = SearchForm()

  try:
    artist=Artist.query.get(artist_id)

    artist={
      "id": artist.id,
      "name": artist.name,
      "genres": artist.genres,
      "city": artist.city,
      "state": artist.state,
      "phone": artist.phone,
      "website": artist.website,
      "facebook_link": artist.facebook_link,
      "seeking_venue": artist.seeking_venue,
      "seeking_description": artist.seeking_description,
      "image_link": artist.image_link,
      "available_from": artist.available_from.strftime("%H:%M"),
      "available_to": artist.available_to.strftime("%H:%M"),
      "albums": Album.query.filter(Album.artist_id == artist_id).order_by(Album.id),
      "albums_count": Album.query.filter(Album.artist_id == artist_id).count(),
      "past_shows": Show.query.filter(
          db.and_(Show.start_time <= datetime.datetime.now(), Show.artist_id == artist_id)), 
      "upcoming_shows": Show.query.filter(
          db.and_(Show.start_time > datetime.datetime.now(), Show.artist_id == artist_id)),
      "past_shows_count": Show.query.filter(
          db.and_(Show.start_time <= datetime.datetime.now(), Show.artist_id == artist_id)).count(),
      "upcoming_shows_count": Show.query.filter(
          db.and_(Show.start_time > datetime.datetime.now(), Show.artist_id == artist_id)).count(),
    }

  except Exception as e:
    error = True
    print(e)
  finally:
    db.session.close()    

  if not error:
    return render_template('pages/show_artist.html', artist=artist)
  
  else:
    abort(500)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  # TODO: populate form with fields from artist with ID <artist_id>  
  error = False
  form = ArtistForm()

  try:
    artist=Artist.query.get(artist_id)

  except Exception as e:
    error = True
    print(e)
  finally:
    db.session.close()     

  if not error:
    return render_template('forms/edit_artist.html', form=form, artist=artist)
  
  else:
    abort(500)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  error = False
  form = ArtistForm()
  try:

    artist = Artist.query.get(artist_id)

    artist.name = form.name.data
    artist.city = form.city.data
    artist.state = form.state.data
    artist.phone = form.phone.data
    artist.image_link = form.image_link.data
    artist.genres = form.genres.data
    artist.facebook_link = form.facebook_link.data
    artist.website = form.website_link.data
    artist.seeking_venue = form.seeking_venue.data
    artist.seeking_description = form.seeking_description.data
    artist.available_from = form.available_from.data
    artist.available_to = form.available_to.data
    db.session.commit()

  except Exception as e:
    print(e)
    error = True
    db.session.rollback()
  finally:
    db.session.close()

  if not error:
    return redirect(url_for('show_artist', artist_id=artist_id))
  
  else:
    abort(500)

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  # TODO: populate form with values from venue with ID <venue_id>
  error = False
  form = VenueForm()
  try:
    venue = Venue.query.get(venue_id)

  except Exception as e:
    error = True
    print(e)
  finally:
    db.session.close()    

  if not error:
    return render_template('forms/edit_venue.html', form=form, venue=venue)
  
  else:
    abort(500)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  error = False 
  form = VenueForm()
  try:
    venue = Venue.query.get(venue_id)

    venue.name = form.name.data
    venue.city = form.city.data
    venue.state = form.state.data
    venue.address = form.address.data
    venue.phone = form.phone.data
    venue.image_link = form.image_link.data
    venue.genres = form.genres.data
    venue.facebook_link = form.facebook_link.data
    venue.website = form.website_link.data
    venue.seeking_talent = form.seeking_talent.data
    venue.seeking_description = form.seeking_description.data
    db.session.commit()

  except Exception as e:
    print(e)
    error = True
    db.session.rollback()
  finally:
    db.session.close()

  if not error:
    return redirect(url_for('show_venue', venue_id=venue_id))
  
  else:
    abort(500)

@app.route('/artists/<int:artist_id>/albums/<int:album_id>/edit', methods=['GET'])
def edit_album(artist_id, album_id): 
  error = False
  form = AlbumForm()

  try:
    album=Album.query.filter(Album.artist_id == artist_id).first()
    artist_id = artist_id

  except Exception as e:
    error = True
    print(e)
  finally:
    db.session.close()     

  if not error:
    return render_template('forms/edit_album.html', form=form, album=album, artist_id=artist_id)
  
  else:
    abort(500)

@app.route('/artists/<int:artist_id>/albums/<int:album_id>/edit', methods=['POST'])
def edit_album_submission(artist_id, album_id):
  error = False
  form = AlbumForm()
  try:

    album=Album.query.filter(Album.artist_id == artist_id).first()
    print(album)

    album.title = form.title.data
    album.genres = form.genres.data
    album.year = form.year.data
    album.image_link = form.image_link.data
    print(form.title.data, form.genres.data, form.year.data, form.image_link.data)
    db.session.commit()

  except Exception as e:
    print(e)
    error = True
    db.session.rollback()
  finally:
    db.session.close()

  if not error:
    return redirect(url_for('show_artist', artist_id=artist_id))
  
  else:
    abort(500)    

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
  # TODO: modify data to be the data object returned from db insertion

  error = False
  form = ArtistForm()
  try:

    artist = Artist(
      name = form.name.data,
      city = form.city.data,
      state = form.state.data,
      phone = form.phone.data,
      image_link = form.image_link.data,
      genres = form.genres.data,
      facebook_link = form.facebook_link.data,
      website = form.website_link.data,
      seeking_venue = form.seeking_venue.data,
      seeking_description = form.seeking_description.data,
      available_from = form.available_from.data,
      available_to = form.available_to.data,
    )
    db.session.add(artist)
    db.session.commit()
  
  except Exception as e:
    error = True
    db.session.rollback()
    print(e)
  
  finally:
    db.session.close()
  
  if not error:
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
    return redirect(url_for('artists'))
  
  else:
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
    abort(500)


# Albums
#  ----------------------------------------------------------------

@app.route('/artists/<int:artist_id>/albums/create', methods=['GET'])
def create_album_form(artist_id):
  form = AlbumForm()
  return render_template('forms/new_album.html', form=form)

@app.route('/artists/<int:artist_id>/albums/create', methods=['POST'])
def create_album_submission(artist_id):
  error = False
  form = AlbumForm()
  try:

    album = Album(
      title = form.title.data,
      year = form.year.data,
      genres = form.genres.data,      
      image_link = form.image_link.data,
      artist_id = artist_id,
    )
    db.session.add(album)
    db.session.commit()
  
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  
  finally:
    db.session.close()
  
  if not error:
    flash('Album ' + request.form['title'] + ' was successfully listed!')
    return redirect(url_for('show_artist', artist_id=artist_id))
  
  else:
    flash('An error occurred. Album ' + request.form['title'] + ' could not be listed.')
    abort(500)


@app.route('/artists/<int:artist_id>/albums/<int:album_id>')
def show_album(artist_id, album_id):
  error = False
  Form = SearchForm()

  try:
    album=Album.query.filter(Album.artist_id == artist_id).first()

    album={
      "id": album.id,
      "title": album.title,
      "genres": album.genres,
      "year": album.year,
      "image_link": album.image_link,
      "artist": Artist.query.get(artist_id).name,
      "artist_id": artist_id,
    }

  except Exception as e:
    error = True
    print(e)
  finally:
    db.session.close()    

  if not error:
    return render_template('pages/show_album.html', album=album)
  
  else:
    abort(500)

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  error = False

  try:
    shows = Show.query.order_by('id').all()
    data = [{
      "venue_id": show.venue.id,
      "venue_name": show.venue.name,
      "artist_id": show.artist.id,
      "artist_name": show.artist.name,
      "artist_image_link": show.venue.image_link,
      "start_time": show.start_time,   
    } for show in shows]

  except Exception as e:
    error = True
    print(e)
  finally:
    db.session.close()    

  if not error:
    return render_template('pages/shows.html', shows=data)
  
  else:
    abort(500)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead  
  error = False
  form = ShowForm()
  try:
    if time_in_range(
      start=Artist.query.get(form.artist_id.data).available_from, 
      end=Artist.query.get(form.artist_id.data).available_to, 
      current=form.start_time.data.time()):
      
      try:
        show = Show(
          artist_id = form.artist_id.data,
          venue_id = form.venue_id.data,
          start_time = form.start_time.data,
        )
        db.session.add(show)
        db.session.commit()
      
      except Exception as e:
        error = True
        db.session.rollback()
        print(e)
      
      finally:
        db.session.close()

    else:
      flash(f'Show start time outside of artist {form.artist_id.data} availability')
      abort(500)

  except Exception as e:
    error = True
    db.session.rollback()
    print(e)
  if not error:
    flash('Show was successfully listed!')
    return redirect(url_for('shows'))
  
  else:
    flash('An error occurred. Show could not be listed.')
    abort(500)  

@app.errorhandler(404)
def not_found_error(error):
    form = SearchForm()
    return render_template('errors/404.html', form=form), 404

@app.errorhandler(500)
def server_error(error):
    form = SearchForm()
    return render_template('errors/500.html', form=form), 500


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
