# Questa QC wrapper script

This script is made to execute Questa Lint and CDC/RDC jobs using LSF.
## Getting started

To facilitate your onboarding with Questa QC wrapper script, please refer to the following sections.

- [X] [Usage](#usage)
- [X] [Examples](#examples)
- [X] [Templates](#templates)

## Usage

Positional Arguments are required. There are 1 positional arguments currently required.

| Positional Arguments  | Description                                                       | Required?     | Data Type | Default   |
| --------------------- | ----------------------------------------------------------------- |-------------- | --------- |--------   |
| subparser_name        | specify the flow to run. The 3 options are: lint, cdc and rdc     | yes           | string    | None      |

```
usage: lint <common_arguments> <specific_arguments>
or: cdc <common_arguments> <specific_arguments>
or: rdc <common_arguments> <specific_arguments>
```
*(Replace placeholders with actual arguments)*

## Common Arguments
| Short Option | Long Option      | Description                                      | Required?                        | Data Type | Default   |
|--------------|------------------|--------------------------------------------------|----------------------------------|-----------|-----------|
| `-h`         | `--help`         | Shows the help message                           | No                               | N/A       | `False`   |
| `-t`         | `--top`          | Top module name                                  | Yes                              | Text      | `None`    |
| `-f`         | `--filelist`     | Filelist format supported by questa              | Yes (if GUI disabled)            | Path      | `None`    |
| `-cp`        | `--comppath`     | Component path used in .f files gen by febuild   | No                               | Path      | `None`    |
| `-g`         | `--gui`          | Enable gui mode by adding this argument          | No                               | N/A       | `False`   |
| `-l`         | `--lib`          | Library                                          | No                               | Text      | `work`    |
| `-o`         | `--workdir`      | Workdir output directory                         | No                               | Path      | `workdir/`|
| `-p`         | `--pref`         | Tool preference or do commands for pre-analysis  | No                               | Path      | `None`    |
| `-pf`        | `--pref_file`    | Tool preference or do file for pre-analysis      | No                               | Path      | `None`    |  
| `-do`        | `--dofile`       | Custom do file post analysis                     | No                               | Path      | `None`    |
| `-opt`       | `--tool_opts`    | Tool options file path                           | No                               | Path      | `None`    |
| `-pre`       | `--prescript`    | Custom prescript csh file                        | No                               | Path      | `None`    |
| `-post`      | `--postscript`   | Custom postscript csh file                       | No                               | Path      | `None`    |
| `-db`        | `--database_file`| The database_file                                | No                               | Path      | `None`    |

## Lint Specific Arguments
### Overview
This section showcase the available positional and optional arguments available under the lint tool flow.  
#### Lint Specific Command Examples
```
./questa_run lint {<Common_Arguments> <lint_specific_commands}  
```
*(Replace placeholders with actual arguments)*

### Lint Optional Argument  
The table below shows the available an extension of optional arguments that is available when the lint tool is specified.  
| Argument (-)  | Argument (--)  | Description                                      | Required?                           | Data Type  | Default |
| ------------- | -------------- | ------------------------------------------------ | ----------------------------------- | ---------- | ------- |
| -ext          | --external     | Define component is from external source         | No                                  | N/A        | False   |
| -cc           | --compile_cmd  | A vlog/vcom compile option file                  | No                                  | Path       | None    |
| -w            | --waiver       | Lint Waiver File                                 | No                                  | Path       | None    |
| -incr         | --incremental  | Specify lint run is an incremental run           | No                                  | N/A        | False   |

### Lint Positional Argument
The table below shows positional arguments that have further subcommands that run specific functions.

| Positional Arguments  | Description                                                       | Required?     | Data Type | Default   |
| --------------------- | ----------------------------------------------------------------- |-------------- | --------- |--------   |
| report                | Specify after lint to run some report commands.                   | no            | string    | None      |
| fix                   | Specify after lint to fix some lint violations.                   | no            | string    | None      |
| setup                 | Specify after lint to automatically setup lint directory.         | no            | string    | None      |

#### Lint Subcommands Example
```
./questa_run lint {<positional_argument} {<positional_argument_subcommands>}
```
*(Replace placeholders with actual arguments)*

## CDC Specific Arguments
| Argument (-)  | Argument (--)     | Description                                      | Required?                              | Data Type     | Default   |
| ------------- | ----------------- | ------------------------------------------------ | -------------------------------------- | ------------- | --------- |
| -c            | --cons            | Constraints file                                 | No                                     | Path          | None      |
| -s            | --sdc             | SDC Constraints file or .f constraints filelist  | No                                     | Path          | None      |

## RDC Specific Arguments
| Argument (-)  | Argument (--)     | Description                                      | Required?                              | Data Type     | Default   |
| ------------- | ----------------- | ------------------------------------------------ | -------------------------------------- | ------------- | --------- |
| -c            | --cons            | Constraints file                                 | No                                     | Path          | None      |
| -s            | --sdc             | SDC Constraints file or .f constraints filelist  | No                                     | Path          | None      |

## Examples
```
lint -t <top_module> -cc <vlog_compile> -p <pre_analysis_script> -pre <prescript> -do <do_file> -I 
cdc -f <filelist> -t <top_module> -c <constraint_file> -fd <file_directory> -opt <tool_opts> -o <output_dir>
```

## Full Documentation at:
```
https://openchip.atlassian.net/wiki/spaces/SH/pages/268599322/Lint+Flow
```

### Example 1
```
./questa_run cdc -f VtPcl/shared/vt_src_open-full_pkg.f -t VtPcl -c VtPcl/shared/blocks/VtPcl/constraints/VtPcl.sdc -fd /ln/proj/va_10/a0/workareas/TEMP/VT_PCL_JAN_2025/vt_pcl_20250127_33a7a9dd7b4/sim/src -opt questa_run/templates/tool_opts -p questa_run/templates/pref.do -do questa_run/templates/dofile.do -o questa_work
```

### Example 2
```
./questa_run -cdc -f pcl/design/units/Pcl/sim/vt_sanitychk_rtl/vt_src_open-full_pkg.f pcl/design/units/Pcl/sim/vt_sanitychk_rtl/ip_stub_src_pkg.f -t VtPcl -fd pcl/design/units/Pcl/sim/vt_sanitychk_rtl/ -opt questa_run/templates/tool_opts -p questa_run/templates/pref.do -do questa_run/templates/dofile.do -post questa_run/templates/postscript.csh -o questa_work_hier
```

### Example 3
```
./questa_run lint -t VtPcl -o questa_work -g
```
### Example 4 
```
./questa_run lint -t VtPcl -cc compile_vl -p templates/lint_setup.do -pre templates/lint_pre.do -do templates/lint_post.do -I 
```
## Templates

Note: If you need to add paths in the following input files, be sure to specify them as absolute paths, since the working directory will change to {workdir}/{top}/{lint cdc rdc} as defined in the arguments.
### tool_opts
```
vcom=>-64 -quiet
vlog=>-suppress vlog-2583 -svinputport=relaxed
cdc run=>-report_modes
bsub=>-q pa -I
```

### prescript.csh
```bash
echo "Starting..."
```

### pref.do
```tcl
#cdc preference -sdc_sta_mode;
#sdc preference -infer_false_path_domains;
#sdc preference -sta_mode;
#sdc load /ln/proj/va_10/a0/workareas/z2youkassou/VtPcl/shared/blocks/VtPcl/constraints/VtPcl.sdc;
do /ln/proj/va_10/a0/workareas/z2youkassou/VtPcl/shared/cdc.tcl;
hier block VtCpu;
cdc methodology soc -goal release;
```

### dofile.do
```
sdc generate tcl cdc.tcl
cdc generate html html_dashboard
cdc generate tree clock_tree.rpt -clock 
cdc generate tree reset_tree.rpt -reset
report directives
```

### postscript.csh
```bash
echo "Starting HDM Top-Down CDC Analysis..."
make -f Results/hcdc_run.Makefile all
echo "Finished!"
```
