# leave/urls.py

from django.urls import include, path
from .views import request_leave, view_leave_status, approve_leave
from .views import RegisterView,LoginView
from .views import AdminLeaveListView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import CancelLeaveView
from .views import UserInfoView

urlpatterns = [
    path('request-leave/', request_leave, name='request_leave'),#请假
    path('view-leave/', view_leave_status, name='view_leave_status'),#查看请假状态
    path('approve-leave/<int:leave_id>/', approve_leave, name='approve_leave'),#批准请假
    path('register/', RegisterView.as_view(), name='register'),#注册
    path('login/', LoginView.as_view(), name='login'),#登录（不用这个）
    #阅读代码者请注意，为了后期跨平台的可靠性和安全性，我们不予采用传统的登录方式，而是采用了基于token的登录方式
    #所以请使用主urls的api/token/和api/token/refresh/的配置
    #这个login/路由暂时保留，但是不会被使用
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),#登录
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('admin/leaves/', AdminLeaveListView.as_view(), name='admin_leave_list'),
    path('admin/leaves/approve/<int:leave_id>/', AdminLeaveListView.as_view(), name='approve_leave'),
    path('cancel-leave/<int:leave_id>/', CancelLeaveView.as_view(), name='cancel_leave'),#销假
    path('UserInfoView/', UserInfoView.as_view(), name='UserInfoView'),#查看用户信息
]
