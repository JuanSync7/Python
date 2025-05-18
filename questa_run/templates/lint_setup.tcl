##------------------------------------------------------------------------------- 
## Project      : Lint Flow
## Author       : Kok Shew Juan
##------------------------------------------------------------------------------- 
## Copyright (C) 2025, OpenChip & Software Technologies S.L. All rights reserved. 
## 
## This file contains proprietary information of OpenChip and is protected by 
## intellectual property laws. Unauthorized use, reproduction, or distribution 
## of this file or its contents is strictly prohibited without written consent 
## from OpenChip. 
##
##------------------------------------------------------------------------------- 
## Description  : Setup Script for Lint Flow            
##------------------------------------------------------------------------------- 


#====================================================================================================
#Section 1      : Shell Environment Variables
#Description    : Set Qverify Shell envrionment variables
#Example        : configure environment USER_WORKAREA $env(USER_WORKAREA)
#====================================================================================================



#====================================================================================================
#Section 1a     : Softening Filepath
#Description    : Softtening Filepath ensure that filepaths are relative to Envrionment Variable
#Example 1      : configure environment soften_paths -max_upward_levels 1
#Example 2      : configure environment soften_paths USER_WORKAREA (Preferred)
#====================================================================================================



#====================================================================================================
#Section 2      : User Copied Checks
#Description    : Specify directives for new lint checks by using the 'lint copy check' command
#Example        : lint copy check no_fixme -use regex_user_defined -severity error -message "there is a FIXME in the code"
#                 lint preference -check no_fixme -regex_user_defined_patterns_icase fixme
#                 lint on no_fixme
#                 lint report check -severity error no_fixme
#====================================================================================================





#====================================================================================================
#Section 3      : Turn on and off lint checks
#Description    : This is to make changes to any lint checks for the lint run
#Example        : lint on regex_user_defined
#====================================================================================================





#====================================================================================================
#Section 4      : Lint Preferences
#Description    : Modify lint preferences for the lint checks
#Example 1      : lint preference connection -full_bus_connection
#Example 2      : lint preference -exclude_package *
#Example 3      : lint preference -generate_design_summary_report
#Example 4      : lint preference -check clock_internal -clock_gen_module $env(CLOCK_GEN_MODULE)
#Example 5      : lint preference -check generate_port_info -port_info_file_path Results/report/port_info.rpt
#Example 6      : lint preference -check flop_without_control -valid_flop_controls {sync_reset async_reset initial_value}
#Example 7      : lint preference comment -check file_header_template_mismatch -header_template_file $env(HEADER_TEMP_FILE)
#====================================================================================================







#====================================================================================================
#Section 5      : Hierarchical Analysis
#Description    : Add any module names that should be excluded from this lint analysis run
#Example 1      : hier ip  "module_name" 
#Example 2      : hier ip -regexp {^ip[a-zA-Z0-9_]*} 
#====================================================================================================




#====================================================================================================
#Section 6  : Waiver Files
#Description: Add any waiver files to be added to the design
#Example    : do <waiver_file>
#====================================================================================================





#====================================================================================================

