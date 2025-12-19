from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='blog_home'),
    path('home', views.home),
    path('about', views.about),
]
