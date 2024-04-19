from django.urls import path
from . import views
from django.urls import path
from rest_framework_simplejwt import views as jwt_views

from .views import (
    AuthUserRegistrationView,
    AuthUserLoginView,
    UserListView, MyTokenObtainPairView, UserChangeView, UserDeleteView, UserDeletePasswordView, UserSetNewPassword,
)

urlpatterns = [
    path('upldParameter', views.upldParameter),
    path('token/obtain/', MyTokenObtainPairView.as_view(), name='token_create'),
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('register', AuthUserRegistrationView.as_view(), name='register'),
    path('login', AuthUserLoginView.as_view(), name='login'),
    path('users', UserListView.as_view(), name='users'),
    path('change/<uuid:pk>', UserChangeView.as_view()),
    path('delete/<uuid:pk>', UserDeleteView.as_view()),
    path('delete_pass/<uuid:pk>', UserDeletePasswordView.as_view()),
    path('set_pass/<uuid:pk>', UserSetNewPassword.as_view()),
# r'^update_lab_val/(?P<lab_id>[0-9]+)$'
]