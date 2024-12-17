# coding=utf-8

import os
import django
import pandas as pd
import argparse  # 导入 argparse 库

# 配置 Django 设置
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'leave_management.settings')
django.setup()

from django.contrib.auth.models import User, Group
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from leave.models import Class  # 确保这个模型的路径是正确的

def import_teachers_from_xlsx(xlsx_file):
    # 读取教师 XLSX 文件的函数实现...
    print(f"正在导入教师数据：{xlsx_file}")
def import_classes_from_xlsx(xlsx_file):
    # 读取班级 XLSX 文件的函数实现...
    print(f"正在导入班级数据：{xlsx_file}")

def import_students_from_xlsx(xlsx_file, classes_xlsx='classes.xlsx'):
    # 先导入班级
    import_classes_from_xlsx(classes_xlsx)
    # 读取学生 XLSX 文件的函数实现...
    print(f"正在导入学生数据：{xlsx_file}")

def import_teachers_from_xlsx(xlsx_file):
    # 读取教师 XLSX 文件
    df = pd.read_excel(xlsx_file)

    # 创建或获取 'tch' 用户组
    tch_group, _ = Group.objects.get_or_create(name='tch')

    # 默认密码
    default_password = 'Sdutee_tch_b8j5h'

    # 遍历每一行数据并创建教师用户
    for index, row in df.iterrows():
        username = str(row['工号']).strip().zfill(5)
        last_name = str(row['姓名']).strip()
        # email = str(row.get('电子邮箱', '')).strip()
        # department = str(row.get('部门', '')).strip()  # 获取部门信息

        try:
            user = User.objects.create_user(
                username=username,
                password=default_password,
                last_name=last_name,
               # email=email,
                is_active=True,
            )
            # 将用户添加到 'tch' 组
            user.groups.add(tch_group)
            # 通过信号自动创建 TeacherProfile
            if hasattr(user, 'teacherprofile'):
                user.teacherprofile.save()

            print(f"成功创建教师用户: {username}")
        except IntegrityError:
            print(f"用户名已存在，跳过: {username}")

def import_students_from_xlsx(xlsx_file, classes_xlsx='classes.xlsx'):

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
        email = str(row.get('电子信箱', '')).strip()
        class_name = str(row.get('班级', '')).strip()  # 获取班级名称

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


from django.db import IntegrityError
from leave.models import Class

def import_classes_from_xlsx(xlsx_file):
    # 读取班级 XLSX 文件
    df = pd.read_excel(xlsx_file)
    
    # 遍历每一行数据并创建或更新班级
    for index, row in df.iterrows():
        class_name = str(row['班级']).strip()
        description = str(row.get('班级描述', '')).strip()

        try:
            # 尝试获取班级，如果不存在则创建
            class_obj, created = Class.objects.get_or_create(
                name=class_name,
                defaults={'description': description}
            )
            if created:
                print(f"成功创建班级: {class_name}")
            else:
                # 如果班级已存在，可以选择更新描述或跳过
                # class_obj.description = description
                # class_obj.save()
                print(f"跳过班级: {class_name}")
        except IntegrityError:
            print(f"无法创建或更新班级: {class_name}，可能由于重复的班级名")




def main():
    parser = argparse.ArgumentParser(description="导入教师或学生数据到 Django 数据库")
    parser.add_argument('type', help='导入类型（stu 或 tch）')
    parser.add_argument('filename', help='Excel 文件的路径')
    args = parser.parse_args()

    if args.type == 'tch':
        import_teachers_from_xlsx(args.filename)
    elif args.type == 'stu':
        import_students_from_xlsx(args.filename)
    elif args.type == 'cls':
        import_classes_from_xlsx(args.filename)
    else:
        print("错误：未知的用户类型。请使用 'stu' 或 'tch'。")

if __name__ == "__main__":
    main()
