import pdfkit, platform, os, sys, subprocess


#path_wkhtmltopdf = r'C:\Program Files (x86)\wkhtmltopdf\bin\wkhtmltopdf.exe'
#config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)

def _get_pdfkit_config():
     """wkhtmltopdf lives and functions differently depending on Windows or Linux. We
      need to support both since we develop on windows but deploy on Heroku.

     Returns:
         A pdfkit configuration
     """
     if platform.system() == 'Windows':
         return pdfkit.configuration(wkhtmltopdf=os.environ.get('WKHTMLTOPDF_BINARY', 'C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe'))
     else:
         WKHTMLTOPDF_CMD = subprocess.Popen(['which', os.environ.get('WKHTMLTOPDF_BINARY', 'wkhtmltopdf')], stdout=subprocess.PIPE).communicate()[0].strip()
         return pdfkit.configuration(wkhtmltopdf=WKHTMLTOPDF_CMD)

def export_pdf(html,fname,folder):
    pdfkit.from_file(html, fname, configuration=_get_pdfkit_config())