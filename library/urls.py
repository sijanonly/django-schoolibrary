"""Application URL."""
from django.conf.urls import url
from libraryapp.admin_views import (
    LibraryBookView, LibraryListingView,
    LibraryBookIssueView,
    LibraryBookReturnView,
    PrintBarCodes)

from libraryapp.api import (
    BookPost, BookList, BookDetail,
    BookDetailByBarcode,
    BookIssuePost,
    BookIssuesByStudent,
    BookBarcodes,
    BookIssueUpdate,
    BookIssueByBarcode,
    StudentBookFines,
    BookTypeList)

from library.views import (
    LibrarySearchBookView
)


urlpatterns = [

    url(
        r'search/$',
        LibrarySearchBookView.as_view(),
        name='search-book'
    ),

    url(
        r'^print_barcodes/$',
        PrintBarCodes.as_view(),
        name='print_book_barcodes'
    ),


    url(
        r'add/$',
        LibraryBookView.as_view(),
        name='add'),

    url(
        r'listing/$',
        LibraryListingView.as_view(),
        name='listing'),

    url(
        r'issue/$',
        LibraryBookIssueView.as_view(),
        name='issue'),

    url(
        r'return/$',
        LibraryBookReturnView.as_view(),
        name='return'),

    url(
        r'^api/book/post/$',
        BookPost.as_view(),
        name='book-post'),

    url(
        r'^api/book/list/$',
        BookList.as_view(),
        name='book-list'),

    url(
        r'^api/book-type/list/$',
        BookTypeList.as_view(),
        name='book-type-list'),

    url(
        r'^api/book/update/(?P<pk>[0-9]+)$',
        BookDetail.as_view(),
        name='book-detail'
    ),

    url(
        r'^api/book/update_barcodes/$',
        BookBarcodes.as_view(),
        name='book_barcodes'
    ),

    url(
        r'^api/book/(?P<barcode>[-\w]+)$',
        BookDetailByBarcode.as_view(),
        name='book_detail'
    ),

]
