from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('Users.urls')),
    path('api/tasks/', include('Task.urls')),
    path('api/game/', include('Game.urls')),
]
