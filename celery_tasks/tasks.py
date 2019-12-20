from celery_tasks.celery import app as celery_app
from django.core.mail import send_mail


@celery_app.task
def send_mail_task(content, receiver):
    send_mail(
        '教室预定审核状态变动',
        content,
        'lf97310@163.com',
        [receiver, 'lf97310@163.com'],
        fail_silently=False,
    )
