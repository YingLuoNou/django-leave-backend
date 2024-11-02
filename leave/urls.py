# leave/urls.py

from django.urls import include, path
from .views import request_leave, view_leave_status, approve_leave
from .views import RegisterView
from .views import AdminLeaveListView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import CancelLeaveView
from .views import UserInfoView
from .views import reject_leave
from .views import RejectedLeaveListView
from .views import complete_leaving
from .views import completed_leave_list
from .views import view_completed_leave_list
urlpatterns = [
    path('request-leave/', request_leave, name='request_leave'),#请假
    path('view-leave/', view_leave_status, name='view_leave_status'),#查看请假状态
    path('approve-leave/<int:leave_id>/', approve_leave, name='approve_leave'),#批准请假
    path('register/', RegisterView.as_view(), name='register'),#注册
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),#登录（内置函数）
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('admin/leaves/', AdminLeaveListView, name='admin_leave_list'),
    path('admin/leaves/approve/<int:leave_id>/', AdminLeaveListView, name='approve_leave'),
    path('cancel-leave/<int:leave_id>/', CancelLeaveView.as_view(), name='cancel_leave'),#取消请假
    path('UserInfoView/', UserInfoView.as_view(), name='UserInfoView'),#查看用户信息
    path('admin/reject-leave/<int:leave_id>/', reject_leave, name='rejected_leave'),#拒绝请假
    path('CompleteLeavingView/<int:leave_id>/', complete_leaving, name='CompleteLeavingView'),#完成请假(销假)
    path('admin/completed_leave_list/',completed_leave_list,name='completed_leave_list'),#管理员查看已销假列表
    path('view_completed_leave_list/',view_completed_leave_list,name='view_completed_leave_list'),#查看已销假列表
]
# api不要乱改
