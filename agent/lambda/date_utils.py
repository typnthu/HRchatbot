from datetime import datetime

def convert_date_to_standard(date_str):
    """
    Chuyển đổi ngày về định dạng yyyy-mm-dd.
    """
    if not date_str or not isinstance(date_str, str):
        raise ValueError("Ngày không hợp lệ hoặc không có giá trị.")

    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return date_str
    except ValueError:
        pass

    try:
        dt = datetime.strptime(date_str, "%d/%m/%Y")
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        pass

    try:
        dt = datetime.strptime(date_str, "%d-%m-%Y")
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        pass

    raise ValueError(
        f"Ngày không hợp lệ: {date_str}. Vui lòng nhập dạng YYYY-MM-DD (ví dụ: 2025-07-11)."
    )
def validate_date(date_str):
    date_std = convert_date_to_standard(date_str)
    return datetime.strptime(date_std, "%Y-%m-%d").date()
