from rest_framework import serializers
from libraryapp.models import (
    Book, Tag, Publisher, Author,
    BookBorrow, BookType)


class BookTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = BookType


class TagSerializer(serializers.ModelSerializer):
    text = serializers.SerializerMethodField('get_tag_name')

    class Meta:
        model = Tag
        fields = ('text',)

    def get_tag_name(self, obj):
        return obj.name


class PublisherSerializer(serializers.ModelSerializer):

    class Meta:
        model = Publisher


class AuthorSerializer(serializers.ModelSerializer):

    class Meta:
        model = Author


class BookDetailSerializer(serializers.ModelSerializer):
    keywords = TagSerializer(many=True)
    publisher = PublisherSerializer(read_only=True)
    book_type = BookTypeSerializer(read_only=True)
    authors = PublisherSerializer(many=True)
    # student = serializers.SerializerMethodField('get_book_issue')

    class Meta:
        model = Book
        fields = (
            'id', 'title', 'subject',
            'ISBN', 'publisher', 'authors',
            'edition', 'availability', 'keywords',
            'number_of_pages', 'number_of_copies',
            'barcode', 'book_type',
            'language', 'book_class', 'student',)

    # def get_book_issue(self, obj):
    #     # print ('test', obj.borrowed_book.all())
    #     users = {}

    #     for each in obj.borrowed_book.all():
    #         users['name'] = each.student.entrance_application.user.get_full_name()
    #         users['library_id'] = each.student.library_card_number

    #     return users


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = (
            'id', 'title', 'subject',
            'ISBN', 'publisher', 'authors',
            'edition', 'availability', 'keywords',
            'number_of_pages', 'number_of_copies', 'book_type',
            'language', 'book_class',)
