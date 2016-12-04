import os
from glob import glob
# import PIL
from reportlab.lib.units import inch
# try:
#     from StringIO import StringIO
# except ImportError:
#     from io import StringIO
from reportlab.lib.pagesizes import A4
# from reportlab.lib.utils import ImageReader
# from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate, Image, Table)

# from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, View

from django.http import HttpResponse

from reportlab.graphics import renderPDF
from reportlab.graphics.barcode.eanbc import Ean8BarcodeWidget
from reportlab.graphics.shapes import Drawing
from reportlab.platypus import Flowable

from .models import Book
from reportlab.lib import colors

from libraryapp.library_dashboard import get_library_sidebar_links

# from studentprofile.models import Student

# Creates a table with 2 columns, variable width
colwidths = [2.5*inch, .8*inch]

# Two rows with variable height
rowheights = [.4*inch, .2*inch]

table_style = [
    ('GRID', (0, 1), (-1, -1), 1, colors.white),
    ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
    ('ALIGN', (1, 1), (1, -1), 'RIGHT')
]


# Create your views here.
class LibraryBookView(TemplateView):
    """Adding books"""
    template_name = 'library/add_book.html'

    # def test_func(self):
    #     return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super(
            LibraryBookView, self).get_context_data(**kwargs)

        program_slug = self.request.GET.get('program', "plus-two-management")
        context['links'] = get_library_sidebar_links(program_slug)
        return context


class LibraryListingView(TemplateView):
    """All book listing"""
    template_name = 'library/book_listing.html'

    # def test_func(self):
    #     return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super(
            LibraryListingView, self).get_context_data(**kwargs)

        program_slug = self.request.GET.get('program', "plus-two-management")
        context['links'] = get_library_sidebar_links(program_slug)
        return context


class BarCode(Flowable):

    def __init__(self, value="1234567890", ratio=0.5):
        # init and store rendering value
        Flowable.__init__(self)
        self.value = value
        self.ratio = ratio

    def wrap(self, availWidth, availHeight):
        # Make the barcode fill the width while maintaining the ratio
        self.width = availWidth
        self.height = self.ratio * availWidth
        return self.width, self.height

    def draw(self):
        # Flowable canvas
        # print ('print draw')
        # if self.value == 1111307511111:
        # bar_code = Ean13BarcodeWidget(value=self.value)
        bar_code = Ean8BarcodeWidget(value=self.value)
        # code_39 = barcode.get_barcode_class('code39')
        # bar_code = code_39(
        #     self.value, writer=ImageWriter(), add_checksum=False)
        bounds = bar_code.getBounds()
        # print ('bounds are', bounds)
        # bounds = (0, 0, 105.70393700787403, 73.50236220472442)
        bar_width = bounds[2] - bounds[0]
        bar_height = bounds[3] - bounds[1]
        w = float(self.width)
        # w = 200
        h = float(self.height)
        # h = 100
        # print (w, h)
        d = Drawing(
            w, h,
            transform=[w / bar_width, 0, 0, h / bar_height, 0, 0]
        )
        d.add(bar_code)
        # d.add(self.value)
        renderPDF.draw(d, self.canv, 0, 0)


class PrintBarCodes(View):

    def get_image_name(self, file):
        head, tail = os.path.split(file)

        return tail

    def del_images(self):
        result = [y for x in os.walk(os.getcwd()) for y in
                  glob(os.path.join(x[0], '*.png'))]

        results = [self.get_image_name(file) for file in result]
        results = [file for file in results if file.startswith('ean')]
        for filename in results:
            try:
                os.remove(filename)
            except OSError:
                pass

    def create_image(self, absolute_path):
        image = Image(absolute_path)
        inch = 50
        image._restrictSize(2 * inch, 1 * inch)
        return image

    def get(self, request, format=None):
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment;\
        filename="barcodes.pdf"'

        books = Book.objects.all()
        total = []
        for i in range(0, len(books), 2):
            partial = []
            first = books[i]
            im1 = BarCode(first.barcode)
            partial.append(im1)
            try:
                second = books[i + 1]
                im2 = BarCode(second.barcode)
                partial.append(im2)
            except:
                pass
            total.append(partial)

        # table_data = [total]

        barcode_table = Table(total)
        barcode_table.setStyle(table_style)
        doc = SimpleDocTemplate(response, pagesize=A4)
        parts = []
        parts.append(barcode_table)
        doc.build(parts)
        self.del_images()
        return response
