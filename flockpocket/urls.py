from django.urls import path, include
from django.contrib import admin
from django.conf import settings

urlpatterns = [
    path("",
        include(
            [
                path('', include('webapp.urls')),
                path('api/', include('api.urls')),
                path('admin/', admin.site.urls),
            ]
        )
    )
]
