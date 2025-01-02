from imghdr import tests


def get_image_type(data: bytes) -> str | None:
    """Get image type from image data."""
    try:
        for tf in tests:
            res = tf(data, None)
            if res:
                return res
    except Exception:
        return None
