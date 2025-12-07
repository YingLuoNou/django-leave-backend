from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.db.models import Count, F, ExpressionWrapper, DurationField
from django.db.models.functions import ExtractMonth, ExtractWeekDay, TruncDate
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from .models import Leave
import datetime

class StatisticsDataView(APIView):
    """
    数据看板专用接口：一次性返回所有图表所需数据
    """
    # 权限控制：根据需求开启，建议仅管理员或教师可看
    # permission_classes = [IsAuthenticated] 

    # 【核心修改】在此处添加缓存装饰器
    # 60 * 60 * 24 = 86400 秒 (即 24 小时)
    # 在这 24 小时内，无论数据库怎么变，这个接口都只会返回第一次计算的结果
    @method_decorator(cache_page(60 * 60 * 24)) 
    def get(self, request):
        # 1. 获取所有数据
        queryset = Leave.objects.all()

        # ==========================================
        # 维度 1: 班级/年级统计
        # ==========================================
        class_stats = queryset.values(
            name=F('student__studentprofile__assigned_class__name')
        ).annotate(value=Count('id')).order_by('-value')

        # ==========================================
        # 维度 2: 日 K 线 / 走势图
        # ==========================================
        daily_raw = queryset.annotate(
            date=TruncDate('start_date')
        ).values('date').annotate(count=Count('id')).order_by('date')

        dates = [entry['date'].strftime('%Y-%m-%d') for entry in daily_raw]
        counts = [entry['count'] for entry in daily_raw]

        # ==========================================
        # 维度 3: “滤波预测” (平滑算法)
        # ==========================================
        smoothed_counts = []
        window_size = 3
        for i in range(len(counts)):
            start_index = max(0, i - window_size + 1)
            window = counts[start_index : i + 1]
            avg = sum(window) / len(window)
            smoothed_counts.append(round(avg, 2))

        # ==========================================
        # 维度 4: 时长分段统计
        # ==========================================
        leaves_duration = queryset.annotate(
            duration=ExpressionWrapper(F('end_date') - F('start_date'), output_field=DurationField())
        )
        
        duration_dist = {'short': 0, 'medium': 0, 'long': 0}
        for item in leaves_duration:
            if not item.duration: continue
            days = item.duration.days
            if days < 1:
                duration_dist['short'] += 1
            elif days < 3:
                duration_dist['medium'] += 1
            else:
                duration_dist['long'] += 1

        # ==========================================
        # 维度 5: 高发期热力图
        # ==========================================
        heatmap_data = queryset.annotate(
            month=ExtractMonth('start_date'),
            weekday=ExtractWeekDay('start_date')
        ).values('month', 'weekday').annotate(count=Count('id'))

        return Response({
            "class_stats": list(class_stats),
            "trend_data": {
                "dates": dates,
                "real_values": counts,
                "predict_values": smoothed_counts
            },
            "duration_stats": [
                {"name": "1天以内", "value": duration_dist['short']},
                {"name": "1-3天", "value": duration_dist['medium']},
                {"name": "3天以上", "value": duration_dist['long']}
            ],
            "heatmap_data": list(heatmap_data)
        })
