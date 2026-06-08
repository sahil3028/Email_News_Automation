from django.contrib import admin

from .models import Campaign, Delivery, Recipient


@admin.register(Recipient)
class RecipientAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "created_at")
    search_fields = ("name", "email")


class DeliveryInline(admin.TabularInline):
    model = Delivery
    extra = 0
    readonly_fields = ("recipient", "email", "status", "error", "sent_at")


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ("topic", "status", "total_recipients", "delivered_count", "failed_count", "created_at")
    inlines = [DeliveryInline]
