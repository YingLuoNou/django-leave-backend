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

# 学生注册（不用修改了）
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

# # 用户登录 （旧版的方法，不要使用，也请不要删除）
# class LoginView(APIView):
#     def post(self, request):
#         username = request.data.get('username')
#         password = request.data.get('password')
#         user = authenticate(username=username, password=password)
#         if user is not None:
#             refresh = RefreshToken.for_user(user)
#             return Response({
#                 'refresh': str(refresh),
#                 'access': str(refresh.access_token),
#             }, status=status.HTTP_200_OK)
#         return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

# 学生提交请假申请 (未修改，未测试)
# 重要：之前发现了一个bug，用户提交请假请求的后把status字段直接设置为1，这是不对的，应该是管理员来批准
# 请假请求，所以这里要修改一下
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def request_leave(request):
    data = request.data
    student = request.user
    data['student'] = student.id
    data['status'] = 0  # 0表示未批准
    # 解析并验证日期时间数据
    datetime_str = data.get('datetime')
    if datetime_str:
        try:
            # 只解析到年月日小时
            parsed_datetime = datetime.strptime(datetime_str, '%Y-%m-%dT%H')
            data['datetime'] = parsed_datetime.isoformat()
        except ValueError:
            return Response({'error': 'Datetime has wrong format. Use YYYY-MM-DDTHH format.'}, status=status.HTTP_400_BAD_REQUEST)
    serializer = LeaveSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 学生查看请假状态
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_leave_status(request):
    student = request.user
    leaves = Leave.objects.filter(student=student)
    serializer = LeaveSerializer(leaves, many=True)
    return Response(serializer.data)

# 管理员批准请假
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def approve_leave(request, leave_id):
    try:
        leave = Leave.objects.get(id=leave_id)
    except Leave.DoesNotExist:
        return Response({'error': 'Leave not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.user.is_superuser:  # 确保是管理员
        leave.status = 1 # 1表示已批准
        leave.save()
        return Response({'status': 'Leave approved'})
    return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)


## 取消请假
class CancelLeaveView(generics.DestroyAPIView):
    queryset = Leave.objects.all()
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        leave_id = kwargs.get('leave_id')
        try:
            leave_request = Leave.objects.get(id=leave_id, student=request.user)
            if leave_request.status == 0:
                leave_request.delete()
                return Response({'status': 'Leave cancelled successfully'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Only disapproved leaves can be cancelled'}, status=status.HTTP_400_BAD_REQUEST)
        except Leave.DoesNotExist:
            return Response({'error': 'Leave request not found'}, status=status.HTTP_404_NOT_FOUND)



# 销假
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def complete_leaving(request, leave_id):
    try:
        leave_request = Leave.objects.get(id=leave_id, student=request.user)
        if leave_request.status == 1:
            leave_request.status = 3
            return Response(
                {'status': 'Leave completed and stored successfully'},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {'error': 'Only approved leaves can be completed'},
                status=status.HTTP_400_BAD_REQUEST
            )
    except Leave.DoesNotExist:
        return Response(
            {'error': 'Leave request not found'},
            status=status.HTTP_404_NOT_FOUND
        )

# 查看用户信息
class UserInfoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        user_info = {
            'name': user.get_full_name(),
            'username': user.username,  # 假设学号存储在 username 字段
            'is_superuser': user.is_superuser,
        }
        return Response(user_info, status=status.HTTP_200_OK)

# 管理员拒绝请假
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def reject_leave(request, leave_id):
    try:
        leave = Leave.objects.get(id=leave_id)
    except Leave.DoesNotExist:
        return Response({'error': 'Leave not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.user.is_superuser:  # 确保是管理员
        leave.status = 2 # 2表示已拒绝
        return Response({'status': 'Leave rejected'})
    return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)


# 学生用户查询自己被拒绝的请假条列表
class RejectedLeaveListView(generics.ListAPIView):
    serializer_class = LeaveSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Leave.objects.filter(student=self.request.user, status=2)
    

# 管理员查询已销假的请假记录
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def completed_leave_list(request):
    """
    管理员查看所有已销假的请假记录
    """
    completed_leaves = Leave.objects.filter(status=3)
    serializer = LeaveSerializer(completed_leaves, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


# 管理员查询拒绝列表
# 管理员查询已销假的请假记录
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def completed_leave_list(request):
    """
    管理员查看所有已销假的请假记录
    """
    completed_leaves = Leave.objects.filter(status=2)
    serializer = LeaveSerializer(completed_leaves, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


# 学生查看已经销假的列表
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_completed_leave_list(request):
    """
    学生查看已销假的请假记录
    """
    completed_leaves = Leave.objects.filter(student=request.user, status=3)
    serializer = LeaveSerializer(completed_leaves, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)