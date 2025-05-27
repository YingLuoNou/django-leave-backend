# leave/urls.py

from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    RegisterView,
    request_leave,
    get_student_leaves,
    cancel_leave,
    UserInfoView,
    ChangePasswordView,
    AdminLeaveListView,
    approve_leave,
    pre_approve_leave,
    mas_approve_leave,
    reject_leave,
    complete_leaving,
    add_student,
    delete_student,
    get_student_info,
    modify_student_profile,
)

urlpatterns = [
    # 注册与登录
    path('register/', RegisterView.as_view(), name='register'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # 学生接口
    path('request-leave/', request_leave, name='request_leave'),               # 提交请假
    path('view-leave/', get_student_leaves, name='view_leave_status'),         # 学生查看请假（分页可选）
    path('cancel-leave/<int:leave_id>/', cancel_leave, name='cancel_leave'),   # 取消请假

    # 用户信息接口（旧路由和新路由同时保留）
    path('UserInfoView/', UserInfoView, name='UserInfoView'),                  # 旧路由，兼容前端未改动
    path('user-info/', UserInfoView, name='user_info'),                        # 新路由，推荐使用

    path('change-password/', ChangePasswordView.as_view(), name='change_password'),

    # 管理员/教师/mas 接口
    path('admin/leaves/', AdminLeaveListView, name='admin_leave_list'),                             # 分页查看请假列表
    path('admin/students/add/', add_student, name='add-student'),                                  #教师管理员添加学生
    path('admin/students/delete/<str:username>/', delete_student, name='delete-student'),          #管理员删除学生(仅限管理员)
    path('admin/students/modify/<str:username>/', modify_student_profile, name='modify-student'),
    path('admin/students/check/<str:username>/', get_student_info, name='get_student_info'),         # 操作学生前查询学生信息以供确认
    path('admin/approve-leave/<int:leave_id>/', approve_leave, name='approve_leave'),                # 批准请假
    path('admin/pre-approve-leave/<int:leave_id>/', pre_approve_leave, name='pre_approve_leave'),    # 初审批准
    path('admin/mas-approve-leave/<int:leave_id>/', mas_approve_leave, name='mas_approve_leave'),    # mas 批准长假
    path('admin/reject-leave/<int:leave_id>/', reject_leave, name='reject_leave'),                  # 拒绝请假
    path('admin/complete-leave/<int:leave_id>/', complete_leaving, name='complete_leave'),          # 销假
]
