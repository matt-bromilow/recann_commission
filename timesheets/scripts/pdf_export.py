import pdfkit
import os

path_wkhtmltopdf = r'C:\Program Files (x86)\wkhtmltopdf\bin\wkhtmltopdf.exe'
config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)

def export_pdf(html,fname,folder):
    pdfkit.from_file(html, fname, configuration=config)