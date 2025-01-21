from django.contrib import admin

# Register your models here.

from features.bot.models import Conversation

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    """Conversation admin class."""
    list_display = ("user_id", "conversation_id", "timestamp")
    search_fields = ("user_id", "conversation_id")
    ordering = ("id",)
    list_filter = ("timestamp",)
    date_hierarchy = "timestamp"
    readonly_fields = ("timestamp",)
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "user_id",
                    "conversation_id",
                    "timestamp",
                ),
            },
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                "fields": (
                    "user_id",
                    "conversation_id",
                ),
            },
        ),
    )
    actions = ["delete_selected"]  # noqa: RUF012

    def get_readonly_fields(self, request, obj=None):
        """Return readonly fields."""
        if obj:
            return (*self.readonly_fields, "user_id", "conversation_id")
        return self.readonly_fields
