from rest_framework import serializers

from features.bot.models import Conversation


class ConversationSerializer(serializers.ModelSerializer):
    """Conversation serializer."""
    class Meta:
        model = Conversation
        fields = ['user_id', 'conversation_id', 'timestamp']  # noqa: RUF012
