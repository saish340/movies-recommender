import os
import requests
import json
import logging
from flask import Flask, render_template, request, redirect, url_for, jsonify, make_response
from flask.logging import create_logger
from textblob import TextBlob
from bs4 import BeautifulSoup

# Configure Flask app
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False  # Preserve JSON response order
app.config['PROPAGATE_EXCEPTIONS'] = False  # Don't propagate exceptions to the werkzeug handler

# Configure logging
log = create_logger(app)
log.setLevel(logging.INFO)

# Safe environment variable handling
OMDB_API_KEY = os.getenv('OMDB_API_KEY', '8aad5b1b')
if not OMDB_API_KEY:
    log.error("OMDB_API_KEY is not set! Using default key, which may not work.")
    
# Error handling
class APIError(Exception):
    """Custom exception for API-related errors"""
    def __init__(self, message, status_code=500, payload=None):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.payload = payload
        
    def to_dict(self):
        rv = dict(self.payload or ())
        rv['error'] = self.message
        return rv


# Helper: Fetch movie data from OMDb
def fetch_movie_data(query):
    try:
        url = f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}&s={query}"
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if data.get('Response') == 'False':
                log.warning(f"API returned error: {data.get('Error')}")
                return []
            return data.get('Search', [])
        else:
            log.error(f"API request failed with status code: {resp.status_code}")
            return []
    except requests.exceptions.RequestException as e:
        log.error(f"Request exception in fetch_movie_data: {str(e)}")
        return []
    except Exception as e:
        log.error(f"Unexpected error in fetch_movie_data: {str(e)}")
        return []

# Helper: Get movie details from OMDb
def get_movie_details(imdb_id):
    try:
        url = f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}&i={imdb_id}&plot=full"
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if data.get('Response') == 'False':
                log.warning(f"API returned error for movie {imdb_id}: {data.get('Error')}")
                return None
            return data
        else:
            log.error(f"API request failed for movie {imdb_id} with status code: {resp.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        log.error(f"Request exception in get_movie_details: {str(e)}")
        return None
    except Exception as e:
        log.error(f"Unexpected error in get_movie_details: {str(e)}")
        return None

# Helper: Suggest similar movies (by genre)
def get_similar_movies(genre, exclude_id=None):
    try:
        # OMDb does not provide direct similar movies, so we search by genre
        url = f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}&s={genre}"
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if data.get('Response') == 'False':
                log.warning(f"API returned error for genre {genre}: {data.get('Error')}")
                return []
            
            results = data.get('Search', [])
            # Exclude current movie
            if exclude_id:
                results = [m for m in results if m.get('imdbID') != exclude_id]
            return results[:6]
        else:
            log.error(f"API request failed for genre {genre} with status code: {resp.status_code}")
            return []
    except requests.exceptions.RequestException as e:
        log.error(f"Request exception in get_similar_movies: {str(e)}")
        return []
    except Exception as e:
        log.error(f"Unexpected error in get_similar_movies: {str(e)}")
        return []


# Helper: Scrape IMDb reviews and perform sentiment analysis
def get_imdb_reviews(imdb_id):
    reviews = []
    try:
        url = f"https://www.imdb.com/title/{imdb_id}/reviews"
        resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            review_divs = soup.find_all('div', class_='text')
            for div in review_divs[:10]:
                try:
                    text = div.get_text()
                    sentiment = TextBlob(text).sentiment.polarity
                    reviews.append({'text': text, 'sentiment': sentiment})
                except Exception as e:
                    log.error(f"Error processing review: {str(e)}")
                    continue
        else:
            log.error(f"Failed to fetch reviews for {imdb_id}, status code: {resp.status_code}")
    except requests.exceptions.RequestException as e:
        log.error(f"Request exception in get_imdb_reviews: {str(e)}")
    except Exception as e:
        log.error(f"Unexpected error in get_imdb_reviews: {str(e)}")
    return reviews


@app.route('/')
def home():
    try:
        # Fetch popular and top-rated movies for the homepage
        popular_movies = fetch_movie_data("action")[:4]  # Using action genre as a proxy for popular
        top_rated = fetch_movie_data("drama")[:4]  # Using drama genre as a proxy for top-rated
        now_playing = fetch_movie_data("2023")[:4]  # Using current year as a proxy for now playing
        upcoming = fetch_movie_data("coming soon")[:4]  # Using "coming soon" as a proxy for upcoming
        
        return render_template('home.html', 
                            popular=popular_movies, 
                            top_rated=top_rated, 
                            now_playing=now_playing, 
                            upcoming=upcoming)
    except Exception as e:
        log.error(f"Error in home route: {str(e)}")
        # Return minimal template with error message rather than crashing
        return render_template('home.html', 
                           popular=[], 
                           top_rated=[], 
                           now_playing=[], 
                           upcoming=[],
                           error="Unable to load movies at this time")

@app.route('/search')
def search():
    try:
        query = request.args.get('q', '')
        movies = fetch_movie_data(query) if query else []
        return render_template('search.html', movies=movies, query=query)
    except Exception as e:
        log.error(f"Error in search route: {str(e)}")
        return render_template('search.html', movies=[], query="", error="Search unavailable at this time")

@app.route('/movie/<imdb_id>')
def movie_details(imdb_id):
    try:
        details = get_movie_details(imdb_id)
        if not details or details.get('Response') == 'False':
            log.warning(f"No details found for movie {imdb_id}, redirecting to home")
            return redirect(url_for('home'))
            
        # OMDb returns actors as a string
        cast = details.get('Actors', '').split(', ')[:5] if details.get('Actors') else []
        genre = details.get('Genre', '').split(',')[0] if details.get('Genre') else ''
        reviews = get_imdb_reviews(imdb_id) if imdb_id else []
        similar = get_similar_movies(genre, exclude_id=imdb_id)
        return render_template('movie.html', details=details, cast=cast, reviews=reviews, similar=similar)
    except Exception as e:
        log.error(f"Error in movie_details route for {imdb_id}: {str(e)}")
        # Redirect to home on error rather than showing a broken page
        return redirect(url_for('home'))

# Register error handlers to return JSON
@app.errorhandler(APIError)
def handle_api_error(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

@app.errorhandler(404)
def page_not_found(e):
    return jsonify(error="Resource not found"), 404

@app.errorhandler(500)
def internal_server_error(e):
    log.error(f"Internal Server Error: {str(e)}")
    return jsonify(error="An unexpected error occurred"), 500

@app.errorhandler(Exception)
def handle_unexpected_error(e):
    log.error(f"Unexpected error: {str(e)}")
    return jsonify(error="An unexpected error occurred"), 500

# This enables CORS, which is needed for Vercel serverless functions
@app.after_request
def add_cors_headers(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# Handle OPTIONS requests for CORS preflight
@app.route('/', methods=['OPTIONS'])
@app.route('/<path:path>', methods=['OPTIONS'])
def options_handler(path=None):
    response = make_response()
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
