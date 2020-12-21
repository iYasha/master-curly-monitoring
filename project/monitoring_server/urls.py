from django.contrib import admin
from django.urls import path
from .collector import views as views

urlpatterns = [
    path('panel/', admin.site.urls),
    path('server/stats', views.stats),
    path('server/logs', views.logs),
]
