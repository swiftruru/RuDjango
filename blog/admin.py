from django.contrib import admin
from .models import (
    Article, ArticleReadHistory, Comment, Like, Bookmark, ArticleShare,
    UserProfile, Skill, Achievement, UserAchievement,
    LearningCourse, UserCourseProgress, Activity, Follow, Tag
)


# 標籤管理
@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'article_count', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at']


# 文章管理
@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'status', 'publish_at', 'reading_time', 'created_at', 'updated_at']
    list_filter = ['status', 'created_at', 'author']
    search_fields = ['title', 'content']
    date_hierarchy = 'created_at'
    filter_horizontal = ['tags']
    readonly_fields = ['reading_time', 'created_at', 'updated_at']
    fieldsets = (
        ('基本資訊', {
            'fields': ('title', 'content', 'author', 'tags')
        }),
        ('發布設定', {
            'fields': ('status', 'publish_at')
        }),
        ('統計資訊', {
            'fields': ('reading_time', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# 文章閱讀記錄管理
@admin.register(ArticleReadHistory)
class ArticleReadHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'article', 'read_count', 'first_read_at', 'last_read_at', 'reading_time_display']
    list_filter = ['first_read_at', 'last_read_at']
    search_fields = ['user__username', 'article__title']
    date_hierarchy = 'last_read_at'
    readonly_fields = ['first_read_at', 'last_read_at']

    def reading_time_display(self, obj):
        """顯示閱讀時長（分鐘）"""
        minutes = obj.reading_time_seconds // 60
        seconds = obj.reading_time_seconds % 60
        return f"{minutes}分{seconds}秒"
    reading_time_display.short_description = '閱讀時長'


# 留言管理
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['author', 'article', 'content_preview', 'parent', 'created_at']
    list_filter = ['created_at']
    search_fields = ['author__username', 'article__title', 'content']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'updated_at']

    def content_preview(self, obj):
        """顯示留言內容預覽"""
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = '留言內容'


# 按讚管理
@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'article', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'article__title']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at']


# 書籤管理
@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ['user', 'article', 'created_at', 'note_preview']
    list_filter = ['created_at']
    search_fields = ['user__username', 'article__title', 'note']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at']

    def note_preview(self, obj):
        """顯示筆記預覽"""
        if obj.note:
            return obj.note[:50] + '...' if len(obj.note) > 50 else obj.note
        return '-'
    note_preview.short_description = '筆記'


# 文章分享統計管理
@admin.register(ArticleShare)
class ArticleShareAdmin(admin.ModelAdmin):
    list_display = ['article', 'platform', 'user', 'ip_address', 'shared_at']
    list_filter = ['platform', 'shared_at']
    search_fields = ['article__title', 'user__username', 'ip_address']
    date_hierarchy = 'shared_at'
    readonly_fields = ['shared_at']


# 使用者資料管理
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'level', 'points', 'school', 'grade', 'created_at']
    list_filter = ['level', 'school', 'grade']
    search_fields = ['user__username', 'user__email', 'bio']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('基本資料', {
            'fields': ('user', 'bio', 'avatar')
        }),
        ('教育資訊', {
            'fields': ('school', 'grade', 'birthday')
        }),
        ('等級系統', {
            'fields': ('level', 'points')
        }),
        ('社交連結', {
            'fields': ('location', 'website', 'github')
        }),
        ('時間戳記', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# 技能標籤管理
@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['name', 'user_count', 'created_at']
    search_fields = ['name']
    filter_horizontal = ['users']

    def user_count(self, obj):
        return obj.users.count()
    user_count.short_description = '使用者數量'


# 成就管理
@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ['icon', 'name', 'category', 'points', 'condition_type', 'condition_value']
    list_filter = ['category', 'points']
    search_fields = ['name', 'description']
    fieldsets = (
        ('基本資訊', {
            'fields': ('name', 'description', 'icon', 'category')
        }),
        ('獎勵與條件', {
            'fields': ('points', 'condition_type', 'condition_value')
        }),
    )


# 使用者成就管理
@admin.register(UserAchievement)
class UserAchievementAdmin(admin.ModelAdmin):
    list_display = ['user', 'achievement', 'unlocked_at']
    list_filter = ['achievement__category', 'unlocked_at']
    search_fields = ['user__username', 'achievement__name']
    date_hierarchy = 'unlocked_at'
    readonly_fields = ['unlocked_at']


# 學習課程管理
@admin.register(LearningCourse)
class LearningCourseAdmin(admin.ModelAdmin):
    list_display = ['name', 'total_lessons', 'color', 'created_at']
    search_fields = ['name', 'description']


# 使用者課程進度管理
@admin.register(UserCourseProgress)
class UserCourseProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'completed_lessons', 'progress_percentage', 'last_activity']
    list_filter = ['course', 'last_activity']
    search_fields = ['user__username', 'course__name']
    readonly_fields = ['last_activity', 'progress_percentage']


# 使用者活動管理
@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ['user', 'activity_type', 'title', 'created_at']
    list_filter = ['activity_type', 'created_at']
    search_fields = ['user__username', 'title', 'description']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at']


# 追蹤關係管理
@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ['follower', 'following', 'created_at']
    search_fields = ['follower__username', 'following__username']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at']