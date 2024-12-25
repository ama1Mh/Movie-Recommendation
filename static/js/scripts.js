document.addEventListener('DOMContentLoaded', () => {
    const selectedMovies = new Set();
    let isSearchMode = false; // Track whether the user is in search mode

    // Load initial movies
    fetchMovies();

    // Shuffle Movies
    document.getElementById('shuffleMovies').addEventListener('click', () => {
        isSearchMode = false; // Exit search mode
        fetchMovies();
    });

    // Fetch and display 5 random movies
    function fetchMovies() {
        fetch('/shuffle', {
            method: 'GET',
        })
        .then(response => response.json())
        .then(data => {
            const movieSelection = document.getElementById('movieSelection');
            movieSelection.innerHTML = ''; // Clear existing movies
            selectedMovies.clear(); // Clear selection state

            data.forEach(movie => {
                const movieDiv = document.createElement('div');
                movieDiv.classList.add('movie-card');
                movieDiv.setAttribute('data-movie-title', movie.original_title);

                movieDiv.innerHTML = `
                    <img src="${movie.poster_url}" alt="${movie.original_title}" class="poster clickable">
                    <h3 class="movie-title">${movie.original_title}</h3>
                `;

                // Add click event for selection
                movieDiv.addEventListener('click', function () {
                    const movieTitle = movie.original_title;

                    if (selectedMovies.has(movieTitle)) {
                        selectedMovies.delete(movieTitle);
                        movieDiv.classList.remove('selected');
                    } else {
                        selectedMovies.add(movieTitle);
                        movieDiv.classList.add('selected');
                    }
                });

                movieSelection.appendChild(movieDiv);
            });
        })
        .catch(error => {
            console.error('Error fetching movies:', error);
        });
    }

    // Search for a specific movie
    document.getElementById('searchButton').addEventListener('click', function () {
        const searchInput = document.getElementById('searchMovie').value.trim();

        if (!searchInput) {
            alert('Please enter a movie name.');
            return;
        }

        isSearchMode = true; // Enter search mode
        selectedMovies.clear(); // Clear selection state

        fetch('/recommend', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ searched_movie: searchInput }),
        })
        .then(response => response.json())
        .then(data => {
            const recommendationGrid = document.getElementById('recommendationGrid');
            recommendationGrid.innerHTML = ''; // Clear previous recommendations
            const movieSelection = document.getElementById('movieSelection');
            movieSelection.innerHTML = ''; // Clear movie grid

            if (data.error) {
                recommendationGrid.innerHTML = `<p>${data.error}</p>`;
            } else {
                // Display search recommendations in the recommendation section
                data.forEach(movie => {
                    const movieDiv = document.createElement('div');
                    movieDiv.classList.add('movie-card');

                    movieDiv.innerHTML = `
                        <img src="${movie.poster_url}" alt="${movie.original_title}" class="poster">
                        <h3 class="movie-title">${movie.original_title}</h3>
                        <p><strong>Rating:</strong> ${movie.vote_average}</p>
                        <p><strong>Release Year:</strong> ${movie.release_year}</p>
                        <p>${movie.overview}</p>
                    `;

                    recommendationGrid.appendChild(movieDiv);
                });
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });

    // Fetch recommendations for selected movies
    document.getElementById('getRecommendations').addEventListener('click', function () {
        if (isSearchMode) {
            alert('Recommendations are already shown for the searched movie. Shuffle or clear to select movies.');
            return;
        }

        if (selectedMovies.size === 0) {
            alert('Please select at least one movie.');
            return;
        }

        fetch('/recommend', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ selected_movies: Array.from(selectedMovies) }),
        })
        .then(response => response.json())
        .then(data => {
            const recommendationGrid = document.getElementById('recommendationGrid');
            recommendationGrid.innerHTML = ''; // Clear previous recommendations

            if (data.error) {
                recommendationGrid.innerHTML = `<p>${data.error}</p>`;
            } else {
                data.forEach(movie => {
                    const movieDiv = document.createElement('div');
                    movieDiv.classList.add('movie-card');

                    movieDiv.innerHTML = `
                        <img src="${movie.poster_url}" alt="${movie.original_title}" class="poster">
                        <h3 class="movie-title">${movie.original_title}</h3>
                        <p><strong>Rating:</strong> ${movie.vote_average}</p>
                        <p><strong>Release Year:</strong> ${movie.release_year}</p>
                        <p>${movie.overview}</p>
                    `;

                    recommendationGrid.appendChild(movieDiv);
                });
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });
});
