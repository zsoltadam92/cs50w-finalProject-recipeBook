function toggleFavorite(recipeId) {
  const csrfToken = getCookie('csrftoken');
  fetch(`/add-to-favorites/${recipeId}/`, {
      method: 'POST',
      headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken
      },
      body: JSON.stringify({})
  })
  .then(response => response.json())
  .then(data => {
      if (data.success) {
          const btn = document.getElementById('favorite-btn');
          const icon = btn.querySelector('i');
          btn.classList.toggle('btn-transparent');
          btn.classList.toggle('btn-danger');
          icon.classList.toggle('bi-heart');
          icon.classList.toggle('bi-heart-fill');
      }
  })
  .catch(error => console.error('Error:', error));
}
