def compute_target_size(original_size, size_param):
    """
    Tính toán kích thước mục tiêu (width, height) dựa trên kích thước ảnh gốc và tham số size.

    Nếu size_param là None hoặc thuộc các giá trị: "full", "4k", "auto",
    thì không resize (trả về None).

    Các giá trị khác sẽ được quy đổi thành số megapixels mục tiêu:
      - "preview": 0.25 MP
      - "medium": 1.5 MP
      - "hd": 4 MP
      - "50mp": 50 MP

    Chỉ resize nếu diện tích ảnh gốc lớn hơn diện tích mục tiêu (tránh upscaling).

    :param original_size: Tuple (width, height) của ảnh gốc.
    :param size_param: Tham số size dạng chuỗi.
    :return: Tuple (new_width, new_height) nếu cần resize, hoặc None nếu không.
    """
    if not size_param:
        return None
    size_param = size_param.lower().strip()
    # Nếu các giá trị này, giữ nguyên kích thước gốc.
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
    target_mp = mapping[size_param]  # Megapixel mục tiêu
    w, h = original_size
    original_area = w * h
    target_area = target_mp * 1e6  # Diện tích mục tiêu tính bằng pixel
    # Chỉ resize nếu ảnh gốc lớn hơn mục tiêu (tránh upscaling)
    if original_area <= target_area:
        return None
    scale = (target_area / original_area) ** 0.5
    new_w = int(w * scale)
    new_h = int(h * scale)
    return (new_w, new_h)


def get_output_format(fmt_param):
    """Trả về định dạng output dưới dạng chữ thường, mặc định 'auto' nếu không có."""
    if not fmt_param:
        return "png"
    return fmt_param.lower()