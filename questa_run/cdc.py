import os
import sys
from base_tool import BaseTool
from tooldir_setup import ToolDirSetup

class CdcTool(BaseTool):
    
    def __init__(self,logger):
        super().__init__(logger)
        self.add_subcommands()
        
        self._tool_root = self.find_tool_dir(tool_name="cdc") 
    
    def add_subcommands(self):
        self.subparser = self.parser.add_subparsers(help="available cdc positional arguments",dest="subcommand")
        self.parser.add_argument('-abs', '--abstract', help='Enable abstract mode', action="store_true", required=False)
        self.parser.add_argument('-ign', '--ignore_mismatch', help='Ignore RTL and parameter mismatches while loading HDM database between block-level and top-level runs.', action="store_true", required=False)
        self.parser.add_argument('-itf', '--use_interface_hdm', help='Use interface HDM only', action="store_true", required=False)
        self.parser.add_argument('-hd', '--hierdb', help='QuestaCDC abstract file or .f abstracts filelist', required=False, action='extend', nargs='*', default=[])
        self.parser.add_argument('-cs', '--cons', help='QuestaCDC Constraints file or .f constraints filelist', required=False, action='extend', nargs='*', default=[])
        self.parser.add_argument('-s', '--sdc', help='SDC Constraints file or .f constraints filelist', required=False, action='extend', nargs='*', default=[])
        self.parser.set_defaults(func=self.run)
    
    def gen_abspath(self,opts):
        super().gen_abspath(opts) # turn any common arguments into abs path       
        opts.cons = self.replace_comppath(self.abs_path_list(opts.cons),opts.comppath)
        opts.sdc = self.replace_comppath(self.abs_path_list(opts.sdc),opts.comppath)
        opts.hierdb = self.replace_comppath(self.abs_path_list(opts.hierdb),opts.comppath)

    def gen_reports(self,top:str) -> str:
        compile_action = f'#====================================================================================================\\\n'
        compile_action += f'# Start Generating Report Commands\\\n'
        compile_action += f'#====================================================================================================\\\n'
        compile_action += f"configure output directory report \\\n\
cdc generate report {top}_cdc_detail.rpt;\\\n\
cdc generate crossings -csv {top}_cdc_detail.csv\\\n\
configure output directory . \\\n"
        compile_action+= f'#====================================================================================================\\\n'
        return compile_action


    def _def_prescript(self,opts):
        compile_action = ''
        
        return compile_action
    
    def _def_prerun(self,opts):
        compile_action = ''
        # Prioritise QuestaCDC constraints if available over SDC constraints to avoid redundant constraints
        if opts.cons:
            for cons in opts.cons:
                compile_action+= f'do {cons};\\\n'
        elif opts.sdc:
            for sdc in opts.sdc:
                compile_action+= f'sdc load {sdc};\\\n'
                
        if opts.waiver:
            for waiver in opts.waiver:
                compile_action+= f'do {waiver};\\\n'
        if opts.hierdb:
            for hierdb in opts.hierdb:
                compile_action+= f'cdc load hierdb {hierdb} {"-ignore_mismatch" if opts.ignore_mismatch else ""} {"-use_interface_hdm" if opts.use_interface_hdm else ""};\\\n'
        return compile_action
    
    def _def_methodology(self,opts):
        compile_action = f'set check_type 0\\\ncdc methodology soc -goal release;\\\n'
        return compile_action
    
    def _def_postrun(self,opts):
        compile_action = self.gen_reports(opts.top)
        return compile_action
    
    def _def_postscript(self,opts):
        compile_action = ''
        compile_action += f'mv {opts.workdir}/Results/*.rpt {opts.workdir}/Results/report/ \n'
        return compile_action

    def _def_args(self,opts):
        args=''
        if opts.abstract:
            args="-hcdc"
        return args
