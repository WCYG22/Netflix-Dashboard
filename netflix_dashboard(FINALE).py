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

# Load data
def fetch_data():
    data = collection.find()
    return pd.DataFrame(list(data))

df = fetch_data()

# Clean up data
df['YEAR'] = pd.to_numeric(df['YEAR'], errors='coerce')
df['RATING'] = pd.to_numeric(df['RATING'], errors='coerce')

# UI
st.title("🍿 Netflix Movies Dashboard")

# Search
search_term = st.text_input("Search Movie Title")
if search_term:
    df = df[df['TITLE'].str.contains(search_term.upper(), na=False)]

# Filters
year_range = st.slider("Filter by Year", int(df['YEAR'].min()), int(df['YEAR'].max()), (2010, 2025))
rating_range = st.slider("Filter by Rating", float(df['RATING'].min()), float(df['RATING'].max()), (5.0, 10.0))

df_filtered = df[ 
    (df['YEAR'] >= year_range[0]) & 
    (df['YEAR'] <= year_range[1]) & 
    (df['RATING'] >= rating_range[0]) & 
    (df['RATING'] <= rating_range[1])
]

# Center the "Select Genre" dropdown in the middle
col1, col2, col3 = st.columns([1, 3, 1])  # Create three columns: the middle one is wider
with col2:  # Center the genre selection in the middle column
    genre_filter = st.selectbox("🎭 Select Genre", df_filtered['GENRE'].dropna().unique())

genre_df = df_filtered[df_filtered['GENRE'] == genre_filter]

st.subheader(f"🎬 Movies in the {genre_filter} Genre")
st.dataframe(genre_df[['ID', 'TITLE', 'YEAR', 'CERTIFICATE', 'DURATION', 'GENRE', 'RATING']])

# Top Rated
st.subheader("🌟 Top 10 Rated Movies")
top_movies = df_filtered.sort_values(by="RATING", ascending=False).head(10)
st.dataframe(top_movies[['TITLE', 'YEAR', 'GENRE', 'RATING']])

# Chart: Genre Distribution
st.subheader("📊 Genre Distribution")
genre_count = df_filtered['GENRE'].value_counts().reset_index()
genre_count.columns = ['GENRE', 'COUNT']
fig = px.bar(genre_count, x='GENRE', y='COUNT', title="Movies by Genre")
st.plotly_chart(fig)
