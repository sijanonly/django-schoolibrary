import datetime
from itertools import chain
from django.shortcuts import get_object_or_404
# from reportlab.graphics.barcode.eanbc import Ean13BarcodeWidget
from reportlab.graphics.barcode.eanbc import Ean8BarcodeWidget
from django.http import Http404
from django.db.models.functions import Length
from rest_framework import generics, status, views
from rest_framework.response import Response

from .serializers import (
    BookSerializer, BookDetailSerializer,
    BookIssueSerializer,
    BookIssueListSerializer,
    BookTypeSerializer
)

from .models import (
    Book, Tag, Author, Publisher, BookBorrow,
    BookType)


class BookTypeList(generics.ListCreateAPIView):
    model = BookType
    serializer_class = BookTypeSerializer
    queryset = BookType.objects.all()


class BookList(generics.ListAPIView):
    model = Book
    serializer_class = BookDetailSerializer
    queryset = Book.objects.all().order_by('-created')
    ordering = ('student',)

    def get_queryset(self):
        """
        This view should return a list of books.
        """
        return Book.objects.all().select_related(
            'book_type',
            'publisher',).prefetch_related(
            'authors',
            'keywords')


class BookMixin(object):
    """
    Mixin to inherit from.
    Here we're setting the query set and the serializer
    """
    serializer_class = BookDetailSerializer
    # queryset = Book.objects.all()


class BookDetailByBarcode(generics.RetrieveAPIView):
    """Return a specific book"""
    serializer_class = BookDetailSerializer
    lookup_fields = ['barcode']
    queryset = Book.objects.all()
    _0csw = 1
    _1csw = 3

    def get_object(self):
        barcode = self.kwargs['barcode']
        barcode_digit = barcode[:-1]
        last_digit = self._checkdigit(barcode_digit)
        book = Book()
        filter = {}
        if last_digit != barcode[-1]:
                if book.check_barcode(barcode):
                    for field in self.lookup_fields:
                        filter[field] = barcode
                else:
                    return
                # if book.check_barcode(barcode_digit):
                #     for field in self.lookup_fields:
                #         filter[field] = barcode

        #     # return
        else:
            barcode = barcode_digit
            for field in self.lookup_fields:
                filter[field] = barcode
        queryset = self.get_queryset()             # Get the base queryset
        queryset = self.filter_queryset(queryset)  # Apply any filter backends
        return get_object_or_404(queryset, **filter)  # Lookup the object

    def _checkdigit(cls, num):
        z = ord('0')
        iSum = cls._0csw*sum([(ord(x)-z) for x in num[::2]]) \
                 + cls._1csw*sum([(ord(x)-z) for x in num[1::2]])
        return chr(z+((8-(iSum%8))%8))
    _checkdigit=classmethod(_checkdigit)

from reportlab.graphics.barcode import code39, code128, code93

class BookBarcodes(views.APIView):

    def get_barcode(self, id):
        return str(datetime.datetime.now().year + id)

    def post(self, request, *args, **kwargs):
        books1 = Book.objects.annotate(
            barcode_len=Length('barcode')).filter(barcode_len=0)
        books2 = Book.objects.exclude(
            barcode__isnull=False)
        books = list(chain(books1, books2))

        for each_book in books:
            # barcode = self.get_barcode(each_book.id)
            # each_book.barcode = Ean13BarcodeWidget(
            #     value=str(each_book.id)).value
            barcode_id = each_book.id
            barcode_set = True
            while barcode_set:
                # barcode128 = code128.Code128(str(barcode_id))
                barcode128 = Ean8BarcodeWidget(value=str(barcode_id))
                if each_book.check_barcode(barcode128.value):
                    barcode_id += 1
                else:
                    barcode_set = False
            each_book.barcode = barcode128.value
            each_book.availability = True
            each_book.save()
        return Response(True, status=status.HTTP_200_OK)


class StudentBookFines(views.APIView):

    def days_between(self, d2):
        today_date = datetime.date.today()
        d1 = datetime.datetime.strptime(str(today_date), "%Y-%m-%d")
        d2 = datetime.datetime.strptime(str(d2), "%Y-%m-%d")
        return (d2 - d1).days

    def get(self, request, id, format=None):
        fine_status = {'fine': False}
        book_issues = BookBorrow.objects.filter(student__id=id)
        for each_book in book_issues:
            issue_day = self.days_between(each_book.due_date)
            if issue_day < 0:
                each_book.late_fee = abs(issue_day) * 5
                each_book.save()
                fine_status['fine'] = True
        return Response(fine_status, status=status.HTTP_200_OK)

    def put(self, request, id, format=None):
        fine_status = {'fine': False}
        book_issues = BookBorrow.objects.filter(student__id=id)
        for each_book in book_issues:
            if each_book.late_fee:
                each_book.late_fee = None
                each_book.due_date = datetime.date.today()
                each_book.save()
        return Response(fine_status, status=status.HTTP_200_OK)


class BookDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Return a specific book, update it, or delete it.
    """
    model = Book
    serializer_class = BookSerializer
    queryset = Book.objects.all()

    def put(self, request, *args, **kwargs):
        copies = request.data.get('number_of_copies', None)
        if copies is None:
            copies = 1
        else:
            copies = int(copies)
        tags = request.data.get('keywords', None)
        authors = request.data.get('authors', None)
        publisher = request.data.get('publisher', None)
        keywords = []
        authors_list = []
        book = Book.objects.get(id=int(request.data.get('id', None)))
        if tags:
            for each_tag in tags:
                tag, created = Tag.objects.get_or_create(
                    name=each_tag['text'])
                keywords.append(tag.id)
        if authors:
            for each_author in authors:
                author, created = Author.objects.get_or_create(
                    name=each_author['name'])
                authors_list.append(author.id)
        if publisher:
            publisher_obj, created = Publisher.objects.get_or_create(
                name=publisher['name'],
                publication_year=publisher['publication_year'],
                publication_place=publisher['publication_place']
            )
        book_type = request.data.get('book_type', None)
        book_type = book_type['id'] if book_type is not None else None
        number_of_pages = request.data.get('number_of_pages', None)
        total_data = []
        book_obj = Book.objects.get(id=book.id)
        book_obj_copies = book_obj.number_of_copies
        data = {
            'id': book.id,
            'title': request.data.get('title', None),
            'subject': request.data.get('subject', None),
            'ISBN': request.data.get('ISBN', None),
            'edition': request.data.get('edition', None),
            'availability': request.data.get('availability', None),
            'book_type': book_type,
            'number_of_pages':
                int(number_of_pages)
                if number_of_pages is not None else None,
            'number_of_copies': copies,
            'authors': authors_list,
            'book_class': request.data.get('book_class', None),
            'language': request.data.get('language', None),
            'keywords': keywords if keywords else None,
            'publisher': publisher_obj.id
        }
        if book_obj_copies is None and copies:
            if copies == 1:
                pass
            elif copies > 1:
                for each_copy in range(copies - 1):
                    data = {
                        'title': request.data.get('title', None),
                        'subject': request.data.get('subject', None),
                        'ISBN': request.data.get('ISBN', None),
                        'edition': request.data.get('edition', None),
                        'book_type': book_type,
                        'availability': False,
                        'number_of_pages':
                            int(number_of_pages)
                            if number_of_pages is not None else None,
                        'number_of_copies': copies,
                        'authors': authors_list,
                        'book_class': request.data.get('book_class', None),
                        'language': request.data.get('language', None),
                        'keywords': keywords if keywords else None,
                        'publisher': publisher_obj.id
                    }
                    total_data.append(data)
                serializer = BookSerializer(data=total_data, many=True)
                if serializer.is_valid():
                    serializer.save()
        elif book_obj_copies is not None and copies is not None:
            copies = int(copies)
            if book_obj_copies < copies:
                book_list = Book.objects.filter(
                    title=request.data.get('title', None),
                    ISBN=request.data.get('ISBN', None))
                for each_book in book_list:
                    each_book.number_of_copies = copies
                    each_book.save()
                more_copies = copies - book_obj_copies
                for each_copy in range(more_copies):
                    data = {
                        'title': request.data.get('title', None),
                        'subject': request.data.get('subject', None),
                        'ISBN': request.data.get('ISBN', None),
                        'edition': request.data.get('edition', None),
                        'book_type': book_type,
                        'availability': False,
                        'number_of_pages':
                            int(number_of_pages)
                            if number_of_pages is not None else None,
                        'number_of_copies': copies,
                        'authors': authors_list,
                        'book_class': request.data.get('book_class', None),
                        'language': request.data.get('language', None),
                        'keywords': keywords if keywords else None,
                        'publisher': publisher_obj.id
                    }
                    total_data.append(data)
                serializer = BookSerializer(data=total_data, many=True)
                if serializer.is_valid():
                    serializer.save()
        serializer = BookSerializer(book, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BookPost(generics.CreateAPIView):
    model = Book
    serializer_class = BookSerializer

    def check_validity(self, request):
        title = request.data.get('title', None)
        error = {}
        data = {}
        if title is None:
            data['message'] = ["Title field is required."]
            error['msg'] = data
            error['error'] = True
            return error

        subject = request.data.get('subject', None)
        if subject is None:
            data['message'] = ["Subject field is required."]
            error['msg'] = data
            error['error'] = True
            return error
        isbn = request.data.get('isbn', None)
        if isbn is None:
            data['message'] = ["ISBN field is required."]
            error['msg'] = data
            error['error'] = True
            return error
        edition = request.data.get('edition', None)
        if edition is None:
            data['message'] = ["Edition field is required."]
            error['msg'] = data
            error['error'] = True
            return error
        book_class = request.data.get('book_class', None)
        if book_class is None:
            data['message'] = ["Book Class is required."]
            error['msg'] = data
            error['error'] = True
            return error
        # pages = request.data.get('number_of_pages', None)
        # if pages is None:
        #     data['message'] = ["Number of pages field is required."]
        #     error['msg'] = data
        #     error['error'] = True
        #     return error
        tags = request.data.get('tags', None)
        if tags is None or len(tags) == 0:
            data['message'] = ["Keywords field is required."]
            error['msg'] = data
            error['error'] = True
            return error
        authors = request.data.get('authors', None)
        if authors is None or len(authors) == 0:
            data['message'] = ["Authors field is required."]
            error['msg'] = data
            error['error'] = True
            return error
        publisher = request.data.get('publisher', None)
        if publisher is None or len(publisher) == 0:
            data['message'] = ["Publisher field is required."]
            error['msg'] = data
            error['error'] = True
            return error
        publisher = request.data.get('publisher', None)
        if publisher is None or len(publisher) == 0:
            data['message'] = ["Publisher field is required."]
            error['msg'] = data
            error['error'] = True
            return error
        else:
            error['error'] = False
            return error

    def post(self, request, *args, **kwargs):
        check_field = self.check_validity(request)
        if check_field['error']:
            return Response(
                check_field['msg'],
                status=status.HTTP_400_BAD_REQUEST)

        copies = request.data.get('number_of_copies', None)
        tags = request.data.get('tags', None)
        authors = request.data.get('authors', None)
        publisher = request.data.get('publisher', None)
        keywords = []
        authors_list = []
        if copies is None or len(copies) == 0:
            copies = 1
        else:
            copies = int(copies)
        total_data = []
        if tags:
            for each_tag in tags:
                    tag, created = Tag.objects.get_or_create(
                        name=each_tag['text'])
                    keywords.append(tag.id)
        if authors:
            for each_author in authors:
                    author, created = Author.objects.get_or_create(
                        name=each_author['name'])
                    authors_list.append(author.id)
        if publisher:
            publisher_keys = list(publisher.keys())
            if 'publication_year' not in publisher_keys:
                data = {}
                data['message'] = ["Publication year is required"]
                return Response(
                    data,
                    status=status.HTTP_400_BAD_REQUEST)
            if 'publication_place' not in publisher_keys:
                data = {}
                data['message'] = ["Publication place is required"]
                return Response(
                    data,
                    status=status.HTTP_400_BAD_REQUEST)
            publisher_obj, created = Publisher.objects.get_or_create(
                name=publisher['name'],
                publication_year=publisher['publication_year'],
                publication_place=publisher['publication_place']
            )
        book_type = request.data.get('book_type', None)
        book_type = book_type['id'] if book_type is not None else None
        number_of_pages = request.data.get('number_of_pages', None)
        for each_copy in range(copies):
            data = {
                'title': request.data.get('title', None),
                'subject': request.data.get('subject', None),
                'ISBN': request.data.get('isbn', None),
                'edition': request.data.get('edition', None),
                'book_type': book_type,
                'availability': False,
                'number_of_pages':
                    int(number_of_pages)
                    if number_of_pages is not None else None,
                'number_of_copies': int(copies),
                'authors': authors_list,
                'book_class': request.data.get('book_class', None),
                'language': request.data.get('language', None),
                'keywords': keywords,
                'publisher': publisher_obj.id
            }
            total_data.append(data)

        serializer = BookSerializer(data=total_data, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST)


