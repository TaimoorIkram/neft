from django.core.exceptions import ValidationError
from django.shortcuts import render
from django.db.models import Q

from base.models import NEFTStudentUser
from .serializers import NEFTStudentUserSerializer
from fund_tracking.permissions import IsNotStudentUser

from .models import BankDetails, ForwardedTransaction, ProofScreenshot, Transaction, TransactionCycleState, TransactionModes
from .serializers import BankDetailsSerializer, ForwardedTransactionSerializer, ProofScreenshotSerialzer, TransactionSerializer

from rest_framework.generics import ListCreateAPIView, CreateAPIView, ListAPIView, DestroyAPIView, RetrieveAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

# Create your views here.
class ListCreateProofScreenshotView(ListCreateAPIView):
    queryset = ProofScreenshot.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = ProofScreenshotSerialzer
    
    def perform_create(self, serializer):
        serializer.save(
            image = self.request.FILES['image'],
            user = self.request.user,
        )
        
    def list(self, request, *args, **kwargs):
        proof_screenshots = ProofScreenshot.objects.filter(user=request.user)
        proof_screenshots_serialized = ProofScreenshotSerialzer(proof_screenshots, many=True)
        return Response(proof_screenshots_serialized.data)
    
class RetrieveDestroyProofScreenshotView(RetrieveAPIView, DestroyAPIView):
    queryset = ProofScreenshot.objects.all()
    serializer_class = ProofScreenshotSerialzer
    permission_classes = [IsAuthenticated]
    
class ListCreateTransactionsView(ListCreateAPIView):
    queryset = Transaction.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = TransactionSerializer

    def perform_create(self, serializer):
        if self.request.data["mode"] == TransactionModes.CASH:
            serializer.save(
                sender = NEFTStudentUser.objects.get(id=self.request.data["sender_id"]),
            )
        else:
            serializer.save(
                sender = NEFTStudentUser.objects.get(user=self.request.user),
            )
    
    def create(self, request, *args, **kwargs):
        # TODO: linking bank account to an online transaction by creation 
        # of an `OnlineTransaction` object.
        if "receiver_id" not in self.request.data.keys():
            student = NEFTStudentUser.objects.get(user=self.request.user)
            cr = NEFTStudentUser.objects.filter(student_class=student.student_class, class_section=student.class_section, user__groups__name="CR").first()
            if cr != None:
                self.request.data["receiver_id"] = cr.id
            else:
                return Response(data={"receiver_id": "No CR found for your class."}, status=status.HTTP_400_BAD_REQUEST)
        
        return super().create(request, *args, **kwargs)
    
    def get_queryset(self):
        return self.queryset.filter(Q(sender__user=self.request.user) | Q(receiver__user=self.request.user))
    
class RetrieveUpdateDestroyTransactionView(RetrieveUpdateDestroyAPIView):
    queryset = Transaction.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = TransactionSerializer
    
class CreateForwardedTransactionView(CreateAPIView):
    queryset = ForwardedTransaction.objects.all()
    serializer_class = ForwardedTransactionSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        transactions_ids = self.request.data.get('transactions_ids', [])
        previous_transactions_ids = self.request.data.get('previous_transactions_ids', [])
        forwarder = NEFTStudentUser.objects.get(user=self.request.user)

        # Get latest forwarded transaction where any transaction in the list was previously forwarded
        previous_forwarded = (
            self.queryset
            .filter(transactions__id__in=previous_transactions_ids)
            .order_by('-created')
            .first()
        )

        serializer.save(
            forwarder=forwarder,
        )
        
        if self.request.user.groups.filter(name="CR").exists():
            transactions = Transaction.objects.filter(id__in=transactions_ids)
            for transaction in transactions:
                transaction.state = TransactionCycleState.PROCESSING
                transaction.save()
        elif self.request.user.groups.filter(name__in=["BP", "NSFT"]).exists():
            previous_transactions = self.queryset.filter(id__in=previous_transactions_ids)
            for previous_transaction in previous_transactions:
                previous_transaction.is_forwarded = True
                previous_transaction.save()

    def create(self, request, *args, **kwargs):
        user = request.user
        transactions_ids = request.data.get("transactions_ids", [])

        # Ensure the user hasn't already forwarded *any* of the transactions
        existing_forward = self.queryset.filter(
            forwarder__user=user,
            transactions__id__in=transactions_ids
        ).exists()

        if existing_forward:
            return Response(
                {"message": "You have already forwarded one or more of these transactions!"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Ensure at least one transaction was forwarded *to* this user previously
        latest_forward = (
            self.queryset
            .filter(transactions__id__in=transactions_ids)
            .order_by("-created")
            .first()
        )

        if "previous_transactions_ids" in self.request.data.keys() and (not latest_forward or latest_forward.forwardee.user != user):
            return Response(
                {"message": "This transaction has not been forwarded to you yet!"},
                status=status.HTTP_400_BAD_REQUEST
            )

        return super().create(request, *args, **kwargs)
    
class ListForwardedTransactionsForTransactionView(ListAPIView):
    serializer_class = ForwardedTransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        transaction_id = self.kwargs.get("pk")
        return ForwardedTransaction.objects.filter(transactions__id__contains=transaction_id).order_by("-created")
    
class RetrieveBankDetailsView(RetrieveAPIView):
    queryset = BankDetails.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = BankDetailsSerializer
    
class ListMyClassStudentsView(ListAPIView):
    queryset = NEFTStudentUser.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = NEFTStudentUserSerializer
    
    def get_queryset(self):
        student = NEFTStudentUser.objects.get(user=self.request.user)
        return NEFTStudentUser.objects.filter(student_class=student.student_class, class_section=student.class_section)
    
class ListMyForwardedTransactions(ListAPIView):
    queryset = ForwardedTransaction.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = ForwardedTransactionSerializer
    
    def get_queryset(self):
        return self.queryset.filter(forwardee__user=self.request.user)
    
class RetrieveUpdateDestroyForwardedTransactionView(RetrieveUpdateDestroyAPIView):
    queryset = ForwardedTransaction.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = ForwardedTransactionSerializer
    
    def update(self, request, pk, *args, **kwargs):
        if "is_verified_by_forwardee" in self.request.data.keys() and self.request.user.groups.filter(name="NSFT").exists():
            forwarded_transaction = self.queryset.get(id=pk)
            transactions = Transaction.objects.filter(id__in=[transaction.id for transaction in forwarded_transaction.transactions.all()])
            for transaction in transactions:
                transaction.state = TransactionCycleState.COMPLETED
                transaction.save()
            
            print("Transactions marked complete!")

        return super().update(request, *args, **kwargs)