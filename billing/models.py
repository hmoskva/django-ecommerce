from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from accounts.models import GuestEmail

User = settings.AUTH_USER_MODEL


class BillingProfileManager(models.Manager):
    def new_or_get(self, request):
        guest_email_id = request.session.get('guest_email_id')
        created = False
        obj = None
        user = request.user
        if user.is_authenticated():
            # logged in user checkout. will remember payment stuff
            obj, created = self.model.objects.get_or_create(user=user,
                                                            email=user.email)
        elif guest_email_id is not None:
            # guest checkout. will reload payment stuff automatically
            guest_email_obj = GuestEmail.objects.get(id=guest_email_id)
            obj, created = self.model.objects.get_or_create(
                email=guest_email_obj.email)
        else:
            pass
        return obj, created


class BillingProfile(models.Model):
    user = models.OneToOneField(User, null=True, blank=True,
                                related_name='billing_profile')
    email = models.EmailField()
    active = models.BooleanField(default=True)
    updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = BillingProfileManager()

    def __str__(self):
        return self.email


@receiver(post_save, sender=User)
def user_create_receiver(sender, instance, created, *args, **kwargs):
    if created and instance.email:
        BillingProfile.objects.get_or_create(user=instance, email=instance.email)