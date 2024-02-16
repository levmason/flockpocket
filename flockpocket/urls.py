from django.urls import path, include
from django.contrib import admin

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
