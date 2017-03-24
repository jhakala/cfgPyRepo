import os
import shutil
from .models import Snippet, SnippetHistory, Directory

# Functions for recreating the CfgCVS directory structure
# John Hakala 3/21/17

# compiles a list of available versions
def mapVersions(history):
  versionArray = []
  for snippet in Snippet.objects.filter(snippetHistory = history):
    versionArray.append((int(snippet.version), str(snippet.content), str(snippet.tag)))
  return versionArray
  
# gets all the stuff mapped to one of the database Directory objects
def mapChildren(directory):
  snippetMap = {}
  for subDir in Directory.objects.filter(parentDir = directory.id):
    snippetMap[str(subDir)] = mapChildren(subDir)
  for snippetHistory in SnippetHistory.objects.filter(parentDir = directory.id):
    snippetMap[str(snippetHistory)] = mapVersions(snippetHistory)
  return snippetMap           

# Converts the mapChildren map into a list of directory names
def parseMapToFS(snipMap, prefix, fsList):
  for key in snipMap.keys():
    if type(snipMap[key]) is dict:
      fsList.append(("dir", os.path.join(prefix, key)))
      parseMapToFS(snipMap[key], os.path.join(prefix, key), fsList)
    elif type(snipMap[key]) is list:
      fsList.append(("dir", os.path.join(prefix, key)))
      for (version, content, tag) in snipMap[key]:
        versionPath = os.path.join(prefix, os.path.join(key, str(version)))
        fsList.append(("file", (versionPath, str(content))))
        if len(str(tag)) > 0:
          fsList.append(("link", (os.path.join(prefix, os.path.join(key, str(tag))), versionPath)))
  
# Builds the cfgCVS-type directory structure
def mapSnippets():
  rootDir = Directory.objects.filter(parentDir = None).first()
  #if os.path.exists(str(rootDir.name)):
  #  shutil.rmtree(str(rootDir.name))
  if not os.path.exists(str(rootDir.name)):
    os.mkdir(str(rootDir.name))
  masterMap = mapChildren(rootDir)
  fsList = []
  parseMapToFS(masterMap, str(rootDir), fsList)
  pathToDir = os.getcwd()
  for (kind, data) in fsList:
    if kind == "dir":
      if not os.path.exists(data):
        os.mkdir(data)
    else:
      if kind == "file":
        (path, content) = data
        if not os.path.exists(path):
          with open(path, "w") as cacheFile:
            cacheFile.write(content)
      elif kind == "link":
        (path, version) = data
        if os.path.exists(path):
          os.unlink(path)
        os.symlink(os.path.join(pathToDir, version), path)
