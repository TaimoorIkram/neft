from django.urls import path

from .views import *

app_name = 'fund_tracking'
urlpatterns = [
    path('screenshots/', ListCreateProofScreenshotView.as_view(), name='list_create_proof_screenshot_view'),
    path('screenshots/<int:pk>/', RetrieveDestroyProofScreenshotView.as_view(), name='retrieve_destroy_proof_screenshot_view'),
]