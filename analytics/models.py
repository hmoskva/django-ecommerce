from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.sessions.models import Session
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from accounts.signals import user_logged_in

from .signals import object_viewed_signal
from .utils import get_client_ip

User = settings.AUTH_USER_MODEL


class ObjectViewed(models.Model):
    user = models.ForeignKey(User, null=True, blank=True)
    ip_address = models.CharField(max_length=255, null=True, blank=True)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s viewed on %s" %(self.content_object, self.timestamp)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Object viewed'
        verbose_name_plural = 'Objects viewed'


@receiver(object_viewed_signal)
def object_viewed_receiver(sender, instance, request, *args, **kwargs):
    c_type = ContentType.objects.get_for_model(sender)  # same as instance.__class__
    new_view_obj = ObjectViewed.objects.create(
        user=request.user,
        content_type=c_type,
        object_id=instance.id,
        ip_address=get_client_ip(request),

    )


class UserSession(models.Model):
    user = models.ForeignKey(User, null=True, blank=True)
    session_key = models.CharField(max_length=100, null=True, blank=True)
    ip_address = models.CharField(max_length=255, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
    ended = models.BooleanField(default=False)

    def end_session(self):
        session_key = self.session_key
        ended = self.ended
        try:
            Session.objects.get(pk=session_key).delete()
            self.active = False
            self.ended = True
            self.save()
        except:
            pass
        return self.ended


@receiver(post_save, sender=UserSession)
def post_save_session_receiver(sender, instance, created, *args, **kwargs):
    if created:
        qs = Session.objects.filter(user=instance.user).exclude(id=instance.id)
        for i in qs:
            i.end_session()
    if not instance.active and not instance.ended:
        instance.end_session()


@receiver(post_save, sender=UserSession)
def post_save_user_changed_receiver(sender, instance, created, *args, **kwargs):
    if not created:
        if not instance.is_active:
            qs = UserSession.objects.filter(user=instance.user, ended=False, active=False)
            for i in qs:
                i.end_session()


@receiver(user_logged_in)
def user_logged_in_receiver(sender, instance, request, *args, **kwargs):
    session_key = request.session.session_key
    ip_address = get_client_ip(request)
    user = instance

    UserSession.objects.create(
        user=user,
        session_key=session_key,
        ip_address=ip_address,
    )