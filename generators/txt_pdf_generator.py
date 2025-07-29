from fpdf import FPDF
# import os


class TxtToPDF:
    def __init__(self, font="Arial", font_size=12, title_font_size=16):
        self.font = font
        self.font_size = font_size
        self.title_font_size = title_font_size
        # self.text_columns(ncols=1, text_align="J")
        # self.line_height = self.font_size * 0.4  # Adjust line spacing based on font size

    def convert(self, txt_path, pdf_path=None, title="Cover Letter"):
        # if not os.path.exists(txt_path):
        #     raise FileNotFoundError(f"File not found: {txt_path}")

        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_font(self.font, size=self.font_size)
        # pdf.set_margin(10)

        # Set maximum width (e.g., 190mm for A4 with 10mm margins)
        max_width = 190

        # Title
        if title:
            pdf.set_font(self.font, size=self.title_font_size, style='B')
            pdf.cell(200, 10, txt=title, ln=True, align='C')
            pdf.ln(10)
            pdf.set_font(self.font, size=self.font_size)

        # with pdf.text_columns() as cols:
        #     cols.write(text=LOREM_IPSUM[:400])
        #     with cols.paragraph(
        #         text_align="J",
        #         top_margin=pdf.font_size,
        #         bottom_margin=pdf.font_size
        #     ) as paragraph:
        #         paragraph.write(text=LOREM_IPSUM[:400])
        #     cols.write(text=LOREM_IPSUM[:400])
        # pdf.output("text_columns.pdf")

        # with pdf.text_columns() as cols:
        # Content
        with open(txt_path, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if line:
                    # pdf.multi_cell(200, 4, txt=line)
                    # pdf.cell(0, 10, txt=line, ln=True)
                    pdf.multi_cell(max_width, 4, txt=line)

                else:
                    pdf.ln(4)  # Add a line break for empty lines

        pdf.output(pdf_path)
        return pdf_path

