from django.urls import path
from . import views, webhooks

urlpatterns = [
    path("transactions/", views.CreateTransactionView.as_view(), name="transaction-create"),
    path("transactions/list/", views.TransactionListView.as_view(), name="transaction-list"),
    path("transactions/<uuid:id>/", views.TransactionDetailView.as_view(), name="transaction-detail"),

    path("webhooks/payme/", webhooks.payme_webhook, name="webhook-payme"),
    path("webhooks/click/", webhooks.click_webhook, name="webhook-click"),
]