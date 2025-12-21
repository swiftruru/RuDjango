from django.contrib import admin
from .models import (
    Article, UserProfile, Skill, Achievement, UserAchievement,
    LearningCourse, UserCourseProgress, Activity, Follow
)


# 文章管理
@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'created_at', 'updated_at']
    list_filter = ['created_at', 'author']
    search_fields = ['title', 'content']
    date_hierarchy = 'created_at'


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