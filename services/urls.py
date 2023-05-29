from django.urls import path

from . import views

urlpatterns = [
    path('list/', views.viewListBook, name='view_list'),
    path("", views.index, name="index"),
]