/**
 * 文章目錄(TOC)功能
 * 處理目錄導航、平滑滾動和當前位置高亮
 */

// 防止重複載入
if (typeof window.tocInitialized === 'undefined') {
    window.tocInitialized = true;

    document.addEventListener('DOMContentLoaded', function() {
        const tocToggle = document.getElementById('toc-toggle');
        const tocNav = document.getElementById('toc-nav');
        const tocLinks = document.querySelectorAll('.toc-link');

        if (!tocNav) {
            return; // 沒有目錄，直接返回
        }

        // 目錄折疊/展開功能
        if (tocToggle) {
            tocToggle.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();

                const toggleIcon = this.querySelector('.toc-toggle-icon');
                const isCollapsed = tocNav.classList.contains('toc-collapsed');

                if (isCollapsed) {
                    tocNav.classList.remove('toc-collapsed');
                    toggleIcon.textContent = '▼';
                } else {
                    tocNav.classList.add('toc-collapsed');
                    toggleIcon.textContent = '▶';
                }
            });
        }

    // 平滑滾動到對應標題
    tocLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();

            const targetId = decodeURIComponent(this.getAttribute('href').substring(1));
            const targetElement = findHeadingElement(targetId);

            if (targetElement) {
                // 計算滾動位置，讓標題顯示在畫面上方留有空間
                const headerOffset = 100; // 標題上方預留空間 (可調整)
                const elementPosition = targetElement.getBoundingClientRect().top;
                const offsetPosition = elementPosition + window.pageYOffset - headerOffset;

                // 平滑滾動到計算後的位置
                window.scrollTo({
                    top: offsetPosition,
                    behavior: 'smooth'
                });

                // 更新URL hash (不觸發滾動)
                history.pushState(null, null, `#${targetId}`);

                // 高亮當前連結
                updateActiveLink(this);
            }
        });
    });

    // 滾動時高亮當前章節
    let ticking = false;
    window.addEventListener('scroll', function() {
        if (!ticking) {
            window.requestAnimationFrame(function() {
                highlightCurrentSection();
                ticking = false;
            });
            ticking = true;
        }
    });

    // 頁面載入時如果有hash，滾動到對應位置
    if (window.location.hash) {
        const targetId = decodeURIComponent(window.location.hash.substring(1));
        const targetElement = findHeadingElement(targetId);

        if (targetElement) {
            setTimeout(() => {
                // 計算滾動位置，讓標題顯示在畫面上方留有空間
                const headerOffset = 100;
                const elementPosition = targetElement.getBoundingClientRect().top;
                const offsetPosition = elementPosition + window.pageYOffset - headerOffset;

                window.scrollTo({
                    top: offsetPosition,
                    behavior: 'smooth'
                });
            }, 100);
        }
    }
});

/**
 * 查找標題元素
 * 由於Markdown轉換後的HTML可能不包含ID，需要智能匹配
 */
function findHeadingElement(anchorId) {
    // 首先嘗試直接查找ID
    let element = document.getElementById(anchorId);
    if (element) {
        return element;
    }

    // 如果找不到，嘗試在文章內容中查找匹配的標題
    const articleContent = document.querySelector('.article-content');
    if (!articleContent) return null;

    const headings = articleContent.querySelectorAll('h1, h2, h3, h4');

    // 將文字標準化用於比對（移除特殊符號和空白）
    const normalizeForComparison = (text) => {
        return text.toLowerCase()
            .replace(/[^\w\s]/g, '')  // 移除所有標點符號
            .replace(/\s+/g, '');      // 移除所有空白
    };

    const normalizedAnchor = normalizeForComparison(anchorId);

    for (const heading of headings) {
        const headingText = heading.textContent.trim();
        const normalizedHeading = normalizeForComparison(headingText);

        // 精確匹配標準化後的文字
        if (normalizedHeading === normalizedAnchor) {
            // 為找到的標題添加ID
            if (!heading.id) {
                heading.id = anchorId;
            }
            return heading;
        }
    }

    return null;
}

/**
 * 高亮當前章節
 */
function highlightCurrentSection() {
    const articleContent = document.querySelector('.article-content');
    if (!articleContent) return;

    const headings = articleContent.querySelectorAll('h1, h2, h3, h4');
    const scrollPosition = window.scrollY + 100; // 偏移量

    let currentHeading = null;

    headings.forEach(heading => {
        if (heading.offsetTop <= scrollPosition) {
            currentHeading = heading;
        }
    });

    if (currentHeading) {
        const headingText = currentHeading.textContent.trim();
        const tocLinks = document.querySelectorAll('.toc-link');

        tocLinks.forEach(link => {
            const linkText = link.textContent.trim();
            if (linkText === headingText) {
                updateActiveLink(link);
            }
        });
    }
}

/**
 * 更新當前活動連結
 */
function updateActiveLink(activeLink) {
    // 移除所有活動狀態
    document.querySelectorAll('.toc-link').forEach(link => {
        link.classList.remove('toc-link-active');
    });

    // 添加活動狀態到當前連結
    activeLink.classList.add('toc-link-active');
}

}
