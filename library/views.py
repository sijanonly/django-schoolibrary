# -*- coding: utf-8 -*-
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    UpdateView,
    ListView
)

from .models import (
	User,
	Book,
)


class UserCreateView(CreateView):

    model = User


class UserDeleteView(DeleteView):

    model = User


class UserDetailView(DetailView):

    model = User


class UserUpdateView(UpdateView):

    model = User


class UserListView(ListView):

    model = User


class BookCreateView(CreateView):

    model = Book


class BookDeleteView(DeleteView):

    model = Book


class BookDetailView(DetailView):

    model = Book


class BookUpdateView(UpdateView):

    model = Book


class BookListView(ListView):

    model = Book

