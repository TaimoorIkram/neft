from .models import ProofScreenshot

from rest_framework.serializers import ModelSerializer, SerializerMethodField

# Create your serializers here
class ProofScreenshotSerialzer(ModelSerializer):
    image_url = SerializerMethodField()
    
    class Meta:
        model = ProofScreenshot
        fields = ('id', 'user', 'image_url')
        
    def get_image_url(self, obj: ProofScreenshot):
        return obj.image.url if (obj.image.url.find('http://') != -1) else f'http://localhost:8000{obj.image.url}'