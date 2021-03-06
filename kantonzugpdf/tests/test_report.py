import io
import pkg_resources

from kantonzugpdf import ReportZug
from reportlab.lib.units import cm

from PyPDF2 import PdfFileReader

# PyPDF2 does not support Python 3 (github.com/mstamy2/PyPDF2/issues/171)
# we need to use pdfminer (which fails to support Python 2!)
try:
    from pdfminer.pdfparser import PDFParser, PDFDocument
    from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
    from pdfminer.converter import TextConverter
except:
    pass


class TestReport(ReportZug):

    def populate(self):
        self.title = u'report title'
        self.adjust_style()

        # The first page contains the title and table of contents
        self.pdf.h(self.title)
        self.pdf.table_of_contents()
        self.pdf.pagebreak()

        # The second page has some titles and paragraphs
        self.pdf.h1(u'level 1 title 1')
        self.pdf.h2(u'level 2 title 1')
        self.pdf.h3(u'level 3 title 1')
        self.pdf.p(u'This is a paragraph.')
        self.pdf.h3(u'level 3 title 2')
        self.pdf.p(u'This is another paragraph.')
        self.pdf.h2(u'level 2 title 2')
        self.pdf.h3(u'level 3 title 3')
        self.pdf.h4(u'level 4 title 4')
        self.pdf.h5(u'level 5 title 5')
        self.pdf.h6(u'level 6 title 6')
        self.pdf.p(u'And again, a paragraph.')
        self.pdf.pagebreak()

        # The third page contains a table
        self.pdf.h1(u'level 1 title 2')
        self.pdf.table([[u'a', u'b'], [u'c', u'd']], [5 * cm, 10 * cm])
        self.pdf.spacer()
        self.pdf.p(u'Above we see a table.')
        self.pdf.pagebreak()

        # The fourth page a markup paragraph
        markup = """
        <p>
            <img class="image" src="http://example.com/image" alt="image" />
            <span class="text" title="Text">Text</span>
            <a class="link" href="http://example.com" target="_blank">Link</a>
        </p>
        """
        self.pdf.styled_paragraph(markup)
        self.pdf.pagebreak()

        # The fifth and sixth pages images
        image = pkg_resources.resource_filename(
            'kantonzugpdf', 'resources/logo_zug.png'
        )
        self.pdf.image(image, 0.8)
        self.pdf.pagebreak()
        self.pdf.image(image, 1.2)
        self.pdf.pagebreak()


def extract_pdf_pages_p2(pdf):
    return [page.extractText() for page in PdfFileReader(pdf).pages]


def extract_pdf_pages_p3(pdf):
    parser = PDFParser(pdf)
    doc = PDFDocument()
    parser.set_document(doc)
    doc.set_parser(parser)
    doc.initialize('')
    assert doc.is_extractable

    pages = []
    rsrcmgr = PDFResourceManager()
    for page in doc.get_pages():
        result = io.StringIO()
        device = TextConverter(rsrcmgr, result)
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        interpreter.process_page(page)
        pages.append(result.getvalue())
        result.close()
        device.close()
    return pages


def test_report():
    pages = []
    try:
        pages = extract_pdf_pages_p2(TestReport().build())
    except:
        pass
    if not pages:
        pages = extract_pdf_pages_p3(TestReport().build())

    assert len(pages) == 6

    page = pages[0]
    assert u'report title' in page
    assert u'1 level 1 title 1' in page
    assert u'1.1 level 2 title 1' in page
    assert u'1.1.1 level 3 title 1' in page
    assert u'1.1.2 level 3 title 2' in page
    assert u'1.2 level 2 title 2' in page
    assert u'1.2.1 level 3 title 3' in page
    assert u'1.2.1.1 level 4 title 4' in page
    assert u'1.2.1.1.1 level 5 title 5' in page
    assert u'1.2.1.1.1.1 level 6 title 6' in page
    assert u'2 level 1 title 2'
    assert u'This is a paragraph.' not in page
    assert u'This is another paragraph.' not in page
    assert u'And again, a paragraph.' not in page

    page = pages[1]
    assert u'1 level 1 title 1' in page
    assert u'1.1 level 2 title 1' in page
    assert u'1.1.1 level 3 title 1' in page
    assert u'1.1.2 level 3 title 2' in page
    assert u'1.2 level 2 title 2' in page
    assert u'1.2.1 level 3 title 3' in page
    assert u'1.2.1.1 level 4 title 4' in page
    assert u'1.2.1.1.1 level 5 title 5' in page
    assert u'1.2.1.1.1.1 level 6 title 6' in page
    assert u'This is a paragraph.' in page
    assert u'This is another paragraph.' in page
    assert u'And again, a paragraph.' in page
    assert u'report title' in page
    assert u'Print date:' in page

    page = pages[2]
    assert u'report title' in page
    assert u'Print date:' in page
    assert u'2 level 1 title 2' in page
    assert u'a\nb\nc\nd\n' in page or u'abcd' in page
    assert u'Above we see a table.' in page

    page = pages[3]
    assert u'Text' in page
    assert u'Link' in page
