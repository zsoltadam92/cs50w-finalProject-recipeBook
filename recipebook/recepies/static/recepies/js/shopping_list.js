window.toggleStrikethrough = function(checkbox) {
    const listItem = checkbox.nextElementSibling;
    if (checkbox.checked) {
        listItem.style.textDecoration = 'line-through';
        listItem.style.color = '#999';
    } else {
        listItem.style.textDecoration = 'none';
        listItem.style.color = '#333';
    }
}

window.deleteListItem = function(itemId) {
    fetch(`/delete-list-item/${itemId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            document.getElementById(`item-${itemId}`).remove();
            updateEmptyMessage();

            const cartCountElement = document.querySelector('.nav-item .badge');
            if (cartCountElement) {
                cartCountElement.textContent = data.shopping_list_items_count;
            }
        } else {
            alert('Hiba történt a törlés során.');
        }
    })
    .catch(error => console.error('Hiba:', error));
}


function updateEmptyMessage() {
const list = document.getElementById('shoppingList');
if (list.children.length === 0) {
    list.innerHTML = '<li class="justify-content-center"> The list is empty</li>';
}
}

function getCookie(name) {
let cookieValue = null;
if (document.cookie && document.cookie !== '') {
  const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
            break;
        }
    }
}
return cookieValue;
}
