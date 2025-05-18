from base_tool import BaseTool
import os,sys
import subprocess

class VC_SpyglassLintTool(BaseTool):
    prj_root = os.getenv("PRJ_ROOT")

    def __init__(self,logger):
        super().__init__(logger)
        self.add_subcommands()
        self._tool_root = self.find_tool_dir(tool_name="vclint") 

    def add_subcommands(self):
        self.subparser = self.parser.add_subparsers(help="SpyGlass lint commands", dest="spyglass_subcommand")
        self.parser.add_argument('-s', '--sdc', help='SDC Constraints file or .f constraints filelist', required=False, action='extend', nargs='*', default=[])
        self.parser.set_defaults(func=self.run)

    def gen_abspath(self, opts):
        super().gen_abspath(opts) # turn any common arguments into abs path       
        opts.sdc = self.replace_comppath(self.abs_path_list(opts.sdc),opts.comppath)

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
        os.makedirs('Results', exist_ok=True)
        self.logger.info(f"Make Result Directory {opts.workdir}/Results")
        
        self.logger.info("Begin writing script in compile_lint.")
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

        script_path = os.path.join(opts.workdir, f'vclint_{opts.top}.tcl')
        with open(script_path, 'w') as f:
            f.write(tcl_script)

        print(f"[✔] TCL script generated at: {script_path}")
        print(f"[▶] Running vc_static_shell...")        
        compile_action += "vc_static_shell -f "+ script_path + "| tee vc_shell.log"

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
        # f"set rtl_path \"{opts.rtl_path}\"",
        tcl_script = "set_app_var save_session_default true"
        tcl_script += '\n' + "set_app_var lint_report_same_similar_rules true"
        tcl_script += '\n' + "set_app_var sh_continue_on_error true"
        tcl_script += '\n' + "set_app_var enable_lint true"
        tcl_script += '\n' + f"set DESIGN {opts.top}"
        #tcl_script += '\n' + f"set file_path {opts.filelist}"
        tcl_script += '\n' + """set search_path "."\nset link_library "*"\n"""
        # Add waivers
        for waiver in opts.waiver:
            if waiver.endswith(".awl"):
                tcl_script += '\n' + f'sg_read_waiver -file "{waiver}" -output "{opts.workdir}/waivers/waiver.tcl"'
            else:
                tcl_script += '\n' + f"source {waiver}"

##            "set_app_var search_path \"$rtl_path/modules $rtl_path/includes $rtl_path/includes/axi /technos/ARM7FF/customMacros/cincoranch_macros\"",
        tcl_script += '\n' + f"source {os.path.join(self._questa_run_dir, 'lint_goal', 'lint_rules.tcl')}"
        tcl_script += '\n' + "analyze -verbose -format sverilog -vcs {-f "+opts.filelist+"}"
        tcl_script += '\n' + f"elaborate -verbose $DESIGN"

        for sdc in opts.sdc:
            tcl_script += '\n' + "read_sdc "+sdc
        tcl_script += '\n' + "check_lint"
        tcl_script += '\n' + "set sg_reports {sg_violations_report_xml sg_rules_report_xml sg_moresimple sg_stop_summary sg_summary sg_waiver sg_no_msg_reporting_rules}"
        tcl_script += '\n' + "set outdir .\nfile mkdir $outdir/reports"
        tcl_script += '\n' + "set reports_dir reports"
        tcl_script += '\n' + "report_blackbox > $reports_dir/blackbox.rpt"
        tcl_script += '\n' + "report_violations -verbose -file $reports_dir/report.rpt"
        tcl_script += '\n' + "report_violations -list -limit 0 -file $reports_dir/full_report.rpt"
        tcl_script += '\n' + "report_violations"
        tcl_script += '\n' + "exit"
        return tcl_script

    def gui_mode(self,opts):
        self.gen_abspath(opts=opts)
        command=opts.workdir+'/'+"compile_"+opts.subparser_name+"_gui"
        os.chdir(opts.workdir)
        compile_action="#!/usr/bin/csh -f\n"
        compile_action+="vc_static_shell -restore -gui"

        with open(command,'w+') as f:
            f.write(compile_action)    

        return command
