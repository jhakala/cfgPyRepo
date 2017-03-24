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

# This is minimalistic as of right now -- it just provides a link to the root dir
class IndexView(generic.ListView):
    template_name = 'cfgRepo/home.html'
    context_object_name = 'dir_list'

    def get_queryset(self):
        """List of dirs"""
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
    """List of children dirs"""
    return {"thisDir"          : self.fullPath(),
            "subdirs"          : Directory.objects.filter(parentDir = self.kwargs['pk']),
            "snippetHistories" : SnippetHistory.objects.filter(parentDir = self.kwargs['pk']) }
    
    return children


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
      """List of versions"""
      return Snippet.objects.filter(snippetHistory = self.kwargs['pk']).order_by('-version')

# Interface for making a new version of a snippet
class UpdateSnippetView(generic.CreateView):
  model = Snippet
  template_name = "cfgRepo/updateSnippet.html"
  fields = ['snippetHistory', 'tag', 'content']

  def get_initial(self):
    referer = self.request.META.get('HTTP_REFERER').split("/")
    snippetHistory=""
    if "snippetHistory" in referer:
      snippetHistoryID = referer[referer.index("snippetHistory") + 1]
      print snippetHistoryID
      snippetHistory = get_object_or_404(SnippetHistory, id=snippetHistoryID)  
    return {"snippetHistory" : snippetHistory}

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
    referer = self.request.META.get('HTTP_REFERER').split("/")
    parentDir = ""
    if "dir" in referer:
      dirID = referer[referer.index("dir") + 1]
      print dirID
      parentDir = get_object_or_404(Directory, id=dirID)  
    return {"parentDir" : parentDir}

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
    referer = self.request.META.get('HTTP_REFERER').split("/")
    parentDir = ""
    if "dir" in referer:
      dirID = referer[referer.index("dir") + 1]
      parentDir = get_object_or_404(Directory, id=dirID)  
    return {"parentDir" : parentDir}

  def form_valid(self, form):
    newDir = form.save(commit=False)
    newDir.save()
    return HttpResponseRedirect("dir/%s" % newDir.id)
    
