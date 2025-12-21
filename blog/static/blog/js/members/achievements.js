/**
 * 成就徽章頁面互動功能
 */

document.addEventListener('DOMContentLoaded', function() {
    initAchievementCards();
    initModal();
    initAnimations();
});

/**
 * 初始化成就卡片互動
 */
function initAchievementCards() {
    const achievementCards = document.querySelectorAll('.achievement-card');

    achievementCards.forEach(card => {
        // 點擊卡片顯示詳細資訊
        card.addEventListener('click', function() {
            const achievementId = this.dataset.achievementId;
            const icon = this.querySelector('.achievement-icon').textContent.trim();
            const name = this.querySelector('.achievement-name').textContent;
            const desc = this.querySelector('.achievement-desc').textContent;
            const isUnlocked = this.classList.contains('unlocked');

            // 取得分類
            const categorySection = this.closest('.category-section');
            const category = categorySection ? categorySection.querySelector('.category-title').textContent : '';

            // 取得積分
            const pointsElement = this.querySelector('.achievement-points');
            const points = pointsElement ? pointsElement.textContent : '';

            showAchievementModal({
                id: achievementId,
                icon: icon,
                name: name,
                description: desc,
                category: category,
                points: points,
                isUnlocked: isUnlocked
            });
        });

        // 滑鼠懸停效果增強
        if (card.classList.contains('unlocked')) {
            card.addEventListener('mouseenter', function() {
                this.style.transform = 'translateY(-8px) scale(1.02)';
            });

            card.addEventListener('mouseleave', function() {
                this.style.transform = 'translateY(-4px) scale(1)';
            });
        }
    });
}

/**
 * 初始化模態框
 */
function initModal() {
    const modal = document.getElementById('achievement-modal');
    if (!modal) return;

    const closeBtn = modal.querySelector('.modal-close');
    const overlay = modal.querySelector('.modal-overlay');

    // 關閉按鈕
    if (closeBtn) {
        closeBtn.addEventListener('click', function() {
            hideModal();
        });
    }

    // 點擊遮罩關閉
    if (overlay) {
        overlay.addEventListener('click', function() {
            hideModal();
        });
    }

    // ESC 鍵關閉
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && modal.style.display !== 'none') {
            hideModal();
        }
    });
}

/**
 * 顯示成就詳細資訊模態框
 */
function showAchievementModal(achievement) {
    const modal = document.getElementById('achievement-modal');
    if (!modal) return;

    // 填充內容
    const modalIcon = modal.querySelector('.modal-icon');
    const modalTitle = modal.querySelector('.modal-title');
    const modalDesc = modal.querySelector('.modal-description');
    const modalCategory = modal.querySelector('.modal-category');
    const modalPoints = modal.querySelector('.modal-points');

    if (modalIcon) modalIcon.textContent = achievement.icon;
    if (modalTitle) modalTitle.textContent = achievement.name;
    if (modalDesc) modalDesc.textContent = achievement.description;
    if (modalCategory) modalCategory.textContent = achievement.category;
    if (modalPoints) modalPoints.textContent = achievement.points;

    // 根據解鎖狀態調整樣式
    if (achievement.isUnlocked) {
        modal.querySelector('.modal-content').style.background =
            'linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%)';
    } else {
        modal.querySelector('.modal-content').style.background = 'white';
    }

    // 顯示模態框
    modal.style.display = 'flex';
    document.body.style.overflow = 'hidden'; // 防止背景滾動
}

/**
 * 隱藏模態框
 */
function hideModal() {
    const modal = document.getElementById('achievement-modal');
    if (!modal) return;

    modal.style.display = 'none';
    document.body.style.overflow = ''; // 恢復滾動
}

/**
 * 初始化動畫效果
 */
function initAnimations() {
    // 頁面載入時的卡片動畫
    const cards = document.querySelectorAll('.achievement-card');

    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach((entry, index) => {
            if (entry.isIntersecting) {
                setTimeout(() => {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }, index * 50); // 延遲效果
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    cards.forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        observer.observe(card);
    });

    // 進度條動畫
    animateProgressBar();
}

/**
 * 進度條動畫
 */
function animateProgressBar() {
    const progressFill = document.querySelector('.overall-progress .progress-fill');
    if (!progressFill) return;

    const targetWidth = progressFill.style.width;
    progressFill.style.width = '0%';

    setTimeout(() => {
        progressFill.style.width = targetWidth;
    }, 300);
}

/**
 * 成就解鎖特效（當用戶解鎖新成就時調用）
 */
function celebrateUnlock(achievementId) {
    const card = document.querySelector(`[data-achievement-id="${achievementId}"]`);
    if (!card) return;

    // 添加解鎖動畫
    card.classList.add('unlocked');
    card.style.animation = 'unlockPop 0.5s ease';

    // 創建慶祝特效
    createConfetti(card);

    // 播放音效（如果需要）
    // playUnlockSound();

    setTimeout(() => {
        card.style.animation = '';
    }, 500);
}

/**
 * 創建五彩紙屑效果
 */
function createConfetti(element) {
    const rect = element.getBoundingClientRect();
    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 2;

    const colors = ['#fbbf24', '#f59e0b', '#dc2626', '#059669', '#3b82f6'];
    const confettiCount = 30;

    for (let i = 0; i < confettiCount; i++) {
        const confetti = document.createElement('div');
        confetti.style.position = 'fixed';
        confetti.style.width = '10px';
        confetti.style.height = '10px';
        confetti.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
        confetti.style.left = centerX + 'px';
        confetti.style.top = centerY + 'px';
        confetti.style.borderRadius = '50%';
        confetti.style.pointerEvents = 'none';
        confetti.style.zIndex = '9999';

        document.body.appendChild(confetti);

        const angle = (Math.PI * 2 * i) / confettiCount;
        const velocity = 100 + Math.random() * 100;
        const vx = Math.cos(angle) * velocity;
        const vy = Math.sin(angle) * velocity - 50;

        animateConfetti(confetti, vx, vy);
    }
}

/**
 * 動畫化五彩紙屑
 */
function animateConfetti(element, vx, vy) {
    let x = 0;
    let y = 0;
    let opacity = 1;
    const gravity = 2;

    function update() {
        x += vx * 0.016;
        y += vy * 0.016;
        vy += gravity;
        opacity -= 0.016;

        element.style.transform = `translate(${x}px, ${y}px)`;
        element.style.opacity = opacity;

        if (opacity > 0) {
            requestAnimationFrame(update);
        } else {
            element.remove();
        }
    }

    requestAnimationFrame(update);
}

/**
 * 篩選成就（可擴展功能）
 */
function filterAchievements(category) {
    const sections = document.querySelectorAll('.category-section');

    sections.forEach(section => {
        const sectionTitle = section.querySelector('.category-title').textContent;

        if (category === 'all' || sectionTitle === category) {
            section.style.display = 'block';
        } else {
            section.style.display = 'none';
        }
    });
}

/**
 * 統計資訊更新
 */
function updateStats() {
    const totalCards = document.querySelectorAll('.achievement-card').length;
    const unlockedCards = document.querySelectorAll('.achievement-card.unlocked').length;
    const percentage = Math.round((unlockedCards / totalCards) * 100);

    // 更新數字顯示
    const totalElement = document.querySelector('.stat-item:nth-child(1) .stat-value');
    const unlockedElement = document.querySelector('.unlock-count');
    const percentageElement = document.querySelector('.stat-item:nth-child(3) .stat-value');

    if (totalElement) totalElement.textContent = totalCards;
    if (unlockedElement) unlockedElement.textContent = unlockedCards;
    if (percentageElement) percentageElement.textContent = percentage + '%';

    // 更新進度條
    const progressFill = document.querySelector('.overall-progress .progress-fill');
    if (progressFill) {
        progressFill.style.width = percentage + '%';
    }
}

// 導出函數供外部使用
window.achievementUtils = {
    celebrateUnlock,
    filterAchievements,
    updateStats
};
