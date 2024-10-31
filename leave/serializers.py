# leave/serializers.py
from rest_framework import serializers
from .models import Leave
from django.contrib.auth.models import User
from rest_framework import serializers
from .models import RejectedLeave


class LeaveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Leave
        fields = '__all__'
# serializers.py


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password')

    def create(self, validated_data):
        user = User(
            username=validated_data['username'],
        )
        user.set_password(validated_data['password'])  # 使用 set_password 来加密密码
        user.save()
        return user

class LeaveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Leave
        fields = '__all__'  # 根据你的 Leave 模型，定义字段



class RejectedLeaveSerializer(serializers.ModelSerializer):
    class Meta:
        model = RejectedLeave
        fields = '__all__'