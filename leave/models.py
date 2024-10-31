from django.db import models
from django.contrib.auth.models import User

class Leave(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)  # 学生账号
    name = models.CharField(max_length=100)
    class_name = models.CharField(max_length=100)  # 班级
    start_date = models.DateTimeField()  # 请假开始时间
    end_date = models.DateTimeField()  # 请假结束时间
    reason = models.TextField()  # 请假理由
    leave_time = models.DateTimeField(auto_now_add=True)  # 请假申请时间
    is_approved = models.BooleanField(default=False)  # 是否批准

    def __str__(self):
        return f'{self.name} - {self.class_name} - {self.reason}'

class LeaveStub(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)  # 学生账号
    name = models.CharField(max_length=100)
    class_name = models.CharField(max_length=100)  # 班级
    start_date = models.DateTimeField()  # 请假开始时间
    end_date = models.DateTimeField()  # 请假结束时间
    reason = models.TextField()  # 请假理由
    leave_time = models.DateTimeField(auto_now_add=True)  # 请假申请时间
    is_approved = models.BooleanField(default=False)  # 是否批准


class RejectedLeave(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)  # 学生账号
    name = models.CharField(max_length=100)
    class_name = models.CharField(max_length=100)  # 班级
    start_date = models.DateTimeField()  # 请假开始时间
    end_date = models.DateTimeField()  # 请假结束时间
    reason = models.TextField()  # 请假理由
    leave_time = models.DateTimeField(auto_now_add=True)  # 请假申请时间
    is_approved = models.BooleanField(default=False)  # 是否批准

    def __str__(self):
        return f'{self.name} - {self.class_name} - {self.reason}'