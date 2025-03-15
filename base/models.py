from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser

# Create your models here.
class NEFTAbstractUser(AbstractUser):
    pass

class NEFTStudentUser(models.Model):
    """
    Represents the student entity from LMS.
    
    All the information of the user data comes from LMS database
    and gets populated into these models. Note that the username
    from LMS of this object, becomes the username of the base_user.
    """
    # database linkage
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    
    # identification information
    cms = models.IntegerField()
    
    # batch and class related information
    student_class = models.CharField(max_length=10)
    class_section = models.CharField(max_length=1)
    batch = models.IntegerField()
    
    def __str__(self):
        return self.user.username