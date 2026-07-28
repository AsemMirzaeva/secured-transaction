from django.contrib import admin
from .models import VerificationSession


@admin.register(VerificationSession)
class VerificationSessionAdmin(admin.ModelAdmin):
    list_display = ("id", "transaction", "status", "operator", "created_at")
    list_filter = ("status",)
    search_fields = ("livekit_room_name", "transaction__id")