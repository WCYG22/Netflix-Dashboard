import streamlit as st
import pandas as pd
import plotly.express as px
from pymongo import MongoClient

# MongoDB Connection
password = "M44100127"
connection_string = f"mongodb+srv://JIEUN:{password}@netflixclusters.ennf3.mongodb.net/?retryWrites=true&w=majority&appName=NetflixClusters"
client = MongoClient(connection_string)
db = client["NetflixDB"]
collection = db["MOVIES_FINALE"]

# Load Data
def fetch_data():
    data = collection.find()
    return pd.DataFrame(list(data))

df = fetch_data()

# Clean up data
df['YEAR'] = pd.to_numeric(df['YEAR'], errors='coerce')
df['RATING'] = pd.to_numeric(df['RATING'], errors='coerce')

# UI
st.title("🍿 Netflix Movies Dashboard")

# Add a New Movie Form Section
st.subheader("🎬 Add a New Movie")
with st.expander("➕ Fill out the movie details to add"):
    movie_title = st.text_input("Movie Title")
    movie_genre = st.selectbox("Genre", sorted(df['GENRE'].dropna().unique()))
    movie_rating = st.number_input("Rating (0.0 - 10.0)", min_value=0.0, max_value=10.0, value=5.0, step=0.1)
    movie_year = st.number_input("Year", min_value=1900, max_value=2025, value=2022)
    movie_duration = st.number_input("Duration (minutes)", min_value=1, value=120)
    movie_description = st.text_area("Description", height=100)

    if st.button("Add Movie"):
        if not movie_title:
            st.error("❌ Movie title is required.")
        elif movie_rating < 0 or movie_rating > 10:
            st.error("❌ Rating should be between 0 and 10.")
        elif not movie_genre:
            st.error("❌ Genre is required.")
        else:
            # Check if movie already exists
            if collection.find_one({"TITLE": movie_title.upper()}):
                st.error(f"❌ Movie with the title '{movie_title}' already exists!")
            else:
                # Prepare the data to insert into MongoDB
                new_movie = {
                    "TITLE": movie_title.upper(),
                    "GENRE": movie_genre.upper(),
                    "RATING": movie_rating,
                    "YEAR": movie_year,
                    "CERTIFICATE": "Not Provided",  # You can add more inputs if needed
                    "DURATION": movie_duration,
                    "DESCRIPTION": movie_description
                }

                try:
                    collection.insert_one(new_movie)
                    st.success(f"✅ Movie '{movie_title}' added successfully!")

                    # Fetch new data and show it instantly
                    df = fetch_data()  # Fetch the latest data
                    st.write("### Preview of the New Movie:")
                    st.write(f"**Title**: {movie_title}")
                    st.write(f"**Genre**: {movie_genre}")
                    st.write(f"**Rating**: {movie_rating}")
                    st.write(f"**Year**: {movie_year}")
                    st.write(f"**Duration**: {movie_duration} minutes")
                    st.write(f"**Description**: {movie_description}")

                except Exception as e:
                    st.error(f"❌ Error adding movie: {e}")

# Search and Filter Section
st.subheader("🔍 Search and Filter Movies")
search_term = st.text_input("Search Movie Title")
if search_term:
    df = df[df['TITLE'].str.contains(search_term.upper(), na=False)]

year_range = st.slider("📅 Filter by Year", int(df['YEAR'].min()), int(df['YEAR'].max()), (2010, 2025))
rating_range = st.slider("⭐ Filter by Rating", float(df['RATING'].min()), float(df['RATING'].max()), (5.0, 10.0))

df_filtered = df[ 
    (df['YEAR'] >= year_range[0]) & 
    (df['YEAR'] <= year_range[1]) & 
    (df['RATING'] >= rating_range[0]) & 
    (df['RATING'] <= rating_range[1])
]

genre_filter = st.selectbox("🎭 Select Genre", df_filtered['GENRE'].dropna().unique())

genre_df = df_filtered[df_filtered['GENRE'] == genre_filter]

st.subheader(f"🎬 Movies in the {genre_filter} Genre")
st.dataframe(
    genre_df[['ID', 'TITLE', 'YEAR', 'CERTIFICATE', 'DURATION', 'GENRE', 'RATING']], 
    height=500, use_container_width=True  # Full-width table and fixed height
)

# Top 10 Movies Table
st.subheader("🌟 Top 10 Rated Movies")
top_movies = df_filtered.sort_values(by="RATING", ascending=False).head(10)
st.dataframe(
    top_movies[['TITLE', 'YEAR', 'GENRE', 'RATING']], 
    height=300, use_container_width=True  # Full-width table and fixed height
)

# Genre Distribution Chart Section
st.subheader("📊 Genre Distribution")
genre_count = df_filtered['GENRE'].value_counts().reset_index()
genre_count.columns = ['GENRE', 'COUNT']
fig = px.bar(genre_count, x='GENRE', y='COUNT', title="Movies by Genre")
st.plotly_chart(fig)

# Top Rated Movie Metric
st.subheader("🏆 Top Rated Movie")
st.metric("Top Rated Movie", top_movies.iloc[0]['TITLE'], delta=f"{top_movies.iloc[0]['RATING']} / 10")
