from django.urls import path
from . import views

app_name = 'messenger'

urlpatterns = [
    path('', views.IndexView.as_view(), name="index"),
    path('dashboard/', views.DashboardView.as_view(), name="dashboard"),
    path('group/list/', views.GroupListView.as_view(), name="group_list"),
    path('group/create/', views.GroupCreateView.as_view(), name="group_create"),
    path('group/update/<int:pk>', views.GroupUpdateView.as_view(), name="group_update"),
    path('group_user/create/<int:group_id>', views.GroupUserCreateView.as_view(), name='group_user_create'),
    path('message/talk/<int:group_id>', views.MessageTalkView.as_view(), name='message_talk'),
]