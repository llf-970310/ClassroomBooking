from celery import Celery

import os

# 为celery设置环境变量
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "classroom_booking.settings")

# 创建celery app
app = Celery('celery_tasks')

# 从单独的配置模块中加载配置
app.config_from_object('classroom_booking.settings')

# 设置app自动加载任务
app.autodiscover_tasks(['celery_tasks'])
