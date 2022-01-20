
# Imports

import json
import logging
from logging import Formatter, FileHandler

import babel
import dateutil.parser
from flask import Flask, render_template, request, flash, redirect, url_for, abort
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy

from forms import *


# Config.


app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app, db)


# Models.


class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(120))
    shows = db.relationship('Show', backref='venue', lazy=True)

    def __repr__(self):
        return f'<Venue {self.id} {self.name}>'


class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(120))
    shows = db.relationship('Show', backref='artist', lazy=True)

    def __repr__(self):
        return f'<Artist {self.id} {self.name}>'


class Show(db.Model):
    __tablename__ = 'shows'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False)
    start_time = db.Column(db.DateTime, default=datetime.now(), nullable=False)

    def __repr__(self):
        return f'<Show {self.id} {self.artist_id} {self.venue_id} {self.start_time}>'



# Filters.



def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


app.jinja_env.filters['datetime'] = format_datetime

# Controllers.


@app.route('/')
def index():
  return render_template('pages/home.html')



@app.route('/venues')
def venues():

    areas = db.session.query(Venue.city, Venue.state).distinct(Venue.city, Venue.state)
    response = []
    for area in areas:

        # Querying venues and filter them based on area (city, venue)
        result = Venue.query.filter(Venue.state == area.state).filter(Venue.city == area.city).all()

        venue_data = []

        # Creating venues' response
        for venue in result:
            venue_data.append({
                'id': venue.id,
                'name': venue.name,
                'num_upcoming_shows': len(db.session.query(Show).filter(Show.start_time > datetime.now()).all())
            })

            response.append({
                'city': area.city,
                'state': area.state,
                'venues': venue_data
            })

    return render_template('pages/venues.html', areas=response)




@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  try:
    
    venue =Venue(
      name=request.form.get('name'),
      city=request.form.get('city'),
      state=request.form.get('state'),
      address=request.form.get('address'),
      phone=request.form.get('phone'),
      genres=request.form.get('genres'),
      image_link=request.form.get('image_link'),
      facebook_link=request.form.get('facebook_link'),
      website=request.form.get('website_link'),
      seeking_talent=bool(request.form.get('seeking_talent')=='y'),
      seeking_description=request.form.get('seeking_description'))
      
    db.session.add(venue)
    db.session.commit()
    
    flash("Added!")

  except Exception as ex:
    print(ex)
    
    flash("Venue not added! Error occured!")
    db.session.rollback()

  finally:
      db.session.close()
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    try:
        Venue.query.filter(Venue.id == venue_id).delete()
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return render_template('pages/home.html')
    

@app.route('/artists')
def artists():
  response = Artist.query.all()
  return render_template('pages/artists.html', artists=response)

#done!
@app.route('/artists/search', methods=['POST'])
def search_artists():
    search_term = request.form.get('search_term', '')
    result = db.session.query(Artist).filter(Artist.name.ilike(f'%{search_term}%')).all()
    count = len(result)
    response = {
        "count": count,
        "data": result
    }
    return render_template('pages/search_artists.html', results=response, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    artist = Artist.query.filter(Artist.id == artist_id).first()

    past = db.session.query(
        Show
        ).filter(
            Show.artist_id == artist_id
        ).filter(
            Show.start_time < datetime.now()
        ).join(
            Venue,
            Show.venue_id == Venue.id
        ).add_columns(
            Venue.id, 
            Venue.name,
            Venue.image_link,
            Show.start_time
        ).all()

    upcoming = db.session.query(
        Show
        ).filter(
            Show.artist_id == artist_id
        ).filter(
            Show.start_time > datetime.now()
        ).join(
            Venue, 
            Show.venue_id == Venue.id
        ).add_columns(
            Venue.id, 
            Venue.name,
            Venue.image_link,
            Show.start_time
        ).all()

    upcoming_shows = []

    past_shows = []

    for show in upcoming:
        upcoming_shows.append({
            'venue_id': show[1],
            'venue_name': show[2],
            'image_link': show[3],
            'start_time': str(show[4])
        })

    for show in past:
        past_shows.append({
            'venue_id': show[1],
            'venue_name': show[2],
            'image_link': show[3],
            'start_time': str(show[4])
        })

    if artist is None:
        abort(404)

    response = {
        "id": artist.id,
        "name": artist.name,
        "genres": [artist.genres],
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past),
        "upcoming_shows_count": len(upcoming),
    }
    return render_template('pages/show_artist.html', artist=response)


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = Artist.query.filter(Artist.id == artist_id).first()
    return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    try:
      artist = Artist.query.get(artist_id)

      if artist is None:
          return abort(404)
          

      artist.name = request.form.get('name')
      artist.city = request.form.get('city')
      artist.state = request.form.get('state')
      artist.phone = request.form.get('phone')
      artist.genres= request.form.get('genres')
      artist.facebook_link = request.form.get('facebook_link')
      artist.image_link = request.form.get('image_link')
      artist.seeking_venue = bool(request.form.get('seeking_venue')=='y')
      artist.seeking_description= request.form.get('seeking_description')



      db.session.add(artist)
      db.session.commit()

      flash(f"{artist.name}'s page was successfully updated!")

    except Exception as ex:
        print(ex)
        flash(f'An error occurred. {artist.name} could not updated.')
        db.session.rollback()

    finally:
        db.session.close()

    return redirect(url_for('show_artist', artist_id=artist.id))

#done?
@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
      
    venue = Venue.query.filter(Venue.id == venue_id).first()

    past = db.session.query(
            Show
            ).filter(
                Show.venue_id == venue_id
            ).filter(
                Show.start_time < datetime.now()
            ).join(
                Artist,
                Show.artist_id == Artist.id
            ).add_columns(
                Artist.id,
                Artist.name,
                Artist.image_link,
                Show.start_time
            ).all()

    upcoming = db.session.query(
        Show
        ).filter(
            Show.venue_id == venue_id
        ).filter(
            Show.start_time > datetime.now()
        ).join(
            Artist, Show.artist_id == Artist.id
        ).add_columns(
            Artist.id,
            Artist.name,
            Artist.image_link,
            Show.start_time
        ).all()

    upcoming_shows = []

    past_shows = []

    for show in upcoming:
        upcoming_shows.append({
            'artist_id': show[1],
            'artist_name': show[2],
            'image_link': show[3],
            'start_time': str(show[4])
        })

    for show in past:
        past_shows.append({
            'artist_id': show[1],
            'artist_name': show[2],
            'image_link': show[3],
            'start_time': str(show[4])
        })

    if venue is None:
        abort(404)

    response = {
        "id": venue.id,
        "name": venue.name,
        "genres": [venue.genres],
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past),
        "upcoming_shows_count": len(upcoming),
    }
    return render_template('pages/show_venue.html', venue=response)

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.filter(Venue.id == venue_id).first()
    return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    try:
      venue = Venue.query.get(venue_id)

      if venue is None:
          return abort(404)
          

      venue.name = request.form.get('name')
      venue.city = request.form.get('city')
      venue.state = request.form.get('state')
      venue.phone = request.form.get('phone')
      venue.genres= request.form.get('genres')
      venue.facebook_link = request.form.get('facebook_link')
      venue.image_link = request.form.get('image_link')
      venue.seeking_venue = bool(request.form.get('seeking_venue')=='y')
      venue.seeking_description= request.form.get('seeking_description')



      db.session.add(venue)
      db.session.commit()

      flash(f"{venue.name}'s page was successfully updated!")

    except Exception as ex:
        print(ex)
        flash(f'An error occurred. {venue.name} could not updated.')
        db.session.rollback()

    finally:
        db.session.close()

    return redirect(url_for('show_venue', venue_id=venue.id))


@app.route('/venues/search', methods=['POST'])
def search_venues():
    search_term = request.form.get('search_term', '')
    result = db.session.query(Venue).filter(Venue.name.ilike(f'%{search_term}%')).all()
    count = len(result)
    response = {
        "count": count,
        "data": result
    }
    return render_template('pages/search_venues.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    try:
        artist = Artist(
            name=request.form.get('name'),
            city=request.form.get('city'),
            state=request.form.get('state'),
            phone=request.form.get('phone'),
            genres=request.form.get('genres'),
            image_link=request.form.get('image_link'),
            facebook_link=request.form.get('facebook_link'),
            seeking_venue=bool(request.form.get('seeking_venue')=='y'),
            website=request.form.get('website'),
            seeking_description=request.form.get('seeking_description')
        )
        db.session.add(artist)
        db.session.commit()
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except Exception as ex:
        print(ex)
        flash('An error occurred. Artist ' + request.form['name'] + ' could not be added')
        db.session.rollback()
    finally:
        db.session.close()
    return render_template('pages/home.html')



@app.route('/shows')
def shows():
    data = Show.query.join(Artist, Artist.id == Show.artist_id).join(Venue, Venue.id == Show.venue_id).all()

    response = []
    for show in data:
        response.append({
            "venue_id": show.venue_id,
            "venue_name": show.venue.name,
            "artist_id": show.artist_id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": str(show.start_time)
        })
    return render_template('pages/shows.html', shows=response)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    try:
        show = Show(
            artist_id=request.form['artist_id'],
            venue_id=request.form['venue_id'],
            start_time=request.form['start_time']
        )
        db.session.add(show)
        db.session.commit()
        flash('Show was successfully added!')
    except Exception as ex:
        print(ex)
        flash('An error occurred. Show could not be added')
        db.session.rollback()
    finally:
        db.session.close()

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
    

# Launch.


# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
