/* UI Micro-interactions & Mobile Menu Toggle */

document.addEventListener('DOMContentLoaded', () => {
  const toggleBtn = document.getElementById('mobileNavToggle');
  const navLinks = document.getElementById('navLinks');

  if (toggleBtn && navLinks) {
    toggleBtn.addEventListener('click', () => {
      navLinks.classList.toggle('show');
    });
  }
});
