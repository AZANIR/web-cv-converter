from generate import build_pdf_bytes


def generate_pdf(cv_data: dict, include_header_image: bool = True) -> bytes:
    return build_pdf_bytes(cv_data, include_header_image)
