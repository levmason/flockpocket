from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('user_activate/<slug:invite_id>/', views.user_activate, name='user_activate'),
    path('login/', views.login_view, name='login_view'),
    path('logout/', views.logout_view, name='logout_view'),
]
