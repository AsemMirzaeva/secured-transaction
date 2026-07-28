from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/accounts/", include("apps.accounts.urls")),
    path("api/payments/", include("apps.payments.urls")),
    path("api/verification/", include("apps.verification.urls")),
]