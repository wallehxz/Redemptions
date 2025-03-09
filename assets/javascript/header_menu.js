
// 切换菜单显示/隐藏
const menuToggle = document.querySelector('.menu-toggle');
const mobileMenu = document.querySelector('.mobile-menu');

menuToggle.addEventListener('click', () => {
  mobileMenu.classList.toggle('active');
});

const hamburgerMenu = document.getElementById('hamburger-menu');
const header = document.querySelector('.header');

hamburgerMenu.addEventListener('click', () => {
  // 切换菜单展开状态
  header.classList.toggle('menu-open');
});