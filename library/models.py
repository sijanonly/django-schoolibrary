from autoslug import AutoSlugField

from django.db import models
from django.utils.translation import ugettext_lazy as _
from model_utils.models import TimeStampedModel

from studentprofile.models import Student


class Tag(models.Model):
    """ Class defines the tags for a book. """

    # Attributes:
    name = models.CharField(unique=True, max_length=60)
    slug = AutoSlugField(
        populate_from='name', always_update=True, unique=True)

    # Meta and Strings:
    class Meta:
        verbose_name = _('Tag')
        verbose_name_plural = _('Tags')

    def __str__(self):
        return self.name


class Publisher(models.Model):
    """ Class defines book's publisher """

    # Attributes:
    name = models.CharField(max_length=100)
    publication_year = models.IntegerField(
        ('Publication Year'),
        blank=True,
        null=True
    )
    publication_place = models.CharField(
        max_length=200, blank=True, null=True)

    # Meta and Strings:
    class Meta:
        get_latest_by = "name"
        ordering = ['name']
        verbose_name = _("Publisher")
        verbose_name_plural = _("Publishers")

    def __str__(self):
        return 'Publisher: %s' % self.name


class Author(models.Model):
    """ Class defines book's author """

    # Attributes:
    name = models.CharField(max_length=100)

    # Meta and Strings:
    class Meta:
        get_latest_by = "name"
        verbose_name = _("Author")
        verbose_name_plural = _("Authors")

    def __str__(self):
        return 'Author: ' + self.name


class BookType(models.Model):
    """ Users can borrow books from library for different
    time period. This class defines frequently-used
    lending periods. """

    # Attributes:
    name = models.CharField(max_length=50)
    days_amount = models.IntegerField(blank=True, null=True)

    # Meta and Strings:
    class Meta:
        get_latest_by = "days_amount"
        ordering = ['days_amount']
        verbose_name = _("Book Type")
        verbose_name_plural = _("Book Types")

    def __str__(self):
        return '%s' % self.name


class Book(TimeStampedModel):
    """ A Book class - to describe book in the system. """

    # Relations:
    publisher = models.ForeignKey(
        Publisher,
        blank=True, null=True,
        on_delete=models.SET_NULL,
        related_name='book_publisher'
    )
    book_type = models.ForeignKey(
        BookType,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='book_lend_type'
    )
    authors = models.ManyToManyField(
        Author,
        blank=True,
        verbose_name=("Book Authors"),
        related_name='book_author'
    )
    keywords = models.ManyToManyField(
        Tag,
        blank=True,
        related_name='book_tag'
    )

    # Attributes:
    title = models.CharField(max_length=200)
    subject = models.CharField(max_length=200)
    ISBN = models.CharField(max_length=200, blank=True)
    book_class = models.CharField(max_length=200, blank=True)
    edition = models.CharField(max_length=100, blank=True)
    language = models.CharField(max_length=100, blank=True)
    availability = models.BooleanField(default=False)
    status = models.TextField(blank=True)
    number_of_pages = models.IntegerField(blank=True, null=True)
    number_of_copies = models.IntegerField(blank=True, null=True)
    barcode = models.CharField(
        max_length=500,
        verbose_name=('Barcode'),
        unique=True,
        blank=True, null=True
    )

    # Meta and Strings:
    class Meta:
        ordering = ['created']
        verbose_name = _("Book")
        verbose_name_plural = _("Books")

        permissions = (
            ("add_new_book_as_admin", "Can create new book form as admin"),
            ("update_book_as_admin", "Can update book form as admin"),
            # ("export_book_forms", "Can export book forms"),
            ("delete_book_from_listing", "Can delete book"),
            ("generate_barcode", "Can generate book barcode"),
            ("print_barcode", "Can print book barcode"),
        )

    def __str__(self):
        return 'Book: ' + self.title

    def display_authors(self):
        return u', '.join([a.name for a in self.authors.all()])

    def display_year_published(self):
        "We only care about the year"
        return self.publisher.publication_year

    def check_barcode(self, code):
        barcodes = Book.objects.all().values_list('barcode', flat=True)
        if code in barcodes:
            return True
        else:
            return False
