from urllib.parse import urlencode

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from libraryapp.library_dashboard import get_library_sidebar_links

from libraryapp.models import Book


class LibrarySearchBookView(LoginRequiredMixin, ListView):
    """Searching books"""
    model = Book
    template_name = 'library/search_book.html'
    url_name = 'library-search'

    def check_barcode(self, code):
        barcodes = Book.objects.all().values_list('barcode', flat=True)
        if code in barcodes:
            return True
        else:
            return False

    def get_queryset(self):
        queryset = super(LibrarySearchBookView, self).get_queryset()
        search_text = self.request.GET.get('q')
        if search_text:
            try:
                barcode = int(search_text)
                if self.check_barcode(barcode):
                    queryset = Book.objects.filter(
                        barcode=search_text
                    )
                elif self.check_barcode(search_text[:-1]):
                    queryset = Book.objects.filter(
                        barcode=search_text[:-1]
                    )
            except:
                queryset = Book.objects.filter(
                    Q(title__icontains=search_text) |
                    Q(publisher__name__icontains=search_text) |
                    Q(authors__name__icontains=search_text),
                    availability=True
                ).order_by('-created')
        else:
            queryset = Book.objects.all().order_by('-created')
        page_limit = 30

        # Show 30 applications per page
        paginator = Paginator(queryset, page_limit)
        page = self.request.GET.get('page')
        try:
            queryset = paginator.page(page)
            page = int(page) if page else page
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            page = 1
            queryset = paginator.page(page)
        except EmptyPage:
            # If page is out of range (e.g. 9999),
            # deliver last page of results.
            page = paginator.num_pages
            queryset = paginator.page(page)
        self.kwargs['start'] = (page - 1) * page_limit + 1
        end = page * page_limit
        end = paginator.count if end > paginator.count else end
        self.kwargs['end'] = end

        self.kwargs['total'] = paginator.count
        return queryset

    def get_context_data(self, **kwargs):
        context = super(
            LibrarySearchBookView, self).get_context_data(**kwargs)

        current_path = self.request.path
        query_params = dict(self.request.GET)
        filtered_query_params = {
            key: value[0] for key, value in query_params.items() if key != 'page'
        }
        params = urlencode(filtered_query_params)
        if params:
            current_path += '?' + params
        current_path = current_path + '?' \
            if current_path.find('?') == -1 else current_path + '&'
        context['current_path'] = current_path

        program_slug = self.request.GET.get('program', "plus-two-management")
        context['links'] = get_library_sidebar_links(program_slug)
        return context
