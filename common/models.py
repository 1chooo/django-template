from typing import Any, ClassVar
from uuid import UUID, uuid4

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser
from django.db import models
from django.utils import timezone

from common.managers import BaseModelManager


class BaseModel(models.Model):
    """Base model for all database models in the application.

    This abstract base model defines common fields and methods for other database models.
    It includes fields for tracking creation and modification timestamps, user associations,
    and soft deletion status. The model is tied to a company.

    Attributes:
        id (UUIDField): The unique identifier for the record.
        created_at (DateTimeField): The timestamp when the record was created.
        created_by_user (ForeignKey): The user who created the record.
        updated_at (DateTimeField): The timestamp when the record was last updated.
        updated_by_user (ForeignKey): The user who last updated the record.
        is_deleted (BooleanField): Indicates if the record is marked as deleted.
        deleted_by_user (ForeignKey): The user who marked the record as deleted.
        company (ForeignKey): The associated company.

    Methods:
        save(self, user: AbstractBaseUser, *args: list[Any], **kwargs: dict[Any, Any]):
            Saves the model instance, updating the modified timestamp and associating the user who updated it.

        create(self, user: AbstractBaseUser, *args: list[Any], **kwargs: dict[Any, Any]):
            Creates and saves a new model instance, associating the user who created it.

        delete(self, user: AbstractBaseUser) -> None:
            Marks the model instance as deleted, associating the user who marked it as deleted.
    """

    id = models.UUIDField(primary_key=True, unique=True, default=uuid4, editable=False)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name="%(class)s_created_by_user",
    )
    updated_at = models.DateTimeField(auto_now=True)
    updated_by_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name="%(class)s_updated_by_user",
    )
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True, default=None)
    deleted_by_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name="%(class)s_deleted_by_user",
    )

    objects = BaseModelManager()

    class Meta:
        abstract = True

    class ExtraMeta:
        date_filter_fields: ClassVar[list[str]] = []

    DEFAULT_EXCLUDE_FIELDS: ClassVar = [
        "created_at",
        "created_by_user",
        "updated_at",
        "updated_by_user",
        "is_delete",
        "deleted_at",
        "deleted_by_user",
    ]
    DEFAULT_GET_EXCLUDE_FIELDS = DEFAULT_EXCLUDE_FIELDS
    DEFAULT_UPDATE_EXCLUDE_FIELDS: ClassVar = [*DEFAULT_EXCLUDE_FIELDS, "id"]
    DEFAULT_CREATE_EXCLUDE_FIELDS: ClassVar = [*DEFAULT_EXCLUDE_FIELDS, "id"]

    def save(self, user: AbstractBaseUser | UUID | str | None = None, *args: list[Any], **kwargs: dict[Any, Any]):
        """Save and update the object with user information.

        This method saves or updates the object and sets the 'updated_by_user' field to the specified user.
        Additionally, any extra keyword arguments provided will be applied to the object.

        Args:
            user (AbstractBaseUser | UUID | str | None): The user responsible for the update.
            *args (list[Any]): Additional positional arguments.
            **kwargs (dict[Any, Any]): Additional keyword arguments to be applied to the object.

        Returns:
            None

        """
        if user is not None:
            if isinstance(user, AbstractBaseUser):
                if self._state.adding:
                    self.created_by_user = user
                self.updated_by_user = user
            else:
                if isinstance(user, str):
                    user = UUID(user)
                if self._state.adding:
                    self.created_by_user_id = UUID(user)
                self.updated_by_user_id = UUID(user)
        super().save(*args, **kwargs)  # type: ignore

    def delete(self, user: AbstractBaseUser | UUID | str | None = None) -> None:
        """Marks this object as deleted and assigns the user responsible for the deletion. (soft delete).

        The `delete` method sets the `is_deleted` flag to True, indicating that the object is deleted,
        and records the `user` responsible for the deletion. After making these changes, it saves
        the object.

        Args:
            user (AbstractBaseUser | UUID | str | None): The user who is marking the record as deleted.

        Returns:
            None

        Note:
            The `save` method is called internally to persist the changes.
        """
        if user is not None:
            if isinstance(user, UUID):
                self.deleted_by_user_id = user
            elif isinstance(user, str):
                self.deleted_by_user_id = UUID(user)
            else:
                self.deleted_by_user = user
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(user)
