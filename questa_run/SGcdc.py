from base_tool import BaseTool
import os,sys
import subprocess

class SpyglassCDCPlugin(BaseTool):
    prj_root = os.getenv("PRJ_ROOT")

    def __init__(self,logger):
        super().__init__(logger)
        self.add_subcommands()
        self._tool_root = self.find_tool_dir(tool_name="sgcdc") 

    def add_subcommands(self):
        self.subparser = self.parser.add_subparsers(help="SpyGlass cdc commands", dest="spyglasscdc_subcommand")
        self.parser.add_argument('-s', '--sgdc', help='SGDC Constraints file or .f constraints filelist', required=False, action='extend', nargs='*', default=[])
        self.parser.set_defaults(func=self.run)

    def gen_abspath(self, opts):
        super().gen_abspath(opts) # turn any common arguments into abs path       
        opts.sgdc = self.replace_comppath(self.abs_path_list(opts.sgdc),opts.comppath)

    def run(self, opts):

        if not opts.febuild: # if the febuild option is not specified
            # generate absolute paths for files
            self.gen_abspath(opts=opts)
            # turn the filelist into absolute path
            self.logger.info("Turn all relative paths arguments into absolute paths.")
            opts.filelist = self.gen_filelist_abspaths(filelist=opts.filelist,workdir=opts.workdir,comppath=opts.comppath)
        else:
            # generate absolute paths for files
            self.gen_abspath(opts=opts)
            opts.filelist = self.gen_filelist_abspaths(filelist=opts.filelist,workdir=opts.workdir,comppath=opts.comppath,febuild=opts.febuild)
            
        os.chdir(opts.workdir)
        #self.logger.switch_log_file(new_log_file=f"questa_run.log",keep_handlers=False)
        
        self.logger.info(f"Enter work directory {opts.workdir}")
        
        self.logger.info("Begin writing script in compile_sgcdc.")
        compile_action="#!/usr/bin/csh -f\n"
        
        compile_action += self._def_prescript(opts) # run any default prescripts
                
        # if the prescript option is specified
        if opts.prescript:
            compile_action += f'#====================================================================================================\n'
            compile_action += f'# User Specified Prescript...\n'
            compile_action += f'#====================================================================================================\n'
            for prescript in opts.prescript:
                prescript = self._filepath_err_handling(prescript) # handle the fileread and sanitized the filepath
                # Open file with explicit encoding (avoid platform-dependent issues)
                compile_action += f'Reading {prescript}...\n'
                with open(prescript, 'r', encoding='utf-8') as f:
                    content = f.read()
                # Validate content was read (empty files are allowed, but handle if needed)
                if not prescript.strip():
                    self.logger.warning(f"Prescript file is empty: {opts.prescript}")
                compile_action += content
                compile_action += f'Closing {prescript}...\n'
            compile_action += f'#====================================================================================================\n'
        self.parse_tool_opts(opts.tool_opts)

        tcl_script = self.generate_tcl(opts)

        script_path = os.path.join(opts.workdir, f'sgcdc_{opts.top}.prj')
        with open(script_path, 'w') as f:
            f.write(tcl_script)

        print(f"[✔] Project file generated at: {script_path}")
        print(f"[▶] Running sg_shell...")   
        #compile_action += f"{os.path.join(self._questa_run_dir, 'cdc_setup', 'env.spy')}\n"     
        compile_action += "sg_shell < "+ script_path + " |& tee sg_shell.log"

        if opts.postscript:
            compile_action += f'#====================================================================================================\n'
            compile_action += f'# Reading User Specified Postscript: {postscript}\n'
            compile_action += f'#====================================================================================================\n'
            for postscript in opts.postscript:
                postscript = self._filepath_err_handling(postscript)
                with open (postscript, 'r') as f:
                    content = f.read()
                compile_action += content
            compile_action += f'#====================================================================================================\n'
        
        compile_action += self._def_postscript(opts)
        
        with open("compile_"+opts.subparser_name, 'w+') as f:
                    f.write(compile_action)
        return "compile_"+opts.subparser_name

    def generate_tcl(self, opts):
        tcl_script = f"new_project {opts.top} -force"
        tcl_script += '\n' + f"source {os.path.join(self._questa_run_dir, 'cdc_setup', 'sgcdc_default_opts.prj')}"
        tcl_script += '\n' + "read_file -type sourcelist "+opts.filelist
        tcl_script += '\n' + f"set_option top {opts.top}"
        tcl_script += '\n' + "set_option I $env(SPYGLASS_HOME)/auxi/custom_reports"
        tcl_script += '\n' + "set_option report {count moresimple moresimple_csv moresimple_sevclass sign_off summary waiver spyglass_violations no_msg_reporting_rules}"
        tcl_script += '\n' + "set_option enhance_moresimple_csv yes"
        tcl_script += '\n' + f"current_methodology {os.path.join(self._questa_run_dir, 'cdc_setup')}"
        tcl_script += '\n' + "current_goal cdc_verify_struct"

        for sgdc in opts.sgdc:
            tcl_script += '\n' + "read_file -type sgdc "+sgdc

        for waiver in opts.waiver:
            if waiver.endswith(".awl"):
                tcl_script += '\n' + f'read_file -type awl {waiver}'
            else:
                tcl_script += '\n' + f"source {waiver}"

        tcl_script += '\n' + "run_goal"

        tcl_script += '\n' + "write_report moresimple > moresimple.rpt"
        tcl_script += '\n' + "write_report moresimple_csv > moresimple.csv"
        tcl_script += '\n' + f"save_project {opts.top}.prj"

        return tcl_script

    def gui_mode(self,opts):
        self.gen_abspath(opts=opts)
        command=opts.workdir+'/'+"compile_"+opts.subparser_name+"_gui"
        os.chdir(opts.workdir)
        compile_action="#!/usr/bin/csh -f\n"
        compile_action+="spyglass -project "+ f'{opts.top}.prj'

        with open(command,'w+') as f:
            f.write(compile_action)    

        return command
