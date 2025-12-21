// 活動頁面篩選功能
document.addEventListener('DOMContentLoaded', function () {
    const filterTabs = document.querySelectorAll('.filter-tab');
    const activityCards = document.querySelectorAll('.activity-card');

    filterTabs.forEach(tab => {
        tab.addEventListener('click', function () {
            // 移除所有 active 狀態
            filterTabs.forEach(t => t.classList.remove('active'));

            // 添加 active 到當前 tab
            this.classList.add('active');

            // 取得篩選類型
            const filterType = this.dataset.filter;

            // 篩選活動卡片
            activityCards.forEach(card => {
                const cardType = card.dataset.type;

                if (filterType === 'all') {
                    card.classList.remove('hidden');
                    // 重新觸發動畫
                    card.style.animation = 'none';
                    setTimeout(() => {
                        card.style.animation = '';
                    }, 10);
                } else if (cardType === filterType) {
                    card.classList.remove('hidden');
                    card.style.animation = 'none';
                    setTimeout(() => {
                        card.style.animation = '';
                    }, 10);
                } else {
                    card.classList.add('hidden');
                }
            });

            // 檢查是否有顯示的卡片
            const visibleCards = Array.from(activityCards).filter(
                card => !card.classList.contains('hidden')
            );

            // 如果沒有可見的卡片，可以顯示空狀態訊息
            const activitiesList = document.querySelector('.activities-list');
            let emptyMessage = activitiesList.querySelector('.filter-empty-state');

            if (visibleCards.length === 0 && !emptyMessage) {
                emptyMessage = document.createElement('div');
                emptyMessage.className = 'empty-state filter-empty-state';
                emptyMessage.innerHTML = `
                    <div class="empty-icon">🔍</div>
                    <h3 class="empty-title">沒有符合的活動</h3>
                    <p class="empty-text">此類型沒有活動記錄</p>
                `;
                activitiesList.appendChild(emptyMessage);
            } else if (visibleCards.length > 0 && emptyMessage) {
                emptyMessage.remove();
            }
        });
    });
});
