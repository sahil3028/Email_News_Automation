from django.urls import path

from . import views


app_name = "newsletter"

urlpatterns = [
    path("", views.recipient_list, name="recipients"),
    path("recipients/", views.recipient_list, name="recipients"),
    path("recipients/<int:recipient_id>/delete/", views.delete_recipient, name="delete_recipient"),
    path("recipients/import/", views.import_recipients, name="import_recipients"),
    path("campaigns/", views.campaigns, name="campaigns"),
]
