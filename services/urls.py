from django.urls import path

from . import views
from .views import OrderCreateAPIView, ServiceUserCreateAPIView, OrderDetailCreateAPIView, BookCopyCreateAPIView, \
    OrderStatusUpdateAPIView

urlpatterns = [
    path('list/', views.viewListBook, name='view_list'),
    path('book/<int:book_id>/update/', views.BookUpdateAPIView.as_view(), name='book-update'),
    path('orders/create/', OrderCreateAPIView.as_view(), name='order-create'),
    path('book/list/', views.BookListAPIView.as_view(), name='book-list'),
    path('service-users/create/', ServiceUserCreateAPIView.as_view(), name='service-user-create'),
    path('order-details/create/', OrderDetailCreateAPIView.as_view(), name='order-detail-create'),
    path('book-copies/create/', BookCopyCreateAPIView.as_view(), name='book-copy-create'),
    path('orders/<int:pk>/status/', OrderStatusUpdateAPIView.as_view(), name='order-status-update'),
    path("", views.index, name="index"),
]