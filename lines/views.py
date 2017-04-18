from django.shortcuts import get_object_or_404, render

from .models import Line

def index(request):
    lines_list = Line.objects.order_by('publicref')
    context = {'lines_list': lines_list,}
    return render(request, 'lines/index.html', context)

def detail(request, line_id):
    line = get_object_or_404(Line, ref=line_id)
    return render(request, 'lines/detail.html', {'line': line})

def results(request, line_id):
    line = get_object_or_404(Line, ref=line_id)
    return render(request, 'lines/detail.html', {'line': line})

