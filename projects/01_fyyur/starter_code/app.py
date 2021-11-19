#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from flask_migrate import Migrate
from flask_wtf import Form, CSRFProtect
from forms import *
from model import db, Artist, Venue, Show

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
# db = SQLAlchemy(app)
db.init_app(app)
migrate = Migrate(app, db)
csrf = CSRFProtect(app)

# TODO: connect to a local postgresql database

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
  venues = Venue.query.order_by(Venue.id.desc()).limit(10).all()
  artists = Artist.query.order_by(Artist.id.desc()).limit(10).all()
  return render_template('pages/home.html', venues=venues, artists=artists)


#  Venues
#  ----------------------------------------------------------------

# 1)
@app.route('/venues')
#got this from https://knowledge.udacity.com/questions/501471
def venues():
  areas = []
  venues = Venue.query.all()
  places = Venue.query.distinct(Venue.city, Venue.state).all()
	
  for place in places:
    areas.append({
        'city': place.city,
        'state': place.state,
        'venues': [{
            'id': venue.id,
            'name': venue.name
        } for venue in venues if
            venue.city == place.city and venue.state == place.state]
    })
  return render_template('pages/venues.html', areas=areas)

# 2)
@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term = request.form.get('search_term', '')
  results = db.session.query(Venue).filter(Venue.name.ilike('%' + search_term + '%')).all()
  response = {
      'count': len(results),
      'data': results
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

# got the idea from https://knowledge.udacity.com/questions/737881
@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue = Venue.query.get_or_404(venue_id)
  past_shows = []
  upcoming_shows = []
  for show in venue.shows:
    if show.start_time <= datetime.now():
        past_shows.append({
          'artist_id': show.artist_id,
        'artist_name': show.artist.name,
        'artist_image_link': show.artist.image_link,
        'start_time': show.start_time.strftime("%m/%d/%Y, %H:%M")
        })
    else:
        upcoming_shows.append({
          'artist_id': show.artist_id,
        'artist_name': show.artist.name,
        'artist_image_link': show.artist.image_link,
        'start_time': show.start_time.strftime("%m/%d/%Y, %H:%M")
        })
  return render_template('pages/show_venue.html', venue=venue)

#  Create Venue
#  ----------------------------------------------------------------

# 4)
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
                seeking_talent = True if request.form.get('seeking_talent') == 'true' else False,
                website_link  = request.form['website_link'],
                seeking_description = request.form['seeking_description'])
            db.session.add(venue)
            db.session.commit()
            flash('The ' + request.form['name'] + ' Venue was successfully listed!')
            return render_template('pages/venues.html')
    except:
            db.session.rollback()
            flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
       
    finally:
      db.session.close()
  else:
        for error in form.errors:
            flash(form.errors[error][0])

        return render_template('forms/new_venue.html', form=form)
  return render_template('pages/venues.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # delete = 
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    artists = Artist.query.order_by(Artist.id.asc()).all()
    return render_template('pages/artists.html', artists=artists)
  

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term = request.form.get('search_term', '')
  results = db.session.query(Artist).filter(Artist.name.ilike('%' + search_term + '%')).all()
  response = {
      'count': len(results),
      'data': results
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

# got the idea from https://knowledge.udacity.com/questions/737881
@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):

  artist = Artist.query.get_or_404(artist_id)
  past_shows = []
  upcoming_shows = []
  for show in artist.shows:
    temp_show = {
        'venue_id': show.venue_id,
        'venue_name': show.venue.name,
        'venue_image_link': show.venue.image_link,
        'start_time': show.start_time
    }
    if show.start_time <= datetime.now():
        past_shows.append(temp_show)
    else:
        upcoming_shows.append(temp_show)
  return render_template('pages/show_artist.html', artist=artist)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.filter(Artist.id==artist_id).first()
  form = ArtistForm(obj=artist)
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
        "seeking_venue": True if request.form.get('seeking_venue') == 'true' else False,
        "website_link": request.form['website_link'],
        "seeking_description": request.form['seeking_description'],
      }
      Artist.query.filter_by(id=artist_id).update(artist)
      db.session.commit()
      flash('Artist: ' + request.form['name'] + ' was successfully updated!')
    except:
      db.session.rollback()
      flash('Artist: ' + request.form['name'] + ' was not successfully updated!')
    finally:
        db.session.close()
  else:
        for error in form.errors:
            flash(form.errors[error][0])
        return redirect(url_for('edit_artist', artist_id=artist_id))
        
  return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.filter(Venue.id==venue_id).first()
  form = VenueForm(obj=venue)
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
  return render_template('pages/artists.html')
  
# 6)
@app.route('/shows')
def shows():
  data = []
  shows = Show.query.order_by(Show.start_time.desc()).all()
  for show in shows:
    venue = Venue.query.filter_by(id=show.venue_id).first()
    artist = Artist.query.filter_by(id=show.artist_id).first()
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

# 7)
@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  form =ShowForm(request.form)
  error = False
  if form.validate():
        try:
            show = Show(
            venue_id = request.form['venue_id'],
            artist_id = request.form['artist_id'],
            start_time = request.form['start_time'])
            db.session.add(show)
            db.session.commit()
            flash('Show was successfully listed!')
        except Exception as e:
            db.session.rollback()
            error = True
            flash('An error occurred. Show could not be listed.')
        finally:
          db.session.close()
  else:
    # print(sys.exc_info())
    for error in form.errors:
      flash(form.errors[error][0])
    return render_template('forms/new_show.html', form=form)
    
  return render_template('pages/shows.html')

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
