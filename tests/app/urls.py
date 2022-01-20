# coding: utf-8
from __future__ import unicode_literals

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import path, re_path as url

from .models import ExampleModel


def test_view(request):
    return HttpResponse("OK")


def test_model_view(request, pk):
    obj = get_object_or_404(ExampleModel, pk=pk)

    return HttpResponse(obj.name)


urlpatterns = [url("^$", test_view), path("test/<int:pk>/", test_model_view)]
