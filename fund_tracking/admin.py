from django.contrib import admin

from .models import BankDetails, ForwardedTransaction, ProofScreenshot, Transaction

# Register your models here.
admin.site.register(ProofScreenshot)
admin.site.register(Transaction)
admin.site.register(ForwardedTransaction)
admin.site.register(BankDetails)