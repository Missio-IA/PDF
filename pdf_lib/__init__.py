# my_pdf_lib/__init__.py
from .pdf import flatten_pdf_bytes
from .firebase_service import (
    download_pdf_from_firebase,
    upload_pdf_to_firebase,
    get_pdf
)
