from django.urls import path
from d_free_book import views

urlpatterns = [
    path('club_book/get_ids', views.ClubBookGetIdsView.as_view()),
    # path('book/update', views.BookListAPIView.as_view()),
    # path('order/create', views.BookListAPIView.as_view()),
    # path('order/return', views.BookListAPIView.as_view()),
]
