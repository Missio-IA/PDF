# my_pdf_lib/pdf_flatten.py
import io
from pdfrw import PdfReader, PdfWriter, PageMerge
from reportlab.pdfgen import canvas

ANNOT_KEY = '/Annots'
ANNOT_FIELD_KEY = '/T'
ANNOT_RECT_KEY = '/Rect'
SUBTYPE_KEY = '/Subtype'
WIDGET_SUBTYPE_KEY = '/Widget'

def create_overlay(data, template_page, page_size):
    """
    Crea una página (overlay) con los campos a rellenar.
    """
    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=page_size)
    c.setFont("Times-Roman", 12)

    if template_page.get(ANNOT_KEY):
        for annot in template_page[ANNOT_KEY]:
            if annot.get(SUBTYPE_KEY) == WIDGET_SUBTYPE_KEY:
                field_name = annot.get(ANNOT_FIELD_KEY)
                if field_name:
                    key = field_name.strip("()")
                    if key in data:
                        rect = annot.get(ANNOT_RECT_KEY)
                        if rect:
                            try:
                                llx, lly, urx, ury = [float(x) for x in rect]
                            except Exception as e:
                                print("Error leyendo coordenadas:", e)
                                continue
                            x = llx
                            y = lly + 4
                            c.drawString(x, y, data[key])
    c.save()
    packet.seek(0)
    from pdfrw import PdfReader as PdfReaderOverlay
    overlay_pdf = PdfReaderOverlay(packet)
    return overlay_pdf.pages[0]

def flatten_pdf_bytes(pdf_bytes: bytes, data: dict) -> bytes:
    """
    Rellena y aplana un PDF dado en 'pdf_bytes' con el diccionario 'data'.
    Retorna el PDF resultante como bytes.
    """
    input_buffer = io.BytesIO(pdf_bytes)
    template_pdf = PdfReader(input_buffer)

    for page in template_pdf.pages:
        media_box = page.MediaBox
        try:
            page_width = float(media_box[2])
            page_height = float(media_box[3])
        except Exception as e:
            print("Error al obtener el tamaño de la página:", e)
            page_width, page_height = 612, 792

        page_size = (page_width, page_height)
        overlay = create_overlay(data, page, page_size)
        merger = PageMerge(page)
        merger.add(overlay).render()

        # Eliminar anotaciones (aplanar)
        if ANNOT_KEY in page:
            del page[ANNOT_KEY]

    output_buffer = io.BytesIO()
    PdfWriter().write(output_buffer, template_pdf)
    output_buffer.seek(0)
    return output_buffer.read()
