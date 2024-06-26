
from fastapi import FastAPI, File, UploadFile
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import pandas as pd
from io import BytesIO
from typing import List
from docx import Document

app = FastAPI()
custom_directory = "C:\\Users\\mpudi\\xlsx_docx"

def xlsx_to_formatted_text_pdf(input_xlsx_bytes: bytes, output_pdf_path: str):
    df = pd.read_excel(BytesIO(input_xlsx_bytes))

    pdf = SimpleDocTemplate(output_pdf_path, pagesize=letter)

    styles = getSampleStyleSheet()
    styleN = styles['BodyText']

    elements = []

    for index, row in df.iterrows():
        record = {col: str(value) for col, value in row.items()}
        record_str = "{{" + ", ".join([f'"{key}": "{value}"' for key, value in record.items()]) + "}}"
        elements.append(Paragraph(record_str, styleN))
        elements.append(Spacer(1, 12))

    pdf.build(elements)

def docx_to_pdf(input_docx_bytes: bytes, output_pdf_path: str):
    document = Document(BytesIO(input_docx_bytes))
    pdf = SimpleDocTemplate(output_pdf_path, pagesize=letter)
    styles = getSampleStyleSheet()
    styleN = styles['BodyText']
    elements = []
    for para in document.paragraphs:
        elements.append(Paragraph(para.text, styleN))
        elements.append(Spacer(1, 12))

    pdf.build(elements)

@app.post("/convert/")
async def convert_to_pdf(files: List[UploadFile] = File(...)):
    for file in files:
        file_bytes = await file.read()
        file_extension = file.filename.split('.')[-1].lower()
        output_pdf_path = f"{custom_directory}/{file.filename.split('.')[0]}.pdf"
        
        if file_extension == 'xlsx':
            xlsx_to_formatted_text_pdf(file_bytes, output_pdf_path)
        elif file_extension == 'docx':
            docx_to_pdf(file_bytes, output_pdf_path)
        else:
            return {"message": f"Unsupported file type: {file_extension}"}

    return {"message": "Conversion successful"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
