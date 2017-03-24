from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views import generic
from django.utils import timezone
from django.db.models import Max
from itertools import chain

from .models import Snippet, SnippetHistory, Directory

from cfgFileSystem import mapSnippets

# Views for making a web interface to view and edit the snippets
# John Hakala, 3/21/2017

# Helper method for channeling the user to the correct destination
def getRefererID(referer, tag):
  refererID = ""
  if referer is not None:
    url = referer.split("/")
    if tag in url:
      refererID = url[url.index(tag) + 1]
  return refererID

# This is minimalistic as of right now -- it just provides a link to the root dir
class IndexView(generic.ListView):
    template_name = 'cfgRepo/home.html'
    context_object_name = 'dir_list'

    def get_queryset(self):
        return Directory.objects.filter(parentDir = None)

# Lists all snippet histories within a directory
class DirectoryView(generic.ListView):
  model = Directory
  template_name = "cfgRepo/dir.html"
  context_object_name = 'dir_list'
  
  def fullPath(self):
    fullPath = []
    ancestor = Directory.objects.filter(id = self.kwargs['pk']).first()
    while  ancestor is not None:
      fullPath.append(ancestor.name);
      ancestor = Directory.objects.filter(name = ancestor.parentDir).first()
    fullPath.reverse()
    print fullPath
    return "/".join(fullPath)

  def get_queryset(self):
    return {"thisDir"          : self.fullPath(),
            "subdirs"          : Directory.objects.filter(parentDir = self.kwargs['pk']),
            "snippetHistories" : SnippetHistory.objects.filter(parentDir = self.kwargs['pk']) }

# Shows info about a snippet
class SnippetView(generic.DetailView):
  model = Snippet
  template_name = "cfgRepo/snippet.html"

# Shows a list of the snippet's versions
class SnippetHistoryView(generic.ListView):
  model = SnippetHistory
  template_name = "cfgRepo/snippetHistory.html"
  context_object_name = 'version_list'

  def get_queryset(self):
      return Snippet.objects.filter(snippetHistory = self.kwargs['pk']).order_by('-version')

# Interface for making a new version of a snippet
class UpdateSnippetView(generic.CreateView):
  model = Snippet
  template_name = "cfgRepo/updateSnippet.html"
  fields = ['snippetHistory', 'tag', 'content']

  def get_initial(self):
    snippetHistoryID = getRefererID(self.request.META.get('HTTP_REFERER'), "snippetHistory")
    if snippetHistoryID:
      return {"snippetHistory" : get_object_or_404(SnippetHistory, id=snippetHistoryID)}

  def form_valid(self, form):
    newSnippet = form.save(commit=False)
    newSnippet.date=timezone.now()
    otherVersions = Snippet.objects.filter(snippetHistory = newSnippet.snippetHistory)
    latestVersion = otherVersions.aggregate(Max('version'))['version__max']
    otherVersions.filter(tag = newSnippet.tag).update(tag = "")
    if latestVersion is None:
      latestVersion = 0
    newSnippet.version=latestVersion+1
    newSnippet.save()
    mapSnippets()
    return HttpResponseRedirect("snippet/%i" % newSnippet.id)

# Interface for making a new snippet to track in the repo
class CreateSnippetHistoryView(generic.CreateView):
  model = SnippetHistory
  fields = ['snippetName', 'parentDir']
  template_name = "cfgRepo/createSnippetHistory.html"

  def get_initial(self):
    eirID =  getRefererID(self.request.META.get('HTTP_REFERER'), "dir")
    if dirID:
      return {"parentDir" : get_object_or_404(Directory, id=dirID)}

  def form_valid(self, form):
    newSnippetHistory = form.save(commit=False)
    newSnippetHistory.save()
    return HttpResponseRedirect("snippetHistory/%i" % newSnippetHistory.id)

# Interface for creating a new directory
class CreateDirectoryView(generic.CreateView):
  model = Directory
  fields = ['name', 'parentDir']
  template_name = "cfgRepo/createDir.html"

  def get_initial(self):
    dirID =  getRefererID(self.request.META.get('HTTP_REFERER'), "dir")
    if dirID:
      return {"parentDir" : get_object_or_404(Directory, id=dirID)}

  def form_valid(self, form):
    newDir = form.save(commit=False)
    newDir.save()
    return HttpResponseRedirect("dir/%s" % newDir.id)
