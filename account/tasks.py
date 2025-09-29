from celery import shared_task
from django.core.cache import cache
import random
import time


@shared_task
def send_otp(phone_number):
    otp = random.randint(1000, 9999)
    cache.set(phone_number, otp, 120)
    time.sleep(3)
    print(otp)
    return otp
