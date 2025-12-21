/**
 * 編輯個人資料頁面 JavaScript
 * 處理技能標籤的新增、刪除和管理，以及文件上傳顯示
 */

document.addEventListener('DOMContentLoaded', function () {
    const skillInput = document.getElementById('skill-input');
    const skillsDisplay = document.getElementById('skills-display');
    const skillsHidden = document.getElementById('skills-hidden');
    const quickSkillButtons = document.querySelectorAll('.quick-skill-btn');
    const form = document.querySelector('form');

    // 文件上傳處理與即時預覽
    const fileInput = document.querySelector('.file-input');
    const fileUploadName = document.querySelector('.file-upload-name');
    const avatarPreviewImg = document.getElementById('avatar-preview-img');

    if (fileInput && fileUploadName) {
        fileInput.addEventListener('change', function () {
            if (this.files && this.files.length > 0) {
                const file = this.files[0];
                const fileName = file.name;

                // 更新檔案名稱顯示
                fileUploadName.textContent = fileName;
                fileUploadName.classList.add('has-file');

                // 即時預覽頭像
                if (avatarPreviewImg && file.type.startsWith('image/')) {
                    const reader = new FileReader();
                    reader.onload = function (e) {
                        avatarPreviewImg.src = e.target.result;
                    };
                    reader.readAsDataURL(file);
                }
            } else {
                fileUploadName.textContent = '尚未選擇檔案';
                fileUploadName.classList.remove('has-file');
            }
        });
    }

    // 存儲當前技能的集合
    let currentSkills = new Set();

    /**
     * 從表單初始值載入技能
     */
    function loadInitialSkills() {
        const initialValue = skillsHidden.value;
        if (initialValue) {
            const skills = initialValue.split(',').map(s => s.trim()).filter(s => s);
            skills.forEach(skill => addSkill(skill));
        }
    }

    /**
     * 添加技能標籤
     * @param {string} skillName - 技能名稱
     */
    function addSkill(skillName) {
        skillName = skillName.trim();
        if (!skillName || currentSkills.has(skillName)) {
            return;
        }

        if (skillName.length > 50) {
            alert('技能名稱不能超過 50 個字元');
            return;
        }

        currentSkills.add(skillName);
        updateDisplay();
        updateHiddenField();
        updateQuickButtons();
    }

    /**
     * 刪除技能標籤
     * @param {string} skillName - 技能名稱
     */
    function removeSkill(skillName) {
        currentSkills.delete(skillName);
        updateDisplay();
        updateHiddenField();
        updateQuickButtons();
    }

    /**
     * 更新技能標籤顯示
     */
    function updateDisplay() {
        skillsDisplay.innerHTML = '';
        currentSkills.forEach(skill => {
            const tag = document.createElement('span');
            tag.className = 'skill-tag';
            tag.innerHTML = `${skill} <span class="remove">×</span>`;
            tag.addEventListener('click', () => removeSkill(skill));
            skillsDisplay.appendChild(tag);
        });
    }

    /**
     * 更新隱藏表單字段
     */
    function updateHiddenField() {
        const skillsValue = Array.from(currentSkills).join(',');
        skillsHidden.value = skillsValue;
    }

    /**
     * 更新快速選擇按鈕狀態
     */
    function updateQuickButtons() {
        quickSkillButtons.forEach(btn => {
            const skillName = btn.dataset.skill;
            if (currentSkills.has(skillName)) {
                btn.classList.add('selected');
            } else {
                btn.classList.remove('selected');
            }
        });
    }

    // 快速選擇按鈕事件
    quickSkillButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const skillName = btn.dataset.skill;
            if (currentSkills.has(skillName)) {
                removeSkill(skillName);
            } else {
                addSkill(skillName);
            }
        });
    });

    // 自訂輸入框事件（顯示輸入框）
    skillsDisplay.addEventListener('click', function (e) {
        if (e.target === skillsDisplay) {
            skillInput.style.display = 'block';
            skillInput.focus();
        }
    });

    // 輸入框處理
    skillInput.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' || e.key === ',' || e.key === ';') {
            e.preventDefault();
            const value = this.value.trim();
            if (value) {
                addSkill(value);
                this.value = '';
            }
        } else if (e.key === 'Escape') {
            this.style.display = 'none';
            this.value = '';
        }
    });

    skillInput.addEventListener('blur', function () {
        const value = this.value.trim();
        if (value) {
            addSkill(value);
        }
        this.value = '';
        this.style.display = 'none';
    });

    // 表單提交前確保隱藏字段有值
    form.addEventListener('submit', function () {
        updateHiddenField();
    });

    // 載入初始技能
    loadInitialSkills();
});
