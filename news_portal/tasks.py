import logging
from datetime import timedelta
from django.utils import timezone
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
from .models import Post, Category, User
from celery import shared_task
from django.core.mail import get_connection
from django.core.mail import EmailMultiAlternatives
import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

logger = logging.getLogger(__name__)

# @shared_task
# def printer(N):
#     for i in range(N):
#         time.sleep(1)
#         print(i+1)
#
# @shared_task
# def hello():
# #    time.sleep(10)
#     print("Hello from Celery!")
#     return "OK"

@shared_task
def send_notifications_task(post_id):
    try:
        post = Post.objects.get(id=post_id)

        for category in post.categories.all():
            print(f'Категория: {category.name}')
            for subscriber in category.subscribers.all():
                if subscriber.email:
                    message = f'''
                    Новая публикация в категории {category.name}:
                    {post.preview()}\n\nЧитать полностью: {settings.SITE_DOMAIN}{post.get_absolute_url()}
                    '''
                    html_message = f'''
                    <p>Новая публикация в категории <strong>{category.name}</strong>:</p>
                    <h4>{post.headline}</h4>
                    <p>{post.preview()}</p>
                    <p><a href="{settings.SITE_DOMAIN}{post.get_absolute_url()}">Читать полностью</a></p>
                    '''

                    send_mail(
                        subject=f'Новая публикация в категории {category.name}: {post.headline}',
                        message=message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[subscriber.email],
                        html_message=html_message,
                        fail_silently=False
                    )

                else:
                    print(f'У пользователя {subscriber.username} нет email')

    except Exception as e:
        # Логируем ошибку для последующего анализа
        # logger.error(f"Error sending notifications: {str(e)}")
        print(f"Ошибка отправки нотификации: {str(e)}")
        raise

@shared_task
def send_welcome_email_task(user_id):
    user = User.objects.get(id=user_id)
    subject = 'Добро пожаловать на наш сайт!'
    message = f'''
    Приветствуем, {user.username}!
    Спасибо за регистрацию на нашем сайте.
    Ваш email: {user.email}
    '''
    html_message = f'''
    <h2>Добро пожаловать, {user.username}!</h2>
    <p>Спасибо за регистрацию на нашем сайте.</p>
    <p>Ваш email: <strong>{user.email}</strong></p>
    '''

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_message,
        fail_silently=False
    )

def send_weekly_articles():
    # Определяем дату неделю назад
    week_ago = timezone.now() - timedelta(days=7)
    # print('week_ago', week_ago)
    # Для каждой категории находим новые статьи за неделю
    for category in Category.objects.all():
        # Получаем статьи этой категории, созданные за последнюю неделю
        new_articles = Post.objects.filter(
            categories=category,
            time_in__gte=week_ago,
            publication_type='AR'  # Только статьи
        ).order_by('-time_in')

        if new_articles.exists():
            # Получаем всех подписчиков категории
            subscribers = category.subscribers.all()

            for subscriber in subscribers:
                # Формируем контекст для письма
                context = {
                    'category': category,
                    'articles': new_articles,
                    'domain': settings.SITE_DOMAIN,
                }

                # Рендерим HTML-письмо
                message = render_to_string('email/weekly_articles.html', context)
                plain_message = render_to_string('email/weekly_articles.txt', context)

                # Отправляем письмо
                send_mail(
                    subject=f'Новые статьи в категории "{category.name}" за неделю',
                    message=plain_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[subscriber.email],
                    html_message=message,
                    fail_silently=False
                )
                # print('send_mail', subscriber.email)