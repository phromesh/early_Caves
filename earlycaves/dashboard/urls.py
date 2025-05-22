from django.urls import path,include
from dashboard.views import AdminDashboard, AdminLogin, CustomLogoutView, PunchInView, \
OnboardingListView, PayoutListView, ReviewProductView
from rest_framework.routers import DefaultRouter
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin-dashboard/', AdminDashboard.as_view(), name="admin_dashboard"),
    path('', AdminLogin.as_view(), name="admin_login"),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('punch-in/', PunchInView.as_view(), name='punch_in'),
    path('onboarding-list/', OnboardingListView.as_view(), name='onboarding_list'),
    path('payment-list/', PayoutListView.as_view(), name='payment_list'),
    path('review-product/', ReviewProductView.as_view(), name='review_product'),

    ]