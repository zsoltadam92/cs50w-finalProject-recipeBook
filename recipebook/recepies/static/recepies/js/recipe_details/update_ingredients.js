function updateIngredients() {
  const originalServings = parseInt(document.getElementById('original-servings').value);
  const newServings = parseInt(document.getElementById('new-servings').value);

  if (isNaN(originalServings) || isNaN(newServings) || originalServings <= 0 || newServings <= 0) {
      alert('Please enter valid servings.');
      return;
  }

  const scale = newServings / originalServings;

  document.querySelectorAll('.ingredient-quantity').forEach(function(item) {
      const originalQuantity = parseFloat(item.dataset.originalQuantity.replace(',', '.'));

      if (!isNaN(originalQuantity)) {
          let scaledQuantity = (originalQuantity * scale).toFixed(2);

          if (scaledQuantity.endsWith('.00')) {
              scaledQuantity = parseInt(scaledQuantity, 10).toString();
          } else if (scaledQuantity.endsWith('0')) {
              scaledQuantity = scaledQuantity.slice(0, -1);
          }

          item.textContent = scaledQuantity;
      } else {
          item.textContent = "Error";
      }
  });
}
