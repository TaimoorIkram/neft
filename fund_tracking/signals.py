import os
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.conf import settings
from .models import ProofScreenshot

@receiver(post_delete, sender=ProofScreenshot)
def delete_screenshot_file(sender, instance, **kwargs):
    """Deletes the file from the filesystem when a ProofScreenshot object is deleted."""
    if instance.image:
        image_path = instance.image.path
        if os.path.isfile(image_path):  # Ensure the file exists before deleting
            os.remove(image_path)
