import streamlit as st
import pickle
import pandas as pd
import requests

# ── Config + CSS ──────────────────────────────────────────────────────────────echo similarity.pkl >> .gitignore
st.set_page_config(page_title="CineMatch", page_icon="🎬", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@300;400;600&display=swap');

* { font-family: 'Inter', sans-serif; }
.stApp { background: #0a0a0a; }
#MainMenu, footer, header { visibility: hidden; }

.navbar {
    display: flex; align-items: center; gap: 14px;
    background: linear-gradient(180deg, #000000cc, transparent);
    padding: 22px 40px; margin-bottom: 0px;
}
.logo-box {
    background: #e50914; color: white;
    font-family: 'Bebas Neue'; font-size: 28px;
    padding: 6px 14px; border-radius: 6px; letter-spacing: 3px;
}
.logo-text {
    font-family: 'Bebas Neue'; font-size: 28px;
    color: white; letter-spacing: 4px;
}
.hero-banner {
    background: linear-gradient(135deg, #1a0000 0%, #0a0a0a 60%);
    border: 1px solid #1f1f1f; border-radius: 16px;
    padding: 22px 40px; margin-bottom: 10px;
    position: relative; overflow: hidden;
}
.hero-banner::before {
    content: '🎬';
    position: absolute; right: 60px; top: 50%;
    transform: translateY(-50%);
    font-size: 120px; opacity: 0.07;
}
.hero-banner h2 {
    font-family: 'Bebas Neue' !important;
    font-size: 32px !important; letter-spacing: 4px !important;
    color: white !important; margin: 0 0 8px 0 !important;
}
.hero-banner p {
    color: #888; font-size: 15px;
    font-weight: 300; letter-spacing: 1px; margin: 0;
}
.stSelectbox label {
    color: #666 !important; font-size: 11px !important;
    letter-spacing: 2px !important; text-transform: uppercase !important;
}
.stSelectbox > div > div {
    background: #141414 !important; border: 1px solid #2a2a2a !important;
    border-radius: 8px !important; color: white !important;
    font-size: 15px !important;
}
.stButton > button {
    background: #e50914 !important; color: white !important;
    border: none !important; border-radius: 8px !important;
    padding: 14px 0 !important; font-weight: 600 !important;
    font-size: 13px !important; letter-spacing: 2px !important;
    text-transform: uppercase !important; width: 100% !important;
}
.stButton > button:hover {
    background: #ff1a1a !important; transform: translateY(-1px) !important;
    box-shadow: 0 8px 25px #e5091455 !important;
}
.section-label {
    color: #555; font-size: 11px; letter-spacing: 3px;
    text-transform: uppercase; margin: 40px 0 20px 0;
    padding-bottom: 12px; border-bottom: 1px solid #1a1a1a;
}
.section-label span { color: #e50914; }
img { border-radius: 10px !important; }
[data-testid="stImage"]:hover { transform: scale(1.05) !important; }
.stCaption {
    color: #aaaaaa !important; text-align: center !important;
    font-size: 12px !important; margin-top: 6px !important;
}
.stSpinner > div { border-top-color: #e50914 !important; }
</style>

<div class="navbar">
    <div class="logo-box">C</div>
    <div class="logo-text">CINEMATCH</div>
</div>

<div class="hero-banner">
    <h2>FIND YOUR NEXT FILM</h2>
    <p>Pick a movie you love — we'll find 5 you'll love even more</p>
</div>
""", unsafe_allow_html=True)


data_dict = pickle.load(open('data_dict.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))
final_df = pd.DataFrame(data_dict)

OMDB_API_KEY = "768ac12"

def fetch_poster(title):
    details = {}
    try:
        url = f"http://www.omdbapi.com/?t={title}&apikey={OMDB_API_KEY}"
        response = requests.get(url, timeout=5)      # send request to OMDb API with the movie title
        data = response.json()                         # get back JSON data
        poster = data.get('Poster')              # extracts the Poster url
        details = {
            'Year': data.get('Year', 'N/A'),
            'Genre': data.get('Genre', 'N/A'),
            'Rating': data.get('imdbRating', 'N/A'),
            'Plot': data.get('Plot', 'N/A'),
            'Runtime': data.get('Runtime', 'N/A')}
        if (poster) and (poster != 'N/A'):
            return poster, details
    except Exception:
        pass
    return "https://placehold.co/300x450?text=No+Poster", details        # If no poster found then returns a placeholder image with no poster watermark


def recommend_mov(movie_title):
    movie_id = final_df[final_df['title'] == movie_title]['movieId'].values[0]
    sim_scores = similarity.loc[movie_id]
    sim_scores = sim_scores.sort_values(ascending=False).drop(movie_id)
    top_movies = sim_scores.head(5).index

    titles = []
    posters = []
    details_list = []
    for i in top_movies:
        title = final_df[final_df['movieId'] == i]['title'].values[0]
        titles.append(title)
        poster, details = fetch_poster(title)
        posters.append(poster)
        details_list.append(details)
    return titles, posters, details_list

st.title('Movie Recommendation System')
selected_movie = st.selectbox('Discover Movies Tailored Just for You', sorted(final_df.title.values))

if st.button('Recommend'):
    with st.spinner('Finding movies...'):
        titles, posters, details_list = recommend_mov(selected_movie)

        cols = st.columns(5)
        for col, title, poster, details in zip(cols, titles, posters, details_list):
            with col:
                st.image(poster, width=160)
                st.caption(title)
                with st.expander("ℹ️ Details"):
                     st.markdown(f"⭐ **{details.get('Rating')}** &nbsp;|&nbsp; 🕐 **{details.get('Runtime')}**")
                     st.markdown(f"🎭 {details.get('Genre')}")
                     st.markdown(f"📅 {details.get('Year')}")
                     st.caption(details.get('Plot'))