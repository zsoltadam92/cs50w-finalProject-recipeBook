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

function toggleClass(element, className, condition) {
  condition ? element.classList.add(className) : element.classList.remove(className);
}

function toggleStrikethrough(checkbox) {
  const textElement = checkbox.nextElementSibling.nextElementSibling;
  toggleClass(textElement, 'strikethrough', checkbox.checked);
}

document.addEventListener('DOMContentLoaded', function() {
  const urlParams = new URLSearchParams(window.location.search);
  if (urlParams.has('submitted')) {
      document.getElementById('scroll-bottom').scrollIntoView({
          behavior: 'smooth'
      });
  }
});

document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function(e) {
      e.preventDefault();

      const targetId = this.getAttribute('href').substring(1); // remove the '#' character
        const targetElement = document.getElementById(targetId);
        
        if (targetElement) {
            targetElement.scrollIntoView({
                behavior: 'smooth'
            });
        }
  });
});

document.querySelectorAll('.rating label').forEach(label => {
  label.addEventListener('click', () => {
      document.querySelectorAll('.rating label').forEach(innerLabel => {
          innerLabel.style.color = 'grey';
      });

      let currentLabel = label;
      while (currentLabel) {
          currentLabel.style.color = 'gold';
          currentLabel = currentLabel.previousElementSibling ? currentLabel.previousElementSibling.previousElementSibling : null;
      }
  });
});
