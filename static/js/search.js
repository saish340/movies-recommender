document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('searchInput');
    const suggestions = document.getElementById('suggestions');
    let timeout = null;

    searchInput.addEventListener('input', function() {
        clearTimeout(timeout);
        const query = this.value.trim();
        if (query.length < 2) {
            suggestions.style.display = 'none';
            return;
        }
        timeout = setTimeout(() => {
            fetch(`/search?q=${encodeURIComponent(query)}`)
                .then(res => res.text())
                .then(html => {
                    const parser = new DOMParser();
                    const doc = parser.parseFromString(html, 'text/html');
                    const movieCards = doc.querySelectorAll('.movie-card');
                    suggestions.innerHTML = '';
                    movieCards.forEach(card => {
                        const title = card.querySelector('.card-title').textContent;
                        const item = document.createElement('div');
                        item.className = 'suggestion-item';
                        item.textContent = title;
                        item.onclick = () => {
                            searchInput.value = title;
                            suggestions.style.display = 'none';
                        };
                        suggestions.appendChild(item);
                    });
                    suggestions.style.display = movieCards.length ? 'block' : 'none';
                });
        }, 300);
    });

    document.addEventListener('click', function(e) {
        if (!suggestions.contains(e.target) && e.target !== searchInput) {
            suggestions.style.display = 'none';
        }
    });
});
