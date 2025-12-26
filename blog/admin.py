from django.contrib import admin
from .models import (
    Article, ArticleReadHistory, Comment, Like, Bookmark, ArticleShare,
    UserProfile, Skill, Achievement, UserAchievement,
    LearningCourse, UserCourseProgress, Activity, Follow, Tag,
    Mention, ArticleCollaborator, ArticleEditHistory,
    UserGroup, GroupMembership, GroupPost,
    Event, EventParticipant, Announcement
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


# ========== 社群互動功能管理 ==========

# @提及管理
@admin.register(Mention)
class MentionAdmin(admin.ModelAdmin):
    list_display = ['mentioned_user', 'mentioning_user', 'mention_type', 'is_read', 'created_at']
    list_filter = ['mention_type', 'is_read', 'created_at']
    search_fields = ['mentioned_user__username', 'mentioning_user__username', 'context']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at']


# 文章協作者管理
@admin.register(ArticleCollaborator)
class ArticleCollaboratorAdmin(admin.ModelAdmin):
    list_display = ['article', 'user', 'role', 'permission', 'is_accepted', 'invited_by', 'invited_at']
    list_filter = ['role', 'permission', 'is_accepted', 'invited_at']
    search_fields = ['article__title', 'user__username', 'invited_by__username']
    date_hierarchy = 'invited_at'
    readonly_fields = ['invited_at', 'accepted_at']


# 文章編輯歷史管理
@admin.register(ArticleEditHistory)
class ArticleEditHistoryAdmin(admin.ModelAdmin):
    list_display = ['article', 'editor', 'edit_summary_preview', 'edited_at']
    list_filter = ['edited_at']
    search_fields = ['article__title', 'editor__username', 'edit_summary']
    date_hierarchy = 'edited_at'
    readonly_fields = ['edited_at']

    def edit_summary_preview(self, obj):
        if obj.edit_summary:
            return obj.edit_summary[:50] + '...' if len(obj.edit_summary) > 50 else obj.edit_summary
        return '-'
    edit_summary_preview.short_description = '編輯摘要'


# 使用者群組管理
@admin.register(UserGroup)
class UserGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'group_type', 'creator', 'member_count', 'post_count', 'created_at']
    list_filter = ['group_type', 'created_at']
    search_fields = ['name', 'description', 'tags']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('基本資訊', {
            'fields': ('name', 'description', 'group_type', 'creator')
        }),
        ('設定', {
            'fields': ('cover_image', 'tags')
        }),
        ('統計資訊', {
            'fields': ('member_count', 'post_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# 群組成員管理
@admin.register(GroupMembership)
class GroupMembershipAdmin(admin.ModelAdmin):
    list_display = ['user', 'group', 'role', 'join_method', 'posts_count', 'comments_count', 'joined_at']
    list_filter = ['role', 'join_method', 'joined_at']
    search_fields = ['user__username', 'group__name']
    date_hierarchy = 'joined_at'
    readonly_fields = ['joined_at']


# 群組文章管理
@admin.register(GroupPost)
class GroupPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'group', 'author', 'post_type', 'is_pinned', 'views_count', 'created_at']
    list_filter = ['post_type', 'is_pinned', 'created_at']
    search_fields = ['title', 'content', 'group__name', 'author__username']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'updated_at']


# 活動管理
@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'event_type', 'organizer', 'status', 'start_time', 'end_time', 'participants_count']
    list_filter = ['event_type', 'status', 'start_time']
    search_fields = ['title', 'description', 'organizer__username']
    date_hierarchy = 'start_time'
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('基本資訊', {
            'fields': ('title', 'description', 'event_type', 'organizer', 'group')
        }),
        ('時間資訊', {
            'fields': ('start_time', 'end_time', 'registration_deadline')
        }),
        ('地點資訊', {
            'fields': ('location', 'online_link')
        }),
        ('參與設定', {
            'fields': ('max_participants', 'status')
        }),
        ('統計資訊', {
            'fields': ('views_count', 'participants_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# 活動參與者管理
@admin.register(EventParticipant)
class EventParticipantAdmin(admin.ModelAdmin):
    list_display = ['user', 'event', 'status', 'registered_at']
    list_filter = ['status', 'registered_at']
    search_fields = ['user__username', 'event__title', 'note']
    date_hierarchy = 'registered_at'
    readonly_fields = ['registered_at']


# 系統公告管理
@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ['title', 'priority', 'author', 'is_active', 'is_pinned', 'expires_at', 'created_at']
    list_filter = ['priority', 'is_active', 'is_pinned', 'created_at']
    search_fields = ['title', 'content', 'author__username']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'updated_at', 'views_count']
    fieldsets = (
        ('基本資訊', {
            'fields': ('title', 'content', 'author')
        }),
        ('設定', {
            'fields': ('priority', 'is_active', 'is_pinned', 'expires_at')
        }),
        ('統計資訊', {
            'fields': ('views_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )