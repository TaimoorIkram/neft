from base.models import NEFTStudentUser
from base.serializers import NEFTAbstractUserSerializer
from .models import BankDetails, ForwardedTransaction, ProofScreenshot, Transaction

from rest_framework.serializers import ModelSerializer, SerializerMethodField, IntegerField

# Create your serializers here
class ProofScreenshotSerialzer(ModelSerializer):
    image_url = SerializerMethodField()
    transaction_id = IntegerField(write_only=True)
    
    class Meta:
        model = ProofScreenshot
        fields = ('id', 'transaction', 'user', 'image_url', 'transaction_id')
        read_only_fields = ('id', 'transaction', 'user', 'image_url')
        
    def get_image_url(self, obj: ProofScreenshot):
        return obj.image.url if (obj.image.url.find('http://') != -1) else f'http://localhost:8000{obj.image.url}'

class NEFTStudentUserSerializer(ModelSerializer):
    user = NEFTAbstractUserSerializer(read_only=True)
    
    class Meta:
        model = NEFTStudentUser
        fields = "__all__"
        depth = 1    

class TransactionSerializer(ModelSerializer):
    receiver_id = IntegerField(write_only=True)
    sender = NEFTStudentUserSerializer(read_only=True)
    receiver = NEFTStudentUserSerializer(read_only=True)
    
    class Meta:
        model = Transaction
        fields = "__all__"
        depth=1
        
class ForwardedTransactionSerializer(ModelSerializer):
    transaction_id = IntegerField(write_only=True)
    forwardee_id = IntegerField(write_only=True)
    
    class Meta:
        model = ForwardedTransaction
        fields = "__all__"
        read_only_fields = ["forwarder", "forwardee", "transaction"]
        depth=1
        
class BankDetailsSerializer(ModelSerializer):
    class Meta:
        model = BankDetails
        fields = "__all__"