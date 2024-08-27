from django.contrib.auth.views import LogoutView
from django.urls import path

from apps.views import HomeListView, ProductListView, ProductDetailView, AdminDashboardView, CustomLoginView, \
    ProfileView, AdminMarketView, AdminStatisticsView, StreamListView, AdminPaymentView, OrderCreateView, \
    StreamFormView

urlpatterns = [
    path('', HomeListView.as_view(), name='home'),

    path('product/', ProductListView.as_view(), name='product-list-page'),
    path('product/<int:pk>/', ProductDetailView.as_view(), name='product-detail-page'),

    # TODO LAZIZBEK AKA
    path('contacts', AdminDashboardView.as_view(), name='contacts'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('admin1/profile', ProfileView.as_view(), name='profile'),
    path('admin1/', AdminDashboardView.as_view(), name='dashboard'),
    path('admin1/market', AdminMarketView.as_view(), name='market'),
    path('admin1/statistics', AdminStatisticsView.as_view(), name='statistics'),
    path('admin1/payment', AdminPaymentView.as_view(), name='payment'),
    path('admin1/stream-form', StreamFormView.as_view(), name='stream-form'),
    path('admin1/list-stream', StreamListView.as_view(), name='stream'),
    path('admin1/profile', ProfileView.as_view(), name='profile'),

    # TODO IXLOSBEK AKA
    path('product/<int:pk>/order/', OrderCreateView.as_view(), name='product-order'),

]
