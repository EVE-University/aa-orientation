"""Routes."""

from django.urls import path

from . import views

app_name = "orientation"

urlpatterns = [
    path('', views.index, name='index'),
    path('mark_talked/', views.mark_talked, name='mark_talked'),
]
