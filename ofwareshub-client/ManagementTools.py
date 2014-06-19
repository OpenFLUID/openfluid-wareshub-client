
import os
import stat
import json
import urllib2
import subprocess
import getpass
import tempfile
import shutil

class ManagementTools:
          
  
############################################################################
############################################################################
            
  def __init__(self):

    ConfigFilePath = os.getcwd()+"/ofwareshub-client.conf.json"
        
    if not os.path.isfile(ConfigFilePath):
      raise Exception("Configuration file not found in "+os.getcwd())
    else:
      ConfigContent=open(ConfigFilePath)
      self.LocalConfig = json.load(ConfigContent)
      
    self.TempDir = tempfile.mkdtemp(prefix="ofwhub-client-")
    os.chmod(self.TempDir,stat.S_IRWXU | stat.S_IXGRP | stat.S_IXOTH)


############################################################################
############################################################################

      
  def __del__(self):
    shutil.rmtree(self.TempDir)
    
    
############################################################################
############################################################################


  def isWareCloned(self,WareID):
    if os.path.isdir(os.getcwd()+"/"+WareID):
      return True
    return False
  

############################################################################
############################################################################

 
  def getWareUserGitURL(self,GitURL):    
    if (GitURL.startswith("https://")):
      return GitURL.replace("https://","https://"+self.LocalConfig["username"]+"@")
    if (GitURL.startswith("http://")):
      GitURL.replace("http://","http://"+self.LocalConfig["username"]+"@")

  
############################################################################
############################################################################

  def getRemoteWaresList(self):
    URL = self.LocalConfig["wareshub-report-url"]+"/fluidhub.php?request=wares-list-detailed"
    Content = urllib2.urlopen(URL)
    return json.load(Content)
    

############################################################################
############################################################################


  def cacheUserPassword(self):
    Passwd = getpass.getpass(prompt="Enter the password for user "+self.LocalConfig["username"]+": ")
    F = open(self.TempDir+"/"+"getpass.sh", 'w')
    F.write("#!/usr/bin/env sh\n")
    F.write("echo \""+Passwd+"\"\n")
    F.close()
    os.chmod(self.TempDir+"/"+"getpass.sh",stat.S_IRWXU | stat.S_IRGRP | stat.S_IROTH | stat.S_IXGRP | stat.S_IXOTH)
    

############################################################################
############################################################################


  def getReportData(self):
    RemoteWaresList = self.getRemoteWaresList()

    Report = {}

    RemoteWaresList = RemoteWaresList["wares"][self.LocalConfig["warestype"]]
    Report["cloned"] = {}
    Report["uncloned"] = {}
    
    for WareID in RemoteWaresList:
      if (self.isWareCloned(WareID)) :
        Report["cloned"][WareID] = RemoteWaresList[WareID]
      else:
        Report["uncloned"][WareID] = RemoteWaresList[WareID]
    return Report 


############################################################################
############################################################################


  def runReport(self,Options):
    Report = self.getReportData()
    
    print ""    
    
    print "Cloned wares:"
    print "============="
    for WareID in Report["cloned"].keys():
      print "  +",
      print WareID
   
    print ""
 
    print "Not cloned wares:"
    print "================="
    for WareID in Report["uncloned"].keys():
      print "  -",
      print WareID

    print ""

        
############################################################################
############################################################################


  def runClone(self,Options):
    Report = self.getReportData()
        
    if Report["uncloned"]:
      self.cacheUserPassword()
         
      for WareID, WareInfos in Report["uncloned"].iteritems():
        Command = ["git","clone",self.getWareUserGitURL(WareInfos["git-url"])]
        Env = os.environ.copy()
        Env["GIT_ASKPASS"] = self.TempDir+"/"+"getpass.sh"
        P = subprocess.Popen(Command,env=Env)
        P.wait()
    else:
      print "All available wares are already cloned"    


############################################################################
############################################################################

    
  def runFetch(self,Options):
    Report = self.getReportData()
        
    if Report["cloned"]:
      print "not implemented"
    else:
      print "No ware available"    


############################################################################
############################################################################

    
  def runBuild(self,Options):
    Report = self.getReportData()
        
    if Report["cloned"]:
      print "not implemented"
    else:
      print "No ware available"    

        
############################################################################
############################################################################


  def runSim2Doc(self,Options):
    Report = self.getReportData()
        
    if Report["cloned"]:
      print "not implemented"
    else:
      print "No ware available"    
