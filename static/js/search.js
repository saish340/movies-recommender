document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const searchInput = document.getElementById('searchInput');
    const suggestions = document.getElementById('suggestions');
    
    // Variables
    let timeout = null;
    let currentFocus = -1;
    let suggestionItems = [];
    
    // Show loading indicator during search
    function showLoadingIndicator() {
        suggestions.innerHTML = '';
        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'suggestion-item loading-indicator';
        loadingDiv.innerHTML = '<div class="spinner-border spinner-border-sm text-primary me-2" role="status"></div> Searching...';
        suggestions.appendChild(loadingDiv);
        suggestions.style.display = 'block';
    }

    // Handle input event for search suggestions
    searchInput.addEventListener('input', function() {
        clearTimeout(timeout);
        const query = this.value.trim();
        
        if (query.length < 2) {
            suggestions.style.display = 'none';
            return;
        }
        
        // Reset current focus
        currentFocus = -1;
        
        // Show loading after a tiny delay to prevent flickering for fast typing
        timeout = setTimeout(() => {
            showLoadingIndicator();
            
            // Fetch search results
            fetch(`/search?q=${encodeURIComponent(query)}`)
                .then(res => res.text())
                .then(html => {
                    const parser = new DOMParser();
                    const doc = parser.parseFromString(html, 'text/html');
                    const movieCards = doc.querySelectorAll('.movie-card');
                    
                    // Clear suggestions
                    suggestions.innerHTML = '';
                    suggestionItems = [];
                    
                    if (movieCards.length === 0) {
                        // Show no results message
                        const noResults = document.createElement('div');
                        noResults.className = 'suggestion-item no-results';
                        noResults.innerHTML = '<i class="fas fa-search me-2"></i> No movies found';
                        suggestions.appendChild(noResults);
                        suggestions.style.display = 'block';
                        return;
                    }
                    
                    // Add suggestions with enhanced data
                    movieCards.forEach((card, index) => {
                        if (index >= 5) return; // Limit to 5 suggestions
                        
                        const title = card.querySelector('.movie-caption h5').textContent;
                        const year = card.querySelector('.movie-year')?.textContent || '';
                        const posterUrl = card.querySelector('img').getAttribute('src');
                        const movieId = card.querySelector('a').getAttribute('href').split('/').pop();
                        
                        const item = document.createElement('div');
                        item.className = 'suggestion-item';
                        item.innerHTML = `
                            <div class="d-flex align-items-center">
                                <div class="suggestion-poster me-3">
                                    <img src="${posterUrl}" alt="${title}" width="40" height="60">
                                </div>
                                <div>
                                    <div class="suggestion-title">${title}</div>
                                    <div class="suggestion-year">${year}</div>
                                </div>
                            </div>
                        `;
                        
                        item.addEventListener('click', () => {
                            window.location.href = `/movie/${movieId}`;
                        });
                        
                        item.addEventListener('mouseenter', () => {
                            removeActiveSuggestion();
                            item.classList.add('active');
                            currentFocus = suggestionItems.indexOf(item);
                        });
                        
                        suggestions.appendChild(item);
                        suggestionItems.push(item);
                    });
                    
                    // Display suggestions with animation
                    suggestions.style.opacity = '0';
                    suggestions.style.display = 'block';
                    setTimeout(() => {
                        suggestions.style.opacity = '1';
                        suggestions.style.transition = 'opacity 0.3s ease';
                    }, 10);
                })
                .catch(error => {
                    console.error('Error fetching search suggestions:', error);
                    suggestions.innerHTML = '';
                    const errorItem = document.createElement('div');
                    errorItem.className = 'suggestion-item error';
                    errorItem.textContent = 'Error fetching results';
                    suggestions.appendChild(errorItem);
                });
        }, 300);
    });
    
    // Remove active class from all suggestion items
    function removeActiveSuggestion() {
        suggestionItems.forEach(item => {
            item.classList.remove('active');
        });
    }
    
    // Handle keyboard navigation
    searchInput.addEventListener('keydown', function(e) {
        if (suggestions.style.display === 'none' || suggestionItems.length === 0) return;
        
        // Down arrow
        if (e.keyCode === 40) {
            currentFocus++;
            currentFocus = Math.min(currentFocus, suggestionItems.length - 1);
            removeActiveSuggestion();
            suggestionItems[currentFocus].classList.add('active');
            suggestionItems[currentFocus].scrollIntoView({ block: 'nearest' });
            e.preventDefault();
        }
        // Up arrow
        else if (e.keyCode === 38) {
            currentFocus--;
            currentFocus = Math.max(currentFocus, 0);
            removeActiveSuggestion();
            suggestionItems[currentFocus].classList.add('active');
            suggestionItems[currentFocus].scrollIntoView({ block: 'nearest' });
            e.preventDefault();
        }
        // Enter key
        else if (e.keyCode === 13 && currentFocus > -1) {
            e.preventDefault();
            suggestionItems[currentFocus].click();
        }
        // Escape key
        else if (e.keyCode === 27) {
            suggestions.style.display = 'none';
        }
    });
    
    // Close suggestions on click outside
    document.addEventListener('click', function(e) {
        if (!suggestions.contains(e.target) && e.target !== searchInput) {
            suggestions.style.display = 'none';
        }
    });
    
    // Fade in animation for movie cards
    function animateMovieCards() {
        const movieCards = document.querySelectorAll('.movie-card');
        movieCards.forEach((card, index) => {
            card.style.opacity = '0';
            card.style.animation = `fadeIn 0.5s ease forwards ${index * 0.1}s`;
        });
    }
    
    // Run animation on page load
    if (document.querySelector('.movie-section')) {
        animateMovieCards();
    }
});
