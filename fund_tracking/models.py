from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.
class ProofScreenshot(models.Model):
    image = models.ImageField(upload_to='screenshots/')
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)