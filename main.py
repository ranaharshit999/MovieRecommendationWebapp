import os
import pickle

import requests
import streamlit as st


st.set_page_config(page_title="Reelwise | Movie Recommendations", page_icon="🎬", layout="wide")


@st.cache_resource
def load_movie_data():
    with open("movies.pkl", "rb") as movie_file:
        movie_data = pickle.load(movie_file)
    with open("similarity.pkl", "rb") as similarity_file:
        similarity_data = pickle.load(similarity_file)
    return movie_data, similarity_data


movies, similarity = load_movie_data()


def tmdb_api_key():
    try:
        return st.secrets.get("TMDB_API_KEY", os.getenv("TMDB_API_KEY", ""))
    except FileNotFoundError:
        return os.getenv("TMDB_API_KEY", "")


@st.cache_data(show_spinner=False)
def get_poster(movie_id):
    """Fetch official TMDB artwork when a key has been configured."""
    api_key = tmdb_api_key()
    if not api_key:
        return None
    try:
        response = requests.get(
            f"https://api.themoviedb.org/3/movie/{movie_id}",
            params={"api_key": api_key}, timeout=5,
        )
        poster_path = response.json().get("poster_path") if response.ok else None
        return f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None
    except requests.RequestException:
        return None


def recommended_movies(movie_title):
    movie_index = movies.index[movies["title"] == movie_title][0]
    ranked = sorted(enumerate(similarity[movie_index]), key=lambda item: item[1], reverse=True)[1:6]
    return [movies.iloc[index] for index, _ in ranked]


def poster_fallback(title, rank):
    palette = ["#6957f7", "#e95e55", "#0d9e92", "#d28b31", "#c54c9b"]
    short_title = title if len(title) <= 34 else title[:31].rsplit(" ", 1)[0] + "…"
    return f'''<div class="poster-fallback" style="--poster-color:{palette[rank % len(palette)]}">
        <span class="poster-mark">REELWISE</span><span class="poster-title">{short_title}</span>
        <span class="poster-reel">● ● ●</span></div>'''


st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@600;700&display=swap');
.stApp {background:radial-gradient(circle at 10% -10%,rgba(111,87,247,.26),transparent 31rem),radial-gradient(circle at 90% 10%,rgba(233,94,85,.16),transparent 26rem),#111116;color:#f7f5f2}
#MainMenu,footer,header {visibility:hidden}.block-container {max-width:1180px;padding:2.4rem 2rem 4rem}
.brand {font:700 1rem 'DM Sans',sans-serif;letter-spacing:.18em;color:#f1c46b}.hero {padding:3.5rem 0 2.2rem;max-width:780px}
.hero h1 {font:700 clamp(2.7rem,6vw,5.2rem)/.98 'Playfair Display',serif;letter-spacing:-.055em;margin:.65rem 0 1.1rem;color:#fffdf9}
.hero p {font:400 1.08rem/1.6 'DM Sans',sans-serif;color:#b7b3bd;max-width:580px;margin:0}
.stSelectbox label {font:600 .76rem 'DM Sans',sans-serif!important;letter-spacing:.1em;text-transform:uppercase;color:#d8d4dc!important}
.stSelectbox div[data-baseweb="select"]>div {background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.15);border-radius:12px;color:#fff;min-height:3.25rem}
.stButton>button {width:100%;min-height:3.25rem;border:0;border-radius:12px;background:#f1c46b;color:#17131a;font:700 .9rem 'DM Sans',sans-serif;transition:transform .18s ease,box-shadow .18s ease}
.stButton>button:hover {background:#ffda8b;color:#17131a;transform:translateY(-2px);box-shadow:0 10px 28px rgba(241,196,107,.2)}
.result-kicker {font:600 .76rem 'DM Sans',sans-serif;letter-spacing:.13em;text-transform:uppercase;color:#f1c46b;margin:3.1rem 0 .5rem}.result-heading {font:700 2rem 'Playfair Display',serif;color:#fffdf9;margin:0 0 1.6rem}
.movie-card {margin-bottom:1rem}.movie-card img,.poster-fallback {width:100%;aspect-ratio:2/3;object-fit:cover;border-radius:12px;display:block;box-shadow:0 18px 34px rgba(0,0,0,.28)}.movie-card img {transition:transform .25s ease,box-shadow .25s ease}.movie-card:hover img {transform:translateY(-5px);box-shadow:0 24px 45px rgba(0,0,0,.46)}
.movie-name {font:600 1rem/1.25 'DM Sans',sans-serif;color:#f7f5f2;margin:.85rem .1rem .15rem}.movie-meta {font:500 .75rem 'DM Sans',sans-serif;letter-spacing:.08em;color:#9d98a5;text-transform:uppercase;margin:0 .1rem}
.poster-fallback {box-sizing:border-box;padding:1rem;position:relative;overflow:hidden;background:linear-gradient(145deg,var(--poster-color),#17151d 72%);color:white;display:flex;flex-direction:column;justify-content:space-between}.poster-fallback:after {content:'';position:absolute;width:12rem;height:12rem;border:1px solid rgba(255,255,255,.25);border-radius:50%;right:-5rem;top:23%}.poster-mark,.poster-reel {font:700 .57rem 'DM Sans',sans-serif;letter-spacing:.16em;z-index:1}.poster-title {font:700 clamp(1.15rem,2vw,1.7rem)/1.02 'Playfair Display',serif;z-index:1;letter-spacing:-.03em}.poster-reel {color:#f1c46b}
</style>""", unsafe_allow_html=True)

st.markdown('<div class="brand">REELWISE · DISCOVER CINEMA</div>', unsafe_allow_html=True)
st.markdown("""<section class="hero"><h1>Find your next<br>great watch.</h1><p>Choose a film you love and let its stories, moods, and worlds lead you somewhere new.</p></section>""", unsafe_allow_html=True)

form_col, button_col = st.columns([4, 1], vertical_alignment="bottom")
with form_col:
    selected_movie = st.selectbox("Start with a film", movies["title"].values)
with button_col:
    recommend_clicked = st.button("Find movies", use_container_width=True)

if recommend_clicked:
    recommendations = recommended_movies(selected_movie)
    st.markdown('<p class="result-kicker">Because you enjoyed</p>', unsafe_allow_html=True)
    st.markdown(f'<h2 class="result-heading">{selected_movie}</h2>', unsafe_allow_html=True)
    recommendation_columns = st.columns(5, gap="medium")
    for rank, (column, movie) in enumerate(zip(recommendation_columns, recommendations)):
        title = movie["title"]
        with column:
            st.markdown('<div class="movie-card">', unsafe_allow_html=True)
            poster = get_poster(movie["movie_id"])
            if poster:
                st.image(poster, use_container_width=True)
            else:
                st.markdown(poster_fallback(title, rank), unsafe_allow_html=True)
            st.markdown(f'<p class="movie-name">{title}</p><p class="movie-meta">Your next watch</p></div>', unsafe_allow_html=True)
