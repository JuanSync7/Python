import os
import sys
import argparse
from base_tool import BaseTool
from tooldir_setup import ToolDirSetup
from tool_report import ToolReport
from tool_fix import ToolFix
from logger import Logger
from string_util import StringUtil
from argsparser import Extend, ArgParser
import generate_txt 

import lint_func

class CustomHelpFormatter(argparse.HelpFormatter):
    def _format_usage(self, *args, **kwargs):
        return ""  # Remove usage line
    
    def add_arguments(self, actions):
        pass  # Skip adding arguments to help
    
    def format_help(self):
        # Only return your custom help text
        return generate_txt.lint_report_console()  # Your pre-formatted help

# ======================== Tool: Lint ========================      
class LintTool(BaseTool):
    
    def __init__(self,logger):
        BaseTool.__init__(self,logger) # call __init__ BaseTool
        self.add_subcommands()  # Initialize subcommands
        self._tool_root = self.find_tool_dir(tool_name="lint")
        self.waiver_file = r'${{LINT_RUN_DIR}}/rtl_lint/waivers/'+ '{top}_lint_waivers.tcl'   

        
    def add_subcommands(self):
        self.subparser = self.parser.add_subparsers(help="available lint positional arguments",dest="lint_subcommand")
        
        # create parser for lint
        self.add_args(parser=self.parser,args=self._get_args())

        self.parser.set_defaults(func=self.run)
        
        subparser_dict = self.add_parsers(subparsers=self.subparser,parsers_kwargs=self._get_lint_subparsers())
 
        # create class for lint report
        tool_report = ToolReport(tool='lint',path_dict=self.path_dict,cwd=self._current_dir,git_root=self._git_root,logger=self.logger,subparser=subparser_dict['report'])
        # create class for lint fix
        tool_fix = ToolFix(tool='lint',path_dict=self.path_dict,cwd=self._current_dir,git_root=self._git_root,logger=self.logger,subparser=subparser_dict['fix'])
        # create class for lint setup
        tool_setup = ToolDirSetup(tool='lint',path_dict=self.path_dict,cwd=self._current_dir,git_root=self._git_root,logger=self.logger,subparser=subparser_dict['setup'])
    
    # overwrite BaseTool gen_abspath 
    def gen_abspath(self,opts) -> None:
        super().gen_abspath(opts) # turn any common arguments into abs path
        self.logger.underline("Starting Lint Specific Arguments path Processing...")
        # any lint subcommands that require the absolute path to be generated
        opts.compile_cmd = self.abs_path(path=opts.compile_cmd,var_name="vlog_cmd",strict=False,check_exists=False)
        opts.incremental = self.abs_path(path=opts.incremental,var_name="incremental_database_file",strict=False,check_exists=False)
        self.logger.info("Path processing completed successfully")
        self.logger.line()

    def gen_reports(self,top:str) -> str:
        compile_action = ''
        compile_action += self.line(with_backslash=True,newline=True)
        compile_action += self.close_header(msg='Start Generating Report Commands', count_len=True , level=2, with_backslash=True,symbol='-')
        compile_action += f"  configure output directory report \\\n\
  lint generate report {top}_lint_detail.rpt;\\\n\
  lint generate report -design_audit {top}_lint_design_audit.rpt \\\n\
  lint generate report -group_by_module {top}_lint_by_module.rpt \\\n\
  lint generate report -status \\\n\
  lint generate report -csv {top}_lint.csv \\\n\
  lint generate report -html {top}_lint.html \\\n\
  lint generate report -json {top}_lint.json \\\n\
  configure output directory . \\\n"
        compile_action += '\\\n' + self.line(with_backslash=True,newline=False)
        return compile_action
    
    def _def_prescript(self, opts) -> str:
        """Generate default environment variable settings for the lint script.
        
        Args:
            opts: Namespace object containing configuration options with:
                - febuild: Boolean flag for FE build mode
                - comppath: Component path (for FE builds)
                
        Returns:
            str: Formatted script commands with proper line continuations
        """
        # Log initialization
        self.logger.space()
        self.logger.underline("Generating default environment prescript")
        self.logger.info(f"Lint Run Directory: {self._tool_root}")
        self.logger.info(f"User: {self._user}")
        self.logger.info(f'Top Module: {opts.top}')
        self.logger.info(f"Git root: {self._git_root}")
        self.logger.info(f'Work Directory: {opts.workdir.replace(self._user,r"${USER}")}')

        compile_action = self.line()
        compile_action += self.close_header(msg='DEFAULT LINT ENVIRONMENT VARIABLES',symbol='=',with_backslash=False,count_len=True, level=3)
        compile_action += self.underline(msg='Core environment paths',with_backslash=False)
        compile_action += (
            f'setenv LINT_RUN_DIR {self._tool_root}\n'
            f'setenv GIT_ROOT {self.path_dict["git_root"]}\n'
            f'setenv TOP {opts.top}\n'
            f'setenv WORKDIR {opts.workdir.replace(self._user,r"${USER}")}\n'
        )
        
        compile_action += '\n'
        
        # CompPath configuration
        if not opts.febuild:
            self.logger.info("Standard build mode - using git root for CompPath")
            compile_action += self.underline(msg='Standard build configuration',with_backslash=False)
            compile_action += f'setenv CompPath {os.getenv("CompPath",self.path_dict["git_root"]).replace(self._user,r"${USER}")}\n'
        else:
            self.logger.info(f"FE build mode - using comppath: {opts.comppath}")
            compile_action += (
                '# FE build configuration\n'
                f'setenv CompPath {str(opts.comppath)}\n'
            )

        compile_action += '\n' + self.line(with_backslash=False,newline=False)
        
        self.logger.info(f'Finished adding default prescript directives.')
        self.logger.space()
        return compile_action
    
    def _def_methodology(self, opts) -> str:        
        """Generate lint methodology setup commands with proper path configuration.
        
        This function creates a script block that configures the lint methodology,
        including search paths, custom lint goals, and waiver file configuration.
        
        Args:
            opts: Options object containing configuration settings including 'top'
                which is used to format the waiver file path
        
        Returns:
            str: Formatted script commands for lint methodology configuration with
                all lines properly terminated with backslash continuation characters
        """
        self.logger.underline('Generating lint methodology...')
        compile_action = ''
        compile_action += self.close_header(msg='LINT METHODOLOGY CONFIGURATION',level=2,with_backslash=True, count_len=True,symbol='-')
        compile_action += self.underline(msg='Set methodology search path',with_backslash=True)
        compile_action += f'  lint methodology searchpath {self._questa_run_dir}/lint_goal; \\\n\\\n'
        compile_action += self.underline(msg='Configure custom lint goal',with_backslash=True)
        compile_action += '  lint methodology custom -goal oc_lint; \\\n\\\n'
        compile_action += self.underline(msg='Set default waiver export file',with_backslash=True)
        compile_action += f'  configure status flow -default_export_file {self.waiver_file.format(top=opts.top)} \\\n\\\n'
        self.logger.debug(f'Lint Goal Directory: {self._questa_run_dir}/lint_goal')
        self.logger.debug(f'Lint Goal File: oc_lint')
        self.logger.debug(f'Set Default Waiver File: {self.waiver_file.format(top=opts.top)}')
        self.logger.info('Generated lint methodology.')
        self.logger.space()
        return compile_action
    
    def _def_prerun(self, opts) -> str:
        """Generate pre-execution commands for the compilation/lint script.
        
        Constructs the preliminary commands that run before the main tool execution,
        including environment configuration, path softening, and special mode setups.

        Args:
            opts: Namespace object containing configuration options with attributes:
                - incremental: Path to incremental database (optional)
                - waiver: List of waiver files (optional)
                
        Returns:
            str: Formatted script commands for the pre-execution phase
        """
        compile_action = ''
        self.logger.underline(f"Generating pre-lint analysis directives for compile_lint")
        
        # ------------------------------------------------------------
        # Default Pre-run Section Header
        # ------------------------------------------------------------
        #compile_action += self.line(with_backslash=True)
        #compile_action += self.close_header(msg='DEFAULT PRE-LINT DIRECTIVES', symbol = '-', with_backslash=True, level=2,count_len=True)

        # ------------------------------------------------------------
        # 1. Environment Configuration
        # ------------------------------------------------------------
        compile_action += self.underline(msg='Default Environment Configuration',with_backslash=True)
        compile_action += r'  configure environment CompPath ${CompPath}' + '\\\n'
        compile_action += r'  configure environment TOP ${TOP}' + '\\\n'
        compile_action += r'  configure environment LINT_RUN_DIR ${LINT_RUN_DIR}' + '\\\n'
        compile_action += f'  configure environment soften_paths CompPath \\\n'
        self.logger.debug("Pass CompPath environment variable to Qverify")
        self.logger.debug("Pass TOP environment variable to Qverify")
        self.logger.debug("Pass LINT_RUN_DIR environment variable to Qverify")
        self.logger.debug("Set CompPath variable to Soften absolute path in Qverify")
        
        # ------------------------------------------------------------
        # 2. Incremental Mode Handling
        # ------------------------------------------------------------
        if opts.incremental:
            self.logger.debug(f"Configuring incremental mode with reference: {opts.incremental}")
            compile_action += '\\\n'
            compile_action += self.underline(msg='lint incremental database',with_backslash=True)
            compile_action += f'  lint configure reference {opts.incremental};\\\n'
            
            # Historical note: Previously copied the reference database
            # os.system(f'cp {opts.incremental} Reference/lint_ref.db')
            # opts.incremental = f'lint/Reference/lint_ref.db'
        
        # ------------------------------------------------------------
        # 3. Waiver File Processing
        # ------------------------------------------------------------
        if opts.waiver:
            self.logger.debug(f"Processing {len(opts.waiver)} waiver files for Qverify compile script")
            compile_action += '\\\n'
            compile_action += self.underline(msg='Waiver File Addition',with_backslash=True)
            for waiver in opts.waiver:
                compile_action += f'  do {waiver};\\\n'
            self.logger.debug(f"Loaded {len(opts.waiver)} waiver files")
        
        # ------------------------------------------------------------
        # Section Footer
        # ------------------------------------------------------------
        compile_action += '\\\n'
        self.logger.info("Generated pre-lint analysis directives in compile_lint.")
        self.logger.space()
        return compile_action
    
    def _def_postrun(self,opts) -> str:
        compile_action = self.gen_reports(opts.top)
        # run a lint diff between the 2 lint databases
        if opts.incremental:
            compile_action += f'  lint diff {opts.workdir}/Result/lint.db -refdb {opts.incremental};\\\n'
        
        return compile_action
            
    def _def_postscript(self,opts) -> str:
        compile_action = ''
        compile_action += self.close_header(msg="Begin Postscript Section",with_backslash=False,level=1, symbol='=')
        # move all suffix ending with .rpt to a report folder    
        compile_action += r'mkdir -p ${LINT_RUN_DIR}/rtl_lint/waivers'
        compile_action += f'\ntouch {self.waiver_file.format(top=opts.top)}\n'
        compile_action += r'mv ${WORKDIR}/Results/*.rpt ${WORKDIR}/Results/report/.' +'\n\n'
        return compile_action
    
    def _def_vlog(self,opts):
        self.logger.underline("Generating vlog command in compile_lint")
        compile_action = ''
        compile_action += self.underline(msg='Vlog Commands',with_backslash=True)
        if not opts.febuild:
            if opts.subparser_name == "lint" and opts.compile_cmd:
                compile_action+= f'  {self._vlog} -work {opts.lib} -f ' + opts.compile_cmd + ';\\\n'
            elif opts.filelist:
                compile_action+= f'  {self._vlog} -work {opts.lib} -f ' + opts.filelist + ';\\\n'
            else:
                print("no Filelist can be found.")
                sys.exit(1)
        
        compile_action += '\\\n'
        self.logger.info("Generated vlog command in compile_lint")
        self.logger.space()
        return compile_action
    
    def _get_args(self)-> dict:
        lint_args = {
            'external': {
                'short': '-ext',
                'long': '--external',
                'help': 'Specify if it is an external component',
                'action': 'store_false',
                'default': False
            },
            'incremental': {
                'short': '-incr',
                'long': '--incremental',
                'help': 'specify lint.db file for incremental runs',
                'type': str,
                'default': ""
            },
            'compile_cmd': {
                'short': '-cc',
                'long': '--compile_cmd',
                'help': 'vlog compile command',
                'nargs': '*',
                'action': Extend,
                'type': str,
                'default': []
            }
        }
        return lint_args
    
    def _get_lint_subparsers(self) -> dict:
        parsers_config = {
            "report": {
                "help": "Some setting to help split your lint reports",
                "formatter_class": CustomHelpFormatter,
                "add_help": False
            },
            "fix": {
                "help": "Some function to help fix some lint errors.",
                "formatter_class": CustomHelpFormatter,
                "add_help": False
            },
            "setup": {
                "help": "Specify to create the lint directory tree.",
                "formatter_class": CustomHelpFormatter,
                "add_help": False
            }
        }
        return parsers_config
        
    def generate_parser_help(self)->str:
        su=StringUtil()
        output = []
        
        output.append("")
        output.append(su.underline("Questa QC wrapper script", symbol='double', with_comment_prefix=False, newline=False))
        output.append("This script is made to execute Questa Lint and CDC/RDC jobs using LSF.")
        output.append("")
        # Usage text
        output.append(su.underline("Usage", symbol='double', with_comment_prefix=False, newline=False))
        output.append(su.text_box("""lint <common_arguments> <specific_arguments>
or: cdc <common_arguments> <specific_arguments>
or: rdc <common_arguments> <specific_arguments>""", style="double", language='bash'))
        output.append("")
    
        # Define common headers
        common_headers = ["Short Option", "Long Option", "Description", "Required?", "Data Type", "Default"]

        output.append(su.underline("Lint Flag Arguments", symbol='double', with_comment_prefix=False, newline=False))
        # Generate common_rows from _get_shared_args() dictionary
        args_dict = self._get_flag_args()
        common_rows = []

        # Build rows dynamically
        for arg_name, arg_info in args_dict.items():
            # Get option strings
            short_opt = arg_info.get('short', '')
            long_opts = [arg_info.get('long', '')]
            if 'alt_long' in arg_info:
                long_opts.append(arg_info['alt_long'])
            long_opt = "/".join(long_opts)
            
            # Determine required status
            required = "No"
            
            # Determine data type
            if 'action' in arg_info:
                if arg_info['action'] == 'store_true' or arg_info['action'] == 'store_false':
                    data_type = "Flag"
                    default = "False"  # Override since store_true defaults to False
                else:
                    data_type = "Path"
            else:
                data_type = "Text" if arg_name in ['lib', 'top', 'comppath'] else "Path"
            
            # Add (s) suffix if nargs is + or *
            if 'nargs' in arg_info and arg_info['nargs'] in ('+', '*'):
                data_type += "(s)"
            
            # Get properly formatted default value
            default = self.format_default(arg_info.get('default'))
            
            common_rows.append([
                short_opt,
                long_opt,
                arg_info['help'],  # Description from help text
                required,
                data_type,
                default
            ])

        output.append(su.table(common_headers, common_rows, style="round", align='left'))
        output.append("")


        # Common Arguments
        output.append(su.underline("Lint Run Arguments", symbol='double', with_comment_prefix=False, newline=False))
        
        # Generate common_rows from _get_shared_args() dictionary
        args_dict = self._get_shared_args()
        common_rows = []

        # Build rows dynamically
        for arg_name, arg_info in args_dict.items():
            # Get option strings
            short_opt = arg_info.get('short', '')
            long_opts = [arg_info.get('long', '')]
            if 'alt_long' in arg_info:
                long_opts.append(arg_info['alt_long'])
            long_opt = "/".join(long_opts)
            
            # Determine required status
            required = ("Yes" if arg_name == 'top' or arg_name == 'filelist' else "No")
            
            # Determine data type
            if 'action' in arg_info:
                if arg_info['action'] == 'store_true' or arg_info['action'] == 'store_false':
                    data_type = "Flag"
                    default = "False"  # Override since store_true defaults to False
                else:
                    data_type = "Path"
            else:
                data_type = "Text" if arg_name in ['lib', 'top', 'comppath'] else "Path"
            
            # Add (s) suffix if nargs is + or *
            if 'nargs' in arg_info and arg_info['nargs'] in ('+', '*'):
                data_type += "(s)"
            
            # Get properly formatted default value
            default = self.format_default(arg_info.get('default'))
            
            common_rows.append([
                short_opt,
                long_opt,
                arg_info['help'],  # Description from help text
                required,
                data_type,
                default
            ])

        output.append(su.table(common_headers, common_rows, style="round", align='left'))
        output.append("")
        
        common_rows = []
        args_dict = self._get_gui_args()
        
        # Common Arguments
        output.append(su.underline("GUI Arguments", symbol='double', with_comment_prefix=False, newline=False))
         # Build rows dynamically
        for arg_name, arg_info in args_dict.items():
            # Get option strings
            short_opt = arg_info.get('short', '')
            long_opts = [arg_info.get('long', '')]
            if 'alt_long' in arg_info:
                long_opts.append(arg_info['alt_long'])
            long_opt = "/".join(long_opts)
            
            # Determine required status
            required = 'No'
            
            # Determine data type
            if 'action' in arg_info:
                if arg_info['action'] == 'store_true' or arg_info['action'] == 'store_false':
                    data_type = "Flag"
                    default = "False"  # Override since store_true defaults to False
                else:
                    data_type = "Path"
            else:
                data_type = "Text" if arg_name in ['lib', 'top', 'comppath'] else "Path"
            
            # Add (s) suffix if nargs is + or *
            if 'nargs' in arg_info and arg_info['nargs'] in ('+', '*'):
                data_type += "(s)"
            
            # Get properly formatted default value
            default = self.format_default(arg_info.get('default'))
            
            common_rows.append([
                short_opt,
                long_opt,
                arg_info['help'],  # Description from help text
                required,
                data_type,
                default
            ])
        output.append(su.table(common_headers, common_rows, style="round", align='left'))
        output.append("")

        common_rows = []
        args_dict = self._get_args()
        
        # Common Arguments
        output.append(su.underline("Lint Specific Arguments", symbol='double', with_comment_prefix=False, newline=False))
         # Build rows dynamically
        for arg_name, arg_info in args_dict.items():
            # Get option strings
            short_opt = arg_info.get('short', '')
            long_opts = [arg_info.get('long', '')]
            if 'alt_long' in arg_info:
                long_opts.append(arg_info['alt_long'])
            long_opt = "/".join(long_opts)
            
            # Determine required status
            required = 'No'
            
            # Determine data type
            if 'action' in arg_info:
                if arg_info['action'] == 'store_true' or arg_info['action'] == 'store_false':
                    data_type = "Flag"
                    default = "False"  # Override since store_true defaults to False
                else:
                    data_type = "Path"
            else:
                data_type = "Text" if arg_name in ['lib', 'top', 'comppath'] else "Path"
            
            # Add (s) suffix if nargs is + or *
            if 'nargs' in arg_info and arg_info['nargs'] in ('+', '*'):
                data_type += "(s)"
            
            # Get properly formatted default value
            default = self.format_default(arg_info.get('default'))
            
            common_rows.append([
                short_opt,
                long_opt,
                arg_info['help'],  # Description from help text
                required,
                data_type,
                default
            ])
        output.append(su.table(common_headers, common_rows, style="round", align='left'))
        output.append("")
        
        common_headers = ["Option","Description"]
        
        output.append(su.underline("Lint Subcommands", symbol='double', with_comment_prefix=False, newline=False))
        output.append("These are the available Lint subcommands")
        arg_dict = self._get_lint_subparsers()
        common_rows = []
        for arg_name, arg_info in arg_dict.items():
            help_info = arg_info.get('help','')
        
            common_rows.append([arg_name,help_info])
        
        output.append(su.table(common_headers, common_rows, style="round", align='left'))
        output.append("")
        
        return "\n".join(output)
        