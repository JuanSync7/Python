import os
import sys
import re
import subprocess
import logging
from datetime import datetime
from argparse import RawTextHelpFormatter
from pathlib import Path
from subprocess import check_output,CalledProcessError,DEVNULL
from logger import Logger
import common_py_func as func


def get_git_root():
    try:
        # Run git command to get repo root
        git_root = subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"],
            stderr=subprocess.DEVNULL,
            universal_newlines=True,
        ).strip()
        return git_root
    except subprocess.CalledProcessError:
        return None  # Not in a Git repo
        
CURRENT_DIR = os.getcwd()
QUESTA_RUN_DIR = os.path.abspath(os.path.dirname(__file__))
TOP_MODULE = os.getenv('TOP_MODULE',default=None)
PRJ_ROOT = os.getenv('PRJ_ROOT',default=None)
USER = os.getenv('USER')
WAIVER_FILE = '{dir}/lint_rtl/waivers/{top_module}_lint_waivers.tcl'
LINT_DIR = '{dir}/lint/lint_{mode}'
GIT_ROOT_DIR = get_git_root()

def lint_gui_setup(opts):
    dir_to_use = ''

    print("Running Lint GUI setup...")
    compile_action = ''
    if PRJ_ROOT.startswith("/"): # IF PRJ_ROOT Defined with abspath
        print(f"Using Project Root: {PRJ_ROOT}")
        dir_to_use = PRJ_ROOT
    elif not GIT_ROOT_DIR==None:
        print(f"Using Git Root: {GIT_ROOT_DIR}")
        dir_to_use = GIT_ROOT_DIR
    else:
        print(f"Using Current Directory {CURRENT_DIR}")
        dir_to_use = CURRENT_DIR       
        
    if opts.top == None:
        opts.top = "top"
        print("WARNING: top module not explicitly defined. Given default name: top")
        print(f"Top Module: {opts.top}")
    else:
        print(f"Top Module: {opts.top}")

    waiver_file = WAIVER_FILE.format(dir=dir_to_use,top_module=f'{opts.top}')
    lint_dir = LINT_DIR.format(dir=dir_to_use,mode='rtl')
    print(f"waiver file is: {waiver_file}")
    print(f'Lint Directory is: {lint_dir}')
        
    if not os.path.isfile(waiver_file):
        compile_action += f'\nmkdir -p {lint_dir}/waivers \n'
        compile_action += f'touch {waiver_file} \\\n'
        print(f"create file: {waiver_file} ")
    
    print(f"configure status flow -default_export_file {waiver_file}")
    compile_action += f'configure status flow -default_export_file {waiver_file} \\\n'          

    return compile_action
    
'''def lint_run(opts):
    # remove the workdir/<top_module>/<tool>/
    os.system(f'rm -rf {opts.workdir}/*')
    compile_action = "#!/usr/bin/csh -f\n"
    #TODO need to be in the GIT_ROOT/design/unit/<top>
    compile_action += f'setenv PRJ_ROOT {CURRENT_DIR} \n'
    compile_action += f'setenv USER_WORKAREA /ln/proj/va_10/a0/workareas/{USER}/ \n'
    
    waiver_file = r'${PRJ_ROOT}/lint/lint_rtl/waivers/'+ f'{opts.top}_lint_waivers.tcl'
    
    # store the tool options into a dictionary

    opts_dict = func.parse_tool_opts(opts.tool_opts)

    # change directory to the work directory 
    os.chdir(opts.workdir)
    os.makedirs('Results', exist_ok=True)

    if opts.prescript:
        for script in opts.prescript:
            with open (script, 'r') as f:
                prescript = f.read()
            compile_action+=prescript
            
    if opts_dict:
        vlog = "vlog " + opts_dict.get('vlog', '')
        qverify = "qverify " + opts_dict.get('qverify', '')
        vopt = "vopt " + opts_dict.get('vopt', '')
    else: # if no options are specified, use default values
        vlog = "vlog -64 -sv17compat -svinputport=relaxed -l compile_vl.log"
        qverify = "qverify"
    
    # make the lint waiver directory
    compile_action += '\n'+r'vlib ' + opts.lib
    compile_action += '\n'+r'vmap work ' + opts.lib

    compile_action+= f'\n{qverify} -c -od Results/ -do "\\\n'
    
    # append the lint methodology into compile_action
    compile_action += cmd_act_md.lint_methodology(QUESTA_RUN_DIR,waiver_file)

    # if the incremental option is specified 
    if opts.incremental:
        # move reference lint database into a Reference folder
        os.system(f'cp {opts.incremental} Reference/lint_ref.db')
        # configure the lint reference to point to the new copy of that folder
        opts.incremental = f'lint/Reference/lint_ref.db'
        compile_action+= f'lint configure reference {opts.incremental};\\\n'
    
    if opts.pref_file:
        for pref_file in opts.pref_file:   
            compile_action+= f'do {pref_file};\\\n'
    if opts.pref:
        for pref in opts.pref:   
            compile_action+= f'{pref};\\\n'
            
    if opts.waiver:
        for waiver in opts.waiver:
            compile_action+= f'do {waiver};\\\n'
            
    if not opts.febuild:      
        compile_action += f'{vlog} -work work'

        
    if opts.compile_cmd:
        compile_action+= f' -f ' + opts.compile_cmd + ';\\\n'
    elif not opts.filelist==[]:
        compile_action+= f' -f ' + opts.filelist + ';\\\n'
        
    compile_action += f'{vopt};\\\n'

    lint = r"lint run " + opts_dict.get('lint run', '')
    compile_action+= f'{lint} -d {opts.top};\\\n'
    compile_action+= f'lint generate report lint_detail.rpt;\\\n'
    
    # run a post script
    #compile_action+= f'do {os.path.abspath(os.path.dirname(__file__))}/templates/lint_post.do\\\n'

    # add any do file 
    if opts.dofile:
        for dofile in opts.dofile:
            compile_action+= f'do {dofile};\\\n'
    else:
        compile_action += cmd_act_md.gen_reports() # append the lines for generating reports

    # run a lint diff between the 2 lint databases
    if opts.incremental:
        compile_action += f'lint diff {opts.workdir}/Result/lint.db -refdb {opts.incremental};\\\n'
        
    compile_action+= f'exit;"\n'
    
    if 'suppress' in opts_dict:
        with open("suppressed_error",'w+')as f:
            # Explain any suppression of error messages
            f.write(f'Suppression Explaination: \n')
            for suppress_msg in opts_dict['suppress']:  # Iterate over each message
                f.write(suppress_msg + '\n')   # Append each message + newline

    if opts.postscript:
        for script in opts.postscript:
            with open (script, 'r') as f:
                postscript = f.read()
            compile_action+=postscript
    
    # move all suffix ending with .rpt to a report folder    
    compile_action += '\n'+r'mkdir -p ${PRJ_ROOT}/lint/lint_rtl/waivers'
    compile_action += f'\ntouch {waiver_file}\\\n'
    compile_action+=f'mv {opts.workdir}/Results/*.rpt {opts.workdir}/Results/report/. \n'
      
    with open("compile_"+opts.subparser_name, 'w+') as f:
        f.write(compile_action)
    return "compile_"+opts.subparser_name
'''
def lint_split_by_module(report):
    regex_pattern =  r"Module\s+\d+:\s*(\w+)\s*\n" # Use capture group to obtain the Module name 
    with open(report, 'r') as file:
        content = file.read()
    
    # report split would be:
    # index[0] = summary
    # index[1] = <Module_name1>
    # index[2] = <All violations in Module_name1>
    # index[3] = <Module_name2>
    # ...
    report_split = re.split(regex_pattern, content)
        
        # Create checks directory if needed
    module_dir = os.path.join(os.getcwd(), 'module')
    if not os.path.exists(module_dir):
        os.mkdir(module_dir)
    
    for i,item in enumerate(report_split):
        if i == 0:
            output_path = os.path.join(module_dir, 'lint_summary_module.rpt')
            with open(output_path, 'w') as file:
                file.write(item)
            print(f"lint_summary_module.rpt: file created")
        else:
            if i % 2 == 0: # index is even
                output_path = os.path.join(checks_dir,output_file)
                with open(output_path, 'w') as file:
                    file.write(item)
                print(f"{output_file}: file created")  
            else: # index is odd
                output_file = item
    
                   
def lint_split_by_checks(report):
    regex_pattern = r"Check:\s*(\w+)\s*\n" # Use capture group to obtain the check name
    with open(report, 'r') as file:
        content = file.read()
    
    # report split would be:
    # index[0] = summary
    # index[1] = <Check_name1>
    # index[2] = <All violation of that check>
    # index[3] = <Check_name2>
    # ...
    report_split = re.split(regex_pattern, content)

    # Create checks directory if needed
    checks_dir = os.path.join(os.getcwd(), 'checks')
    if not os.path.exists(checks_dir):
        os.mkdir(checks_dir)
    
    for i,item in enumerate(report_split):
        if i == 0:
            output_path = os.path.join(checks_dir, 'lint_summary_checks.rpt')
            with open(output_file, 'w') as file:
                file.write(item)
            print(f"lint_summary_checks.rpt: file created")
        else:
            if i % 2 == 0: # index is even
                output_path = os.path.join(checks_dir,output_file)
                with open(output_path, 'w') as file:
                    file.write(item)
                print(f"{output_file}: file created")   
            else: # index is odd
                output_file = item
         
def lint_report_handling(opts):
    if not opts.file == '':
        input_file = f'{opts.file}'
    else: # try to locate the default file
        if opts.split_by_checks:
            input_file = f'{opts.workdir}/Results/report/lint.rpt' if os.path.isfile(f'{opts.workdir}/Results/report/lint.rpt') else print("no lint report file")
        elif opts.split_by_module:
            input_file = f'{opts.workdir}/Results/report/lint_full.rpt' if os.path.isfile(f'{opts.workdir}/Results/report/lint_full.rpt') else print("no such file.")
    
    # change directory into the report folder
    os.chdir(f'{opts.workdir}/Results/report')
    
    if opts.split_by_module:
        lint_split_by_module(input_file)
    elif opts.split_by_checks:
        lint_split_by_checks(input_file)
    
    report_action = ''
    with open("report_"+opts.subparser_name, 'w+') as f:
        f.write(report_action)
    return "report_"+opts.subparser_name

def lint_fix_handling(opts):
    #TODO would be just case statement to execute all the specified fix optional arguments
    ''
    
def get_git_root() -> Path:
    """Safely get Git root directory with error handling.
    
    Returns:
        Path: Absolute path to Git root directory if in a Git repo, else None.
    """
    try:
        git_root = Path(
            check_output(
                ["git", "rev-parse", "--show-toplevel"],
                stderr=DEVNULL,
                text=True
            ).strip()
        ).resolve()
        return git_root
    except (CalledProcessError, FileNotFoundError):
        return None  # Not in a Git repo or git not installed
            
if __name__ == "__main__":
    ''