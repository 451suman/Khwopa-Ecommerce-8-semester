# import pyotp
# import time
# from django.db.models.signals import post_save
# from django.core.mail import send_mail
# from django.dispatch import receiver
# from django.conf import settings
# from accounts.models import CustomUser


# @receiver(post_save, sender=CustomUser)
# def user_post_save_handler(sender, instance, created, **kwargs):
#     if created:
#         breakpoint()

#         print(f"New user created: {instance.email}")

#         # Optional: Send welcome email
#         send_mail(
#             subject="Welcome to Our Website!",
#             message="Thank you for registering with us.",
#             from_email=settings.DEFAULT_FROM_EMAIL,
#             recipient_list=[instance.email],
#             fail_silently=True,
#         )
#     else:
#         print(f"User updated: {instance.email}")
