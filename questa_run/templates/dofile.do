##------------------------------------------------------------------------------- 
## Project      : CDC Flow
## Author       : Yassine Oukassou
##------------------------------------------------------------------------------- 
## Copyright (C) 2025, OpenChip & Software Technologies S.L. All rights reserved. 
## 
## This file contains proprietary information of OpenChip and is protected by 
## intellectual property laws. Unauthorized use, reproduction, or distribution 
## of this file or its contents is strictly prohibited without written consent 
## from OpenChip. 
##
##------------------------------------------------------------------------------- 
## Description  : Setup Script for CDC Flow            
##------------------------------------------------------------------------------- 


#====================================================================================================
#Section 1  : Generating Reports
#Description: generate the necessary reports
#====================================================================================================
#sdc generate tcl cdc.tcl
#cdc generate html html_dashboard
#cdc generate tree clock_tree.rpt -clock 
#cdc generate tree reset_tree.rpt -reset
#report directives