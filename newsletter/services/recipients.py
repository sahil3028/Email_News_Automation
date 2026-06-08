import csv
import io

from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import IntegrityError

from newsletter.models import Recipient


def normalize_email(email):
    return (email or "").strip().lower()


def import_recipients_from_csv(uploaded_file):
    try:
        text = uploaded_file.read().decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ValueError("CSV must be UTF-8 encoded.") from exc

    reader = csv.DictReader(io.StringIO(text))
    if not reader.fieldnames or {"name", "email"} - set(reader.fieldnames):
        raise ValueError("CSV must include headers: name,email")

    added = skipped = rejected = 0
    seen_in_file = set()

    for row in reader:
        name = (row.get("name") or "").strip()
        email = normalize_email(row.get("email"))

        try:
            validate_email(email)
        except ValidationError:
            rejected += 1
            continue

        if not name:
            rejected += 1
            continue

        if email in seen_in_file:
            skipped += 1
            continue
        seen_in_file.add(email)

        try:
            Recipient.objects.create(name=name, email=email)
            added += 1
        except IntegrityError:
            skipped += 1

    return {"added": added, "skipped": skipped, "rejected": rejected}
