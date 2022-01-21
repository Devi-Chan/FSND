

#---#Imports---
import logging
from logging import Formatter, FileHandler
import babel
import dateutil.parser
from flask import Flask, render_template, request, flash, redirect, url_for, abort


from flask_migrate import Migrate
from flask_moment import Moment
from forms import *
#-------------



# Models
from models.tables import *

#Time
def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


app.jinja_env.filters['datetime'] = format_datetime

#Controllers.


@app.route('/')
def index():
  return render_template('pages/home.html')



@app.route('/venues')
def venues():

    areas = db.session.query(Venue.city, Venue.state).distinct(Venue.city, Venue.state)
    response = []
    for area in areas:

        # Querying venues and filter them based on area (city, venue)

        result = Venue.query.filter(Venue.state == area.state).filter(Venue.city == area.city
        ).all()

        venue_data = []

        # Creating venues' response
        for venue in result:
            venue_data.append({
                'id': venue.id,
                'name': venue.name,
                'num_upcoming_shows': len(db.session.query(
                  Show
                    ).filter(
                    Show.start_time > datetime.now()
                    ).all())
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
    
    form=VenueForm(request.form)
    venue=Venue(
    name = form.name.data,
    city = form.city.data,
    state = form.state.data,
    phone = form.phone.data,
    genres = form.genres.data,
    image_link = form.image_link.data,
    facebook_link = form.facebook_link.data,
    website = form.website_link.data,
    seeking_talent = bool(form.seeking_talent.data=='y'),
    seeking_description = form.seeking_description.data
    )
      
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
        Venue.query.filter(Venue.id == venue_id
        ).delete()

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
    
    artist = Artist.query.filter(Artist.id == artist_id
    ).first()

    return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    try:
      artist = Artist.query.get(artist_id)
      
      if artist is None:
          return abort(404)
          
      form=ArtistForm(request.form)
      artist = Artist(
        name=form.name.data,
        city=form.city.data,
        state=form.state.data,
        phone=form.phone.data,
        genres=form.genres.data,
        image_link=form.image_link.data,
        facebook_link=form.facebook_link.data,
        website=form.website_link.data,
        seeking_venue=bool(form.seeking_venue.data=='y'),
        seeking_description=form.seeking_description.data
        )



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
      
    venue = Venue.query.filter(Venue.id == venue_id
    ).first()

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

    venue = Venue.query.filter(Venue.id == venue_id
    ).first()

    return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    try:
      venue = Venue.query.get(venue_id)

      if venue is None:
          return abort(404)
      form=VenueForm(request.form)
      venue=Venue(
        name=form.name.data,
        city=form.city.data,
        state=form.state.data,
        phone=form.phone.data,
        genres=form.genres.data,
        image_link=form.image_link.data,
        facebook_link=form.facebook_link.data,
        website=form.website_link.data,
        seeking_talent=bool(form.seeking_talent.data=='y'),
        seeking_description=form.seeking_description.data
        )


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
    
    result = db.session.query(
      Venue
      ).filter(
        Venue.name.ilike(f'{search_term}')
      ).all()

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
  form = ArtistForm(request.form)
  try:
    artist = Artist(
      name=form.name.data,
      city=form.city.data,
      state=form.state.data,
      phone=form.phone.data,
      genres=form.genres.data,
      image_link=form.image_link.data,
      facebook_link=form.facebook_link.data,
      website=form.website_link.data,
      seeking_venue=bool(form.seeking_venue.data=='y'),
      seeking_description=form.seeking_description.data
    )
    db.session.add(artist)
    db.session.commit()
    flash(f'Artist {artist.name} was successfully listed!')
  except Exception as ex:
    print(ex)
    flash(f"An error occurred! {artist.name}'s artist page failed to be added")
    db.session.rollback()
  finally:
        db.session.close()
  return render_template('pages/home.html')



@app.route('/shows')
def shows():
    data = Show.query.join(
      Artist, 
      Artist.id == Show.artist_id
      ).join(
        Venue, Venue.id == Show.venue_id
      ).all()

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
        flash('An error occurred! Show could not be added')
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
