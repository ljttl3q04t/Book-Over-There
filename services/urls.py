from django.urls import path

from . import views
from .views import OrderCreateAPIView, ServiceUserCreateAPIView, OrderDetailCreateAPIView, BookCopyCreateAPIView, \
    OrderStatusUpdateAPIView, GetOrderCreateAPIView

urlpatterns = [
    # book
    path('book/<int:book_id>/update/', views.BookUpdateAPIView.as_view(), name='book-update'),
    path('book/list/', views.BookListAPIView.as_view(), name='book-list'),
    path('book-copies/create/', BookCopyCreateAPIView.as_view(), name='book-copy-create'),
    # user
    path('service-users/create/', ServiceUserCreateAPIView.as_view(), name='service-user-create'),
    # order
    path('orders/create/', OrderCreateAPIView.as_view(), name='order-create'),
    path('orders/<int:pk>/status/', OrderStatusUpdateAPIView.as_view(), name='order-status-update'),
    path('orders/<int:order_id>/', GetOrderCreateAPIView.as_view(), name='order-detail'),
    # orderDetail
    path('order-details/create/', GetOrderCreateAPIView.as_view(), name='order-detail-create'),
    path("", views.index, name="index"),
]