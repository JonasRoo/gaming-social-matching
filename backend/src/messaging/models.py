import uuid
from django.conf import settings
from django.db import models


class Channel(models.Model):
    """
    A chat channel with an arbitrary amount of participating users.
    A channel consists of [0..n] messages.
    """

    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    users = models.ManyToManyField(to=settings.AUTH_USER_MODEL, through="Participant")
    icon = models.URLField(blank=True, null=True)


# NOTE(jonas): we need this surrogate model to facilitate "leaving" of group chats
# Problem being that, to get all messages within a channel,
# we need to query both the "Participant" model and the "Message" model
class Participant(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    channel = models.ForeignKey(to="Channel", on_delete=models.CASCADE, db_index=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("user", "channel")


class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    channel = models.ForeignKey(to="Channel", on_delete=models.CASCADE)
    author = models.ForeignKey(
        to="Participant", db_index=True, on_delete=models.CASCADE
    )
    content = models.TextField()
    timestamp = models.TimeField(auto_now_add=True, editable=False)
