from datetime import timedelta
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from .models import Post, Category

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