const tg = window.Telegram.WebApp;
tg.expand();

// Навигация
document.querySelectorAll('.nav-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        // Убираем активный класс у всех
        document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
        
        // Добавляем активный класс
        btn.classList.add('active');
        document.getElementById(btn.dataset.section).classList.add('active');
        
        // Haptic feedback
        tg.HapticFeedback.impactOccurred('light');
        
        // Scroll to top
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });
});

// Готово
tg.ready();