from __future__ import unicode_literals
import os

import datetime

from django.db import models
from django.utils import timezone

# Models for the representing the stuff we need to keep track of wrt cfg snippets
# John Hakala, 3/21/2017

# This is basically just a directory
class Directory(models.Model):
  name = models.SlugField(unique = True)
  parentDir = models.ForeignKey("Directory", on_delete=models.CASCADE, null=True)
  def __str__(self):
    #if self.parentDir is not None:
    #  return os.path.join(self.parentDir, self.name) 
    #else:
      return self.name 

# This is the container for all the versions of a snippet.
class SnippetHistory(models.Model):
  # To establish the heirarchy, the history is assigned to one of the directories
  parentDir = models.ForeignKey(Directory, on_delete=models.CASCADE)
  snippetName = models.CharField(max_length=255, unique = True)
  def __str__(self):
     return self.snippetName 


# a model for an HCAL Cfg snippet
class Snippet(models.Model):

  # the snippet history object that this will be added to
  # i.e. each version is an element inside the SnippetHistory object
  snippetHistory = models.ForeignKey(SnippetHistory)
  
  # creation time of this snippet version
  date = models.DateField()

  # version
  version = models.PositiveSmallIntegerField()

  # tag
  tag = models.SlugField(null=True, blank=True)
  
  # the text of the snippet
  content = models.TextField(null=True)
  
  def __str__(self):
    return "%s: version %i" % (self.snippetHistory, self.version)
    
