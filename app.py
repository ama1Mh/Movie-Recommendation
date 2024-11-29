from flask import Flask, request, jsonify,  render_template
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

# Load pre-trained model and embeddings
movies_df = pd.read_csv("cleaned_movies.csv")
movie_embeddings = np.load("movie_embeddings.npy")  # Precomputed embeddings

# Recommendation logic
def recommend_movies(selected_movies, top_n=5):
    selected_indices = [movies_df[movies_df['title'] == title].index[0] for title in selected_movies]
    selected_embeddings = movie_embeddings[selected_indices]
    similarity_scores = cosine_similarity(selected_embeddings, movie_embeddings).mean(axis=0)
    similar_indices = similarity_scores.argsort()[-(top_n + len(selected_movies)):-len(selected_movies)][::-1]
    recommendations = movies_df.iloc[similar_indices][['title']].copy()
    recommendations['similarity'] = similarity_scores[similar_indices]
    return recommendations.to_dict(orient='records')

# API endpoint
@app.route('/', methods=['GET'])
def home():
        return render_template('index.html')

@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.json
    selected_movies = data.get('selectedMovies', [])
    if not selected_movies:
        return jsonify({"error": "No movies selected"}), 400

    # Call the recommendation logic
    recommendations = recommend_movies(selected_movies)
    return jsonify({"recommendations": recommendations})
if __name__ == "__main__":
    app.run(debug=True)