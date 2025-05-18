import os
import sys
import argparse
from logger import Logger
from argsparser import Extend, ArgParser
import generate_txt 

import lint_func

class ToolFix:

    def __init__(self, tool,path_dict, cwd, git_root,logger,subparser):
        self._tool = tool
        self._templates_dir = f"{path_dict['questa_run_dir']}/templates"
        self._cwd = cwd
        self._tool_run_dir = path_dict['current_dir'].replace(path_dict['git_root'],r"${CompPath}")
        self._git_root = path_dict['git_root']
        # Initialize logger
        self.logger = logger
        self.add_subcommands(subparser)
        
    def add_subcommands(self,subparser):
        #self.add_args(subparser,args=self._get_args())
        subparser.add_argument('-f','--file',help='filelist',action=Extend,nargs='*',required=False,type=str,default=[])
        subparser.add_argument('-r','--report',help='report file with checks',required=False,type=str)
        subparser.add_argument('-mm','--multiple_module',help='fix source file having multiple module defined',required=False,action='store_true')
        subparser.set_defaults(func=lint_func.lint_fix_handling)