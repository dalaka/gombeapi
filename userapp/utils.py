import random
from django.core.mail import EmailMessage
import pyotp
from rest_framework import pagination, status
from rest_framework.response import Response

from GombeLine import settings
from userapp.models import User, OTP


def generate_activation_code(code):
    import random
    res= code+str(random.randint(1111111, 9999999))
    return res
class CustomPagination(pagination.PageNumberPagination):

    def get_paginated_response(self, data):
        return  Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'results': data
        })

def send_email(subject, to_email,full_name, code,tmpid):
    from mailjet_rest import Client

    api_key = settings.MJ_APIKEY_PUBLIC
    api_secret = settings.MJ_APIKEY_PRIVATE
    mailjet = Client(auth=(api_key, api_secret), version='v3.1')
    data = {
        'Messages': [
            {
                "From": {
                    "Email": "dalaka@ruban.ng",
                    "Name": subject
                },
                "To": [
                    {
                        "Email": to_email,
                        "Name": subject
                    }
                ],
                "TemplateID": tmpid,
                "TemplateLanguage": True,
                "Subject": "Password Reset",
                "Variables": {"code":code,"firstname":full_name}
            }
        ]
    }

    res =  mailjet.send.create(data=data)
    return res


def send_code_to_user(email):

    Subject = "One time passcode for email verification"
    # Generate OTP
    otp_secret = pyotp.random_base32()
    otp = pyotp.TOTP(otp_secret,interval=300)
    otp_code = otp.now()
    user = User.objects.get(email=email)
    current_site = "Gombe Transport System"
    email_body = f"Thanks you for signing up on {current_site} please verify your email with the \n " \
                 f"otp code {otp_code}"
    from_email = 'info@rubang.ng'
    OTP.objects.create(user=user,otp_secret=otp_secret,email=user.email)
    snd_email=send_email(subject=Subject,to_email=user.email,full_name=user.first_name,code=email_body,tmpid=5384171)
    #EmailMessage(subject=Subject, body=email_body, from_email=from_email, to=[email])
    #send_email.send(fail_silently=True)
    return snd_email

def reset_pwd_email(data):

    res = send_email(subject=data["email_subject"],to_email=data['to_email'], full_name=data['first_name'],
                     code=data['email_body'], tmpid=4028276)
    return res
