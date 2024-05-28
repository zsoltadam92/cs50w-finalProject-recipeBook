function toggleShoppingList(recipeId, ingredientName, button) {
    let isInList = button.querySelector('i').classList.contains('bi-cart-check-fill');
    let encodedIngredientName = encodeURIComponent(ingredientName);

    let url = isInList 
        ? `/remove-from-shopping-list/${recipeId}/${encodedIngredientName}/` 
        : `/add-to-shopping-list/${recipeId}/${encodedIngredientName}/`;

    fetch(url, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ingredientName: ingredientName, 'action': isInList ? 'remove' : 'add'})
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        if (data.status === 'success') {
            if (isInList) {
                button.innerHTML = '<i class="bi bi-cart4"></i>';
                button.classList.remove("btn-success");
                button.classList.add("btn-info");
            } else {
                button.innerHTML = '<i class="bi bi-cart-check-fill"></i>';
                button.classList.remove("btn-info");
                button.classList.add("btn-success");
            }

            // Update the cart item count
            const cartCountElement = document.querySelector('.nav-item .badge');
            if (cartCountElement) {
                cartCountElement.textContent = data.shopping_list_items_count;
            }
        } else if (data.status === 'exists') {
            alert('Ingredient is already in the shopping list');
        } else {
            alert(data.message);
        }
    })
    .catch(error => console.error('Error:', error));
}

