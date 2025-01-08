from pathlib import Path
from uuid import uuid4

from botocore.config import Config
from django.core.files import File
from django.db import models
from inflection import dasherize, underscore
from storages.backends.s3 import S3Storage


def get_model_file_path(instance: models.Model, filename: str) -> Path:
    """Generate a file path for the uploaded file of model."""
    return (
        Path(dasherize(instance._meta.app_label))
        / dasherize(underscore(instance.__class__.__name__))
        / f"{uuid4()}{Path(filename).suffix}"
    )


class StaticS3Storage(S3Storage):  # noqa: D101
    location = "static"
    default_acl = "public-read"


class MediaS3Storage(S3Storage):  # noqa: D101
    location = "media"
    file_overwrite = False


class MediaS3Boto3Storage(MediaS3Storage):  # noqa: D101
    default_acl = "public-read"
    config = Config(signature_version="s3v4")


class CustomizedMediaS3Boto3Storage(MediaS3Boto3Storage):
    """Customized S3 Boto3 media storage class.

    This class inherits from MediaS3Boto3Storage and allows customization
    of the charset in the Content-Type header when uploading files.

    Parameters:
        charset (str, optional): The charset to set, e.g., 'utf-8'.
            If not specified, the Content-Type will not be modified.
    """

    def __init__(self, charset: str | None = None, *args, **kwargs) -> None:  # noqa: ANN002, ANN003, D107
        super().__init__(*args, **kwargs)
        self.custom_charset = charset

    def _get_write_parameters(self, name: str, content: File) -> dict:
        """Get file upload parameters.

        Override the parent method to add a custom charset to Content-Type.

        Parameters:
            name (str): The file name
            content (File): The file content object

        Returns:
            dict: A dictionary containing the upload parameters
        """
        params = super()._get_write_parameters(name, content)
        if self.custom_charset:
            params["ContentType"] = f'{params["ContentType"]}; charset={self.custom_charset}'

        return params
