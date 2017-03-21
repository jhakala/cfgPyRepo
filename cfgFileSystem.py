import os
from .models import Snippet, SnippetHistory, Directory

def mapVersions(history):
  versionArray = []
  for snippet in Snippet.objects.filter(snippetHistory = history):
    versionArray.append((int(snippet.version), str(snippet.content)))
  return versionArray
  
def mapChildren(directory):
  snippetMap = {}
  for subDir in Directory.objects.filter(parentDir = directory.id):
    snippetMap[str(subDir)] = mapChildren(subDir)
  for snippetHistory in SnippetHistory.objects.filter(parentDir = directory.id):
    snippetMap[str(snippetHistory)] = mapVersions(snippetHistory)
  return snippetMap           

def parseMapToFS(snipMap, prefix, fsList):
  for key in snipMap.keys():
    if type(snipMap[key]) is dict:
      fsList.append(("dir", os.path.join(prefix, key)))
      parseMapToFS(snipMap[key], os.path.join(prefix, key), fsList)
    elif type(snipMap[key]) is list:
      fsList.append(("dir", os.path.join(prefix, key)))
      for iVersion in snipMap[key]:
        fsList.append(("file", (os.path.join(prefix, os.path.join(key, str(iVersion[0]))), str(iVersion[1]))))
  
def mapSnippets():
  rootDir = Directory.objects.filter(parentDir = None).first()
  if os.path.exists(str(rootDir.name)):
    os.removedirs(str(rootDir.name))
  os.mkdir(str(rootDir.name))
  masterMap = mapChildren(rootDir)
  fsList = []
  parseMapToFS(masterMap, str(rootDir), fsList)
  print fsList
  for (kind, data) in fsList:
    if kind == "dir":
      os.mkdir(data)
    elif kind == "file":
      (path, content) = data
      with open(path, "w") as cacheFile:
        cacheFile.write(content)
  
    
    
  
  
  
  
