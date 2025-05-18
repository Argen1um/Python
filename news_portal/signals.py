from django.db.models.signals import post_save
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.core.mail import send_mail
from pyexpat.errors import messages

from .models import Post
from django.conf import settings
from django.contrib.auth.models import User

@receiver(m2m_changed, sender=Post.categories.through)
def notify_subscribers_on_category_change(sender, instance, action, **kwargs):
    print(f'\n=== m2m_changed сигнал. Action: {action} ===')

    if action == "post_add":  # только после добавления категорий
        # print('Категории были добавлены')
        for category in instance.categories.all():
            print(f'Категория: {category.name}')
            for subscriber in category.subscribers.all():
                if subscriber.email:
                    message = f'''
                    Новая публикация в категории {category.name}:
                    {instance.preview()}\n\nЧитать полностью: {settings.SITE_DOMAIN}{instance.get_absolute_url()}
                    '''
                    html_message = f'''
                    <p>Новая публикация в категории <strong>{category.name}</strong>:</p>
                    <h4>{instance.headline}</h4>
                    <p>{instance.preview()}</p>
                    <p><a href="{settings.SITE_DOMAIN}{instance.get_absolute_url()}">Читать полностью</a></p>
                    '''

                    send_mail(
                        subject=f'Новая публикация в категории {category.name}: {instance.headline}',
                        message=message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[subscriber.email],
                        html_message=html_message,
                        fail_silently=False
                    )
                    print(f'Отправлено {subscriber.email}')
                else:
                    print(f'У пользователя {subscriber.username} нет email')

@receiver(post_save, sender=User)
def send_welcome_email(sender, instance, created, **kwargs):
    if created:
        subject = 'Добро пожаловать на наш сайт!'
        message = f'''
        Приветствуем, {instance.username}!

        Спасибо за регистрацию на нашем сайте.
        Ваш email: {instance.email}
        '''
        html_message = f'''
        <h2>Добро пожаловать, {instance.username}!</h2>
        <p>Спасибо за регистрацию на нашем сайте.</p>
        <p>Ваш email: <strong>{instance.email}</strong></p>
        '''

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[instance.email],
            html_message=html_message,
            fail_silently=False
        )