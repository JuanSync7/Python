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
## Description  : Setup Script for Lint Flow - Generating Reports         
##------------------------------------------------------------------------------- 


#====================================================================================================
#Section 1  : Generating Reports
#Description: generate the necessary reports
#====================================================================================================
configure output directory ./report/
lint generate report -design_audit lint_design_audit.rpt
lint generate report -group_by_module lint_full.rpt
lint generate report -status report/.
lint generate report -csv lint_full.csv
lint generate report -html lint_full.html
lint generate report -json lint_full.json
configure output directory .