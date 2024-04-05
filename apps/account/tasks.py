from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from config.celery import app
import os
from dotenv import load_dotenv

load_dotenv()

@app.task
def send_activation_code(email, activation_code):
    context = {
        'text_detail': 'Активация аккаунта',
        'email': email,
        'domain': 'http://0.0.0.0:80',
        'activation_code': activation_code
    }

    msg_html = render_to_string('email.html', context)
    message = strip_tags(msg_html)

    send_mail(
        'Активация аккаунта',
        message=message,
        from_email='admin@admin.com',
        recipient_list=[email],
        html_message=msg_html,
        fail_silently=False
    )

@app.task
def send_verification_email(email, activation_code):
    context = {
        'text_detail': 'Восстановление пароля',
        'email': email,
        'domain': 'http://0.0.0.0:80',
        'activation_code': activation_code
    }

    msg_html = render_to_string('email.html', context)
    message = strip_tags(msg_html)

    send_mail(
        'Восстановление пароля',
        message=message,
        from_email='admin@admin.com',
        recipient_list=[email],
        html_message=msg_html,
        fail_silently=False
    )