function toggleTheme() {
  document.body.classList.toggle('light');
  localStorage.setItem('nw_theme', document.body.classList.contains('light') ? 'light' : 'dark');
}
if (localStorage.getItem('nw_theme') === 'light') { document.body.classList.add('light'); }
