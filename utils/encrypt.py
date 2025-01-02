import ast

from cryptography import fernet
from django.conf import settings

__encoder = fernet.Fernet(str(settings.FILE_INFO_SECRET_KEY).encode("utf-8"))


def __get_file_info_encode(file_info: dict) -> str:
    """Encodes and encrypts file information into a string.

    Args:
        file_info (dict): The file information to be encoded and encrypted.

    Returns:
        str: The encrypted string representation of the file information.
    """
    return __encoder.encrypt(str(file_info).encode("utf-8")).decode("utf-8")


def __get_file_info_decode(file_info_hash: str) -> dict:
    """Decrypts and decodes file information from a string.

    Args:
        file_info_hash (str): The encrypted string representation of the file information.

    Returns:
        dict: The decrypted and decoded file information.
    """
    decrypted_str = __encoder.decrypt(file_info_hash.encode("utf-8")).decode("utf-8")
    return ast.literal_eval(decrypted_str)


def get_s3_key(file_info: dict, file_name_key: str = "file_name") -> str:
    """Generates an S3 key for a file based on its information.

    Args:
        file_info (dict): The information about the file.
        file_name_key (str): The key in the file information dictionary that contains the file name.

    Returns:
        str: A string representing the S3 key for the file.
    """
    return f"{__get_file_info_encode(file_info)}.{file_info[file_name_key].split('.')[-1]}"


def get_file_info(s3_key: str) -> dict:
    """Retrieves file information from an S3 key.

    This function decodes the file information encoded in the S3 key. It splits the S3 key
    to extract the encoded file information and then decodes it to retrieve the original
    file information.

    Args:
        s3_key (str): The S3 key of the file, which contains encoded file information.

    Returns:
        dict: The decoded file information.
    """
    return __get_file_info_decode(s3_key.split(".")[0])
