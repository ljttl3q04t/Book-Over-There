from django.urls import path

from . import views
from .views import change_borrowing_status, create_borrowing

urlpatterns = [
    path('list/', views.viewListBook, name='view_list'),

    path('api/borrowing/<int:borrowing_id>/status/', change_borrowing_status, name='change_borrowing_status'),
    path('api/borrowing/create/', create_borrowing, name='create_borrowing'),
    path('book/list/', views.BookListAPIView.as_view(), name='book-list'),
    path("", views.index, name="index"),
]