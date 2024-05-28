function toggleFridge() {
  const image = document.getElementById("fridgeImage");
  const content = document.getElementById("fridgeContent");
  if (image.src.match("closed_fridge")) {
      image.src = "/static/recepies/images/open_fridge.jpg";
      image.alt = "Open Fridge";
      content.style.display = "block";
  } else {
      image.src = "/static/recepies/images/closed_fridge.jpg";
      image.alt = "Closed Fridge";
      content.style.display = "none";
  }
}

document.addEventListener("DOMContentLoaded", function() {
  if (submitted) {
      window.scrollTo({
          top: document.getElementById('recipes-section').offsetTop,
          behavior: 'smooth'
      });
  }
});
