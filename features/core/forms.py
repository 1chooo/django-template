from typing import ClassVar

from allauth.account.forms import SignupForm
from allauth.socialaccount.forms import SignupForm as SocialSignupForm
from django.contrib.auth import forms as admin_forms
from django.forms import EmailField
from django.utils.translation import gettext_lazy as _

from features.core.models import User


class UserAdminChangeForm(admin_forms.UserChangeForm):
    """Form for User Change in the Admin Area."""

    class Meta(admin_forms.UserChangeForm.Meta):
        model = User
        field_classes: ClassVar = {"email": EmailField}


class UserAdminCreationForm(admin_forms.UserCreationForm):
    """Form for User Creation in the Admin Area.

    To change user signup, see UserSignupForm and UserSocialSignupForm.
    """

    class Meta(admin_forms.UserCreationForm.Meta):
        model = User
        fields = ("email",)
        field_classes: ClassVar = {"email": EmailField}
        error_messages: ClassVar = {"email": {"unique": _("This email has already been taken.")}}


class UserSignupForm(SignupForm):
    """Form that will be rendered on a user sign up section/screen.

    Default fields will be added automatically.
    Check UserSocialSignupForm for accounts created from social.
    """


class UserSocialSignupForm(SocialSignupForm):
    """Renders the form when user has signed up using social accounts.

    Default fields will be added automatically.
    See UserSignupForm otherwise.
    """
