
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
  
  FetchParser = SubParsers.add_parser("fetch", help="fetch latest commits for wares")
  FetchParser.add_argument("-f","--filter-id",help="process wares filtered by given id")
  FetchParser.set_defaults(which="fetch")
  
  Sim2DocParser = SubParsers.add_parser("sim2doc", help="generate doc for wares")
  Sim2DocParser.add_argument("-f","--filter-id",help="process wares filtered by given id")
  Sim2DocParser.add_argument("-b","--branch")
  Sim2DocParser.add_argument("-g","--grouped",action="store_true")  
  Sim2DocParser.set_defaults(which="sim2doc")
    
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
  elif SubCommand == "fetch":
    ManTools.runFetch(Args)        
  elif SubCommand == "sim2doc":
    ManTools.runSim2Doc(Args)
    
  del ManTools

  
except Exception as e:
  print "Error:",
  print e