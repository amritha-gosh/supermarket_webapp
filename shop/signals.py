
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order
from django.core.mail import send_mail
from django.conf import settings
from twilio.rest import Client

@receiver(post_save, sender=Order)
def notify_customer(sender, instance, created, **kwargs):
    # only on status change:
    if created: return
    msg = None
    if instance.status=='accepted':
       msg = "Your order #%d has been accepted!" % instance.id
    elif instance.status=='out_for_delivery':
       msg = "Your order #%d is out for delivery!" % instance.id
    elif instance.status=='delivered':
       msg = "Your order #%d has been delivered. Enjoy!" % instance.id
    if not msg: return

    # 1) send email
    send_mail(
      f"Order #{instance.id} update",
      msg,
      settings.DEFAULT_FROM_EMAIL,
      [instance.email],
    )
    # 2) send SMS (Twilio)
    client = Client(settings.TWILIO_SID, settings.TWILIO_TOKEN)
    client.messages.create(
      body=msg,
      from_=settings.TWILIO_FROM,
      to=instance.phone
    )
