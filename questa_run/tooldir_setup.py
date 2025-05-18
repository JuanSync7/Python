import os
import sys
import time
import shutil
import stat
from textwrap import dedent
from typing import Optional, Callable
from pathlib import Path
from subprocess import check_output,CalledProcessError,DEVNULL
from string_util import StringUtil
from abspath_tool import AbsPathTool
from argsparser import ArgParser

#from logger import Logger

class ToolDirSetup(AbsPathTool,StringUtil,ArgParser):
    
    def __init__(self, tool,path_dict, cwd, git_root,logger,subparser):
        StringUtil.__init__(self)
        AbsPathTool.__init__(self)
        ArgParser.__init__(self)
        self._tool = tool
        self._templates_dir = f"{path_dict['questa_run_dir']}/templates"
        self._cwd = cwd
        self._tool_run_dir = path_dict['current_dir'].replace(path_dict['git_root'],r"${CompPath}")
        self._git_root = path_dict['git_root']
        # Initialize logger
        self.logger = logger
        self.add_subcommands(subparser)

    def add_subcommands(self,subparser):
        self.add_args(subparser,args=self._get_args())
        subparser.set_defaults(func=self.tool_dir_setup)
    
    def _copy_file(
        self,
        src: str,
        dst: str,
        chunk_size: int = 1024 * 1024,  # 1MB chunks
        max_retries: int = 3,
        retry_delay: float = 1.0,
        progress_callback: Optional[Callable[[int, int], None]] = None,
        verify: bool = True
    ) -> bool:
        """
        Robust file copy with error handling, retries, and verification.
        
        Args:
            src: Source file path
            dst: Destination file path
            chunk_size: Copy chunk size in bytes
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
            progress_callback: Callback function(bytes_copied, total_size)
            verify: Verify copy after completion
        
        Returns:
            bool: True if copy succeeded, False otherwise
        """
        # Validate inputs
        if not os.path.exists(src):
            self.logger.error(f"Source file does not exist: {src}")
            return False
        if os.path.isdir(src):
            self.logger.error(f"Source is a directory, not a file: {src}")
            return False

        last_error = None
        total_bytes = os.path.getsize(src)
        bytes_copied = 0

        for attempt in range(max_retries + 1):
            try:
                # Ensure destination directory exists
                os.makedirs(os.path.dirname(dst), exist_ok=True)

                # Temporary file during copy
                temp_dst = f"{dst}.tmp"

                with open(src, 'rb') as src_file, open(temp_dst, 'wb') as dst_file:
                    while True:
                        chunk = src_file.read(chunk_size)
                        if not chunk:
                            break
                        dst_file.write(chunk)
                        bytes_copied += len(chunk)
                        if progress_callback:
                            progress_callback(bytes_copied, total_bytes)

                # Verify copy if requested
                if verify:
                    if not self._verify_copy(src, temp_dst):
                        raise RuntimeError("Copy verification failed")

                # Atomic rename from temp to final destination
                if os.path.exists(dst):
                    os.replace(temp_dst, dst)
                else:
                    os.rename(temp_dst, dst)

                # Preserve metadata
                self._preserve_metadata(src, dst)

                self.logger.debug(f"Successfully copied {src} to {dst}")
                return True

            except (IOError, OSError, RuntimeError) as e:
                last_error = e
                self.logger.warning(
                    f"Attempt {attempt + 1} failed copying {src} to {dst}: {str(e)}"
                )
                if attempt < max_retries:
                    time.sleep(retry_delay)
                    bytes_copied = 0  # Reset for next attempt
                    continue

        # Clean up failed temp file if it exists
        if os.path.exists(temp_dst):
            try:
                os.remove(temp_dst)
            except OSError as e:
                self.logger.error(f"Failed to clean up temp file {temp_dst}: {str(e)}")

        self.logger.error(
            f"Failed to copy {src} to {dst} after {max_retries + 1} attempts. Last error: {str(last_error)}"
        )
        return False

    def _verify_copy(self, src: str, dst: str) -> bool:
        """Verify that source and destination files are identical."""
        try:
            if os.path.getsize(src) != os.path.getsize(dst):
                return False

            # Compare contents if sizes match
            with open(src, 'rb') as f1, open(dst, 'rb') as f2:
                while True:
                    b1 = f1.read(4096)
                    b2 = f2.read(4096)
                    if b1 != b2:
                        return False
                    if not b1:
                        break
            return True
        except OSError as e:
            self.logger.error(f"Verification failed: {str(e)}")
            return False

    def _preserve_metadata(self, src: str, dst: str):
        """Preserve file metadata including permissions and timestamps."""
        try:
            st = os.stat(src)
            
            # Preserve permissions
            os.chmod(dst, st.st_mode)
            
            # Preserve timestamps (atime and mtime)
            os.utime(dst, (st.st_atime, st.st_mtime))
            
            # Try to preserve owner/group (requires root on Unix)
            try:
                os.chown(dst, st.st_uid, st.st_gid)
            except (AttributeError, PermissionError):
                pass  # Not available on Windows or without permissions
                
        except OSError as e:
            self.logger.warning(f"Could not preserve all metadata for {dst}: {str(e)}")
        
    def tool_dir_setup(self,opts, **kwargs) -> None:
        
        self.logger.line()
        self.logger.underline(f"Starting {self._tool} directory setup...")

        # First check if we're already in a matching directory
        if self._cwd.name == self._tool and self._cwd.is_dir():
            self.logger.info(f"Already in {self._tool} directory: {self._cwd}. This will be the {self._tool} directory root.")
        else: # if not in a matching directory
            # make a sub directory named after the tool
            os.makedirs(f'{self._tool}', exist_ok=True)
            os.chdir(f'{self._tool}')
            self._cwd = self._cwd/self._tool
            self.logger.info(f'Not in a directory called {self._tool}.')
            self.logger.info(f'Make {self._tool} subdirectory: {self._cwd}/')
            self.logger.info(f'Entering {self._tool} directory: {self._cwd}/')
        
        os.system(f'rm {self._cwd}/lint_setup.log')
        self.logger.start_logging(log_file=f'{self._cwd}/lint_setup.log')
        self.logger.disable_console()
        self.logger.enable_console()
       
        if opts.all:
            # make script directory
            os.makedirs('scripts',exist_ok=True)
            self.logger.underline(f"Make Script Directory...")
            self.logger.info(f"copying file from template directory into: ./scripts/prescript.csh")
            self._copy_file(src=f"{self._templates_dir}/{self._tool}_prescript.csh",dst=f"./scripts/prescript.csh")
            self.logger.info(f"copying file from template directory into: ./scripts/prescript.csh")
            self._copy_file(src=f"{self._templates_dir}/{self._tool}_post.csh",dst=f"./scripts/postscript.csh")
            self.logger.info(f"copying file from template directory into: ./scripts/setup.tcl")
            self._copy_file(src=f"{self._templates_dir}/{self._tool}_setup.tcl",dst=f"./scripts/setup.tcl")
            self.logger.info(f"copying file from template directory into: ./scripts/tool_opts")
            self._copy_file(src=f"{self._templates_dir}/tool_opts",dst=f"./scripts/tool_opts")
            
            # make waiver directory
            os.makedirs(f'rtl_{self._tool}/waivers',exist_ok=True)
            self.logger.info(f"making {self._tool} waiver directory: ./rtl_{self._tool}/waivers")
            if opts.top: # if top is specified
                os.system(f'touch ./rtl_{self._tool}/waivers/{opts.top}_rtl_{self._tool}_waivers.tcl')
                self.logger.info(f"Make waiver file in: ./rtl_{self._tool}/waivers/{opts.top}_rtl_{self._tool}_waivers.tcl")
            else:
                self.logger.info(f"No Top Module Specified. Leave waiver directory empty for now.")
            
            self.logger.info("Generate Lint Check Run Script in: ./run_script.sh")
            run_string = '#!/usr/bin/sh -f \n\n\n'
            # set some required environment variable
            run_string += self.close_header(msg=f'Default {self._tool} environment variable settings',symbol='=')

            run_string += self.underline('Required Environment Variables')
            if opts.comppath:
                run_string += f"export CompPath={opts.comppath}\n"
                self.logger.debug('set CompPath using argument specified by --comppath')
            else:
                run_string += f"export CompPath={self._git_root}\n"
                self.logger.debug('set CompPath to git root directory')
            run_string += f'export {self._tool.upper()}_RUN_DIR={self._tool_run_dir}\n'
            self.logger.debug(f'set {self._tool.upper()}_RUN_DIR to the current {self._tool} directory.')
            run_string += self.line() + '\n'

            # header
            run_string += self.close_header(msg=f'Variables for questa_run {self._tool} optional arguments',symbol='=')
            
            # top module
            run_string += self.underline('top module')
            if opts.top:
                run_string += f'top="{opts.top}"\n\n'
                self.logger.debug(f'set top module using argument specified by --top: {opts.top}')
            else:
                run_string += f'top="" \n\n' 
                self.logger.debug('no top module was set. Remember to add top module.')
            
            # tool option 
            run_string += self.underline('qverify tool options file')
            run_string += f'tool_opts=("${{{self._tool.upper()}_RUN_DIR}}/scripts/tool_opts")\n\n'
            # prescript file
            run_string += self.underline(f'{self._tool} prescript file')
            run_string += f'prescript=("${{{self._tool.upper()}_RUN_DIR}}/scripts/prescript.csh")\n\n'
            # setup file
            run_string += self.underline(f'{self._tool} setup file')
            run_string += f'setup=("${{{self._tool.upper()}_RUN_DIR}}/scripts/setup.tcl")\n\n'
            # postscript file
            run_string += self.underline(f'{self._tool} postscript file')
            run_string += f'postscript=("${{{self._tool.upper()}_RUN_DIR}}/scripts/postscript.csh")\n\n'

            # do files
            run_string += self.underline('do files. ensure file is enhanced .tcl compliant')
            if opts.dofile:
                run_string += f"dofile=({' '.join(opts.dofile)})\n\n"
            else:
                run_string += f'dofile=()\n\n'
            
            # filelist 
            run_string += self.underline('filelist of the design')
            if opts.filelist:
                run_string += f"filelist=({' '.join(opts.filelist)})\n\n"
            else:
                run_string += f'filelist=()\n\n'

            # waiver files
            run_string += self.underline('waiver files')
            if opts.waiver:
                run_string += f"waiver_file=({' '.join(opts.waiver)})\n\n"
            else:
                run_string += f'waiver_file=("rtl_lint/waivers/{opts.top}_{self._tool}_waivers.tcl")\n\n'
            
            # work library 
            run_string += self.underline('Qverify Lib')
            if opts.lib:
                run_string += f'lib="{opts.lib}"\n\n'
            else:
                run_string += f'lib="oc_libVlog"\n\n'

            # work directory
            run_string += self.underline('work directory')
            run_string += f'workdir="workdir"\n\n'
            
            # incremental database file
            run_string += self.underline("incremental database file for incremental runs")
            if opts.database_file:
                run_string += f'incr_db="{opts.database_file}.db"\n\n'
            else:
                run_string += f'incr_db="workdir/{opts.top}/{self._tool}/Results/{self._tool}.db"\n\n'
            run_string += self.line(newline=True) + '\n'
            
            run_string += self.close_header(msg='Argument variable',symbol='=')

            run_string += dedent(f'''\
            required_args=(
                "{self._tool}"
                "-t" "$top"
                "--workdir" "$workdir"
                "-f" "${{filelist[@]}}"
                "-I"
            )
        ''') + '\n'

            run_string += dedent(f'''\
                optional_args=(
                    # Uncomment if needed:
                    #"--tool_opts" "${{tool_opts[@]}}"
                    #"--prescript" "${{prescript[@]}}"
                    #"--pref_file" "${{setup[@]}}"
                    #"--postscript" "${{postscript[@]}}"
                    #"--dofile" "${{dofile[@]}}"
                    #"--waiver" "${{waiver_file[@]}}"
                    #"--verbose"
                    #"--comppath" "${{CompPath}}"
                )
            ''') + '\n'
            
            if self._tool == "lint":
                run_string += dedent('''\
                    lint_specific_args=(
                        # Uncomment if needed: 
                        #"-incr" "$incr_db"
                        #"-ext"
                        #"-cc" "$vlog_cmd_file"
                    )
                ''') + '\n'
            elif self._tool == "cdc":
                run_string += dedent('''\
                    cdc_specific_args=(  
                    )

                ''') + '\n'
            elif self._tool == "rdc":
                run_string += dedent('''\
                    rdc_specific_args=( 
                    )
                ''') + '\n'
                
            else:
                run_string += dedent('''\
                    tool_specific_args= (
                        #"no specific arg"
                    )
                ''') + '\n'
                
            run_string += self.close_header(msg='questa_run command line',symbol='=',newline=False)
            run_string += f'''questa_run "${{required_args[@]}}" "${{optional_args[@]}}" "${{{self._tool}_specific_args[@]}}"\n'''
            run_string += self.line(newline=True) + '\n'


            self.logger.debug('Printing run_script.sh ...')
            self.logger.header(message='Start',symbol='*',debug=True, newline=False)
            for line in run_string.splitlines():
                self.logger.debug(line)
            self.logger.header(message='End...',symbol='*',debug=True)
            with open('run_script.sh', 'w') as f:
                f.write(run_string)
                f.close()
            os.chmod('run_script.sh', 0o755)
            self.logger.info(f'Created "run_script.sh". Use this for runnning {self._tool} checks. Update the var in the script accordingly.')
            self._gui_setup(opts)
            self.logger.info(f"Finished setting up {self._tool} directory.")
            self.logger.line()
            self.logger.disable_console()
            self.logger.close()
        return None
        
    def _gui_setup(self,opts,**kwargs):
        run_string = '#!/usr/bin/sh -f \n\n\n'
        # set some required environment variable
        run_string += self.close_header(msg=f'Default {self._tool} environment variable settings',symbol='=')
        run_string += self.underline('Required Envrionment Variable')
        if opts.comppath:
            run_string += f"export CompPath={opts.comppath}\n"
        else:
            run_string += f"export CompPath={self._git_root}\n"
            run_string += f'export LINT_RUN_DIR={self._tool_run_dir}\n'
            run_string += self.line(newline=True) + '\n'
            
            run_string += self.close_header(msg=f'Variables for questa_run  {self._tool} GUI arguments',symbol='=')
            run_string += self.underline('# top module')
            if opts.top:
                run_string += f'top="{opts.top}"\n\n'
            else:
                run_string += f'top=""\n\n'
            run_string += self.underline(f"{self._tool} database file")
            run_string += f'db_file={opts.workdir}/Results/{self._tool}.db\n\n'
            run_string += self.underline("Work Directory")
            run_string += f'workdir=workdir\n\n'
            run_string += self.line(newline=True) + '\n'
            
            run_string += self.close_header(msg='Argument Variables',symbol='=')
            
            run_string += dedent(f'''\
                first_option=(
                    "{self._tool}"
                    "-t" "$top"
                    "--workdir" "$workdir"
                    "-I"
                    "--gui"
                )
            ''') + '\n'

            run_string += dedent(f'''\
                second_option=(
                    "{self._tool}"
                    "-t" "$top"
                    "-db" "$db_file"
                    "-I"
                    "--gui"
                )
            ''') + '\n'
            run_string += self.line(newline=True) + '\n'
        
            run_string += self.close_header(msg='questa_run command line', symbol='=')
            run_string += 'questa_run "${first_option[@]}"\n'
            run_string += '# questa_run "${second_option[@]}"\n'
            run_string += self.line(newline=True) + '\n'
            
            self.logger.debug('Printing gui_script.sh ...')
            self.logger.header(message='Start of script ', symbol='*', debug=True, newline=False)
            for line in run_string.splitlines():
                self.logger.debug(line)
            self.logger.header('End printing gui_script.sh ...', symbol='*', debug=True)
            self.logger.line(debug=True)
            
        with open('gui_script.sh', 'w') as f:
            f.write(run_string)
            f.close()
        self.logger.debug("chmod gui_script.sh to 755")
        os.chmod('gui_script.sh', 0o755)
        self.logger.info(f'Created "gui_script.sh". Use this for opening the {self._tool} lint check with the GUI. Update the var in the script accordingly.')
        
    def _get_args(self):
        return    {
            'all': {
                'short': '-all',
                'long': '--all',
                'help': 'setup the full directory',
                'action': 'store_true',
                'default': False
            },
            'top': {
                'short': '-t',
                'long': '--top',
                'help': 'Define the top module',
                'type': str,
                'default': False
            },
            'workdir': {
                'short': '-o',
                'long': '--workdir',
                'help': 'Workdir output directory',
                'type': str,
                'default': "workdir"
            },
            'filelist': {
                'short': '-f',
                'long': '--filelist',
                'help': 'Specify the filelist for lint setup.',
                'nargs': '*',
                'type': str,
                'default': []
            },
            'verbose': {
                'short': '-v',
                'long': '--verbose',
                'help': 'Specify for log file Debugging',
                'action': 'store_true',
                'default': False
            }
        }
            
if __name__ == "__main__":
    opts = opts()
    tool_dict = {}
    tool_dict.update({ 'current_dir' : os.getcwd() ,
                    'questa_run_dir' : os.path.abspath(os.path.dirname(__file__)),
                    'git_root' : get_git_root(), 
                    'user' : os.getenv('USER')})
    
    tool_dir_setup(opts,tool_dict=tool_dict)