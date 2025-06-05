from django.db import models
from django.contrib.auth import get_user_model

from base.models import NEFTStudentUser
from fund_tracking.validators import validate_iban

# Create your enums here
class TransactionModes(models.TextChoices):
  ONLINE = ("online", "Online")
  CASH = ("cash", "Cash")
    
class TransactionVerificationState(models.TextChoices):
  PENDING = ("pending", "Pending")
  VERIFIED = ("verified", "Verified")
  REJECTED = ("rejected", "Rejected")
    
class TransactionCycleState(models.TextChoices):
  INITIATED = ("initiated", "Initiated")
  PROCESSING = ("forwarded", "Forwarded")
  COMPLETED = ("completed", "Completed")
  
class OnlineTransactionState(models.TextChoices):
  PENDING = ("pending", "Pending")
  VERIFIED = ("verified", "Verified")
  REJECTED = ("rejected", "Rejected")
  
class BankOptions(models.TextChoices):
  SADAPAY = ("sadapay", "SadaPay")
  EASYPAISA = ("easypaisa", "EasyPaisa")
  JAZZCASH = ("jazzcash", "JazzCash")
  HBL = ("hbl", "Habib Bank Limited")
  MEEZAN = ("meezan", "Meezan Bank Limited")

# Create your models here.
class ProofScreenshot(models.Model):
  image = models.ImageField(upload_to='screenshots/')
  transaction = models.ForeignKey("Transaction", on_delete=models.CASCADE, null=True)
  user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
  date_created = models.DateTimeField(auto_now_add=True)
    
class Transaction(models.Model):
  """
  The transaction model to represent the base transaction. For
  example, when a student sends the CR 60 PKR in cash, they are
  registered here, but are tracked as a `ForwardedTransaction`.

  Each `Transaction` object is tracked using a forwarded transaction
  chain where:
  - the transaction is initiated at the time of logging this 
    transaction
  - the transaction is updated to forwarded when a `ForwardedTransaction`
    object is created
  - the transaction is set to completed when the `ForwardedTransaction` 
    terminates at the NSF account
  """
  
  sender = models.ForeignKey(NEFTStudentUser, related_name="sender_transactions", on_delete=models.CASCADE)
  """
  The sender of the cash; a student of role CR/GR/NSFRep
  """
  
  receiver = models.ForeignKey(NEFTStudentUser, related_name="receiver_transactions", on_delete=models.SET_NULL, null=True)
  """
  The receiver of the cash
  """
  
  amount = models.IntegerField()
  """
  The cash transferred in whole numbers (0, 1, ...)
  """
  
  mode = models.TextField(choices=TransactionModes)
  """
  The medium of transaction; a meta data for how the cash
  was received.
  """
  
  state = models.TextField(choices=TransactionCycleState, default=TransactionCycleState.INITIATED)
  """
  The state of the funds; a flag that keeps a check of whether
  the funds have entered the cycle, reached their destination or
  not.
  """
  
  verification_state = models.TextField(choices=TransactionVerificationState, default=TransactionVerificationState.PENDING)
  """
  Once the initial transaction is added, it has to be approved 
  or disapproved by the receiver before it is added to the transaction 
  forwarding cycle.
  """
  
  created = models.DateTimeField(auto_now_add=True)
  updated = models.DateTimeField(auto_now=True)
  
  def __str__(self):
    return ' '.join([self.sender.user.email, "sent", self.receiver.user.email, "PKR", str(self.amount)])
    
class ForwardedTransaction(models.Model):
  """
  Each `Transaction` is tracked by many small `ForwardedTransaction`
  objects, that tracks where the initial transaction from the student 
  to a representative has gone.
  
  A transaction can only be forwarded by a non-student user.
  """
  
  transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
  """
  The original `Transaction` that is being tracked.
  """
  
  previous_transaction = models.ForeignKey("ForwardedTransaction", on_delete=models.SET_NULL, null=True, default=None)
  """
  A `ForwardedTransaction` event that took place before this one.
  """
  
  forwarder = models.ForeignKey(NEFTStudentUser, related_name="forwarder_forwarded_transactions", on_delete=models.SET_NULL, null=True)
  """
  The person forwarding the cash to the other person.
  """
  
  forwardee = models.ForeignKey(NEFTStudentUser, related_name="forwardee_forwarded_transactions", on_delete=models.SET_NULL, null=True)
  """
  The person being forwarded the cash.
  """
  
  created = models.DateTimeField(auto_now_add=True)
  is_verified_by_forwardee = models.BooleanField(default=False)
  # sender_role = ???
    
class BankDetails(models.Model):
  """
  An entity to store the bank accounts of the NSF. Not to be used for
  storing the bank account details of the student users.
  """
  
  account_number = models.CharField(max_length=50, help_text="The complete IBAN of the bank account.")
  """
  The IBAN of the user's bank account. 
  Example: `PKXXBANK<account-number>` or a phone number.
  """
  
  account_title = models.CharField(max_length=50)
  """
  The name of the account holder. Should be the exact name of the holder.
  """
  
  bank = models.TextField(choices=BankOptions, default=BankOptions.SADAPAY)
  """
  The bank from where this account operates.
  """
  
  is_active = models.BooleanField(default=True)
  """
  Only one account must be active at a time, set all others to false.
  """
  
  def __str__(self):
    return ' '.join([self.account_title, f'({self.account_number})', '@', self.bank])
    
class OnlineTransaction(models.Model):
  """
  A database linkage to `BankDetail` for an online transaction.
  """
    
  transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
  
  bank_details = models.ForeignKey(BankDetails, models.CASCADE)
  
  state = models.TextField(choices=OnlineTransactionState, default=OnlineTransactionState.PENDING)
  """
  The current state of this online transaction, can either be pending, 
  or one of verified or rejected.
  """
