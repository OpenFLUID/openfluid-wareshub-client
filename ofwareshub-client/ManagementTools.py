
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
      return GitURL.replace("http://","http://"+self.LocalConfig["username"]+"@")

  
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


  def filterByID(selfself,WareData,FilterStr):
    
    Keys = WareData.keys()

    for K in Keys:
      if FilterStr not in K:
        del WareData[K]
    
    return WareData
    

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

      if Options["filter_id"]:
        Report["uncloned"] = self.filterByID(Report["uncloned"],Options["filter_id"])
        
      self.cacheUserPassword()
         
      for WareID, WareInfos in Report["uncloned"].iteritems():
        
        print "################################################################"
        print " Cloning",
        print WareID
        print "################################################################"
        
        Command = ["git","clone",self.getWareUserGitURL(WareInfos["git-url"])]
        Env = os.environ.copy()
        Env["GIT_ASKPASS"] = self.TempDir+"/"+"getpass.sh"
        P = subprocess.Popen(Command,env=Env)
        P.wait()
        
        print ""
        
    else:
      print "All available wares are already cloned"    


############################################################################
############################################################################

    
  def runUpdate(self,Options):
    
    if Options["merge_branch"] and not Options["remote"]:
      print "-r/--remote option is missing"
      return
    
    Report = self.getReportData()
    
    
    Errors = {}    
    Errors["branch"] = []
    Errors["merge"] = []
        
    if Report["cloned"]:
      
      if Options["filter_id"]:
        Report["cloned"] = self.filterByID(Report["cloned"],Options["filter_id"])
      
      self.cacheUserPassword()
      
      for WareID, WareInfos in Report["cloned"].iteritems():
        
        print "################################################################"
        print " Updating",
        print WareID
        print "################################################################"

        SourceDir = os.path.join(os.getcwd(),WareID)
        
        # checkout branch
        
        Command = ["git","fetch"]
        
        if Options["remote"]:
          Command.append(Options["remote"])  

        if Options["all"]:
          Command.append("--all")
        
        Env = os.environ.copy()
        Env["GIT_ASKPASS"] = self.TempDir+"/"+"getpass.sh"
        
        P = subprocess.Popen(Command,cwd=SourceDir,env=Env)
        P.wait()
        
        if Options["merge_branch"]:
          
          P = subprocess.Popen(["git","checkout",Options["merge_branch"]],cwd=SourceDir)
          P.wait()
          
          if P.returncode == 0:
            P = subprocess.Popen(["git","merge",Options["remote"]+"/"+Options["merge_branch"]],cwd=SourceDir)
            P.wait()
            
            if P.returncode != 0:
              Errors["merge"].append(WareID)
              
          else:
            Errors["branch"].append(WareID)  
                  
        print "" 
                
        
      if len(Errors["branch"]) > 0:
        print "Branch errors:"
          
        for ErrorID in Errors["branch"]:
            print "  -",
            print ErrorID    
      
      if len(Errors["merge"]) > 0:
        print "Merge errors:"
          
        for ErrorID in Errors["config"]:
            print "  -",
            print ErrorID

    else:
      print "No ware available"    


############################################################################
############################################################################

    
  def runBuild(self,Options):

    if not Options["branch"]:
      print "-b/--branch option is missing"
      return
    
    Report = self.getReportData()
    
    Errors = {}    
    Errors["branch"] = []
    Errors["config"] = []
    Errors["build"] = []
     
        
    if Report["cloned"]:
      
      if Options["filter_id"]:
        Report["cloned"] = self.filterByID(Report["cloned"],Options["filter_id"])
      
      for WareID, WareInfos in Report["cloned"].iteritems():
        
        print "################################################################"
        print " Building",
        print WareID
        print "################################################################"
        
        SourceDir = os.path.join(os.getcwd(),WareID)
        BuildDir = os.path.join(os.getcwd(),WareID,"_build-"+Options["branch"])        
        
        # checkout branch
        
        P = subprocess.Popen(["git","checkout",Options["branch"]],cwd=SourceDir)
        P.wait()
        
        if P.returncode == 0:
          # create build dir
          shutil.rmtree(BuildDir,ignore_errors=True)
          os.makedirs(BuildDir)
          
          # configure build
          Command = ["cmake",SourceDir,"-DSIM_SIM2DOC_MODE=off"]
          
          if Options["grouped"] :
            Command = ["cmake",SourceDir,"-DSIM_SIM2DOC_MODE=off",
                       "-DSIM_INSTALL_PATH="+os.path.join(os.getcwd(),"_build-"+Options["branch"])]
          
          P = subprocess.Popen(Command,cwd=BuildDir)
          P.wait()
          
          if P.returncode == 0:      
                                
            # run build          
            Command = ["cmake","--build",BuildDir]
            if Options["grouped"] :
              Command = ["cmake","--build",BuildDir,"--target","install"]
            
            P = subprocess.Popen(Command,cwd=BuildDir)
            P.wait()
          
            if P.returncode != 0 :
              Errors["build"].append(WareID)            
          else:
            Errors["config"].append(WareID)            
        else:
          Errors["branch"].append(WareID)          
        
        print ""
          
        # reporting 
        
      if len(Errors["branch"]) > 0:
        print "Branch errors:"
          
        for ErrorID in Errors["branch"]:
            print "  -",
            print ErrorID    
      
      if len(Errors["config"]) > 0:
        print "Configuration errors:"
          
        for ErrorID in Errors["config"]:
            print "  -",
            print ErrorID

      if len(Errors["build"]) > 0:
        print "Build errors:"
          
        for ErrorID in Errors["build"]:
            print "  -",
            print ErrorID                  

    else:
      print "No ware available"    

        
############################################################################
############################################################################


  def runSim2Doc(self,Options):
    
    print Options
    
    if not Options["branch"]:
      print "-b/--branch option is missing"
      return
    
    Report = self.getReportData()
        
    Errors = {}    
    Errors["branch"] = []
    Errors["config"] = []
    Errors["sim2doc"] = []        
        
    if Report["cloned"]:
      
      if Options["filter_id"]:
        Report["cloned"] = self.filterByID(Report["cloned"],Options["filter_id"])      
      
      for WareID, WareInfos in Report["cloned"].iteritems():
        
        print "################################################################"
        print " Running sim doc on",
        print WareID
        print "################################################################"
        
        SourceDir = os.path.join(os.getcwd(),WareID)
        BuildDir = os.path.join(os.getcwd(),WareID,"_sim2doc-"+Options["branch"])        
        
        # checkout branch
        
        P = subprocess.Popen(["git","checkout",Options["branch"]],cwd=SourceDir)
        P.wait()
        
        if P.returncode == 0:
          # create build dir
          shutil.rmtree(BuildDir,ignore_errors=True)
          os.makedirs(BuildDir)
          
          # configure build
          Command = ["cmake",SourceDir,"-DSIM_SIM2DOC_MODE=on"]
                    
          P = subprocess.Popen(Command,cwd=BuildDir)
          P.wait()                
          
          if P.returncode == 0:
                                
            # run build          
            Command = ["cmake","--build",BuildDir,"--target",WareID+"-doc"]
            
            P = subprocess.Popen(Command,cwd=BuildDir)
            P.wait()
          
            if Options["grouped"] :
              GroupedDir = os.path.join(os.getcwd(),"_sim2doc-"+Options["branch"]) 
              if not os.path.isdir(GroupedDir):
                os.makedirs(GroupedDir)
              shutil.copyfile(os.path.join(BuildDir,WareID+".pdf"), os.path.join(GroupedDir,WareID+".pdf"))
          
          else:    
            Errors["config"].append(WareID)  
        else:
          Errors["branch"].append(WareID)

      print ""
          
      # reporting 
        
      if len(Errors["branch"]) > 0:
        print "Branch errors:"
          
        for ErrorID in Errors["branch"]:
            print "  -",
            print ErrorID    
      
      if len(Errors["config"]) > 0:
        print "Configuration errors:"
          
        for ErrorID in Errors["config"]:
            print "  -",
            print ErrorID

      if len(Errors["sim2doc"]) > 0:
        print "Build errors:"
          
        for ErrorID in Errors["sim2doc"]:
            print "  -",
            print ErrorID                             
    else:
      print "No ware available"    


############################################################################
############################################################################


  def runCheck(self,Options):
    Report = self.getReportData()
    
    if Report["cloned"]:
      
      if Options["filter_id"]:
        Report["cloned"] = self.filterByID(Report["cloned"],Options["filter_id"])
      
      for WareID, WareInfos in Report["cloned"].iteritems():
        
        print "################################################################"
        print " Checking",
        print WareID
        print "################################################################"
        
        print "not implemented"
        
    else:
      print "No ware available"        