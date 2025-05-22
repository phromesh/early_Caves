from django.contrib import admin
from django.urls import path,include
from account import views
from rest_framework.routers import DefaultRouter
from django.conf import settings
from django.conf.urls.static import static


router = DefaultRouter()
router.register(r'registor', views.UserAccountViewSet, basename='registor')
router.register(r'telegram', views.TelegramViewSet, basename='telegram')
router.register(r'payment-link', views.PaymentLinkViewSet, basename='payment-link')
router.register(r'email-marketing', views.EmailMarketingViewSet, basename='email-marketing')
router.register(r'whatapp-marketing', views.WhatappMarketingViewSet, basename='whatapp-marketing')
router.register(r'payment', views.RazorpayViewSet, basename='razor_earlycave_payment')
router.register(r'telegramproduct', views.TelegramChannelViewSet, basename='telegram_channel')
router.register(r'customer', views.CustomerView, basename='customer')
router.register(r'lock-messages', views.LockMessagingViewSet, basename='lock-messaging')
router.register(r'analyticdata', views.AnalyticsView, basename='analytic_data')
router.register(r'cashfreepayment', views.CashfreeViewSet, basename='cashfree_earlycave_payment')

urlpatterns = [
      path('', include(router.urls)),
      # path('registor/', views.UserAccountViewSet.as_view()),
      # path('registor/getotp', views.UserAcoount.as_view(),name='get_otp'),
      path('', views.index,name='index'),
      path('signin/', views.signin,name='signin'),
      path('signup/', views.signup,name='signup'),
      path('registor/submitotp', views.UserAccountViewSet.as_view({'post':'login'}),name='submit_otp'),
      path('registor/getotp', views.UserAccountViewSet.as_view({'post': 'get_otp'}), name='get_otp'),
      path('registor/userupdate/<int:pk>/', views.UserAccountViewSet.as_view({'post': 'user_partial_update'}), name='user_partial_update'),
      path('registor/getuserdetail', views.UserAccountViewSet.as_view({'get': 'get_user_details'}), name='get_user'),
      path('telegram/getotp/',views.TelegramViewSet.as_view({'post':'get_telegram_otp'}),name='telegram_otp'),
      path('telegram/telegram_authentication/', views.TelegramViewSet.as_view({'post':'telegram_authentication'}), name='telegram_authentication'),
      path('telegram/telegram_creategroup/', views.TelegramViewSet.as_view({'post':'telegram_group_create'}), name='telegra_create_group'),
      path('telegram/group_list/', views.TelegramChannelViewSet.as_view({'get':'get_telegram_grouplist'}), name='telegram_group_list'),
      path('telegram/createdgroupadd/', views.TelegramViewSet.as_view({'post':'created_group_add'}), name='telegram_create_group_add'),
      path('payment/getpaymentlink',views.PaymentLinkViewSet.as_view({'get':'get_payment_link'}),name='get_payment_link'),
      path('payment/<str:uuid>/',views.PaymentLinkViewSet.as_view({'get':'get_payment_product'}),name='get_payment_product'),
      path('addcustomer/',views.CustomerView.as_view({'post':'create_customer'}),name='create_customer'),
      path('addcustomer/verify/',views.CustomerView.as_view({'post':'customer_verify'}),name='customer_verify'),
      path('razorpay/create_order/',views.RazorpayViewSet.as_view({'post':'create_order_razorpay'}),name='create_payment_order'),
      path('cashfreepayment/create_order/',views.CashfreeViewSet.as_view({'post':'create_order_cashfree'}),name='create_payment_order_cashfree'),
      path('razorpay/verify_payment/',views.RazorpayViewSet.as_view({'post':'verify_payment'}),name='verify_payment_order'),
      path('gettelegramlink/',views.TelegramChannelViewSet.as_view({'get':'get_telegramchannel_link'}),name='get_telegram_channel_link'),
      path('telegram/<str:uuid>/',views.TelegramChannelViewSet.as_view({'get':'get_telegramchannel_product'}),name='get_telegram_channel_product'),
      path('getlockmessagelink/',views.LockMessagingViewSet.as_view({'get':'get_lockmessage_link'}),name='get_lockmessage_link'),
      path('lock-messages/<int:pk>/',views.LockMessagingViewSet.as_view({'put': 'update', 'delete': 'destroy'}),name='update_or_delete_lockmessage'),
      path('lock-messages/<int:pk>/',views.LockMessagingViewSet.as_view({'delete': 'destroy'}),name='delete_lockmessagess'),
      path('lockmessage/<str:uuid>/',views.LockMessagingViewSet.as_view({'get':'get_lockmessage_product'}),name='get_lockmessage_product'),
      path('cashfreepayment/verifytowebbook/',views.CashfreeViewSet.as_view({'post':'cashfree_webhook'}),name='cashfree_verify_webbook')
      
]

