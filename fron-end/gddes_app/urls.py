from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('about', views.about, name='about'),
    path('about/', views.about),
    path('register', views.register, name='register'),
    path('register/', views.register),
    path('login', views.login, name='login'),
    path('login/', views.login),
    path('home', views.home, name='home'),
    path('home/', views.home),
    path('prediction', views.prediction, name='prediction'),
    path('prediction/', views.prediction),
    path('model', views.model_view, name='model'),
    path('model/', views.model_view),
]
