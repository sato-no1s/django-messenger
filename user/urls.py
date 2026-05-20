from django.urls import path

from . import views

app_name = "user"

urlpatterns = [
    path('user_detail/<int:pk>', views.UserDetailView.as_view(), name='user_detail'),
    path('user_update/<int:pk>', views.UserUpdateView.as_view(), name='user_update'),
]