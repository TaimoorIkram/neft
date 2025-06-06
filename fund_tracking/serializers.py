from base.models import NEFTStudentUser
from base.serializers import NEFTAbstractUserSerializer
from .models import BankDetails, ForwardedTransaction, ProofScreenshot, Transaction, TransactionModes

from rest_framework.serializers import ModelSerializer, SerializerMethodField, IntegerField, ListField

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
    screenshot = SerializerMethodField()
    
    class Meta:
        model = Transaction
        fields = "__all__"
        depth=1
        
    def get_screenshot(self, obj: Transaction):
        if obj.mode == TransactionModes.ONLINE:
            screenshot = ProofScreenshot.objects.filter(transaction=obj)
            if screenshot.exists():
                return screenshot.first().image.url
            else: return None
        else: return None
        
class ForwardedTransactionSerializer(ModelSerializer):
    transactions_ids = ListField(
        child=IntegerField(), write_only=True
    )
    previous_transactions_ids = ListField(
        child=IntegerField(), write_only=True, required=False
    )
    forwardee_id = IntegerField(write_only=True)
    
    forwarder = NEFTStudentUserSerializer(read_only=True)
    forwardee = NEFTStudentUserSerializer(read_only=True)
    

    class Meta:
        model = ForwardedTransaction
        fields = "__all__"
        read_only_fields = ["forwarder", "forwardee", "transactions", "previous_transactions", "is_forwarded"]
        depth = 1

    def create(self, validated_data):
        transactions_ids = validated_data.pop("transactions_ids", [])
        previous_transactions_ids = validated_data.pop("previous_transactions_ids", [])
        forwardee_id = validated_data.pop("forwardee_id")

        instance = ForwardedTransaction.objects.create(
            forwardee_id=forwardee_id,
            **validated_data
        )        

        instance.transactions.set(transactions_ids)
        if previous_transactions_ids:
            instance.previous_transactions.set(previous_transactions_ids)

        return instance

    def update(self, instance, validated_data):
        transactions_ids = validated_data.pop("transactions_ids", None)
        previous_transactions_ids = validated_data.pop("previous_transactions_ids", None)
        forwardee_id = validated_data.pop("forwardee_id", None)
        is_verified_by_forwardee = validated_data.pop("is_verified_by_forwardee", None)

        if forwardee_id:
            instance.forwardee_id = forwardee_id
        if transactions_ids is not None:
            instance.transactions.set(transactions_ids)
        if previous_transactions_ids is not None:
            instance.previous_transactions.set(previous_transactions_ids)
        if is_verified_by_forwardee is not None:
            instance.is_verified_by_forwardee = is_verified_by_forwardee
            

        instance.save()
        return instance
        
class BankDetailsSerializer(ModelSerializer):
    class Meta:
        model = BankDetails
        fields = "__all__"