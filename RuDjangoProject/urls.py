"""
URL configuration for RuDjangoProject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from blog.sitemaps import ArticleSitemap, TagSitemap, UserProfileSitemap, StaticViewSitemap
from . import views

# Sitemap 配置
sitemaps = {
    'articles': ArticleSitemap,
    'tags': TagSitemap,
    'users': UserProfileSitemap,
    'static': StaticViewSitemap,
}

urlpatterns = [
    path('', views.home, name='home'),
    path('admin/', admin.site.urls),
    path('blog/', include('blog.urls')),
    # Sitemap
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
]

# 在開發環境中提供 media 檔案服務
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
