from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.hashers import make_password
from base.models import NEFTAbstractUser, NEFTStudentUser

# Create your custom admin here.
class NEFTAbstractUserAdmin(UserAdmin):
    def save_model(self, request, obj, form, change):
        # If a new password is set and not already hashed, hash it
        if form.cleaned_data.get("password") and not obj.password.startswith('pbkdf2_'):
            obj.password = make_password(form.cleaned_data["password"])
        super().save_model(request, obj, form, change)

# Register your models here.
admin.site.register(NEFTAbstractUser, NEFTAbstractUserAdmin)
admin.site.register(NEFTStudentUser)