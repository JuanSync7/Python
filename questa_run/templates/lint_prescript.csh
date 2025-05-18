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
#Section 1  : Environment Variables
#Description: Set envrionment variables
# PRJ_ROOT is specified as the current run directory in script. Overwrite by setting PRJ_ROOT below
# USER_WORKAREA is specified as /ln/proj/va_10/a0/workareas/${USER}. Overwrite by setting USER_WORKAREA below
#====================================================================================================
#setenv PRJ_ROOT /ln/proj/va_10/a0/workareas/${USER}/questa_run/
#setenv USER_WORKAREA /ln/proj/va_10/a0/workareas/${USER}/
#setenv LINT_WORKDIR  ${PRJ_ROOT}/lint/workdir/

#====================================================================================================


#====================================================================================================
#Section 2  : Lint Environment Variables
#Description: Set Lint variables
#====================================================================================================
#Set any clock generation module
#set CLOCK_GEN_MODULE "*clock_gen"
#set HEADER_TEMP_FILE "*header_file"