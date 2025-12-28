from django.apps import AppConfig


class AdminDashboardConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'blog.admin_dashboard'
    label = 'admin_dashboard'  # 避免與其他 app 衝突
