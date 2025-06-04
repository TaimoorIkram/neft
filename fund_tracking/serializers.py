from .models import ForwardedTransaction, ProofScreenshot, Transaction

from rest_framework.serializers import ModelSerializer, SerializerMethodField, IntegerField

# Create your serializers here
class ProofScreenshotSerialzer(ModelSerializer):
    image_url = SerializerMethodField()
    
    class Meta:
        model = ProofScreenshot
        fields = ('id', 'user', 'image_url')
        
    def get_image_url(self, obj: ProofScreenshot):
        return obj.image.url if (obj.image.url.find('http://') != -1) else f'http://localhost:8000{obj.image.url}'
    
class TransactionSerializer(ModelSerializer):
    receiver_id = IntegerField(write_only=True)
    
    class Meta:
        model = Transaction
        fields = "__all__"
        read_only_fields = ["sender", "receiver"]
        depth=1
        
class ForwardedTransactionSerializer(ModelSerializer):
    transaction_id = IntegerField(write_only=True)
    forwardee_id = IntegerField(write_only=True)
    
    class Meta:
        model = ForwardedTransaction
        fields = "__all__"
        read_only_fields = ["forwarder", "forwardee", "transaction"]
        depth=1