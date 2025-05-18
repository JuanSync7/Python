import os
import sys
import argparse
from base_tool import BaseTool
from logger import Logger
from argsparser import Extend, ArgParser
import generate_txt 

import lint_func
class ToolReport:

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
        subparser.add_argument('-h','--help', action='help',default=argparse.SUPPRESS,help=argparse.SUPPRESS)
        subparser.add_argument('-t','--top',help='top module. Use as identifier',required=True, type=str, default=None)
        subparser.add_argument('-f','--file',help='full report file',required=False, type=str, default='')
        subparser.add_argument('-regexp','--regexp',help="define a regular expression",required=False, type=str, default='')
        subparser.add_argument('-sbm','--split_by_module',help='split the full lint report into different files based on modules',action='store_true',required=False)
        subparser.add_argument('-sbc','--split_by_checks',help='split the full lint report into individual files based on checks',action='store_true',required=False)
        subparser.set_defaults(func=lint_func.lint_fix_handling)