from flask import Blueprint, render_template, redirect, url_for, request
import requests
from .models import Movie
from .main import db
from .forms import FindMovieForm, RateMovieForm
import os
from dotenv import load_dotenv
load_dotenv()
MOVIE_DB_API_KEY = os.getenv("API_KEY")
MOVIE_DB_SEARCH_URL = "https://api.themoviedb.org/3/search/movie"
MOVIE_DB_INFO_URL = "https://api.themoviedb.org/3/movie"
MOVIE_DB_IMAGE_URL = "https://image.tmdb.org/t/p/w500"

# Define the Blueprint
main = Blueprint('main', __name__)

@main.route("/")
def home():
    result = db.session.execute(db.select(Movie).order_by(Movie.rating))
    all_movies = result.scalars().all()  # Convert ScalarResult to Python List

    for i in range(len(all_movies)):
        all_movies[i].ranking = len(all_movies) - i
    db.session.commit()

    return render_template("index.html", movies=all_movies)

@main.route("/add", methods=["GET", "POST"])
def add_movie():
    form = FindMovieForm()
    if form.validate_on_submit():
        movie_title = form.title.data
        response = requests.get(MOVIE_DB_SEARCH_URL, params={
            "api_key": MOVIE_DB_API_KEY,
            "query": movie_title
        })

        # Handle API response errors
        if response.status_code != 200:
            return render_template("error.html", message="Failed to fetch movies from the database.")

        # Check if "results" exists and is not empty
        data = response.json()
        if "results" not in data or not data["results"]:
            return render_template("error.html", message="No movies found for the given title.")

        # Pass results to the select.html template
        return render_template("select.html", options=data["results"])
    return render_template("add.html", form=form)

@main.route("/find")
def find_movie():
    movie_api_id = request.args.get("id")
    if movie_api_id:
        movie_api_url = f"{MOVIE_DB_INFO_URL}/{movie_api_id}"
        response = requests.get(movie_api_url, params={
            "api_key": MOVIE_DB_API_KEY,
            "language": "en-US"
        })

        # Handle API response errors
        if response.status_code != 200:
            return render_template("error.html", message="Failed to fetch movie details.")

        # Add new movie to the database
        data = response.json()
        new_movie = Movie(
            title=data["title"],
            year=data["release_date"].split("-")[0],
            img_url=f"{MOVIE_DB_IMAGE_URL}{data['poster_path']}",
            description=data["overview"]
        )
        db.session.add(new_movie)
        db.session.commit()
        return redirect(url_for("main.rate_movie", id=new_movie.id))
    return redirect(url_for("main.home"))

@main.route("/edit", methods=["GET", "POST"])
def rate_movie():
    form = RateMovieForm()
    movie_id = request.args.get("id")
    movie = db.get_or_404(Movie, movie_id)
    if form.validate_on_submit():
        movie.rating = float(form.rating.data)
        movie.review = form.review.data
        db.session.commit()
        return redirect(url_for('main.home'))
    return render_template("edit.html", movie=movie, form=form)
@main.route("/delete")
def delete_movie():
    movie_id = request.args.get("id")
    movie = db.get_or_404(Movie, movie_id)
    db.session.delete(movie)
    db.session.commit()
    return redirect(url_for("main.home"))

