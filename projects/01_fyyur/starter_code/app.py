#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import os
import sys
import dateutil.parser
import datetime
import logging
from logging import Formatter, FileHandler, error

from sqlalchemy.sql.schema import MetaData
logging.basicConfig(level=logging.DEBUG)
import babel

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_migrate import Migrate
from flask_wtf import Form, CSRFProtect
from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)
csrf = CSRFProtect(app)

# TODO: connect to a local postgresql database

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
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean())
    seeking_description = db.Column(db.String(500))
    venue_show = db.relationship('Shows', backref='venue', lazy=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean())
    seeking_description = db.Column(db.String(500))
    venue_show = db.relationship('Shows', backref='artist', lazy=True)

class Shows(db.Model):
    __tablename__ ='Shows'

    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id', ondelete='CASCADE'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id', ondelete='CASCADE'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

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
    venues = Venue.query.order_by(Venue.id.desc()).all()
    units = set()

    for venue in venues:
        units.add((venue.city, venue.state));

    areas = []
    for unit in units:
        areas.append({
            "city": unit[0],
            "state": unit[1],
            "venues": []
        })

    num_shows = 0

    for venue in venues:
        for area in areas:
            if area['city'] == venue.city and area['state'] == venue.state:
                area['venues'].append({
                    'id': venue.id,
                    'name': venue.name,
                    'num_upcoming_shows': num_shows
                })

    return  render_template('pages/venues.html', areas=areas);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term = request.form.get('search_term', '')
  results = db.session.query(Venue).filter(Venue.name.ilike('%' + search_term + '%')).all()
  response = {
      'count': len(results),
      'data': results
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue = Venue.query.filter(Venue.id==venue_id).first()
  venue.genres = venue.genres.replace('{', '')
  venue.genres = venue.genres.replace('}', '')
  return render_template('pages/show_venue.html', venue=venue)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm(request.form)

  if form.validate():
    try:
            venue = Venue(
                name  = request.form['name'],
                city  = request.form['city'],
                state = request.form['state'],
                phone = request.form['phone'],
                address = request.form['address'],
                genres= request.form.getlist('genres'),
                image_link    = request.form['image_link'],
                facebook_link = request.form['facebook_link'],
                seeking_talent = True if request.form.get('seeking_talent') == 'y' else False,
                website_link  = request.form['website_link'],
                seeking_description = request.form['seeking_description'])
            db.session.add(venue)
            db.session.commit()
            flash('Artist ' + request.form['name'] + ' was successfully listed!')
            return render_template('pages/home.html')
    except:
            db.session.rollback()
            flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
       
    finally:
      db.session.close()
  else:
        for error in form.errors:
            flash(form.errors[error][0])

        return render_template('forms/new_venue.html', form=form)
  return render_template('pages/home.html')

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
    artists = Artist.query.order_by(Artist.id.desc()).all()
    return render_template('pages/artists.html', artists=artists)
  # TODO: replace with real data returned from querying the database
  

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term = request.form.get('search_term', '')
  results = db.session.query(Artist).filter(Artist.name.ilike('%' + search_term + '%')).all()
  response = {
      'count': len(results),
      'data': results
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):

  artist = Artist.query.filter(Artist.id==artist_id).first()
  artist.genres = artist.genres.replace('{', '')
  artist.genres = artist.genres.replace('}', '')
  return render_template('pages/show_artist.html', artist=artist)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.filter(Artist.id==artist_id).first()
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  form = ArtistForm(request.form)

  if form.validate():
    try:
      artist = {
        "name": request.form['name'],
        "city": request.form['city'],
        "state": request.form['state'],
        "phone": request.form['phone'],
        "genres": request.form['genres'],
        "image_link": request.form['image_link'],
        "facebook_link": request.form['facebook_link'],
        "seeking_venue": True if request.form.get('seeking_venue') == 'y' else False,
        "website_link": request.form['website_link'],
        "seeking_description": request.form['seeking_description'],
      }
      Artist.query.filter_by(id=artist_id).update(artist)
      db.session.commit()
      flash('Artist ' + request.form['name'] + ' was successfully updated!')
    except:
      db.session.rollback()
      flash('Artist ' + request.form['name'] + ' was not successfully updated!')
    finally:
        db.session.close()
  else:
        for error in form.errors:
            flash(form.errors[error][0])
        return redirect(url_for('edit_artist', artist_id=artist_id))
        
  return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()

  venue = Venue.query.filter(Venue.id==venue_id).first()
  return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    error = False
    form = VenueForm(request.form)

    if form.validate():
      try:
        venue = {
        "name": request.form['name'],
        "city": request.form['city'],
        "state": request.form['state'],
        "phone": request.form['phone'],
        "address": request.form['address'],
        "genres": request.form['genres'],
        "image_link": request.form['image_link'],
        "facebook_link": request.form['facebook_link'],
        "seeking_talent": True if request.form.get('seeking_talent') == 'y' else False,
        "website_link": request.form['website_link'],
        "seeking_description": request.form['seeking_description'],
      }
        Venue.query.filter_by(id=venue_id).update(venue)
        db.session.commit()
        flash('Venue: ' + request.form['name'] + ' was successfully updated')
      except Exception as e:
        db.session.rollback()
        error = True
        print(f'Error ==> {e}')
        flash('Venue: ' + request.form['name'] + ' was not successfully updated')
      finally:
        db.session.close()
    else: 
      for error in form.errors:
        flash(form.errors[error][0])
      return redirect(url_for('edit_venue', venue_id=venue_id))
        
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  form = ArtistForm(request.form)

  if form.validate():
        try:
            artist = Artist(
                name  = request.form['name'],
                city  = request.form['city'],
                state = request.form['state'],
                phone = request.form['phone'],
                genres= request.form.getlist('genres'),
                image_link    = request.form['image_link'],
                facebook_link = request.form['facebook_link'],
                seeking_venue = True if request.form.get('seeking_venue') == 'y' else False,
                website_link  = request.form['website_link'],
                seeking_description = request.form['seeking_description'])
            db.session.add(artist)
            db.session.commit()
            flash('Artist ' + request.form['name'] + ' was successfully listed!')

            return render_template('pages/home.html')
        except Exception as e:
            db.session.rollback()
            flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
        finally:
            db.session.close()
  else:
        for error in form.errors:
            flash(form.errors[error][0])

        return render_template('forms/new_artist.html', form=form)
  return render_template('pages/home.html')
  


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  data = []
  shows = Shows.query.order_by(Shows.start_time.desc()).all()
  for show in shows:
    venue = Venue.query.filter_by(id=show.venue_id).first_or_404()
    artist = Artist.query.filter_by(id=show.artist_id).first_or_404()
    data.extend([{
      "venue_id": venue.id,
      "venue_name": venue.name,
      "artist_id": artist.id,
      "artist_name": artist.name,
      "artist_image_link": artist.image_link,
      "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
    }])
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  form =ShowForm(request.form)
  date_format = '%Y-%m-%d %H:%M:%S'
  error = False

  if form.validate():
        try:
            show = Shows(
            venue_id = request.form['venue_id'],
            artist_id = request.form['artist_id'],
            start_time = request.form['start_time'])
            db.session.add(show)
            db.session.commit()
            flash('Show was successfully listed!')
        except Exception as e:
            db.session.rollback()
            error = True
            print(f'Error ==> {e}')
            flash('An error occurred. Show could not be listed.')
        finally:
          db.session.close()
  else:
    print(sys.exc_info())
    for error in form.errors:
      flash(form.errors[error][0])
    return render_template('forms/new_show.html', form=form)
    
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
    app.run(debug=True)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
