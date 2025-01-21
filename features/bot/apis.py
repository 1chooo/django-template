from django.core.handlers.wsgi import WSGIRequest
from django.utils import timezone
from ninja_extra import api_controller, route
from ninja_extra.controllers import ControllerBase
from rest_framework import status
from rest_framework.response import Response

from features.bot.models import Conversation
from features.bot.serializers import ConversationSerializer


@api_controller(prefix_or_class="bot", tags=["bot"])
class BotAPI(ControllerBase):
    """Bot API."""

    @route.get("/", tags=["health_check"])
    def api_root_health_check(self, request: WSGIRequest):  # noqa: ARG002
        """Check api health."""
        return {"status": "healthy"}

    @route.post("/conversation", tags=["conversation"])
    def create_conversation(
        self,
        user_id: str,
        conversation_id: str,
    ):
        """Create a conversation."""
        try:
            conversation = Conversation.objects.create(
                user_id=user_id,
                conversation_id=conversation_id,
                timestamp=timezone.now(),
            )

            serializer = ConversationSerializer(conversation)
            return {
                "user_id": serializer.data["user_id"],
                "conversation_id": serializer.data["conversation_id"],
                "timestamp": serializer.data["timestamp"],
            }

        except Exception as e:
            return Response(
                {
                    "status": "error",
                    "message": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
