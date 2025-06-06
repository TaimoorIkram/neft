from django.shortcuts import render

from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from fund_tracking.serializers import NEFTStudentUserSerializer
from .models import NEFTStudentUser

# Create your views here.
class ListRepresentativesView(ListAPIView):
    queryset = NEFTStudentUser.objects.filter(user__groups__name__in=["BP", "NSFT"])
    permission_classes = [IsAuthenticated]
    serializer_class = NEFTStudentUserSerializer