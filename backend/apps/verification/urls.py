from django.urls import path
from . import views

urlpatterns = [
    path("transactions/<uuid:transaction_id>/start/", views.StartVerificationSessionView.as_view(), name="verification-start"),
    path("sessions/<uuid:session_id>/operator-join/", views.OperatorJoinView.as_view(), name="verification-operator-join"),
    path("sessions/<uuid:session_id>/decision/", views.VerificationDecisionView.as_view(), name="verification-decision"),
]