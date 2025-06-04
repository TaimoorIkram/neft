from django.core.exceptions import ValidationError
from django.shortcuts import render

from base.models import NEFTStudentUser
from fund_tracking.permissions import IsNotStudentUser

from .models import ForwardedTransaction, ProofScreenshot, Transaction
from .serializers import ForwardedTransactionSerializer, ProofScreenshotSerialzer, TransactionSerializer

from rest_framework.generics import ListCreateAPIView, CreateAPIView, ListAPIView, DestroyAPIView, RetrieveAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

# Create your views here.
class ListCreateProofScreenshotView(ListCreateAPIView):
    queryset = ProofScreenshot.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = ProofScreenshotSerialzer
    
    def create(self, request, *args, **kwargs):
        image = self.request.FILES['image']
        proof_screenshot = ProofScreenshot.objects.create(user=request.user, image=image)
        proof_screenshot_serialized = ProofScreenshotSerialzer(proof_screenshot)
        return Response(proof_screenshot_serialized.data, status=201)
    
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
    permission_classes = [IsAuthenticated, IsNotStudentUser]
    serializer_class = TransactionSerializer

    def perform_create(self, serializer):
        serializer.save(
            sender = NEFTStudentUser.objects.get(user=self.request.user)
        )
    
    def create(self, request, *args, **kwargs):
        # TODO: linking bank account to an online transaction by creation 
        # of an `OnlineTransaction` object.
        return super().create(request, *args, **kwargs)
    
class RetrieveUpdateDestroyTransactionView(RetrieveUpdateDestroyAPIView):
    queryset = Transaction.objects.all()
    permission_classes = [IsAuthenticated, IsNotStudentUser]
    serializer_class = TransactionSerializer
    
class CreateForwardedTransactionView(CreateAPIView):
    queryset = ForwardedTransaction.objects.all()
    serializer_class = ForwardedTransactionSerializer
    permission_classes = [IsAuthenticated, IsNotStudentUser]
    
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
    permission_classes = [IsAuthenticated, IsNotStudentUser]
    
    def list(self, request, pk, *args, **kwargs):
        forwarded_transactions = self.queryset.filter(transaction__id=pk).order_by("-created")
        forwarded_transactions_serialized = self.serializer_class(forwarded_transactions, many=True)
        return Response(data=forwarded_transactions_serialized.data, status=status.HTTP_200_OK)