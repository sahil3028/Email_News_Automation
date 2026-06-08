from django.contrib import messages
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import CampaignForm, CsvImportForm, RecipientForm
from .models import Campaign, Recipient
from .services.campaigns import preview_campaign, send_campaign
from .services.recipients import import_recipients_from_csv


def recipient_list(request):
    if request.method == "POST":
        form = RecipientForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Recipient added.")
                return redirect("newsletter:recipients")
            except IntegrityError:
                messages.error(request, "That email is already in the recipient list.")
        else:
            messages.error(request, "Please enter a valid name and email.")
    else:
        form = RecipientForm()

    return render(
        request,
        "newsletter/recipients.html",
        {
            "form": form,
            "csv_form": CsvImportForm(),
            "recipients": Recipient.objects.all(),
        },
    )


@require_POST
def delete_recipient(request, recipient_id):
    recipient = get_object_or_404(Recipient, pk=recipient_id)
    recipient.delete()
    messages.success(request, "Recipient deleted.")
    return redirect("newsletter:recipients")


@require_POST
def import_recipients(request):
    form = CsvImportForm(request.POST, request.FILES)
    if not form.is_valid():
        messages.error(request, "Choose a CSV file to import.")
        return redirect("newsletter:recipients")

    try:
        result = import_recipients_from_csv(form.cleaned_data["csv_file"])
        messages.success(
            request,
            f"Import complete: {result['added']} added, {result['skipped']} skipped, {result['rejected']} rejected.",
        )
    except ValueError as exc:
        messages.error(request, str(exc))

    return redirect("newsletter:recipients")


def campaigns(request):
    preview = None
    form = CampaignForm(request.POST or None)

    if request.method == "POST":
        action = request.POST.get("action")
        if form.is_valid():
            topic = form.cleaned_data["topic"]
            try:
                if action == "preview":
                    preview = preview_campaign(topic)
                elif action == "send":
                    result = send_campaign(topic)
                    level = messages.SUCCESS if result["failed"] == 0 else messages.ERROR
                    messages.add_message(
                        request,
                        level,
                        f"Campaign sent: {result['delivered']} delivered, {result['failed']} failed.",
                    )
                    return redirect("newsletter:campaigns")
            except (RuntimeError, ValueError) as exc:
                messages.error(request, str(exc))
        else:
            messages.error(request, "Enter a topic before previewing or sending.")

    return render(
        request,
        "newsletter/campaigns.html",
        {
            "form": form,
            "preview": preview,
            "campaigns": Campaign.objects.all()[:10],
            "recipient_count": Recipient.objects.count(),
        },
    )
