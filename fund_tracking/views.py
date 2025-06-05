from django.core.exceptions import ValidationError
from django.shortcuts import render

from base.models import NEFTStudentUser
from .serializers import NEFTStudentUserSerializer
from fund_tracking.permissions import IsNotStudentUser

from .models import BankDetails, ForwardedTransaction, ProofScreenshot, Transaction, TransactionModes
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
        return self.queryset.filter(sender__user=self.request.user)
    
class RetrieveUpdateDestroyTransactionView(RetrieveUpdateDestroyAPIView):
    queryset = Transaction.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = TransactionSerializer
    
class CreateForwardedTransactionView(CreateAPIView):
    queryset = ForwardedTransaction.objects.all()
    serializer_class = ForwardedTransactionSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        pervious_forwarded_transaction = self.queryset.filter(transaction__id=self.request.data['transaction_id']).order_by("-created").first() or None

        serializer.save(
            forwarder = NEFTStudentUser.objects.get(user=self.request.user),
            previous_transaction=pervious_forwarded_transaction
        )
    
    def create(self, request, *args, **kwargs):
        if self.queryset.filter(forwarder__user=self.request.user, transaction__id=self.request.data["transaction_id"]).count() != 0: 
            return Response(data={"message": "You have already forwarded this transaction!"}, status=status.HTTP_400_BAD_REQUEST)
        if not self.queryset.filter(transaction__id=self.request.data["transaction_id"]).order_by("-created").first().forwardee.user != self.request.user:
            return Response(data={"message": "This transaction has not been forwarded to you yet!"}, status=status.HTTP_400_BAD_REQUEST)
        return super().create(request, *args, **kwargs)
    
class ListForwardedTransactionsForTransactionView(ListAPIView):
    queryset = ForwardedTransaction.objects.all()
    serializer_class = ForwardedTransactionSerializer
    permission_classes = [IsAuthenticated]
    
    def list(self, request, pk, *args, **kwargs):
        forwarded_transactions = self.queryset.filter(transaction__id=pk).order_by("-created")
        forwarded_transactions_serialized = self.serializer_class(forwarded_transactions, many=True)
        return Response(data=forwarded_transactions_serialized.data, status=status.HTTP_200_OK)
    
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