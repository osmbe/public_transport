from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic

from .models import Operator


class IndexView(generic.ListView):
    template_name = 'operators/index.html'

    def get_queryset(self):
        return Operator.objects.order_by('name')[:50]

class DetailView(generic.DetailView):
    model = Operator
    template_name = 'operators/detail.html'

