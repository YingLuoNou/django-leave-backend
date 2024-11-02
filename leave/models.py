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
    status = models.IntegerField(default=0)  #状态机

    def __str__(self):
        return f'{self.name} - {self.class_name} - {self.reason}'
"""
重构数据库日志：
把数据表缩小为一个
 使用状态机
 状态机的状态：
 0:未批准
 1:已批准
 2:已驳回
 3:已销假

 不得不承认，脑子不清晰的时候，不要上来就写写写，要先想清楚再写
 要修改的地方
 1.请假的方法都要改
 2.查表的方法也要改

 """