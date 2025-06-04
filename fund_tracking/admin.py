from django.contrib import admin

from .models import ProofScreenshot, Transaction

# Register your models here.
admin.site.register(ProofScreenshot)
admin.site.register(Transaction)