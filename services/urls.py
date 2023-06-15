from django.urls import path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view

from . import views
from .views import LogoutView, OverViewAPIView, UserLoginView, UserRegisterView, UserInfoView, \
    UpdateUserInfoView
from .views import OrderCreateAPIView, ServiceUserCreateAPIView, BookCopyCreateAPIView, \
    OrderStatusUpdateAPIView, GetOrderCreateAPIView, BookCopyUpdateView

schema_view = get_schema_view(
   openapi.Info(
      title="Snippets API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
)

urlpatterns = [
    path('', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('overview', OverViewAPIView.as_view(), name='overview'),

    # user
    path('user/register', UserRegisterView.as_view(), name='user-register'),
    path('user/login', UserLoginView.as_view(), name='login'),
    path('user/logout', LogoutView.as_view(), name='logout'),
    path('user/info', UserInfoView.as_view(), name='user-info'),
    path('user/info/update/', UpdateUserInfoView.as_view(), name='update-user-info'),

    # book and book copes
    path('book/<int:book_id>/update/', views.BookUpdateAPIView.as_view(), name='book-update'),
    path('book/list/', views.BookListAPIView.as_view(), name='book-list'),
    path('book-copies/create/', BookCopyCreateAPIView.as_view(), name='book-copy-create'),
    path('bookcopies/<int:pk>/', BookCopyUpdateView.as_view(), name='bookcopy-update'),
    # user
    path('service-users/create/', ServiceUserCreateAPIView.as_view(), name='service-user-create'),
    # order
    path('orders/create/', OrderCreateAPIView.as_view(), name='order-create'),
    path('orders/<int:pk>/status/', OrderStatusUpdateAPIView.as_view(), name='order-status-update'),
    path('orders/<int:order_id>/', GetOrderCreateAPIView.as_view(), name='order-detail'),
    # orderDetail
    path('order-details/create/', GetOrderCreateAPIView.as_view(), name='order-detail-create'),
]
