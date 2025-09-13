import os
import requests
from flask import Flask, render_template, request, redirect, url_for
from textblob import TextBlob
from bs4 import BeautifulSoup

app = Flask(__name__)


OMDB_API_KEY = os.getenv('OMDB_API_KEY', '8aad5b1b')


# Helper: Fetch movie data from OMDb
def fetch_movie_data(query):
    url = f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}&s={query}"
    resp = requests.get(url)
    if resp.status_code == 200:
        data = resp.json()
        return data.get('Search', [])
    return []

# Helper: Get movie details from OMDb
def get_movie_details(imdb_id):
    url = f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}&i={imdb_id}&plot=full"
    resp = requests.get(url)
    if resp.status_code == 200:
        return resp.json()
    return None

# Helper: Suggest similar movies (by genre)
def get_similar_movies(genre, exclude_id=None):
    # OMDb does not provide direct similar movies, so we search by genre
    url = f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}&s={genre}"
    resp = requests.get(url)
    if resp.status_code == 200:
        results = resp.json().get('Search', [])
        # Exclude current movie
        if exclude_id:
            results = [m for m in results if m.get('imdbID') != exclude_id]
        return results[:6]
    return []


# Helper: Scrape IMDb reviews and perform sentiment analysis
def get_imdb_reviews(imdb_id):
    reviews = []
    url = f"https://www.imdb.com/title/{imdb_id}/reviews"
    resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    if resp.status_code == 200:
        soup = BeautifulSoup(resp.text, 'html.parser')
        review_divs = soup.find_all('div', class_='text')
        for div in review_divs[:10]:
            text = div.get_text()
            sentiment = TextBlob(text).sentiment.polarity
            reviews.append({'text': text, 'sentiment': sentiment})
    return reviews


@app.route('/')
def home():
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

@app.route('/search')
def search():
    query = request.args.get('q', '')
    movies = fetch_movie_data(query) if query else []
    return render_template('search.html', movies=movies, query=query)

@app.route('/movie/<imdb_id>')
def movie_details(imdb_id):
    details = get_movie_details(imdb_id)
    if not details or details.get('Response') == 'False':
        return redirect(url_for('home'))
    # OMDb returns actors as a string
    cast = details.get('Actors', '').split(', ')[:5]
    genre = details.get('Genre', '').split(',')[0] if details.get('Genre') else ''
    reviews = get_imdb_reviews(imdb_id) if imdb_id else []
    similar = get_similar_movies(genre, exclude_id=imdb_id)
    return render_template('movie.html', details=details, cast=cast, reviews=reviews, similar=similar)

# This enables CORS, which is needed for Vercel serverless functions
@app.after_request
def add_cors_headers(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
