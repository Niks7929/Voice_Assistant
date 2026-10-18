// Theme switcher (Light/Dark Mode Manager)
(function() {
    const themeToggleBtn = document.getElementById('theme-toggle-btn');
    
    function getPreferredTheme() {
        const savedTheme = localStorage.getItem('vocalis_theme');
        if (savedTheme) {
            return savedTheme;
        }
        return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }

    function applyTheme(theme) {
        if (theme === 'dark') {
            document.documentElement.classList.add('dark');
        } else {
            document.documentElement.classList.remove('dark');
        }
        localStorage.setItem('vocalis_theme', theme);
    }

    // Initial load
    applyTheme(getPreferredTheme());

    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', () => {
            const isDark = document.documentElement.classList.contains('dark');
            applyTheme(isDark ? 'light' : 'dark');
        });
    }
})();
