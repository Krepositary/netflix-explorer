import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from collections import Counter

# --- Page Setup ---
st.set_page_config(page_title="Netflix Explorer", layout="wide", page_icon="🎬")
st.title("🎬 Netflix Explorer Dashboard")
st.markdown("Explore Netflix content by genre, rating, year and more 📺")

# --- Embedded Clean Data ---
@st.cache_data
def load_data():
    data = {
        "title": [
            "The Social Dilemma", "Breaking Bad", "Stranger Things", "The Crown", "Our Planet", 
            "Bridgerton", "The Irishman", "Black Mirror", "Narcos", "The Magic Pencil"
        ],
        "type": [
            "Movie", "TV Show", "TV Show", "TV Show", "TV Show", 
            "TV Show", "Movie", "TV Show", "TV Show", "TV Show"
        ],
        "release_year": [
            2020, 2008, 2016, 2016, 2019, 
            2020, 2019, 2011, 2015, 2018
        ],
        "rating": [
            "PG-13", "TV-MA", "TV-14", "TV-MA", "TV-G", 
            "TV-MA", "R", "TV-MA", "TV-MA", "TV-Y7"
        ],
        "listed_in": [
            "Documentaries, Social & Cultural Docs",
            "Crime TV Shows, Drama",
            "Horror, Drama",
            "Drama, British",
            "Science & Nature Docs",
            "Romance, Drama",
            "Crime, Drama",
            "Sci-Fi & Fantasy, Drama",
            "Crime, Thriller",
            "Animated, Comedy"
        ]
    }
    df = pd.DataFrame(data)
    np.random.seed(42)
    df["simulated_rating"] = np.round(np.random.uniform(3.5, 9.5, len(df)), 1)
    return df

df = load_data()

# --- Sidebar Filters ---
st.sidebar.header("🔍 Filter Options")

content_type = st.sidebar.multiselect("📂 Select Type:", df["type"].unique(), default=df["type"].unique())

all_genres = sorted(set(genre.strip() for sublist in df['listed_in'].str.split(',') for genre in sublist))
genres = st.sidebar.multiselect("🎭 Select Genre:", all_genres, default=all_genres[:4])

rating_range = st.sidebar.slider("⭐ Simulated Rating:", 0.0, 10.0, (4.0, 9.5), 0.1)
min_year, max_year = int(df["release_year"].min()), int(df["release_year"].max())
year_range = st.sidebar.slider("📅 Year Range:", min_year, max_year, (min_year, max_year))

# --- Filtering Logic ---
def has_selected_genre(row_genres):
    return any(genre in row_genres for genre in genres)

filtered_df = df[
    (df["type"].isin(content_type)) &
    (df["release_year"].between(*year_range)) &
    (df["simulated_rating"].between(*rating_range)) &
    (df["listed_in"].apply(has_selected_genre))
]

st.success(f"✅ {filtered_df.shape[0]} titles found matching your filters.")

# --- Display Filtered Table ---
st.subheader("📋 Filtered Netflix Titles")
st.dataframe(
    filtered_df[["title", "type", "release_year", "rating", "listed_in", "simulated_rating"]],
    use_container_width=True
)

# --- Plot: Type Count ---
fig1 = px.histogram(filtered_df, x="type", color="type", title="Content Type Distribution", text_auto=True)
st.plotly_chart(fig1, use_container_width=True)

# --- Plot: Top Genres ---
all_genres_list = [genre.strip() for sublist in filtered_df["listed_in"].str.split(",") for genre in sublist]
top_genres = pd.DataFrame(Counter(all_genres_list).most_common(5), columns=["Genre", "Count"])
fig2 = px.bar(top_genres, x="Genre", y="Count", color="Genre", title="Top 5 Genres")
st.plotly_chart(fig2, use_container_width=True)

# --- Plot: Releases Over Years ---
year_data = filtered_df.groupby("release_year").size().reset_index(name="Count")
fig3 = px.line(year_data, x="release_year", y="Count", title="Releases Over the Years", markers=True)
st.plotly_chart(fig3, use_container_width=True)

# --- Footer ---
st.markdown("---")
st.markdown("💡 *Built with ❤️ using Python, Pandas, Plotly, and Streamlit.*")
