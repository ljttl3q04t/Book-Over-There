from django.urls import path

from d_free_book import views

urlpatterns = [
    path('club_book/get_ids', views.ClubBookGetIdsView.as_view()),
    path('club_book/get_infos', views.ClubBookGetInfosView.as_view()),

    path('order_detail/get_ids', views.OrderDetailGetIdsView.as_view()),
    path('order_detail/get_infos', views.OrderDetailGetInfosView.as_view()),

    path('order/get_ids', views.StaffGetOrderIdsView.as_view()),
    path('order/get_infos', views.OrderInfosView.as_view()),

    path('club_book/add', views.ClubBookAddView.as_view()),
    # path('club_book/update', views.ClubBookUpdateView.as_view()),
    # path('book/update', views.BookListAPIView.as_view()),
    # path('order/create', views.BookListAPIView.as_view()),
    # path('order/return', views.BookListAPIView.as_view()),
]
