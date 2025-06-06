from django.urls import path

from .views import *

app_name = 'fund_tracking'
urlpatterns = [
    path('screenshots/', ListCreateProofScreenshotView.as_view(), name='list_create_proof_screenshot_view'),
    path('screenshots/<int:pk>/', RetrieveDestroyProofScreenshotView.as_view(), name='retrieve_destroy_proof_screenshot_view'),

    path('transactions/', ListCreateTransactionsView.as_view(), name='list_create_transactions_view'),
    path('transactions/<int:pk>/', RetrieveUpdateDestroyTransactionView.as_view(), name='retrieve_update_destroy_transaction_view'),

    path('transactions/forward/', CreateForwardedTransactionView.as_view(), name='create_forwarded_transactions_view'),
    path('transactions/forwarded/<int:pk>/', RetrieveUpdateDestroyForwardedTransactionView.as_view(), name='retrieve_update_destroy_forwarded_transactions_view'),
    path('transactions/linked/', ListMyForwardedTransactions.as_view(), name='list_my_forwarded_transactions_view'),
    path('transactions/trace/<int:pk>/', ListForwardedTransactionsForTransactionView.as_view(), name='list_forwarded_transactions_for_transaction_view'),

    path('banks/<int:pk>/', RetrieveBankDetailsView.as_view(), name='retrieve_bank_details_view'),

    path('students/my/', ListMyClassStudentsView.as_view(), name="list_my_class_students_view"),
]