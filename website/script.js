const AppConfig = {
    version: 'v1.0.0',
    versions: ['v1.0.0'], // List all versions here. Add older versions to show the "Previous Versions" section.
    repo: 'yourusername/vbox',
    downloads: {
        rpm: 'https://github.com/yourusername/vbox/releases/download/{version}/vbox-{version}-1.x86_64.rpm',
        appimage: 'https://github.com/yourusername/vbox/releases/download/{version}/VBox-{version}-x86_64.AppImage'
    }
};

document.addEventListener('DOMContentLoaded', () => {
    // Update Version Info
    const updateVersionInfo = () => {
        const versionBadge = document.getElementById('version-badge');
        const rpmLink = document.getElementById('download-rpm');
        const appImageLink = document.getElementById('download-appimage');

        if (versionBadge) {
            versionBadge.textContent = `${AppConfig.version} Released`;
        }

        const cleanVer = AppConfig.version.replace(/^v/, '');

        if (rpmLink) {
            rpmLink.href = AppConfig.downloads.rpm.replace(/{version}/g, AppConfig.version).replace(/{cleanVer}/g, cleanVer);
        }

        if (appImageLink) {
            appImageLink.href = AppConfig.downloads.appimage.replace(/{version}/g, AppConfig.version).replace(/{cleanVer}/g, cleanVer);
        }
    };

    // Render Previous Versions
    const renderPreviousVersions = () => {
        const versionList = document.getElementById('version-list');
        if (!versionList) return;

        // Filter out current version
        const prevVersions = AppConfig.versions.filter(v => v !== AppConfig.version);

        if (prevVersions.length === 0) {
            const container = document.querySelector('.previous-versions');
            if (container) container.style.display = 'none';
            return;
        }

        versionList.innerHTML = prevVersions.map(ver => {
            const cleanVer = ver.replace(/^v/, '');
            const rpmUrl = AppConfig.downloads.rpm.replace(/{version}/g, ver).replace(/{cleanVer}/g, cleanVer);
            const appImageUrl = AppConfig.downloads.appimage.replace(/{version}/g, ver).replace(/{cleanVer}/g, cleanVer);

            return `
                <div class="version-item">
                    <span class="v-tag">${ver}</span>
                    <div class="v-links">
                        <a href="${rpmUrl}" class="v-link"><i data-feather="box"></i> RPM</a>
                        <a href="${appImageUrl}" class="v-link"><i data-feather="layers"></i> AppImage</a>
                    </div>
                </div>
            `;
        }).join('');

        // Re-initialize icons for new elements
        if (typeof feather !== 'undefined') {
            feather.replace();
        }
    };

    // Toggle Previous Versions
    const toggleBtn = document.getElementById('toggle-versions');
    const versionList = document.getElementById('version-list');

    if (toggleBtn && versionList) {
        toggleBtn.addEventListener('click', () => {
            versionList.classList.toggle('hidden');
            toggleBtn.classList.toggle('active');
        });
    }

    updateVersionInfo();
    renderPreviousVersions();

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });

    // Simple entrance animation for elements
    const observerOptions = {
        threshold: 0.1
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    const animatedElements = document.querySelectorAll('.feature-card, .download-box');

    animatedElements.forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'opacity 0.6s ease-out, transform 0.6s ease-out';
        observer.observe(el);
    });

    // Theme Toggle Logic
    const themeToggle = document.querySelector('.theme-toggle');
    const body = document.body;

    // Check local storage
    if (localStorage.getItem('theme') === 'light') {
        body.classList.add('light-mode');
    }

    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            body.classList.toggle('light-mode');

            if (body.classList.contains('light-mode')) {
                localStorage.setItem('theme', 'light');
            } else {
                localStorage.setItem('theme', 'dark');
            }
        });
    }
});
