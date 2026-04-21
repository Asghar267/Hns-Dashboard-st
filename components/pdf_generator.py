import base64
from fpdf import FPDF
from pathlib import Path
import streamlit as st

def generate_pdf_report(image_paths: list, title: str):
    """
    Generate a PDF from a list of images.
    One image per page.
    """
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    for img_path in image_paths:
        if not Path(img_path).exists():
            continue
            
        pdf.add_page()
        pdf.set_font("helvetica", "B", 16)
        # Using basename for a clean title on each page if needed, 
        # but let's just stick to the image for maximum space.
        # pdf.cell(0, 10, img_path.name, ln=True, align='C')
        
        # Calculate width/height to fit on page (A4 is 210x297mm)
        # Leave some margins.
        pdf.image(str(img_path), x=10, y=20, w=190)
        
    return pdf.output()

def render_pdf_download_button(image_paths: list, filename: str, label: str = "📄 Download PDF Report"):
    """Render a download button for a generated PDF."""
    if not image_paths:
        return
        
    try:
        pdf_bytes = generate_pdf_report(image_paths, filename)
        st.download_button(
            label=label,
            data=pdf_bytes,
            file_name=f"{filename}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    except Exception as e:
        st.error(f"Error generating PDF: {e}")
