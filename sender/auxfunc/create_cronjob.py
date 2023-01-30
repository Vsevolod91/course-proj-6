from smtplib import SMTPException
from sender.models import *
from django.conf import settings

func = """
from django.core.mail import send_mail
from django.conf import settings
from sender.models import *
from smtplib import SMTPException


def send_letter():
    user = {}
    mailing = {}
    mail_dump = ConfigMailing.objects.all().get(id=mailing).mail_dump
    from_email = settings.EMAIL_HOST_USER
    
    sent_letter = sorted(LetterMailing.objects.all().filter(mailing=mailing, status='Ожидает отправки'))[0]
    subject = sent_letter.title
    message = sent_letter.content
    
    if not TryMailing.objects.all().get(mailing=mailing):
        current_try = TryMailing(username=user, mailing=mailing, letter=sent_letter.pk)
    else:
        current_try = TryMailing.objects.all().get(mailing=mailing)
    
    recipient_list = []
    with open(mail_dump, 'r') as clients:
        for client in clients:
            recipient_list.append(client)
    
    try:
        send_mail(subject=subject, message=message, from_email=from_email, recipient_list=recipient_list)
        
    except SMTPException as e:
        current_try.mail_server_respond = e
        current_try.count_try += 1
        
    else:
    
        success_sent = 'Письмо успешно отправлено'
        current_try.count_try += 1
        current_try.mail_server_respond = success_sent
        current_try.letter = sent_letter.pk
        sent_letter.status = 'Отправлено'
    """

