# views.py

from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Leave
from .serializers import LeaveSerializer, UserRegisterSerializer
from datetime import datetime
from rest_framework.permissions import IsAdminUser
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
from rest_framework import generics, status
from rest_framework import status
from .models import Leave
from .serializers import UserProfileSerializer
from .decorators import group_required


# 学生注册
@permission_classes([AllowAny])
class RegisterView(APIView):
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'detail': 'User registered successfully!',
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])  # 确保用户已认证
def request_leave(request):
    """
    学生提交请假申请。
    """
    serializer = LeaveSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save()  # `student` 和 `class_name` 将自动设置
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 管理员批准请假
@api_view(['PATCH'])
@group_required('admin','tch')
def approve_leave(request, leave_id):
    try:
        leave = Leave.objects.get(id=leave_id)
    except Leave.DoesNotExist:
        return Response({'error': 'Leave not found'}, status=status.HTTP_404_NOT_FOUND)
    leave.status = 1 # 1表示已批准
    leave.approver = request.user.last_name
    leave.save()
    return Response({'status': 'Leave approved'})



## 取消请假

# views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Leave

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def cancel_leave(request, leave_id):
    """
    学生取消请假申请。
    要求：
    - 只能取消自己的请假条。
    - 请假条的原始状态必须是未批准（状态码为 0）。
    - 取消后，将状态更新为 -1。
    """
    try:
        # 获取当前用户的指定请假条
        leave = Leave.objects.get(id=leave_id, student=request.user)
    except Leave.DoesNotExist:
        return Response(
            {'error': '未找到请假条或您无权操作此请假条。'},
            status=status.HTTP_404_NOT_FOUND
        )

    # 检查请假条的当前状态是否为未批准
    if leave.status != 0:
        return Response(
            {'error': '只有未批准的请假条才能被取消。'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # 更新状态为已取消（-1）
    leave.status = -1
    leave.save()

    return Response(
        {'message': '请假已成功取消。'},
        status=status.HTTP_200_OK
    )



@api_view(['GET'])
@permission_classes([IsAuthenticated])  # 确保用户已认证
def UserInfoView(request):
    """
    用户查询自己的信息，包括班级、姓名（last_name 字段）、邮箱、学号等所有信息。
    """
    serializer = UserProfileSerializer(request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)


# 管理员拒绝请假
@api_view(['PATCH'])
@group_required('admin','tch')
def reject_leave(request, leave_id):
    try:
        leave = Leave.objects.get(id=leave_id)
    except Leave.DoesNotExist:
        return Response({'error': 'Leave not found'}, status=status.HTTP_404_NOT_FOUND)
    if leave.status == 0 or leave.status == 4:
        leave.status = 2 # 2表示已拒绝
        leave.approver = request.user.last_name
        leave.save()
        return Response({'status': 'Leave rejected'})
    else:
        return Response({'error': 'Only pending leaves can be rejected'}, status=status.HTTP_400_BAD_REQUEST)

# 管理员/tch销假
@api_view(['PATCH'])
@group_required('admin','tch')
def complete_leaving(request, leave_id):
    try:
        leave = Leave.objects.get(id=leave_id)
    except Leave.DoesNotExist:
        return Response({'error': 'Leave not found'}, status=status.HTTP_404_NOT_FOUND)
    if leave.status == 1:
        leave.status = 3 # 3表示已销假
        leave.save()
        return Response({'status': 'Leave completed'})
    else:
        return Response({'error': 'Only pending leaves can be completed'}, status=status.HTTP_400_BAD_REQUEST)




# 管理员/教师查看所有请假条
@api_view(['GET'])
@group_required('admin','tch')
def AdminLeaveListView(request):
    """
    管理员查看所有请假记录
    """
    all_leaves = Leave.objects.all()
    serializer = LeaveSerializer(all_leaves, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

# views.py


@api_view(['GET'])
@group_required('stu')
def get_student_leaves(request):
    """
    学生查询自己所有请假条，包括班级、姓名、学号等所有信息。
    """
    leaves = Leave.objects.filter(student=request.user)
    serializer = LeaveSerializer(leaves, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

