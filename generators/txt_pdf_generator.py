from fpdf import FPDF
# import os


class TxtToPDF:
    def __init__(self, font="Arial", font_size=12, title_font_size=16):
        self.font = font
        self.font_size = font_size
        self.title_font_size = title_font_size
        # self.line_height = self.font_size * 0.4  # Adjust line spacing based on font size

    def convert(self, txt_path, pdf_path=None, title="Cover Letter"):
        # if not os.path.exists(txt_path):
        #     raise FileNotFoundError(f"File not found: {txt_path}")

        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_font(self.font, size=self.font_size)

        # Title
        if title:
            pdf.set_font(self.font, size=self.title_font_size, style='B')
            pdf.cell(200, 10, txt=title, ln=True, align='C')
            pdf.ln(10)
            pdf.set_font(self.font, size=self.font_size)

        # Content
        with open(txt_path, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if line:
                    pdf.multi_cell(195, 4, txt=line)
                else:
                    pdf.ln(5)

        pdf.output(pdf_path)
        return pdf_path
