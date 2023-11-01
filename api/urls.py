from django.urls import path

from . import views

urlpatterns = [
    # configs
    path('ui_config/', views.ui_config, name='api.ui_config'),
    path('users/', views.users, name='api.users'),
    path('update_user/<slug:user_id>/', views.update_user, name='api.update_user'),
    path('invite_user/', views.invite_user, name='api.invite_user'),
]
