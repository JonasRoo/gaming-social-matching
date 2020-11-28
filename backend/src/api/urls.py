from django.urls import path, include

app_name = "api"

urlpatterns = [
    # docs
    # messaging
    path("messages/", include("messaging.urls", namespace="messaging")),
]