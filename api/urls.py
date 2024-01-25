from django.urls import path

from . import views

urlpatterns = [
    # configs
    path('create_user/<slug:invite_id>/', views.create_user, name='api.create_user'),
    path('update_user/<slug:user_id>/', views.update_user, name='api.update_user'),
    path('invite_user/', views.invite_user, name='api.invite_user'),
    path('create_thread/', views.create_thread, name='api.create_thread'),
]
