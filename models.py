from __future__ import unicode_literals
import os

import datetime

from django.db import models
from django.utils import timezone

class Directory(models.Model):
  name = models.SlugField()
  parentDir = models.ForeignKey("Directory", on_delete=models.CASCADE, null=True)
  def __str__(self):
    #if self.parentDir is not None:
    #  return os.path.join(self.parentDir, self.name) 
    #else:
      return self.name 

class SnippetHistory(models.Model):
  parentDir = models.ForeignKey(Directory, on_delete=models.CASCADE)
  snippetName = models.CharField(max_length=255)
  def __str__(self):
     return self.snippetName 


# a model for an HCAL Cfg snippet
class Snippet(models.Model):

  # the snippet history object that this will be added to
  snippetHistory = models.ForeignKey(SnippetHistory)
  
  # creation time of this snippet version
  date = models.DateField()

  # version
  version = models.PositiveSmallIntegerField()

  # tag
  tag = models.SlugField(null=True)
  
  # the text of the snippet
  content = models.TextField(null=True)
  
  def __str__(self):
    return "%s: version %i" % (self.snippetHistory, self.version)
    
