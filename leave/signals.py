# leave/signals.py

from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from django.contrib.auth.models import User, Group
from .models import StudentProfile, TeacherProfile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # 检查用户所属的组并创建相应的 Profile
        if instance.groups.filter(name='stu').exists():
            StudentProfile.objects.create(user=instance)
        elif instance.groups.filter(name='tch').exists():
            TeacherProfile.objects.create(user=instance)

@receiver(m2m_changed, sender=User.groups.through)
def add_user_profile(sender, instance, action, **kwargs):
    if action == 'post_add':
        for group in instance.groups.all():
            if group.name == 'stu' and not hasattr(instance, 'studentprofile'):
                StudentProfile.objects.create(user=instance)
            elif group.name == 'tch' and not hasattr(instance, 'teacherprofile'):
                TeacherProfile.objects.create(user=instance)
    elif action == 'post_remove':
        for group in instance.groups.all():
            if group.name == 'stu' and hasattr(instance, 'studentprofile'):
                instance.studentprofile.delete()
            elif group.name == 'tch' and hasattr(instance, 'teacherprofile'):
                instance.teacherprofile.delete()
