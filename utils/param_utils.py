def compute_target_size(original_size, size_param):
    """
    Calculate target size (width, height) based on original image size and size parameter.

    If size_param is None or belongs to values: "full", "4k", "auto",
    then no resize is performed (returns None).

    Other values will be converted to target megapixels:
      - "preview": 0.25 MP
      - "medium": 1.5 MP
      - "hd": 4 MP
      - "50mp": 50 MP

    Only resize if original image area is larger than target area (avoid upscaling).

    :param original_size: Tuple (width, height) of original image.
    :param size_param: Size parameter as string.
    :return: Tuple (new_width, new_height) if resize needed, or None if not.
    """
    if not size_param:
        return None
    size_param = size_param.lower().strip()
    # If these values, keep original size
    if size_param in ["full", "4k", "auto"]:
        return None
    mapping = {
        "preview": 0.25,
        "medium": 1.5,
        "hd": 4,
        "50mp": 50
    }
    if size_param not in mapping:
        return None
    target_mp = mapping[size_param]  # Target megapixels
    w, h = original_size
    original_area = w * h
    target_area = target_mp * 1e6  # Target area in pixels
    # Only resize if original image is larger than target (avoid upscaling)
    if original_area <= target_area:
        return None
    scale = (target_area / original_area) ** 0.5
    new_w = int(w * scale)
    new_h = int(h * scale)
    return (new_w, new_h)


def get_output_format(fmt_param):
    """Return output format in lowercase, default to 'auto' if not provided."""
    if not fmt_param:
        return "png"
    return fmt_param.lower()