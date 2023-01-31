

func = '''
from django.core.mail import send_mail
from django.conf import settings
from sender.models import *
from smtplib import SMTPException
from config.settings import CRONJOBS


def send_letter():
    print('Иниациализация крона')
    user = {}
    mailing = {}
    mail_dump = ConfigMailing.objects.all().get(id=mailing).mail_dump
    from_email = settings.EMAIL_HOST_USER
    
    letters = sorted(LetterMailing.objects.all().filter(mailing=mailing, status='Ожидает отправки'))
    sent_letter = letters[0]
    subject = sent_letter.title
    message = sent_letter.content
    
    if not TryMailing.objects.all().get(mailing=mailing):
        print('Инициализация попытки')
        current_try = TryMailing(username=user, mailing=mailing, letter=sent_letter.pk)
        ConfigMailing.objects.all().get(id=mailing).status = 'Запущена'
    else:
        current_try = TryMailing.objects.all().get(mailing=mailing)
    
    recipient_list = []
    with open(mail_dump, 'r') as clients:
        for client in clients:
            print('Итерация по почтовым адресам')
            recipient_list.append(client)
    
    try:
        send_mail(subject=subject, message=message, from_email=from_email, recipient_list=recipient_list)
        
    except SMTPException as e:
        current_try.mail_server_respond = e
        current_try.count_try += 1
        
    else:
        print('Успешная попытка')
        success_sent = 'Письмо успешно отправлено'
        current_try.count_try += 1
        current_try.mail_server_respond = success_sent
        current_try.letter = sent_letter.pk
        
        if len(letters) == 1:
            print('Последнее письмо')
            mailing = ConfigMailing.objects.all().get(id=mailing)
            mailing.status = 'Завершена'
            cronjob = (mailing.cron_period, mailing.cron_path)
            
            if cronjob in CRONJOBS:
                CRONJOBS.pop(CRONJOBS.index(cronjob))
        
        sent_letter.status = 'Отправлено'
        print('Успешное завершение крона')
        
        return True
'''


