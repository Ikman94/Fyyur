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
from model import db, Artist, Venue, Shows

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
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
  venues = Venue.query.order_by(Venue.id.desc()).limit(10)
  artists = Artist.query.order_by(Artist.id.desc()).limit(10)
  return render_template('pages/home.html', venues=venues, artists=artists)


#  Venues
#  ----------------------------------------------------------------

# 1)
@app.route('/venues')
def venues():
    venues = Venue.query.order_by(Venue.state.desc(), Venue.city.asc()).all()
    units = set()
    areas = []
    for venue in venues:
        units.add((venue.city, venue.state))

    for unit in units:
        areas.append({
            "city": unit[0],
            "state": unit[1],
            "venues": []
        })
        
    for venue in venues:
        for area in areas:
            if area['city'] == venue.city and area['state'] == venue.state:
                area['venues'].append({
                    'id': venue.id,
                    'name': venue.name
            })

    return  render_template('pages/venues.html', areas=areas)

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

# 3)
@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue = Venue.query.get_or_404(venue_id)
  past_shows = []
  upcoming_shows = []
  for show in venue.venue_show:
    temp_show = {
        'artist_id': show.artist_id,
        'artist_name': show.artist.name,
        'artist_image_link': show.artist.image_link,
        'start_time': show.start_time
    }
    if show.start_time <= datetime.now():
        past_shows.append(temp_show)
    else:
        upcoming_shows.append(temp_show)
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

# 5)
@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):

  artist = Artist.query.filter(Artist.id==artist_id).first()
  app.logger.info(artist.artist_show)
  datas = Shows.query.join("artist").join("venue"). \
        add_columns(Venue.name, Venue.image_link, Artist.id, Shows.start_time). \
        filter(Artist.id == artist_id).all()

  upcoming_shows = []
  past_shows = []
  for index, data in enumerate(datas):
    if data[4] >= datetime.now():
      upcoming_shows.append({
            'venue_id': data[0].venue_id,
            'venue_name': data[1],
            'venue_image_link': data[2],
            'start_time': format_datetime(str(data[0].start_time))
    })
    else:
      past_shows.append({
            'venue_id': data[0].venue_id,
            'venue_name': data[1],
            'venue_image_link': data[2],
            'start_time': format_datetime(str(data[0].start_time))
      })

  artist.upcoming_shows_count = len(upcoming_shows)
  artist.upcoming_shows = upcoming_shows
  artist.past_shows_count = len(past_shows)
  artist.past_shows = past_shows
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
  return render_template('pages/artists.html')
  
# 6)
@app.route('/shows')
def shows():
  data = []
  shows = Shows.query.order_by(Shows.start_time.desc()).all()
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
    # print(sys.exc_info())
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
