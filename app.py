from flask import Flask, request, jsonify, render_template
import joblib
import pandas as pd
import random

app = Flask(__name__)

# Load saved components
tfidf = joblib.load('tfidf_vectorizer.pkl')
cosine_sim = joblib.load('cosine_similarity_matrix.pkl')
dataset = pd.read_csv('processed_movies.csv')

# Home Route
@app.route('/')
def index():
    # Select 5 random movies released after 2000
    recent_movies = dataset[dataset['release_year'] >= 2000]
    random_movies = recent_movies.sample(5)[['original_title', 'poster_url', 'overview']]
    return render_template('index.html', movies=random_movies.to_dict(orient='records'))

# Shuffle Movies Route
@app.route('/shuffle', methods=['GET'])
def shuffle_movies():
    # Select 5 random movies released after 2000
    recent_movies = dataset[dataset['release_year'] >= 2000]
    random_movies = recent_movies.sample(5)[['original_title', 'poster_url', 'overview']]
    return jsonify(random_movies.to_dict(orient='records'))

# Recommendation API
@app.route('/recommend', methods=['POST'])
def recommend():
    # Handle recommendations for selected movies or a single searched movie
    selected_movies = request.json.get('selected_movies', [])
    searched_movie = request.json.get('searched_movie', None)

    if searched_movie:
        if searched_movie not in dataset['original_title'].values:
            return jsonify({'error': f'Movie "{searched_movie}" not found in the dataset.'}), 404

        # Get recommendations based on the searched movie
        idx = dataset[dataset['original_title'] == searched_movie].index[0]
        sim_scores = list(enumerate(cosine_sim[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

        # Get the indices of the top 5 recommended movies
        recommended_indices = [i[0] for i in sim_scores[1:6]]
        recommendations = dataset.iloc[recommended_indices][['original_title', 'poster_url', 'overview', 'vote_average', 'release_year']].to_dict(orient='records')
        return jsonify(recommendations)

    elif selected_movies:
        # Get cumulative recommendations based on selected movies
        sim_scores = sum([cosine_sim[dataset[dataset['original_title'] == movie].index[0]] for movie in selected_movies])
        sim_scores = list(enumerate(sim_scores))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

        # Get the indices of the top 5 recommended movies
        recommended_indices = [i[0] for i in sim_scores if dataset.iloc[i[0]]['original_title'] not in selected_movies][:5]
        recommendations = dataset.iloc[recommended_indices][['original_title', 'poster_url', 'overview', 'vote_average', 'release_year']].to_dict(orient='records')
        return jsonify(recommendations)

    else:
        return jsonify({'error': 'No movies selected or searched.'}), 400

if __name__ == '__main__':
    app.run(debug=True)
