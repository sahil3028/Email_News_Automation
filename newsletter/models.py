from django.db import models


class Recipient(models.Model):
    name = models.CharField(max_length=120)
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        self.email = self.email.strip().lower()
        self.name = self.name.strip()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} <{self.email}>"


class Campaign(models.Model):
    STATUS_DRAFT = "draft"
    STATUS_SENDING = "sending"
    STATUS_SENT = "sent"
    STATUS_PARTIAL = "partial"
    STATUS_FAILED = "failed"

    STATUS_CHOICES = [
        (STATUS_DRAFT, "Draft"),
        (STATUS_SENDING, "Sending"),
        (STATUS_SENT, "Sent"),
        (STATUS_PARTIAL, "Partial"),
        (STATUS_FAILED, "Failed"),
    ]

    topic = models.CharField(max_length=160)
    subject = models.CharField(max_length=220)
    html_body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    total_recipients = models.PositiveIntegerField(default=0)
    delivered_count = models.PositiveIntegerField(default=0)
    failed_count = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.topic} ({self.status})"


class Delivery(models.Model):
    STATUS_SENT = "sent"
    STATUS_FAILED = "failed"

    STATUS_CHOICES = [
        (STATUS_SENT, "Sent"),
        (STATUS_FAILED, "Failed"),
    ]

    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name="deliveries")
    recipient = models.ForeignKey(Recipient, on_delete=models.CASCADE, related_name="deliveries")
    email = models.EmailField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    error = models.TextField(blank=True)
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-sent_at"]
