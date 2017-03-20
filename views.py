from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views import generic
from django.utils import timezone
from django.db.models import Max

from .models import Snippet, SnippetHistory, Directory

# Create your views here.
class IndexView(generic.ListView):
    template_name = 'cfgRepo/dir_list.html'
    context_object_name = 'dir_list'

    def get_queryset(self):
        """List of dirs"""
        return Directory.objects.all().order_by('-name')

class DirectoryView(generic.ListView):
  model = Directory
  template_name = "cfgRepo/dir.html"
  context_object_name = 'dir_list'


  
  def get_queryset(self):
    """List of children dirs"""
    return Directory.objects.filter(parentDir = self.kwargs['pk'])

class SnippetView(generic.DetailView):
  model = Snippet
  template_name = "cfgRepo/snippet.html"

class SnippetHistoryView(generic.DetailView):
  model = SnippetHistory
  fields = ['parentDir', 'content']
  template_name = "cfgRepo/snippetHistory.html"
  def form_valid(self, form):
    return HttpResponseRedirect(newSnippet.id)

class UpdateSnippetView(generic.CreateView):
  model = Snippet
  fields = ['snippetHistory', 'tag', 'content']
  def form_valid(self, form):
    newSnippetHistory = form.save(commit=False)
    newSnippetHistory.save()
    return HttpResponseRedirect(newSnippet.id)

class CreateSnippetHistoryView(generic.CreateView):
  model = SnippetHistory
  fields = ['name', 'parentDir']
  template_name = "cfgRepo/createSnippetHistory.html"
  def form_valid(self, form):
    newSnippetHistory = form.save(commit=False)
    newSnippetHistory.save()
    return HttpResponseRedirect("snippetHistory/%s" % newSnippetHistory.id)

class CreateDirectoryView(generic.CreateView):
  model = Directory
  fields = ['name', 'parentDir']
  template_name = "cfgRepo/createDir.html"
  def form_valid(self, form):
    newDir = form.save(commit=False)
    newDir.save()
    return HttpResponseRedirect("dir/%s" % newDir.id)
    
