from django.utils import timezone

from newsletter.models import Campaign, Delivery, Recipient

from .email_formatting import build_digest_html, build_subject
from .email_sender import send_email
from .news import fetch_news


def preview_campaign(topic):
    articles = fetch_news(topic, limit=5)
    return {
        "topic": topic.strip(),
        "subject": build_subject(topic),
        "articles": articles,
        "html": build_digest_html(topic, articles),
    }


def send_campaign(topic):
    recipients = list(Recipient.objects.all())
    if not recipients:
        raise ValueError("Add at least one recipient before sending.")

    preview = preview_campaign(topic)
    campaign = Campaign.objects.create(
        topic=preview["topic"],
        subject=preview["subject"],
        html_body=preview["html"],
        total_recipients=len(recipients),
        status=Campaign.STATUS_SENDING,
    )

    delivered = failed = 0
    for recipient in recipients:
        status = Delivery.STATUS_SENT
        error = ""
        try:
            send_email(recipient.email, preview["subject"], preview["html"])
            delivered += 1
        except Exception as exc:
            status = Delivery.STATUS_FAILED
            error = str(exc)
            failed += 1

        Delivery.objects.create(
            campaign=campaign,
            recipient=recipient,
            email=recipient.email,
            status=status,
            error=error,
        )

    campaign.delivered_count = delivered
    campaign.failed_count = failed
    campaign.sent_at = timezone.now()
    campaign.status = Campaign.STATUS_SENT if failed == 0 else Campaign.STATUS_PARTIAL if delivered else Campaign.STATUS_FAILED
    campaign.save(update_fields=["delivered_count", "failed_count", "sent_at", "status"])

    return {"campaign_id": campaign.id, "delivered": delivered, "failed": failed}
