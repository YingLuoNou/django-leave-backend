# leave/importer.py

import os
import django
import pandas as pd
from django.contrib.auth.models import User, Group
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist

# 配置 Django 设置
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')  # 请替换为您的项目名称
django.setup()

def import_teachers_from_xlsx(xlsx_file):
    # 读取教师 XLSX 文件
    df = pd.read_excel(xlsx_file)

    # 创建或获取 'tch' 用户组
    tch_group, _ = Group.objects.get_or_create(name='tch')

    # 默认密码
    default_password = '123456'

    # 遍历每一行数据并创建教师用户
    for index, row in df.iterrows():
        username = str(row['工号']).strip()
        last_name = str(row['姓名']).strip()
        email = str(row.get('电子邮箱', '')).strip()
        department = str(row.get('部门', '')).strip()  # 获取部门信息

        try:
            user = User.objects.create_user(
                username=username,
                password=default_password,
                last_name=last_name,
                email=email,
                is_active=True,
            )
            # 将用户添加到 'tch' 组
            user.groups.add(tch_group)
            # 通过信号自动创建 TeacherProfile
            if hasattr(user, 'teacherprofile'):
                user.teacherprofile.department = department
                user.teacherprofile.save()

            print(f"成功创建教师用户: {username}")
        except IntegrityError:
            print(f"用户名已存在，跳过: {username}")

def import_classes_from_xlsx(xlsx_file):
    # 读取班级 XLSX 文件
    df = pd.read_excel(xlsx_file)

    # 创建或获取 'tch' 用户组
    tch_group, _ = Group.objects.get_or_create(name='tch')

    # 遍历每一行数据并创建班级
    for index, row in df.iterrows():
        class_name = str(row['班级名称']).strip()
        teacher_id = str(row['教师工号']).strip()
        description = str(row.get('班级描述', '')).strip()

        try:
            teacher = User.objects.get(username=teacher_id, groups__name='tch')
        except User.DoesNotExist:
            print(f"教师工号 {teacher_id} 不存在或不属于 'tch' 组，跳过班级: {class_name}")
            continue

        try:
            new_class, created = Class.objects.get_or_create(
                name=class_name,
                defaults={
                    'teacher': teacher,
                    'description': description
                }
            )
            if created:
                print(f"成功创建班级: {class_name}")
            else:
                print(f"班级已存在: {class_name}")
        except IntegrityError:
            print(f"无法创建班级: {class_name}")

def import_students_from_xlsx(xlsx_file, classes_xlsx='classes.xlsx'):
    # 读取并导入班级信息
    import_classes_from_xlsx(classes_xlsx)

    # 读取学生 XLSX 文件
    df = pd.read_excel(xlsx_file)

    # 创建或获取 'stu' 用户组
    stu_group, _ = Group.objects.get_or_create(name='stu')

    # 默认密码
    default_password = '123456'

    # 遍历每一行数据并创建学生用户
    for index, row in df.iterrows():
        username = str(row['学号']).strip()
        last_name = str(row['姓名']).strip()
        email = str(row.get('电子邮箱', '')).strip()
        class_name = str(row.get('班级名称', '')).strip()  # 获取班级名称

        try:
            assigned_class = Class.objects.get(name=class_name)
        except Class.DoesNotExist:
            print(f"班级 {class_name} 不存在，无法关联学生: {username}")
            continue

        try:
            user = User.objects.create_user(
                username=username,
                password=default_password,
                last_name=last_name,
                email=email,
                is_active=True,
            )
            # 将用户添加到 'stu' 组
            user.groups.add(stu_group)
            # 通过信号自动创建 StudentProfile
            if hasattr(user, 'studentprofile'):
                user.studentprofile.assigned_class = assigned_class
                user.studentprofile.save()

            print(f"成功创建学生用户: {username}，并关联班级: {class_name}")
        except IntegrityError:
            print(f"用户名已存在，跳过: {username}")

if __name__ == "__main__":
    # 导入教师数据
    import_teachers_from_xlsx('teachers.xlsx')
    # 导入学生数据，并关联班级
    import_students_from_xlsx('students.xlsx', classes_xlsx='classes.xlsx')
    print("用户和班级数据已成功导入到数据库中。")
