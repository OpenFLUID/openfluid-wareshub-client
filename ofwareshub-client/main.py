
from argparse import ArgumentParser
from ManagementTools import ManagementTools


try:

  Parser = ArgumentParser(prog='ofwareshub-client')
  SubParsers = Parser.add_subparsers(help='sub-command help')

  ReportParser = SubParsers.add_parser("report",help="display report")
  ReportParser.set_defaults(which="report")

  CloneParser = SubParsers.add_parser("clone",help="clone wares from repositories")
  CloneParser.add_argument("-f","--filter-id",help="process wares filtered by given id")
  CloneParser.set_defaults(which="clone")

  BuildParser = SubParsers.add_parser("build", help="build wares")
  BuildParser.add_argument("-f","--filter-id",help="process wares filtered by given id")
  BuildParser.add_argument("-b","--branch")
  BuildParser.add_argument("-g","--grouped",action="store_true")
  BuildParser.set_defaults(which="build")
  
  UpdateParser = SubParsers.add_parser("update", help="upate latest commits from remote")
  UpdateParser.add_argument("-f","--filter-id",help="process wares filtered by given id")
  UpdateGroup = UpdateParser.add_mutually_exclusive_group()
  UpdateGroup.add_argument("-r","--remote")
  UpdateGroup.add_argument("-a","--all",action="store_true")
  UpdateParser.add_argument("-m","--merge-branch")
  UpdateParser.set_defaults(which="update")
  
  Sim2DocParser = SubParsers.add_parser("sim2doc", help="generate doc for wares")
  Sim2DocParser.add_argument("-f","--filter-id",help="process wares filtered by given id")
  Sim2DocParser.add_argument("-b","--branch")
  Sim2DocParser.add_argument("-g","--grouped",action="store_true")  
  Sim2DocParser.set_defaults(which="sim2doc")
        
  CheckParser = SubParsers.add_parser("check", help="check wares configuration and metadata")
  CheckParser.add_argument("-f","--filter-id",help="process wares filtered by given id")
  CheckParser.add_argument("-b","--branch")  
  CheckParser.set_defaults(which="check")
   
    
  Args = Parser.parse_args()

  Args = vars(Args)


  SubCommand = Args["which"];
  del Args["which"];

  ManTools = ManagementTools()  
  
  if SubCommand == "report":
    ManTools.runReport(Args)
  elif SubCommand == "clone":
    ManTools.runClone(Args)
  elif SubCommand == "build":
    ManTools.runBuild(Args)
  elif SubCommand == "update":
    ManTools.runUpdate(Args)        
  elif SubCommand == "sim2doc":
    ManTools.runSim2Doc(Args)
  elif SubCommand == "check":
    ManTools.runCheck(Args)    
    
  del ManTools

  
except Exception as e:
  print "Error:",
  print e
