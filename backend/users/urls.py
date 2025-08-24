from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # Authentication endpoints
    path('register/', views.UserRegistrationView.as_view(), name='user-register'),
    path('login/', views.UserLoginView.as_view(), name='user-login'),
    path('logout/', views.user_logout_view, name='user-logout'),
    
    # Profile management
    path('profile/', views.UserProfileView.as_view(), name='user-profile'),
    path('dashboard/', views.user_dashboard_view, name='user-dashboard'),
    
    # Password management
    path('change-password/', views.PasswordChangeView.as_view(), name='change-password'),
    path('reset-password/', views.password_reset_request_view, name='reset-password'),
    path('reset-password/confirm/', views.password_reset_confirm_view, name='reset-password-confirm'),
    
    # Business verification (admin only)
    path('verify-business/', views.verify_business_view, name='user-verify-business'),
]
