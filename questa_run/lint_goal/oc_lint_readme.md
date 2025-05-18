## Description
This is a lint methodology for intel linting requirements.

lint on ansi_style_declaration
lint report check -severity info ansi_style_declaration


## lint copy check

lint copy check allow users to tailor a more specific lint check  by copying the functionality of a pre-defined check.

| Check Name | Check Preference |
| --- | --- |
|lint copy check  -use regex_user_defined -severity error -message "there is a FIXME in the code" |lint preference -check no_fixme -regex_user_defined_patterns FIXME |
|lint copy check no_todo -use regex_user_defined -severity error -message "there is a TODO in the code" |lint preference -check no_todo -regex_user_defined_patterns TODO |
|lint on no_fixme no_todo | lint report check -severity error no_FIXME no_TODO |


## Other check
lint on unsynth_loop
lint report check -severity error unsynth_loop ### unsynth loop
lint on undriven_signal
lint report check -severity error undriven_signal
lint on feedthrough_path 
lint report check -severity warning feedthrough_path
lint on combo_path_input_to_output
lint report check -severity warning combo_path_input_to_output
lint on inst_param_width_overflow
lint report check -severity warning inst_param_width_overflow

lint on div_mod_rhs_zero
lint report check -severity error div_mod_rhs_zero
lint on reg_reset_value_disallowed
lint report check -severity warning reg_reset_value_disallowed
lint on module_with_duplicate_ports
lint report check -severity error module_with_duplicate_ports


lint on design_unit_overwritten
lint report check -severity warning design_unit_overwritten
lint on unsynth_arithmetic_operator
lint report check -severity error unsynth_arithmetic_operator
lint preference -allow_mod_by_power_two
lint on bus_bit_as_clk
lint report check -severity warning bus_bit_as_clk



## Checks by Intel

### sim_race02 - Reports signals that have multiple assignments in the same simulation cycle
lint on multi_driven_signal
lint report check -severity error multi_driven_signal

### PragmaComments-ML - Detects Pragma Comments
lint on pragma_disallowed
lint preference -disallow_pragmas
lint preference -verilog_synth_pragma_prefix
lint preference -vhdl_synth_pragma_prefix
lint report check -severity warning pragma_disallowed

### NoAssignX-ML - Ensure RHS of the assignment does not contains 'X'
lint on assign_or_comparison_has_x  
lint on condition_has_implicit_x
lint report check -severity error assign_or_comparison_has_x
lint report check -severity error condition_has_implicit_x

### InferLatch - latch inferred
lint on latch_inferred  
lint report check -severity error latch_inferred  

### UndrivenInTerm-ML
lint on unconnected_inst_input   
lint report check -severity error -alias UndrivenInTerm unconnected_inst_input  

### CombLoop - Detects combinational loops
lint on combo_loop  
lint on flop_clock_reset_loop  
lint report check -severity error -alias CombLoop combo_loop  
lint report check -severity error -alias CombLoop_RstClk flop_clock_reset_loop  

### FlopClockConstant - Reports flip-flop clock pin driven by a constant value
lint on const_reg_clock  
lint report check -severity error -alias FlopClockConstant const_reg_clock  

### FlopEConst - Reports permanently disabled or enabled flip-flop enable pins
lint on mux_select_const  
lint report check -severity error mux_select_const  

### FlopSRConst - Reports permanently enabled flip-flop set or reset pins
lint on flop_async_reset_const  
lint on reset_port_connection_static
lint report check -severity error -alias FlopSRConst flop_async_reset_const  
lint report check -severity error -alias FlopSRConst reset_port_connection_static

### LatchFeedback - Reports a latch in which a combinational feedback path exists from output pin to data or enable pin
lint on combo_loop_with_latch   
lint report check -severity warning -alias LatchFeedback combo_loop_with_latch  

### mixedsenselist - Mixed conditions in sensitivity list may not be synthesizable
lint on unsynth_sensitivity_list_conditions   
lint report check -severity warning unsynth_sensitivity_list_conditions   

### NoStrengthInput-ML - Synthesis tools ignore strength inputs
lint on unsynth_drive_strength_gate   
lint on unsynth_drive_strength_assign    
lint report check -severity error unsynth_drive_strength_gate   
lint report check -severity error unsynth_drive_strength_assign   

### UnrecSynthDir-ML - Synthesis directive is not recognized
lint on synth_pragma_prefix_invalid   
lint on synopsys_reset_pragma   
lint report check -severity warning synth_pragma_prefix_invalid   
lint report check -severity warning synopsys_reset_pragma  

### UnloadedOutTerm-ML - Unloaded but driven output terminal of an instance detected
lint on unloaded_signal  
lint report check -severity warning unloaded_signal 

### UnloadedInPort-ML - Unloaded but driven input port 
lint on unloaded_input_port  
lint report check -severity warning unloaded_input_port  

### UndrivenOutPort-ML
lint on undriven_output_port  
lint report check -severity error undriven_output_port  

### UndrivenNUnloaded-ML - Signal is undriven and unloaded
lint on undriven_unloaded_signal  
lint report check -severity warning undriven_unloaded_signal   

### UndrivenOutTermNLoaded-ML - Undriven output pins connected to instance input
lint on undriven_output_port  
lint report check -severity error undriven_output_port  


### UnloadedNet-ML - Unloaded but driven net detected in the design
lint on unloaded_signal  
lint report check -severity warning unloaded_signal  

### LatchEnableConstant - latch enable is driven by constant
lint on const_latch_enable  
lint report check -severity error const_latch_enable   

### LatchEnableUndriven - latch enable not driven
lint on undriven_latch_enable  
lint report check -severity error undriven_latch_enable  

### UndrivenNet-ML - Undriven but loaded net is detected in the design
lint on undriven_signal  
lint report check -severity warning undriven_signal  

### NoExprInPort-ML - Port connections in instances should not contain expressions
lint on port_conn_is_expression  
lint report check -severity info port_conn_is_expression  

### NamedAssoc - Use named-association rather than positional association to connect to an instance
lint on ordered_port_connection  
lint report check -severity error ordered_port_connection  

### AssignPatInInst-ML - Detect assignment patterns in parameter override or port connection area
###lint preference connection ‑disallow_port_concat  

### ParamName / GenericName - Parameter name does not follow standard naming rules. 
lint on parameter_name_not_standard  
lint on generic_name_not_standard  
lint preference name –check parameter_name_not_standard -disallow_lower_case -disallow_mixed_case -disallow_consecutive_underscores -max_length 32 -disallow_prefix 0 1 2 3 4 5 6 7 8 9  
lint preference name –check generic_name_not_standard -disallow_lower_case -disallow_mixed_case -disallow_consecutive_underscores -max_length 32 -disallow_prefix 0 1 2 3 4 5 6 7 8 9  
lint report check -severity warning parameter_name_not_standard  
lint report check -severity warning generic_name_not_standard  

### SigName
lint on signal_name_not_standard   
lint preference name ‑check signal_name_not_standard -disallow_special_character -disallow_consecutive_underscores -max_length 32 -disallow_prefix 0 1 2 3 4 5 6 7 8 9  
lint report check -severity warning signal_name_not_standard  

### PortName - Port name does not follow the naming convention
lint on port_name_not_standard  
lint preference name ‑check port_name_not_standard -disallow_special_character -disallow_consecutive_underscores -max_length 32 -disallow_prefix 0 1 2 3 4 5 6 7 8 9  
lint report check -severity warning port_name_not_standard  

### VarName - Variable does not follow recommended naming convention
lint on reg_name_not_standard  
lint preference name ‑check reg_name_not_standard -disallow_special_character -disallow_consecutive_underscores -max_length 32 -disallow_prefix 0 1 2 3 4 5 6 7 8 9  
lint report check -severity warning reg_name_not_standard  

### ConstName
lint on const_name_not_standard  
lint preference name –check const_name_not_standard -disallow_lower_case -disallow_mixed_case -disallow_prefix 0 1 2 3 4 5 6 7 8 9 -disallow_special_character   -disallow_consecutive_underscores -max_length 32  
lint report check -severity warning const_name_not_standard  

### AlwaysEnabledCG AlwaysDisabledCG - Constant value drives register clock pin. 
lint on const_reg_clock   
lint report check -severity error const_reg_clock  

### SensListrepeat-ML - Sensitivity list has one or more bits of a signal repeated. 
lint on sensitivity_list_signal_repeated  
lint report check -severity error sensitivity_list_signal_repeated  

### FlopClockUndriven - Register clock pin is undriven
lint on undriven_reg_clock  
lint report check -severity error undriven_reg_clock  

### ClockEnableRace
lint on clock_enable_race   
lint report check -severity warning clock_enable_race  

### sim_race07
lint on clock_enable_race  
lint report check -severity warning clock_enable_race  

### sim_race04

### clock_used_as_data - Clock is used as a non-clock signal. 
lint on clock_signal_as_non_clock
lint preference -check clock_signal_as_non_clock -report_all_non_clock_usages
lint report check -severity warning clock_signal_as_non_clock  

### IfWithoutElse-ML - If statement does not have the corresponding else statement. 
lint on if_missing_else  
lint preference -report_conditional_gen_stmts  
lint report check -severity error if_missing_else  

### AlwaysFalseTrueCond-ML -  Condition expression is a constant. 
lint on condition_const   
lint report check -severity error condition_const  

### NullPort-ML - module has null port
lint on module_with_null_port   
lint report check -severity error module_with_null_port  

### ExprParen - Parentheses are missing in the expression. 
lint on parentheses_missing   
lint preference -check parentheses_missing -report_standard_styles  
lint preference -check parentheses_missing -ignore_one_operator_expressions  
lint report check -severity error parentheses_missing  

### CheckExprCast

### SignedUnsignedExpr-ML - Do not mix signed & unsigned variables/constants in expressions
lint on signed_unsigned_mixed_expr 
lint preference -report_assign_mixed_expr  
lint preference -report_const_mixed_expr  
lint report check -severity error signed_unsigned_mixed_expr   

### InvalidMacroCall-ML
lint on macro_name_not_standard  
lint preference name -check macro_name_not_standard -prefix { }  
lint report check -severity error macro_name_not_standard  

### Check_forloop_Index - check the index of a for loop
lint on loop_index_modified  
lint on loop_index_not_int  
lint on loop_index_in_multi_always_blocks   
lint report check -severity info loop_index_modified  
lint report check -severity info loop_index_not_int  
lint report check -severity warning loop_index_in_multi_always_blocks  

### DuplicateCase-ML - The conditions of a case/unique-case/unique0-case/priority-case construct should not be duplicated.
lint on case_item_duplicate  
lint report check -severity error case_item_duplicate  

### UseSVAlways-ML
lint on always_comb_recommended   
lint on always_ff_recommended   
lint on always_latch_recommended  
lint report check -severity error always_comb_recommended  
lint report check -severity error always_ff_recommended  
lint report check -severity error always_latch_recommended  

### RptNegEdgeFF-ML
lint on flop_with_inverted_clock  
lint preference -check flop_with_inverted_clock -allow_clock_edge positive
lint report check -severity info flop_with_inverted_clock  

### UnInitializedReset-ML - Ensure that there are no uninitialized signals in reset block of a flip-flop.
lint on flop_without_control  
lint on reset_set_non_const_assign  
lint preference -valid_flop_controls sync_reset   
lint report check -severity error flop_without_control  
lint report check -severity error reset_set_non_const_assign  

### RegInput-ML - Module input ports should be registered
lint on module_input_not_registered   
lint preference -report_all_modules_inputs  
lint report check -severity warning module_input_not_registered  

### RegOutputs - Some output ports from a top module are not registered
lint on module_output_not_registered   
lint preference -report_all_modules_outputs (not on)
lint report check -severity warning module_output_not_registered  

### AvoidAsync
lint on reset_style_disallowed  
lint preference -disallow_reset_style async  
lint report check -severity info reset_style_disallowed  

### DisallowXInCaseZ-ML Do not use "x" in casez statements
lint on casez_has_x  
lint report check -severity error casez_has_x  

### OneModule-ML  File has more than one module
lint on file_with_multi_modules  
lint report check -severity error file_with_multi_modules  

### FileHdr Standard header not found at the top of source file
lint on header_field_file_invalid  
lint on file_header_template_mismatch  
lint on header_missing  
lint report check -severity warning header_field_file_invalid  
lint report check -severity warning file_header_template_mismatch  
lint report check -severity warning header_missing  

### ModuleInIncludeFile - module in include file
lint on include_file_construct_disallowed  
lint report check -severity warning include_file_construct_disallowed  

### ArrayIndex Bus signals are declared with low-order bit first
lint on bus_conn_to_inst_reversed   
lint report check -severity error bus_conn_to_inst_reversed  

### ImproperRangeIndex-ML  Possible discrepancy in the range index or slice of an array
lint on variable_width_slice_disallowed    
lint report check -severity error variable_width_slice_disallowed  

### DetectUnderAndOverFlows-ML (Capture underflow and overflows due to castings)
lint on assign_width_overflow   
lint on assign_width_underflow  
lint report check -severity error assign_width_overflow  
lint report check -severity warning assign_width_underflow  

### UseParamInsteadDefine-ML 

### IfOverlap-ML
lint on if_conditions_overlap  
lint report check -severity error if_conditions_overlap  

### DefaultState
lint on fsm_without_default_state  
lint report check -severity warning fsm_without_default_state  

### BlockHeader - Identifies ports and generics in the block statement header which are not synthesizable
lint on unsynth_block_stmt_header  
lint report check -severity warning unsynth_block_stmt_header  

### bothedges - Identifies the variable whose both the edges are used in an event control list
lint on sensitivity_list_var_both_edges  
lint report check -severity error sensitivity_list_var_both_edges  

### InterfaceWithoutModport-ML - Interfaces should make use of modport declarations.
lint on interface_without_modport  
lint report check -severity error interface_without_modport  

### ReportPortInfo-ML  
lint on generate_port_info 
lint report check -severity info generate_port_info  

 
### badimplicitSM2 - Identifies the implicit sequential logic in a non-synthesizable modeling style where states are not updated on the same clock phase 
lint on clock_with_both_edges  
lint preference -check clock_with_both_edges ‑clock_with_both_edges_scope module  
lint report check -severity error clock_with_both_edges

### badimplicitSM4 - Identifies the non-synthesizable implicit sequential logic where event control expressions have multiple edges
lint on sensitivity_list_var_both_edges
lint report check -severity error sensitivity_list_var_both_edges 

### STX_VE_462 - Expecting assignment pattern in place of concatenation.
lint on preceding_apostrophe_missing  
lint report check -severity error preceding_apostrophe_missing  

### STX_VE_467 - Non-equivalent data types are found in assignment operation.
lint on assign_int_to_real  
lint on assign_int_to_reg  
lint on assign_real_to_bit  
lint on assign_real_to_int  
lint on assign_real_to_reg  
lint on assign_reg_to_int  
lint on assign_reg_to_real  
lint report check -severity error assign_int_to_real  
lint report check -severity error assign_int_to_reg  
lint report check -severity error assign_real_to_bit  
lint report check -severity error assign_real_to_int  
lint report check -severity error assign_real_to_reg  
lint report check -severity error assign_reg_to_int  
lint report check -severity error assign_reg_to_real  

### STX_VE_361 - A procedural assignment statement cannot drive a net other than reg type.


### W421 - Reports “always” or “process” constructs that do not have an event control
lint on always_without_event  
lint report check -severity error always_without_event  

### W442a - Ensure that for unsynthesizable reset sequence, first statement in the block must be an if statement
lint on async_block_top_stmt_not_if  
lint report check -severity error async_block_top_stmt_not_if  

### W442b - Ensure that for unsynthesizable reset sequence, reset condition is not too complex
lint on seq_block_has_complex_cond
lint preference -check seq_block_has_complex_cond -report_complex_reset_set_only
lint report check -severity error seq_block_has_complex_cond

### W110a - Use same port index bounds in component instantiation
lint on inst_port_width_mismatch
lint report check -severity error inst_port_width_mismatch

### W416 - Width of return type and return value of a function should be same
lint on func_return_value_unspecified
lint report check -severity error func_return_value_unspecified

### W215 / W216 - Reports inappropriate bit-selects of integer or time variables
lint on data_type_bit_select_invalid 
lint report check -severity error data_type_bit_select_invalid

### W289 / W292 - Reports real operands that are used in logical comparisons
lint on comparison_has_real_operand  
lint report check -severity error comparison_has_real_operand  

### W293 - Reports functions that return real values
lint on unsynth_func_returns_real  
lint report check -severity error unsynth_func_returns_real   

### W317 - Reports assignment to a supply net
lint on assign_to_supply_net  
lint report check -severity error assign_to_supply_net  

### W352 - Reports for constructs with condition expression that evaluates to a constant.
lint on loop_condition_const  
lint report check -severity error loop_condition_const  

### W398 - Reports a case choice when it is covered more than once in a case statement
lint on case_item_duplicate   
lint report check -severity error case_item_duplicate  

### W422 - Unsynthesizable block or process: event control has more than one clock
lint on seq_block_has_multi_clks  
lint report check -severity error seq_block_has_multi_clks  

### W424 - Ensure that a function or a sub-program does not sets a global signal/variable
lint on func_sets_global_var  
lint on procedure_sets_global_var   
lint report check -severity error func_sets_global_var   
lint report check -severity error procedure_sets_global_var   

### W425 - Ensure that a function or a sub-program does not uses a global signal/variable  
lint on func_uses_global_var   
lint on procedure_uses_global_var   
lint report check -severity error func_uses_global_var   
lint report check -severity error procedure_uses_global_var   

### W426 - Ensure that the task does not sets a global variable
lint on task_sets_global_var   
lint report check -severity error task_sets_global_var  

### W427 - Ensure that a task does not uses a global variable
lint on task_uses_global_var 
lint report check -severity error task_uses_global_var  

### W428 - Ensure that a task is not called inside a combinational block
lint on task_in_combo_block  
lint report check -severity error task_in_combo_block  

### W467 - Use of don’t-care except in case labels may lead to simulation/synthesis mismatch
lint on assign_or_comparison_has_x  
lint report check -severity error assign_or_comparison_has_x    
lint preference -skip_case_dont_care  

### W481a - Ensure that a for loop uses the same step variable as used in the condition
lint on loop_step_incorrect  
lint report check -severity error loop_step_incorrect  

lint on for_loop_infinite  
lint report check -severity error for_loop_infinite

### W481b - Ensure that a for loop uses the same initialization variable as used in the step expression
lint on loop_var_not_in_condition  
lint report check -severity error loop_var_not_in_condition  
  
### W496a - Reports comparison to a tristate in a condition expression 
lint on tristate_enable_with_expr    
lint report check -severity error tristate_enable_with_expr  

### W496b - Reports comparison to a tristate in a case statement
lint on case_condition_with_tristate  
lint report check -severity error case_condition_with_tristate   

### W71 - Ensure that a case statement or a selected signal assignment has a default or OTHERS clause
lint on case_default_missing  
lint preference -missing_others_or_default  
lint report check -severity error case_default_missing  

### W116 - Identifies the unequal length operands in the bit-wise logical, arithmetic, and ternary operators
lint on expr_operands_width_mismatch  
lint report check -severity error expr_operands_width_mismatch  

### W122 - A signal is read inside a combinational always block but is not included in the sensitivity list
lint on sensitivity_list_var_missing  
lint report check -severity error sensitivity_list_var_missing  

### W123 - Identifies the signals and variables that are read but not set
lint on var_read_not_set  
lint report check -severity error var_read_not_set  

### W19 - Reports the truncation of extra bits
lint on const_value_size_mismatch  
lint report check -severity error const_value_size_mismatch  

### W218 - Reports multi-bit signals used in sensitivity list
lint on sensitivity_list_edge_multi_bit  
lint on sensitivity_list_var_range  
lint report check -severity error sensitivity_list_edge_multi_bit   
lint report check -severity error sensitivity_list_var_range  

### W240 -An input has been declared but is not read
lint on input_port_not_read  
lint report check -severity warning input_port_not_read  

### W263 -Reports a case expression width that does not match case select expression width
lint on case_width_mismatch   
lint report check -severity error case_width_mismatch  

### W337 Reports illegal case construct labels 
lint on case_with_x_z  
lint on casez_has_x  
lint on casex_has_z  
lint report check -severity error case_with_x_z  
lint report check -severity error casez_has_x   
lint report check -severity error casex_has_z  

### W486 - Reports shift overflow operations
lint on unsynth_shift_operator  
lint report check -severity error unsynth_shift_operator  

### W499 - Ensure that all bits of a function are set
lint on func_bit_not_set  
lint report check -severity error -alias W499 func_bit_not_set  

### W502 - Ensure that a variable in the sensitivity list is not modified inside the always block
lint on sensitivity_list_var_modified  
lint report check -severity error -alias W502 sensitivity_list_var_modified   

### W505 - Ensure that the signals or variables have consistent value
lint on assigns_mixed   
lint on assigns_mixed_in_always_block  
lint report check -severity error assigns_mixed_in_always_block  
lint report check -severity error -alias W505 assigns_mixed  

### W66 - Ensure that a repeat construct has a static control expression
lint on repeat_ctrl_not_const  
lint report check -severity error -alias W66 repeat_ctrl_not_const  

### W336 - Blocking assignment should not be used in a sequential block (may lead to shoot through)
lint on blocking_assign_in_seq_block  
lint report check -severity error -alias W336 blocking_assign_in_seq_block  

### W414 - Reports nonblocking assignment in a combinational block
lint on nonblocking_assign_and_delay_in_always  
lint on nonblocking_assign_in_combo_block  
lint report check -severity error nonblocking_assign_and_delay_in_always  
lint report check -severity error nonblocking_assign_in_combo_block  

### W450l - Reports multi-bit expression used as latch enable condition multi bit latch

### W259 - Signal has multiple drivers
lint on multi_driven_signal  
lint report check -severity error  multi_driven_signal   

### W415 - Reports variable/signals that do not infer a tristate and have multiple simultaneous drivers
lint on tristate_multi_driven (not on)  
lint on multi_driven_signal   
lint report check -severity error multi_driven_signal  

### W156 - Do not connect buses in reverse order
lint on bus_conn_to_inst_reversed  
lint report check -severity warning bus_conn_to_inst_reversed  

### W287a/b - Some inputs/outputs to instance are not driven or unconnected
lint on unconnected_inst_output   
lint on unconnected_inst_input
lint report check -severity warning unconnected_inst_input 
lint report check -severity warning unconnected_inst_output

### W224 - Multi-bit expression found when one-bit expression expected
lint on condition_is_multi_bit  
lint report check -severity error condition_is_multi_bit  

### W339a - Case equal operator (===) and case not equal (!==) operators may not be synthesizable
lint on operator_disallowed  
lint preference -check operator_disallowed -disallow_verilog_operators !== ===   
lint report check -severity error operator_disallowed  

### W430 - The "initial" statement is not synthesizable
lint on unsynth_initial_stmt  
lint report check -severity warning unsynth_initial_stmt   

### W257 - Synthesis tools ignore delays 
lint on unsynth_delay_in_net_decl  
lint on unsynth_delay_in_stmt  
lint on unsynth_delay_in_bidirectional_switch  
lint on unsynth_delay_in_gate  
lint on unsynth_delay_in_mos_switch  
lint on unsynth_delay_in_cmos_switch  
lint on unsynth_delay_in_blocking_assign   
lint on unsynth_delay_in_tristate_gate  
lint report check -severity error unsynth_delay_in_net_decl   
lint report check -severity error unsynth_delay_in_stmt   
lint report check -severity error unsynth_delay_in_bidirectional_switch   
lint report check -severity error unsynth_delay_in_gate   
lint report check -severity error unsynth_delay_in_mos_switch   
lint report check -severity error unsynth_delay_in_blocking_assign  
lint report check -severity error unsynth_delay_in_tristate_gate  
lint report check -severity error unsynth_delay_in_cmos_switch  

### W294 -  Real variable is not synthesizable. 
lint on unsynth_real_var  
lint report check -severity error unsynth_real_var  

### W182g/h/k Reports trireg, tri1, tri0 declarations that are not synthesizable
lint on unsynth_tri_net  
lint report check -severity error unsynth_tri_net  

### W182n - Reports MOS switches, such as cmos, pmos, and nmos, that are not synthesizable
lint on unsynth_mos_switch   
lint report check -severity error unsynth_mos_switch   

 ### W213 - Reports PLI tasks or functions that are not synthesizable
lint on unsynth_pli_task_func  
###lint preference -check unsynth_pli_task_func -allow_pli_task {display info warning error fatal}   
###lint preference -check unsynth_pli_task_func -disallow_pli_task  
lint report check -severity error unsynth_pli_task_func  

### W495 - inout port is never set
lint on inout_port_not_set  
lint report check -severity warning inout_port_not_set   

### W120 - A variable has been defined but is not used
lint on var_unused   
lint report check -severity warning var_unused  

### W241 - Output is never set
lint on output_port_not_set  
lint report check -severity warning output_port_not_set  

### W494 - Inout port is not used
lint on inout_port_unused  
lint report check -severity warning inout_port_unused  

### W210 - Number of connections made to an instance does not match number of ports on master
lint on unconnected_inst_input   
lint on unconnected_inst_output  
lint on unconnected_inst_inout  
lint on unconnected_inst  
lint report check -severity warning unconnected_inst_input   
lint report check -severity warning unconnected_inst_output  
lint report check -severity warning unconnected_inst_inout  
lint report check -severity warning unconnected_inst  

### W121 - A variable name collides with and may shadow another variable
lint on var_name_duplicate   
lint preference -ignore_var_subroutine_duplicate 
lint report check -severity error var_name_duplicate  

### W164a/b
lint on assign_width_overflow   
lint on assign_width_underflow   
lint preference -calc_width_using_expr_range   
lint report check -alias W164b -severity error assign_width_overflow  
lint report check -alias W164a -severity error assign_width_underflow  

### W362
lint on comparison_width_mismatch  
lint report check -severity error comparison_width_mismatch  

### W110* - Widths of an instance port and its connected net are not equal. 
lint on inst_port_width_mismatch  
lint report check -severity error inst_port_width_mismatch  

### W348 - Operand used in concatenation expression without specifying width. 
lint on concat_expr_with_unsized_operand  
lint report check -severity error concat_expr_with_unsized_operand  

### W193 - Statement is empty
lint on empty_stmt  
lint report check -severity error empty_stmt  

### W527 - Nested conditional statement has a dangling else statement. 
lint on else_condition_dangling   
lint report check -severity warning else_condition_dangling  

### W192
lint on empty_block  
lint report check -severity warning   

### W129 - Variable delay values should be avoided
lint on delay_var  
lint report check -severity error delay_var  

### W188 - Do not write to input ports
lint on input_port_set  
lint report check -severity error input_port_set  

### W504 - Integer is used in port expression
lint on port_exp_with_integer  
lint report check -severity error port_exp_with_integer  

### W171 - Case label is non-constant/invalid.
lint on case_item_not_const  
lint on case_item_invalid  
lint report check -severity warning case_item_not_const   
lint report check -severity warning case_item_invalid  

### W372 - A PLI function ($something) not recognized
lint on unsynth_pli_task_func  
lint report check -severity error unsynth_pli_task_func   

### W468 - Index variable is too short
lint on var_index_range_insufficient 
lint report check -severity warning var_index_range_insufficient 

### W576 Logical operation on a vector
lint on logical_operator_on_multi_bit  
lint report check -severity error logical_operator_on_multi_bit  

### W154 Net is declared and assigned in the same statement
lint on net_decl_with_assign  
lint report check -severity error net_decl_with_assign  

### W175 A parameter/generic has been defined but is not used
lint on parameter_not_used   
lint report check -severity warning parameter_not_used    

### WRN_40
lint on identifier_name_not_unique  
lint preference -check identifier_name_not_unique -report_variables_only  
lint preference -check identifier_name_not_unique -allow_loop_var_in_different_process  
lint report check -severity error identifier_name_not_unique  

### WRN_54 - Overriding undefined parameter with null expression
lint on module_with_null_port
lint report check -severity error module_with_null_port

### WRN_70 - IEEE has deprecated 'Standalone Generate Block'
add this as a check outside lint

### WRN_32 - Only white space or a comment may appear on the same line as the `include compiler directive.
will add this as a check outside lint

### WRN_26 - The macro has been redefined with a different value. If this is not really intended, it may produce unexpected synthesis results.
lint on macro_redefined
lint report check -severity warning macro_redefined

### WRN_1469 - Incompatible assignment to the enum variable

### WRN_1453 - Output/inout port specification for an instance must be valid as per the port definition.
lint on inst_port_net_type_mismatch  
lint report check -severity error inst_port_net_type_mismatch  

### WRN_1467 - Multiple connections to a port in the instance
lint on multi_driven_signal
lint report check -severity error multi_driven_signal 

### WRN_1042 - Identifier not declared for implicit port mapping using .*,an empty connection would be created for this port.
lint on unconnected_inst
lint report check -severity warning unconnected_inst

### WRN_1041 - Underscore (_) present at the start/end of a numeric value will be ignored.

### WRN_1036 Expecting explicit event control immediately after always_ff. (Nested event controls inside always blocks might be not be synthesizable.)
lint on always_has_nested_event_control  
lint report check -severity error always_has_nested_event_control  

lint on flop_output_in_initial
lint report check -severity warning flop_output_in_initial

### SYNTH_5143 - Initial block is ignored for synthesis.
lint on unsynth_initial_stmt  
lint report check -severity error unsynth_initial_stmt

### SYNTH_5142 - Specify block is ignored for synthesis
lint on unsynth_specify_block  
lint report check -severity error unsynth_specify_block  

### SYNTH_5064 Non-synthesizable statements are ignored for synthesis.
lint on unsynth_assert_stmt  
lint preference ‑disallowed_sv_assertion all  
lint report check -severity error unsynth_assert_stmt  

### SYNTH_196 - Task must not have event control statements for synthesis.
lint on task_has_event
lint report check -severity error task_has_event

### SYNTH_132 - Hierarchical reference is not synthesizable. 
lint on unsynth_hier_reference  
lint report check -severity error unsynth_hier_reference  

### SYNTH_12608 - The logic of the always block mismatches with the type of the always block
lint on latch_combo_mixed  
lint report check -severity error latch_combo_mixed  

### SYNTH_12605 - Priority/Unique Type if/case statement is being used but all the conditions are not covered

### SYNTH_1082 - Multiple event control statements associated with always_ff are not permissible.
lint on always_has_multiple_events  
lint report check -severity error always_has_multiple_events  

### SYNTH_1111 - Union [unpacked] is not synthesizable.
lint on unpacked_struct_or_union  
lint report check -severity error unpacked_struct_or_union  

### SYNTH_1092 Multiple event control statements associated with always_ff are not permissible.
lint on always_has_multiple_async_control
lint report check -severity error always_has_multiple_async_control

### STARC05-2.1.6.5 - Do not use x and z for an array index
lint on index_x_z 
lint report check -severity error -alias STARC05-2.1.6.5 index_x_z

### STARC05-2.3.1.2c -  User defined primitives might not be synthesizable. 
lint on unsynth_udp 
lint report check -severity error -alias STARC05-2.3.1.2c unsynth_udp

### STARC05-2.10.2.3 - Do not perform logical negation on vectors.
lint on logical_not_on_multi_bit  
lint report check -severity error -alias STARC05-2.10.2.3 logical_not_on_multi_bit  

### STARC05-2.11.3.1 - Ensure that the sequential and combinational parts of an FSM description should be in separate always blocks. 
lint on fsm_coding_style_disallowed  
lint preference -check fsm_coding_style_disallowed ‑allow_fsm_coding_style separate_processes  
lint report check -severity warning -alias STARC05-2.11.3.1 fsm_coding_style_disallowed  

### STARC05-2.3.1.5b - Ensure that the delay values are non-negative.
lint on delay_negative  
lint report check -severity error -alias STARC05-2.3.1.b delay_negative  

### STARC05-2.1.2.4 - task constructs should not be used in the design.
lint on task_in_seq_block  
lint on task_in_combo_block  
lint report check -severity error -alias STARC05-2.1.2.4 task_in_seq_block  
lint report check -severity error -alias STARC05.2.1.2.4 task_in_combo_block  

### STARC05-2.1.3.1 -Bit-width of function arguments must match bit-width of the corresponding function inputs.
lint on func_input_width_mismatch  
lint report check -severity error -alias STARC05-2.1.3.1 func_input_width_mismatch  

### STARC05-2.2.3.3 - Signal is assigned more than once in a sequential block.
lint on seq_block_has_duplicate_assign   
lint report check -severity error -alias STARC05-2.2.3.3 seq_block_has_duplicate_assign  

 ### STARC05-2.3.1.6 - Check the logic level of the reset signal as specified in the sensitivity list of the always block.
lint on reset_polarity_mismatch  
lint report check -severity error -alias STARC05-2.3.1.6 reset_polarity_mismatch   

### STARC05.2.5.1.7 - Do not use tristate output in the conditional expression of an if statement.
lint on if_condition_with_tristate  
lint report check -severity error -alias STARC05-2.5.1.7 if_condition_with_tristate  

### STARC05-2.5.1.9 - Do not enter a tristate output in the selection expression of casex and casez statement.
lint on case_condition_with_tristate  
lint report check -severity error -alias STARC05-2.5.1.9 case_condition_with_tristate  

### STARC05-2.10.3.2a - Bit-width of operands of a logical operator must match
lint on expr_operands_width_mismatch   
lint report check -severity error -alias STARC05-2.10.3.2a expr_operands_width_mismatch   

### STARC05-1.2.1.2 - Do not create an RS latch using primitive cells such as AND, OR
lint on gate_instantiation   
lint report check -severity error -alias STARC05-1.2.1.2 gate_instantiation  

### STARC05-1.4.3.4 - Do not use flip-flop clock signals as non-clock signals
lint on clock_signal_as_non_clock 
lint preference -check clock_signal_as_non_clock -report_all_non_clock_usages
lint report check -severity error -alias STARC05-1.4.3.4 clock_signal_as_non_clock   

### STARC05-2.1.4.5 - Use bit-wise operators instead of logic operators in multi-bit operations
lint on logical_operator_on_multi_bit   
lint report check -severity error -alias STARC05-2.1.4.5 logical_operator_on_multi_bit  

### STARC05-2.4.1.5 - Do not use two level latches in the same phase clock
lint on serial_latches_open_together  
lint report check -severity error -alias STARC05-2.4.1.5 serial_latches_open_together  

### STARC05-2.5.1.2 Ensure that logic does not exist in tristate enable conditions
lint on tristate_enable_with_expr  
lint report check -severity error -alias STARC05-2.5.1.2 tristate_enable_with_expr   

### STARC05-2.10.1.4a/b - Signals must not be compared with X or Z or ?
lint on assign_or_comparison_has_x   
lint on assign_or_comparison_has_z 
lint preference -check assign_or_comparison_has_z -report_stmt_type comparison
lint report check -alias STARC2.10.1.4 -severity error assign_or_comparison_has_x  
lint report check -alias STARC2.10.1.4 -severity error assign_or_comparison_has_z 

### STARC05-2.3.3.1/2 - Do not use edges of multiple clocks in same always block.
lint on seq_block_has_multi_clks  
lint report check -severity error seq_block_has_multi_clks  

### STARC05-3.2.4.3 - Do not use defparam statements
lint on unsynth_defparam   
lint report check -severity error unsynth_defparam  

### STARC05-1.1.1.2 - Names should follow recommended naming convention
lint on signal_name_not_standard  
lint on port_name_not_standard  
lint on module_name_not_standard  
lint on udp_name_not_standard  
lint on task_name_not_standard   
lint on func_name_not_standard  
lint on inst_name_not_standard   
lint on label_name_not_standard  
lint on process_label_not_standard  
lint preference name -check signal_name_not_standard -disallow_special_character -disallow_prefix 0 1 2 3 4 5 6 7 8 9  
lint preference name -check port_name_not_standard -disallow_special_character -disallow_prefix 0 1 2 3 4 5 6 7 8 9  
lint preference name -check module_name_not_standard -disallow_special_character -disallow_prefix 0 1 2 3 4 5 6 7 8 9  
lint preference name -check udp_name_not_standard -disallow_special_character -disallow_prefix 0 1 2 3 4 5 6 7 8 9  
lint preference name -check task_name_not_standard -disallow_special_character -disallow_prefix 0 1 2 3 4 5 6 7 8 9  
lint preference name -check func_name_not_standard -disallow_special_character -disallow_prefix 0 1 2 3 4 5 6 7 8 9  
lint preference name -check label_name_not_standard -disallow_special_character -disallow_prefix 0 1 2 3 4 5 6 7 8 9  
lint preference name -check process_label_not_standard -disallow_special_character -disallow_prefix 0 1 2 3 4 5 6 7 8 9  
lint report check -severity warning signal_name_not_standard  
lint report check -severity warning port_name_not_standard  
lint report check -severity warning func_name_not_standard   
lint report check -severity warning inst_name_not_standard   
lint report check -severity warning label_name_not_standard   
lint report check -severity warning module_name_not_standard   
lint report check -severity warning process_label_not_standard   
lint report check -severity warning task_name_not_standard   
lint report check -severity warning udp_name_not_standard   

### STARC05-1.1.1.3 - Do not use the reserved Verilog, SystemVerilog, or VHDL keywords. (Verilog)
lint on reserved_keyword  
lint preference -reserved_user_words Unused State McpX Rpt  
lint report check -severity error -alias STARC05-1.1.1.3 reserved_keyword  

### STARC05-2.2.2.2b - Sensitivity list has a constant value. 
lint on sensitivity_list_has_constant   
lint report check -severity error -alias STARC05-2.2.2.2b sensitivity_list_has_constant  

### STARC05-2.2.2.3a - Multiple event Expressions should not be described with always constructs. (Verilog)
lint on always_has_multiple_events  
lint report check -severity error -alias STARC05-2.2.2.3a always_has_multiple_events  

### STARC05-2.10.3.7 - Match the bit-width with the base number part
lint on const_value_size_mismatch  
lint report check -severity error -alias STARC05-2.10.3.7 const_value_size_mismatch  

### STARC05-2.10.3.6 - Bit width of literal is not specified or specified as zero. 
lint on literal_bit_width_not_specified  
lint preference limit -literal_width_unspecified 32  
lint report check -severity error -alias STARC05-2.10.3.6 literal_bit_width_not_specified  

### STARC05-1.4.3.1a - Clocks should not be inverted
lint on flop_with_inverted_clock
lint preference -check flop_with_inverted_clock -allow_clock_edge positive
lint report check -severity warning -alias STARC05-1.4.3.1a flop_with_inverted_clock  

### STARC05-1.4.3.1b - Clocks should not be gated
lint on clock_gated
lint preference -clock_gen_module {}
lint report check -severity warning -alias STARC05-1.4.3.1.b clock_gated

### STARC05-2.8.1.5 - Do not use the full_case directive. (Verilog)
lint on case_stmt_with_full_case  
lint report check -severity error -alias STARC05-2.8.1.5 case_stmt_with_full_case 

### STARC05-2.8.5.1 - Do not use the parallel_case directive. (Verilog)
lint on case_stmt_with_parallel_case  
lint report check -severity error -alias STARC05-2.8.5.1 case_stmt_with_parallel_case

### STARC05-2.8.3.5 - default clause in case constructs must be the last clause. (Verilog)
lint on case_default_not_last_item   
lint report check -severity warning -alias STARC05-2.8.3.5 case_default_not_last_item   

### STARC05-2.2.3.1 Non-blocking assignment should not be used in combinational always blocks 
lint on nonblocking_assign_in_combo_block  
lint report check -severity error -alias STARC05-2.2.3.1 nonblocking_assign_in_combo_block  

### STARC05-1.1.1.1  Filename does not match module name or entity name inside the file. 
lint on file_module_name_mismatch  
lint report check -severity error -alias STARC05-1.1.1.1 file_module_name_mismatch  
lint preference -ignore_file_suffix  
lint preference -ignore_file_prefix  

### INFO_1010 - UDP translated to its synthesizable model.

### WRN_127 Enumeration literal must not be out of range (VHDL)
lint on unsynth_array_index_type_enum
lint report check -severity warning unsynth_array_index_type_enum

### SGDC_waive35 - Reports in waive -import command specifies an ip name which is not present in current design.

lint preference -all_undriven_violations

lint preference comment -file {//\s*File\s?:\s+.*}  ### FileHdr
### lint preference comment -header_template_file <file_path>
lint preference ‑array_order_recommended ascending

lint preference -port_info_file_path port_info/port_info.rpt

### sim race07

### CheckExprCast

### W372 (Cast)

lint preference -check macro_disallowed -disallow_macros 
lint on case_with_memory_output
lint report check -severity warning case_with_memory_output 
