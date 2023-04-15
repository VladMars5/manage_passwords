import smtplib
from email.message import EmailMessage
from api.config import email_templates, SMTP_HOST, SMTP_PORT, REDIS_PORT, REDIS_HOST
from celery import Celery

celery = Celery('api/celery_tasks',
                broker=f'redis://{REDIS_HOST}:{REDIS_PORT}',
                backend=f'redis://{REDIS_HOST}:{REDIS_PORT}')

celery.conf.imports = ['celery_tasks.tasks']


def get_email_template(email_address: str, type_email: str, token: str) -> EmailMessage:
    email = EmailMessage()
    email['Subject'] = email_templates.get(type_email).get('subject')
    email['From'] = 'manager_password@mail.ru'
    email['To'] = email_address
    email.set_content(email_templates.get(type_email).get('content').format(token), subtype='html')
    return email


@celery.task
def send_email(email: str, type_email: str, token: str) -> None:
    email_data = get_email_template(email_address=email, type_email=type_email, token=token)
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.send_message(email_data)
