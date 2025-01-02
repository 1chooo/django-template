from typing import ClassVar
from uuid import UUID

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import AbstractUser
from django.db import models

from common.models import BaseModel
from features.core.managers import UserManager
from utils.storage import get_model_file_path


class User(AbstractUser, BaseModel):
    """Custom user model representing a user in the application.

    This custom user model extends the AbstractUser class and provides additional fields and behavior
    specific to the application's requirements.

    Attributes:
        id (UUIDField): The unique identifier for the user.
        company (ForeignKey to Company): The associated company for the user, if applicable.
        name (CharField): The name of the user.
        email (EmailField): The user's email address (used as the login identifier).
        updated_at (DateTimeField): The timestamp when the user record was last updated.
        is_deleted (BooleanField): Indicates if the user record is marked as deleted.
        is_root (BooleanField): Indicates if the user is a root user in a company.
        is_suspend (BooleanField): Indicates if the user is suspended.

    Fields:
        USERNAME_FIELD (str): The field used as the unique identifier for user login (set to "email").
        REQUIRED_FIELDS (list[str]): The list of fields required when creating a user (empty list).

    Methods:
        delete(self) -> None:
            Marks the user record as deleted by setting the 'is_deleted' flag to True and deactivating the user.

    objects (UserManager): The manager for this user model.

    """

    name = models.CharField(
        blank=True,
        max_length=255,
    )
    first_name = None
    last_name = None
    username = None
    email = models.EmailField(
        unique=True,
    )
    avatar = models.ImageField(
        upload_to=get_model_file_path,
        blank=True,
        null=True,
    )
    date_joined = None
    last_login_ip = models.GenericIPAddressField(
        protocol="IPv4",
        blank=True,
        null=True,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: ClassVar = []

    objects = UserManager()

    def delete(self, user: AbstractBaseUser | UUID | str | None = None) -> None:
        """Marks the record as deleted. (Soft delete).

        This method sets the 'is_delete' flag to True, indicating that the record has been marked as deleted.
        The record is then saved to persist the deletion.

        Args:
            user (AbstractBaseUser | UUID | str | None): The user who is marking the record as deleted.

        Returns:
            None

        """
        self.is_active = False
        super().delete(user)
