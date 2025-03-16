from django.shortcuts import render

from .models import ProofScreenshot
from .serializers import ProofScreenshotSerialzer

from rest_framework.generics import ListCreateAPIView, DestroyAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

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