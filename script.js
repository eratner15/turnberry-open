// Simple poster data for t-shirt designs
const posterData = [
    { year: 1965, era: 'vintage', title: 'Turnberry Open 1965', description: 'Classic inaugural tournament design' },
    { year: 1975, era: 'vintage', title: 'Turnberry Open 1975', description: 'Mid-70s geometric design' },
    { year: 1986, era: 'vintage', title: 'Turnberry Open 1986', description: 'Golden era tournament poster' },
    { year: 1994, era: 'modern', title: 'Turnberry Open 1994', description: 'Modern minimalist approach' },
    { year: 1995, era: 'modern', title: 'Turnberry Open 1995', description: 'Bold 90s championship design' },
    { year: 1998, era: 'modern', title: 'Turnberry Open 1998', description: 'Refined late 90s aesthetic' },
    { year: 2001, era: 'modern', title: 'Turnberry Open 2001', description: 'New millennium celebration' },
    { year: 2002, era: 'modern', title: 'Turnberry Open 2002', description: 'Digital age elegance' },
    { year: 2003, era: 'modern', title: 'Turnberry Open 2003', description: 'Championship refinement' },
    { year: 2004, era: 'modern', title: 'Turnberry Open 2004', description: 'Dynamic movement design' },
    { year: 2005, era: 'modern', title: 'Turnberry Open 2005', description: 'Sophisticated excellence' },
    { year: 2008, era: 'modern', title: 'Turnberry Open 2008', description: 'Resilient legacy design' },
    { year: 2009, era: 'modern', title: 'Turnberry Open 2009', description: 'Timeless principles' },
    { year: 2010, era: 'modern', title: 'Turnberry Open 2010', description: 'Decade transition design' },
    { year: 2011, era: 'modern', title: 'Turnberry Open 2011', description: 'Contemporary artistry' },
    { year: 2012, era: 'modern', title: 'Turnberry Open 2012', description: 'Olympic year inspiration' },
    { year: 2016, era: 'contemporary', title: 'Turnberry Open 2016', description: 'Modern championship design' },
    { year: 2017, era: 'contemporary', title: 'Turnberry Open 2017', description: 'Contemporary excellence' },
    { year: 2018, era: 'contemporary', title: 'Turnberry Open 2018', description: 'Dynamic modern aesthetic' },
    { year: 2019, era: 'contemporary', title: 'Turnberry Open 2019', description: 'Bold contemporary vision' },
    { year: 2020, era: 'contemporary', title: 'Turnberry Open 2020', description: 'Resilient tournament spirit' },
    { year: 2021, era: 'contemporary', title: 'Turnberry Open 2021', description: 'Return to excellence' },
    { year: 2022, era: 'contemporary', title: 'Turnberry Open 2022', description: 'Modern heritage celebration' },
    { year: 2023, era: 'contemporary', title: 'Turnberry Open 2023', description: 'Modern luxury heritage' },
    { year: 2024, era: 'contemporary', title: 'Turnberry Open 2024', description: 'Championship present' },
    { year: 2025, era: 'contemporary', title: 'Turnberry Open 2025', description: 'Future vision design' }
];

// Application state
let currentFilter = 'all';
let isLoading = false;
let imageLoadErrors = new Set();
let loadingProgress = 0;

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    // Show loading screen
    showLoadingScreen();
    
    // Initialize all components
    setTimeout(() => {
        initializeNavigation();
        initializeCollectionGrid();
        initializeFilters();
        initializeScrollAnimations();
        initializeIntersectionObserver();
        initializeLazyLoading();
        initializeErrorHandling();
        
        // Hide loading screen after initialization
        setTimeout(() => {
            hideLoadingScreen();
        }, 2000);
    }, 500);
}

function showLoadingScreen() {
    const loadingScreen = document.getElementById('loading-screen');
    if (loadingScreen) {
        loadingScreen.classList.remove('hidden');
    }
}

function hideLoadingScreen() {
    const loadingScreen = document.getElementById('loading-screen');
    if (loadingScreen) {
        loadingScreen.classList.add('hidden');
        setTimeout(() => {
            loadingScreen.remove();
        }, 500);
    }
}

function initializeNavigation() {
    const navbar = document.querySelector('.navbar');
    const hamburger = document.querySelector('.nav-hamburger');
    const navMenu = document.querySelector('.nav-menu');
    const navLinks = document.querySelectorAll('.nav-link');
    
    // Navbar scroll effect
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });
    
    // Mobile menu toggle
    if (hamburger && navMenu) {
        hamburger.addEventListener('click', () => {
            navMenu.classList.toggle('active');
            hamburger.classList.toggle('active');
        });
    }
    
    // Close menu when clicking on a link
    navLinks.forEach(link => {
        link.addEventListener('click', () => {
            navMenu.classList.remove('active');
            hamburger.classList.remove('active');
        });
    });
    
    // Smooth scrolling for navigation links
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const target = document.querySelector(link.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });
}

function initializeCollectionGrid() {
    const collectionGrid = document.getElementById('collectionGrid');
    if (!collectionGrid) return;
    
    // Clear existing content
    collectionGrid.innerHTML = '';
    
    // Generate poster cards
    posterData.forEach((poster, index) => {
        const card = createPosterCard(poster, index);
        collectionGrid.appendChild(card);
    });
}

function createPosterCard(poster, index) {
    const card = document.createElement('div');
    card.className = `poster-card fade-in ${poster.era}`;
    card.dataset.era = poster.era;
    card.dataset.year = poster.year;
    
    // Create image with error handling - handle both PNG and WebP formats
    const imageExt = (poster.year >= 2016 && poster.year <= 2022) ? 'png' : 'webp';
    const imageUrl = `assets/images/${poster.year}.${imageExt}`;
    
    card.innerHTML = `
        <div class="poster-image-container">
            <img 
                src="${imageUrl}" 
                alt="${poster.title}" 
                class="poster-image"
                loading="lazy"
                onerror="handleImageError(this, ${poster.year})"
            >
            <div class="poster-overlay">
                <h3>${poster.title}</h3>
                <p class="poster-story">${poster.description}</p>
            </div>
        </div>
        <div class="poster-info">
            <div class="poster-year">${poster.year}</div>
            <div class="poster-era">${getEraLabel(poster.era)}</div>
            <div class="poster-title">${poster.title}</div>
            <div class="poster-description">${poster.description}</div>
        </div>
    `;
    
    // Add click event for modal
    card.addEventListener('click', () => {
        showPosterModal(poster);
    });
    
    return card;
}

function getEraLabel(era) {
    const labels = {
        'vintage': 'Classic Era',
        'modern': 'Modern Era',
        'contemporary': 'Contemporary Era'
    };
    return labels[era] || era;
}

function handleImageError(img, year) {
    // Track failed images
    imageLoadErrors.add(year);
    
    // Create placeholder
    const placeholder = document.createElement('div');
    placeholder.className = 'poster-placeholder';
    placeholder.innerHTML = `
        <div class="placeholder-content">
            <div class="placeholder-year">${year}</div>
            <div class="placeholder-text">Image Loading</div>
        </div>
    `;
    
    // Replace image with placeholder
    img.parentNode.replaceChild(placeholder, img);
    
    // Retry loading after delay
    setTimeout(() => {
        retryImageLoad(placeholder, year);
    }, 2000);
}

function retryImageLoad(placeholder, year) {
    const img = document.createElement('img');
    const imageExt = (year >= 2016 && year <= 2022) ? 'png' : 'webp';
    img.src = `assets/images/${year}.${imageExt}`;
    img.alt = `Turnberry Open ${year}`;
    img.className = 'poster-image';
    img.loading = 'lazy';
    
    img.onload = () => {
        placeholder.parentNode.replaceChild(img, placeholder);
        imageLoadErrors.delete(year);
    };
    
    img.onerror = () => {
        // After retry fails, show permanent placeholder
        placeholder.classList.add('error');
        placeholder.innerHTML = `
            <div class="placeholder-content">
                <div class="placeholder-year">${year}</div>
                <div class="placeholder-text">Image Unavailable</div>
            </div>
        `;
    };
}

function initializeFilters() {
    const filterButtons = document.querySelectorAll('.filter-btn');
    
    filterButtons.forEach(button => {
        button.addEventListener('click', () => {
            const filter = button.dataset.filter;
            setActiveFilter(button, filter);
            filterCollection(filter);
        });
    });
}

function setActiveFilter(activeButton, filter) {
    // Update button states
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.remove('active');
        btn.setAttribute('aria-pressed', 'false');
    });
    
    activeButton.classList.add('active');
    activeButton.setAttribute('aria-pressed', 'true');
    currentFilter = filter;
}

function filterCollection(filter) {
    const cards = document.querySelectorAll('.poster-card');
    
    cards.forEach((card, index) => {
        const cardEra = card.dataset.era;
        const shouldShow = filter === 'all' || cardEra === filter;
        
        if (shouldShow) {
            card.style.display = 'block';
            // Staggered animation
            setTimeout(() => {
                card.classList.add('visible');
            }, index * 100);
        } else {
            card.style.display = 'none';
            card.classList.remove('visible');
        }
    });
}

function showPosterModal(poster) {
    const modal = document.createElement('div');
    modal.className = 'poster-modal';
    modal.innerHTML = `
        <div class="modal-backdrop" onclick="closePosterModal()">
            <div class="modal-content" onclick="event.stopPropagation()">
                <button class="modal-close" onclick="closePosterModal()" aria-label="Close modal">&times;</button>
                <div class="modal-image">
                    <img 
                        src="assets/images/${poster.year}.${(poster.year >= 2016 && poster.year <= 2022) ? 'png' : 'webp'}" 
                        alt="${poster.title}"
                        onerror="this.style.display='none'"
                    >
                </div>
                <div class="modal-info">
                    <div class="modal-header">
                        <h2>${poster.title}</h2>
                        <div class="modal-year">${poster.year}</div>
                        <div class="modal-era">${getEraLabel(poster.era)}</div>
                    </div>
                    
                    <div class="modal-description">
                        <p>${poster.description}</p>
                    </div>
                    
                    <div class="modal-actions">
                        <button class="btn btn-primary" onclick="closePosterModal()">Close</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Add modal styles
    addModalStyles();
    
    document.body.appendChild(modal);
    document.body.style.overflow = 'hidden';
    
    // Focus management for accessibility
    modal.querySelector('.modal-close').focus();
}

function closePosterModal() {
    const modal = document.querySelector('.poster-modal');
    if (modal) {
        modal.remove();
        document.body.style.overflow = 'auto';
    }
}


function addModalStyles() {
    if (document.querySelector('#modal-styles')) return;
    
    const styles = `
        .poster-modal {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 2000;
            animation: fadeIn 0.3s ease;
        }
        
        .modal-backdrop {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(46, 46, 46, 0.9);
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
            overflow-y: auto;
        }
        
        .modal-content {
            background: var(--warm-white);
            border-radius: var(--border-radius);
            max-width: 900px;
            width: 100%;
            max-height: 90vh;
            overflow-y: auto;
            position: relative;
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            padding: 30px;
            box-shadow: var(--shadow-strong);
        }
        
        .modal-close {
            position: absolute;
            top: 15px;
            right: 15px;
            background: none;
            border: none;
            font-size: 24px;
            color: var(--text-light);
            cursor: pointer;
            z-index: 1;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: var(--transition);
        }
        
        .modal-close:hover {
            background: var(--heritage-cream);
            color: var(--text-dark);
        }
        
        .modal-image {
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .modal-image img {
            max-width: 100%;
            max-height: 400px;
            object-fit: contain;
            border-radius: var(--border-radius);
            box-shadow: var(--shadow-medium);
        }
        
        .modal-info {
            display: flex;
            flex-direction: column;
            gap: 20px;
        }
        
        .modal-header {
            border-bottom: 2px solid var(--heritage-cream);
            padding-bottom: 20px;
        }
        
        .modal-header h2 {
            color: var(--golf-green);
            margin-bottom: 10px;
        }
        
        .modal-year {
            font-size: 1.2rem;
            font-weight: 700;
            color: var(--club-gold);
            margin-bottom: 5px;
        }
        
        .modal-era {
            font-size: 0.9rem;
            color: var(--text-light);
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 10px;
        }
        
        .rarity-badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .rarity-badge.extremely-rare {
            background: #FFD700;
            color: #1A1A1A;
        }
        
        .rarity-badge.very-rare {
            background: #FF6B6B;
            color: white;
        }
        
        .rarity-badge.rare {
            background: #4ECDC4;
            color: white;
        }
        
        .rarity-badge.scarce {
            background: #45B7D1;
            color: white;
        }
        
        .rarity-badge.limited {
            background: #96CEB4;
            color: #1A1A1A;
        }
        
        .rarity-badge.available {
            background: #FFEAA7;
            color: #1A1A1A;
        }
        
        .rarity-badge.current {
            background: var(--golf-green);
            color: white;
        }
        
        .modal-description p {
            color: var(--text-light);
            line-height: 1.6;
            font-size: 1.1rem;
        }
        
        .modal-actions {
            display: flex;
            gap: 15px;
            padding-top: 20px;
            border-top: 2px solid var(--heritage-cream);
        }
        
        .poster-placeholder {
            width: 100%;
            height: 350px;
            background: var(--heritage-cream);
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: var(--border-radius);
            border: 2px dashed var(--border-light);
        }
        
        .poster-placeholder.error {
            border-color: var(--error-red);
            background: rgba(229, 62, 62, 0.1);
        }
        
        .placeholder-content {
            text-align: center;
            color: var(--text-light);
        }
        
        .placeholder-year {
            font-size: 2rem;
            font-weight: 700;
            color: var(--golf-green);
            margin-bottom: 10px;
        }
        
        .placeholder-text {
            font-size: 0.9rem;
        }
        
        @media (max-width: 768px) {
            .modal-content {
                grid-template-columns: 1fr;
                padding: 20px;
                margin: 10px;
            }
            
            .modal-actions {
                flex-direction: column;
            }
        }
        
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
    `;
    
    const styleSheet = document.createElement('style');
    styleSheet.id = 'modal-styles';
    styleSheet.textContent = styles;
    document.head.appendChild(styleSheet);
}


function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <span class="notification-message">${message}</span>
            <button class="notification-close" onclick="this.parentElement.parentElement.remove()">&times;</button>
        </div>
    `;
    
    // Add notification styles if not present
    if (!document.querySelector('#notification-styles')) {
        const styles = `
            .notification {
                position: fixed;
                top: 20px;
                right: 20px;
                max-width: 400px;
                z-index: 3000;
                animation: slideInRight 0.3s ease;
            }
            
            .notification-content {
                background: var(--warm-white);
                border-radius: var(--border-radius);
                padding: 15px 20px;
                box-shadow: var(--shadow-medium);
                display: flex;
                align-items: center;
                gap: 10px;
                border-left: 4px solid var(--golf-green);
            }
            
            .notification.success .notification-content {
                border-left-color: var(--success-green);
            }
            
            .notification.error .notification-content {
                border-left-color: var(--error-red);
            }
            
            .notification-message {
                flex: 1;
                color: var(--text-dark);
                font-size: 14px;
            }
            
            .notification-close {
                background: none;
                border: none;
                font-size: 18px;
                color: var(--text-light);
                cursor: pointer;
                padding: 0;
                width: 20px;
                height: 20px;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            
            .notification-close:hover {
                color: var(--text-dark);
            }
            
            @keyframes slideInRight {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
        `;
        
        const styleSheet = document.createElement('style');
        styleSheet.id = 'notification-styles';
        styleSheet.textContent = styles;
        document.head.appendChild(styleSheet);
    }
    
    document.body.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 5000);
}

function initializeScrollAnimations() {
    // Hero button smooth scroll
    const heroButton = document.querySelector('.hero-actions .btn-primary');
    if (heroButton) {
        heroButton.addEventListener('click', (e) => {
            e.preventDefault();
            document.getElementById('collection').scrollIntoView({ behavior: 'smooth' });
        });
    }
}

function initializeIntersectionObserver() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, observerOptions);
    
    // Observe all fade-in elements
    document.querySelectorAll('.fade-in').forEach(el => {
        observer.observe(el);
    });
}

function initializeLazyLoading() {
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    if (img.dataset.src) {
                        img.src = img.dataset.src;
                        img.removeAttribute('data-src');
                    }
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
                }
            });
        });
        
        document.querySelectorAll('img[loading="lazy"]').forEach(img => {
            imageObserver.observe(img);
        });
    }
}

function initializeErrorHandling() {
    // Global error handler
    window.addEventListener('error', (e) => {
        console.error('Global error:', e.error);
        
        // Don't show notifications for image errors - they're handled separately
        if (e.target.tagName === 'IMG') {
            return;
        }
        
        // Show user-friendly error message for other errors
        showNotification('Something went wrong. Please refresh the page if problems persist.', 'error');
    });
    
    // Unhandled promise rejection handler
    window.addEventListener('unhandledrejection', (e) => {
        console.error('Unhandled promise rejection:', e.reason);
        showNotification('An unexpected error occurred. Please try again.', 'error');
    });
}

// Global functions for inline event handlers
window.closePosterModal = closePosterModal;
window.handleImageError = handleImageError;

// Utility function to add new posters (for future use)
function addNewPoster(year, era, title, description) {
    const newPoster = {
        year,
        era,
        title,
        description
    };
    
    posterData.push(newPoster);
    posterData.sort((a, b) => a.year - b.year);
    
    // Regenerate the collection
    initializeCollectionGrid();
    initializeIntersectionObserver();
    
    console.log(`Added poster for ${year}: ${title}`);
}

// Make addNewPoster available globally
window.addNewPoster = addNewPoster;