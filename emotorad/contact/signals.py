from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Contact, AuditLog

@receiver(post_save, sender=Contact)
def log_contact_changes(sender, instance, created, **kwargs):
    action = 'CREATE' if created else 'UPDATE'
    AuditLog.objects.create(
        contact=instance,
        action=action,
        details=f"{action} operation on Contact {instance.id}"
    )