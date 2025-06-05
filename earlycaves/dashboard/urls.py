from django.urls import path,include
from dashboard.views import AdminDashboard, AdminLogin, CustomLogoutView, PunchInView, \
OnboardingListView, PayoutListView, ReviewProductView, WhatsAppMarketingView, EmailMarketingView, \
    TelegramProductView, PaymentProductView, LockMessageProdView
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
    path('whatsapp-marketting/', WhatsAppMarketingView.as_view(), name='whatsapp_marketing'),
    path('email-marketting/', EmailMarketingView.as_view(), name='email_marketing'),
    path('telegram-channels/', TelegramProductView.as_view(), name='telegram_chaannels'),
    path('payment-links/', PaymentProductView.as_view(), name='payment_links'),
    path('lock-messages/', LockMessageProdView.as_view(), name='lock_messages'),

    ]