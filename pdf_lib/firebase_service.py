# my_pdf_lib/firebase_pdf_service.py
from .pdf import flatten_pdf_bytes

def download_pdf_from_firebase(bucket, blob_name: str) -> bytes:
    """
    Descarga un PDF del bucket y lo devuelve como bytes.
    """
    blob = bucket.blob(blob_name)
    return blob.download_as_bytes()

def upload_pdf_to_firebase(bucket, pdf_bytes: bytes, blob_name: str):
    """
    Sube un PDF (bytes) al bucket.
    """
    blob = bucket.blob(blob_name)
    blob.upload_from_string(pdf_bytes, content_type='application/pdf')
    print(f"PDF subido a: gs://{bucket.name}/{blob_name}")

def get_pdf(
    bucket,
    source_blob_name: str,
    data: dict,
    local_output_path: str = None,
    upload_blob_name: str = None,
) -> bytes:
    """
    Descarga el PDF 'source_blob_name' del bucket, lo rellena según 'data'
    y:
      - Si 'local_output_path' está presente, lo guarda en disco.
      - Si 'upload_blob_name' está presente, lo sube nuevamente al bucket.
    Retorna los bytes del PDF final.
    """
    # 1) Descargar PDF
    pdf_bytes = download_pdf_from_firebase(bucket, source_blob_name)

    # 2) Rellenar y aplanar
    flattened_pdf_bytes = flatten_pdf_bytes(pdf_bytes, data)

    # 3) Guardar localmente, si procede
    if local_output_path:
        with open(local_output_path, 'wb') as f:
            f.write(flattened_pdf_bytes)
        print(f"PDF final guardado en: {local_output_path}")

    # 4) Subir a bucket, si procede
    if upload_blob_name:
        upload_pdf_to_firebase(bucket, flattened_pdf_bytes, upload_blob_name)

    return flattened_pdf_bytes
