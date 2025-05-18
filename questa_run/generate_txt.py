from string_util import StringUtil

def generate_lint_setup() -> str:
    pass

def lint_report_console() -> str:
    su = StringUtil()
    
    # Title and introduction
    output = []
    output.append("")
    output.append(su.underline("Lint Report Processing Tool", symbol='double', with_comment_prefix=False, newline=False))
    output.append("This tool helps analyze and split Questa Lint reports for better issue tracking.")
    output.append("")
    
    # Usage section
    output.append(su.underline("Usage", symbol='double', with_comment_prefix=False, newline=False))
    output.append("Basic command structure for report processing:")
    output.append(su.text_box("questa_run report -t <top_module> [options]", style="double", language='bash'))
    output.append("")
    
    # Required Arguments
    output.append(su.underline("Required Arguments", symbol='double', with_comment_prefix=False, newline=False))
    req_headers = ["Option", "Description", "Data Type", "Default"]
    req_rows = [
        ["-t, --top", "Top module name (used as identifier)", "string", "None"]
    ]
    output.append(su.table(req_headers, req_rows, style="round", align='left'))
    output.append("")
    
    # Report File Options
    output.append(su.underline("Report File Options", symbol='double', with_comment_prefix=False, newline=False))
    file_headers = ["Short Option", "Long Option", "Description", "Required?", "Default"]
    file_rows = [
        ["-f", "--file", "Full lint report file path", "No", "''"],
        ["-regexp", "--regexp", "Regular expression pattern for filtering", "No", "''"]
    ]
    output.append(su.table(file_headers, file_rows, style="round", align='left'))
    output.append("")
    
    # Splitting Options
    output.append(su.underline("Report Splitting Options", symbol='double', with_comment_prefix=False, newline=False))
    split_headers = ["Short Option", "Long Option", "Description", "Action"]
    split_rows = [
        ["-sbm", "--split_by_module", "Split report by module names", "store_true"],
        ["-sbc", "--split_by_checks", "Split report by check types", "store_true"]
    ]
    output.append(su.table(split_headers, split_rows, style="round", align='left'))
    output.append("")
    
    # Examples
    output.append(su.underline("Examples", symbol='double', with_comment_prefix=False, newline=False))
    examples = [
        "# Basic report analysis:",
        "questa_run report -t top_module -f lint_report.rpt",
        "",
        "# Split report by modules:",
        "questa_run report -t top_module -f lint_report.rpt -sbm",
        "",
        "# Filter with regex and split by checks:",
        "questa_run report -t top_module -f lint_report.rpt -regexp 'WARNING' -sbc"
    ]
    output.append(su.text_box("\n".join(examples), style="double", language='bash'))
    output.append("")
    
    # Processing Flow
    output.append(su.underline("Processing Flow", symbol='single', with_comment_prefix=False, newline=False))
    flow_steps = [
        "1. Loads the specified report file (-f/--file)",
        "2. Applies regex filter if provided (-regexp/--regexp)",
        "3. Splits report according to selected options (-sbm/-sbc)",
        "4. Generates output files in the current directory"
    ]
    output.append("\n".join(flow_steps))
    output.append("")
    
    return "\n".join(output)

def generate_readme_console() ->str:
    su = StringUtil()
    
    # Title and introduction
    output = []
    output.append("")
    output.append(su.underline("Questa QC wrapper script", symbol='double', with_comment_prefix=False, newline=False))
    output.append("This script is made to execute Questa Lint and CDC/RDC jobs using LSF.")
    output.append("")
    
    # Usage section
    output.append(su.underline("Usage", symbol='double', with_comment_prefix=False, newline=False))
    output.append("Positional Arguments are required. There are 1 positional arguments currently required.")
    
    # Positional arguments table
    pos_headers = ["Positional Arguments", "Description", "Required?", "Data Type", "Default"]
    pos_rows = [
        ["subparser_name", "specify the flow to run. The 3 options are: lint, cdc and rdc", "yes", "string", "None"]
    ]
    output.append(su.table(pos_headers, pos_rows, style="round"))
    output.append("")
    
    # Usage text
    output.append(su.text_box("""usage: lint <common_arguments> <specific_arguments>
or: cdc <common_arguments> <specific_arguments>
or: rdc <common_arguments> <specific_arguments>""", style="double", language='bash'))
    output.append("")
    
    # Common Arguments
    output.append(su.underline("Common Arguments", symbol='double', with_comment_prefix=False, newline=False))
    common_headers = ["Short Option", "Long Option", "Description", "Required?", "Data Type", "Default"]
    common_rows = [
        ["-h", "--help", "Shows the help message", "No", "N/A", "False"],
        ["-t", "--top", "Top module name", "Yes", "Text", "None"],
        ["-f", "--filelist", "Filelist format supported by questa", "Yes (if GUI disabled)", "Path", "None"],
        ["-cp", "--comppath", "Component path used in .f files gen by febuild", "No", "Path", "None"],
        ["-g", "--gui", "Enable gui mode by adding this argument", "No", "N/A", "False"],
        ["-l", "--lib", "Library", "No", "Text", "oc_libVlog"],
        ["-o", "--workdir", "Workdir output directory", "No", "Path", "workdir/"],
        ["-p", "--pref", "Tool preference or do commands for pre-analysis", "No", "Path", "None"],
        ["-pf", "--pref_file", "Tool preference or do file for pre-analysis", "No", "Path", "None"],
        ["-do", "--dofile", "Custom do file post analysis", "No", "Path", "None"],
        ["-opt", "--tool_opts", "Tool options file path", "No", "Path", "None"],
        ["-pre", "--prescript", "Custom prescript csh file", "No", "Path", "None"],
        ["-post", "--postscript", "Custom postscript csh file", "No", "Path", "None"],
        ["-db", "--database_file", "The database_file", "No", "Path", "None"]
    ]
    output.append(su.table(common_headers, common_rows, style="round", align='left'))
    output.append("")
    
    # Lint Specific Arguments
    output.append(su.underline("Lint Specific Arguments", symbol='double', with_comment_prefix=False, newline=False))
    output.append(su.underline("Overview", symbol="single", with_comment_prefix=False, newline=False))
    output.append("This section showcase the available positional and optional arguments available under the lint tool flow.")
    output.append("")
    
    # Lint command example
    output.append(su.underline("Lint Specific Command Examples", symbol="double", with_comment_prefix=False, newline=False))
    output.append(su.text_box("questa_run lint {<Common_Arguments> <lint_specific_commands}", style="double",language='bash'))
    output.append("")
    
    # Lint optional arguments
    output.append(su.underline("Lint Optional Argument", symbol="double", with_comment_prefix=False, newline=False))
    lint_opt_headers = ["Argument (-)", "Argument (--)", "Description", "Required?", "Data Type", "Default"]
    lint_opt_rows = [
        ["-ext", "--external", "Define component is from external source", "No", "N/A", "False"],
        ["-cc", "--compile_cmd", "A vlog/vcom compile option file", "No", "Path", "None"],
        ["-w", "--waiver", "Lint Waiver File", "No", "Path", "None"],
        ["-incr", "--incremental", "Specify lint run is an incremental run", "No", "N/A", "False"]
    ]
    output.append(su.table(lint_opt_headers, lint_opt_rows, style="round", align='left'))
    output.append("")
    
    # Lint positional arguments
    output.append(su.underline("Lint Positional Argument", symbol="double", with_comment_prefix=False, newline=False))
    lint_pos_headers = ["Positional Arguments", "Description", "Required?", "Data Type", "Default"]
    lint_pos_rows = [
        ["report", "Specify after lint to run some report commands.", "no", "string", "None"],
        ["fix", "Specify after lint to fix some lint violations.", "no", "string", "None"],
        ["setup", "Specify after lint to automatically setup lint directory.", "no", "string", "None"]
    ]
    output.append(su.table(lint_pos_headers, lint_pos_rows, style="round", align='left'))
    output.append("")
    
    # Lint subcommand example
    output.append(su.text_box("questa_run lint {<positional_argument} {<positional_argument_subcommands>}", style="double", language='bash'))
    output.append("")
    
    # CDC Specific Arguments
    output.append(su.underline("CDC Specific Arguments", symbol='double', with_comment_prefix=False, newline=False))
    cdc_headers = ["Argument (-)", "Argument (--)", "Description", "Required?", "Data Type", "Default"]
    cdc_rows = [
        ["-c", "--cons", "Constraints file", "No", "Path", "None"],
        ["-s", "--sdc", "SDC Constraints file or .f constraints filelist", "No", "Path", "None"]
    ]
    output.append(su.table(cdc_headers, cdc_rows, style="round", align='left'))
    output.append("")
    
    # RDC Specific Arguments
    output.append(su.underline("RDC Specific Arguments", symbol='double', with_comment_prefix=False, newline=False))
    rdc_headers = ["Argument (-)", "Argument (--)", "Description", "Required?", "Data Type", "Default"]
    rdc_rows = [
        ["-c", "--cons", "Constraints file", "No", "Path", "None"],
        ["-s", "--sdc", "SDC Constraints file or .f constraints filelist", "No", "Path", "None"]
    ]
    output.append(su.table(rdc_headers, rdc_rows, style="round", align='left'))
    output.append("")
    
    # Examples section
    output.append(su.underline("Examples", symbol='double', with_comment_prefix=False, newline=False))
    output.append(su.text_box("""questa_run lint -t <top_module> -cc <vlog_compile> -p <pre_analysis_script> -pre <prescript> -do <do_file> -I \n
questa_run cdc -f <filelist> -t <top_module> -c <constraint_file> -opt <tool_opts> -o <output_dir>""", style="double",language='bash'))
    output.append("")
    
    # Documentation link
    output.append(su.underline("Full Documentation at:", symbol='bold', with_comment_prefix=False, newline=False))
    output.append(su.text_box("https://openchip.atlassian.net/wiki/spaces/SH/pages/268599322/Lint+Flow", style="ascii"))
    output.append("")
    return "\n".join(output)

if __name__ == "__main__":
    print(generate_readme_console())