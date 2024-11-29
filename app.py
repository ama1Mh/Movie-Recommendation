from flask import Flask, request, jsonify,  render_template
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

# Load pre-trained model and embeddings
movies_df = pd.read_csv("cleaned_movies.csv")
movie_embeddings = np.load("movie_embeddings.npy")  # Precomputed embeddings

# Recommendation logic
# Recommendation logic
def recommend_movies(selected_movies, top_n=5):
    # Find indices of selected movies
    selected_indices = [movies_df[movies_df['title'] == title].index[0] for title in selected_movies]
    
    # Get embeddings for the selected movies
    selected_embeddings = movie_embeddings[selected_indices]
    
    # Compute similarity scores
    similarity_scores = cosine_similarity(selected_embeddings, movie_embeddings).mean(axis=0)
    
    # Get indices of the most similar movies (excluding the selected ones)
    similar_indices = similarity_scores.argsort()[-(top_n + len(selected_movies)):-len(selected_movies)][::-1]
    
    # Retrieve recommended movies and their details
    recommendations = movies_df.iloc[similar_indices][['title', 'overview']].copy()
    recommendations['similarity'] = similarity_scores[similar_indices]
    
    # Convert to a list of dictionaries
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
    port = int(os.environ.get("PORT", 5000))  # Use the PORT environment variable or default to 5000
    app.run(host="0.0.0.0", port=port)
