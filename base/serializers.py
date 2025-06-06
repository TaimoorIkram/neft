from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import NEFTAbstractUser, NEFTStudentUser
from rest_framework.serializers import ModelSerializer, SerializerMethodField

class NEFTAbstractUserSerializer(ModelSerializer):
    groups = SerializerMethodField()
    
    class Meta:
        model = NEFTAbstractUser
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'groups')
        
    def get_groups(self, obj):
        return list(obj.groups.values_list('name', flat=True))

class NEFTStudentUserSerializer(ModelSerializer):
    class Meta:
        model = NEFTStudentUser
        fields = "__all__"

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user: NEFTAbstractUser):
        token = super().get_token(user)

        # Add custom claims
        token['user_type'] = [role.name for role in user.groups.all()]
        
        token['user'] = NEFTAbstractUserSerializer(user).data
        
        if not user.groups.filter(name__in=["NSFTeam", "Faculty"]).exists():
            student = NEFTStudentUser.objects.get(user=user)
            token['student'] = NEFTStudentUserSerializer(student).data
        # ...

        return token