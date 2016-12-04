# -*- coding: utf-8 -*-
from django.conf.urls import url
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    url(
        regex="^User/~create/$",
        view=views.UserCreateView.as_view(),
        name='User_create',
    ),
    url(
        regex="^User/(?P<pk>\d+)/~delete/$",
        view=views.UserDeleteView.as_view(),
        name='User_delete',
    ),
    url(
        regex="^User/(?P<pk>\d+)/$",
        view=views.UserDetailView.as_view(),
        name='User_detail',
    ),
    url(
        regex="^User/(?P<pk>\d+)/~update/$",
        view=views.UserUpdateView.as_view(),
        name='User_update',
    ),
    url(
        regex="^User/$",
        view=views.UserListView.as_view(),
        name='User_list',
    ),
	url(
        regex="^Book/~create/$",
        view=views.BookCreateView.as_view(),
        name='Book_create',
    ),
    url(
        regex="^Book/(?P<pk>\d+)/~delete/$",
        view=views.BookDeleteView.as_view(),
        name='Book_delete',
    ),
    url(
        regex="^Book/(?P<pk>\d+)/$",
        view=views.BookDetailView.as_view(),
        name='Book_detail',
    ),
    url(
        regex="^Book/(?P<pk>\d+)/~update/$",
        view=views.BookUpdateView.as_view(),
        name='Book_update',
    ),
    url(
        regex="^Book/$",
        view=views.BookListView.as_view(),
        name='Book_list',
    ),
	]
