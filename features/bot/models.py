# models.py
from django.db import models
from django.utils import timezone


class Conversation(models.Model):
    """Conversation model."""

    user_id = models.CharField(max_length=255)
    conversation_id = models.CharField(max_length=255)
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "conversations"

    def __str__(self) -> str:
        """Return the string representation of the model."""
        return f"{self.user_id} - {self.conversation_id}"
