import smtplib
from email.message import EmailMessage
from config import SMTP_HOST, SMTP_PORT, REDIS_PORT, REDIS_HOST, subjects
from celery import Celery
from loguru import logger

celery = Celery('celery_tasks',
                broker=f'redis://{REDIS_HOST}:{REDIS_PORT}',
                backend=f'redis://{REDIS_HOST}:{REDIS_PORT}')

# celery.conf.imports = ['celery_tasks.tasks']


def get_content_html(type_email: str) -> str or None:
    try:
        with open(f'template_email/{type_email}.html', 'r') as file:
            content_html = file.read()
            return content_html
    except FileNotFoundError:
        return None


def get_email_template(email_address: str, username: str, type_email: str, token: str) -> EmailMessage | None:
    subject_email = subjects.get(type_email)
    content = get_content_html(type_email=type_email)
    if not (subject_email and content):
        logger.warning(f'No found template Subject ot HTML by TypeEmail -> {type_email}')
        return None
    email = EmailMessage()
    email['Subject'] = subject_email.format(username)
    email['From'] = 'manager_password@mail.ru'
    email['To'] = email_address
    link_reset = f'http://localhost:8000/auth/change_password/{token}'  # TODO: change link
    email.set_content(content.format(username, link_reset), subtype='html')
    return email


@celery.task
def send_email(email: str, username: str, type_token: str, token: str) -> None:
    email_data = get_email_template(email_address=email, username=username, type_email=type_token, token=token)
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.send_message(email_data)
