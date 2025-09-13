# Movie Recommender App

A modern Flask-based movie recommendation application with a sleek UI that allows users to search for movies, view details, read reviews with sentiment analysis, and discover similar films.

## Deployment Instructions

### Deploying on Vercel

1. Install the Vercel CLI:
   ```
   npm install -g vercel
   ```

2. Login to Vercel:
   ```
   vercel login
   ```

3. Navigate to your project directory and deploy:
   ```
   cd path/to/movies-recommender
   vercel
   ```

4. Follow the prompts and set the environment variable:
   - **OMDB_API_KEY**: Your OMDb API key

5. For subsequent deployments:
   ```
   vercel --prod
   ```

### Deploying on Render

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Configure the Web Service with the following settings:
   - **Name**: movie-recommender (or any name you prefer)
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn main:app`
4. Click "Create Web Service"

### Deploying on Replit

1. Create a new Repl and import from GitHub
2. Select "Python" as the language
3. In the Replit shell, run: `pip install -r requirements.txt`
4. Set up a `.replit` file with the following content:
   ```
   run = "gunicorn main:app"
   ```
5. Click "Run"

## Environment Variables

Set the following environment variable in your deployment platform:

- `OMDB_API_KEY`: Your OMDb API key (default is included in the code)

## Local Development

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the app:
   ```
   python main.py
   ```
   
   Or with Gunicorn:
   ```
   gunicorn main:app
   ```

3. Visit `http://localhost:5000` in your browser

## Features

- Beautiful responsive design for all device sizes
- Movie search with dynamic suggestions
- Detailed movie information including cast, ratings, and plot
- Review sentiment analysis using TextBlob
- Similar movie recommendations based on genre
- Categorized movie sections: Popular, Now Playing, Top Rated, and Upcoming