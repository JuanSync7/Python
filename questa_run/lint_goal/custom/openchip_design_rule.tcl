# openchip goals
# [G001 - G003] not applicable
# [G004] 
lint on interface_modport_unused
# [G005] under review to change to lowercase
# [G006] cant check for this
# [G007] Forbidden signal names
lint on design_element_has_std_word
# [G008-input] Naming Convention for RTL objects - input
lint on input_port_name_not_standard
lint preference -check input_port_name_not_standard -exclude_object_types clock async_reset async_set sync_reset sync_set enable active_low interface output output_driver tristate inout
lint preference name -check input_port_name_not_standard -disallow_consecutive_underscores -disallow_special_characters -disallow_end_with_underscores -suffix i

# [G008] naming conventions for RTL objects - constants
lint on const_name_not_standard
lint preference name -check const_name_not_standard -disallow_lower_case -disallow_mixed_case

# [G008] naming conventions for RTL objects - clock
lint on clock_name_not_standard
lint preference name -check clock_name_not_standard -prefix_or_suffix Clk Clock CLK CLOCK 

# [G008] naming conventions for RTL objects - reset
lint on reset_name_not_standard
lint preference name -check reset_name_not_standard -prefix_or_suffix Res Rst Reset RES RST RESET

# [G009 - G010] not applicable

# [G011] Naming Conventions for RTL files
lint on file_name_not_standard
lint preference name -check file_name_not_standard -regexp {%(module).sv} 
lint preference name -check file_name_not_standard -regexp {%(package)Pkg.sv}
lint preference name -check file_name_not_standard -regexp {%(interface)-i.sv}
lint preference name -check file_name_not_standard -regexp {%(include).svh}

# [G012] not applicable

# [G013] Every RTL needs a header 
lint on file_header_template_mismatch
# lint preference comment -header_template_file <file_path_to_header_file>

# [G014 - G023] not applicable

# [G024] Special Names
lint on reserved_keyword 
lint preference -reserved_user_words Unused State McpX Rpt

# [G025 - G027] not applicable

# [G028] Constant Name (Use parameter instead of `define for constants)
lint on macro_defines_numeric_constant

# [G029a] Include and Define directives
lint on file_extension_not_standard 
lint preference -allow_include_file_extns .svh .vh .h .inc 
# [G029b] Include file must not contain RTL
lint on include_file_construct_disallowed

# [G030] No input/output tie to 1/0
lint on const_output


# [G031] Module instantiations 
lint on inst_name_not_standard
#lint preference name -check inst_name_not_standard -regexp %(design_unit)[0-9]

# [G034] Define Parameter using integer
lint on parameter_with_range
lint on parameter_width_not_specified
lint preference -check parameter_width_not_specified -ignore_string_params
lint preference limit -check parameter_width_not_specified -min_parameter_width 32
lint report check -severity warning parameter_with_range parameter_width_not_specified

# [G035] Case Statements
lint on casex casez
lint report check -alias STARC_2.8.4.3 casex -severity warning casez
lint report check -alias STARC_2.8.4.3 casez -severity warning casex

lint on index_x_z # [G037]
lint report check -severity warning index_x_z # [G037]
lint on gen_label_missing # [G041]
lint report check -severity warning gen_label_missing # [G041]
lint on module_has_multi_clks # [G043]
lint report check -severity warning module_has_multi_clks # [G043]

lint on parameter_assignment_ordered # [E002]
lint report check -severity error parameter_assignment_ordered # [E002]
lint on ordered_port_connection # [E002]
lint report check -severity error ordered_port_connection # [E002]
lint on unsynth_assert_stmt # [E003]
lint report check -severity error unsynth_assert_stmt # [E003]
lint on parameter_width_not_specified # [E006]
lint preference -ignore_string_params # [E006]
lint preference limit -min_parameter_width 32 # [E006]
lint preference -severity error parameter_width_not_specified # [E006]
lint on tristate_inferred # [E007]
lint on tristate_not_at_top_level # [E007]
lint preference -allow_hierarchical_tristate_drives # [E007]
#lint preference -is_block_run # [E007]
lint report check -severity error tristate_inferred # [E007]
lint report check -severity error tristate_not_at_top_level # [E007]
lint on combo_loop # [E008]
lint on combo_loop_with_latch # [E008]
lint report check -severity error combo_loop # [E008]
lint report check -severity error combo_loop_with_latch # [E008]
lint on clock_and_data_same_net_driven # [E009]
lint report check -severity error clock_and_data_same_net_driven # [E009]
lint on design_unit_name_similar # [E010]
lint report check -severity error design_unit_name_similar # [E010]
lint on data_type_not_recommended # [E011]
lint preference -allow_non_port_data_types reg wire tri integer logic interface packed_array struct_union enum #  [G033] [E011]
lint preference -allow_port_data_types tri integer logic interface packed_array struct_union enum # [G033] [E011]
lint report check -severity error data_type_not_recommended # [E011]
lint on bus_conn_to_inst_reversed bit_order_reversed # [E012]
lint report check -severity error bus_conn_to_inst_reversed # [E012]
lint report check -severity error bit_order_reversed # [E012]
# [E013]
# [E014]
lint on assign_or_comparison_has_x # [E015]
lint report check -severity error assign_or_comparison_has_x # [E015]
# [E016]
lint on blocking_assign_in_seq_block # [E017]
lint report check -severity error blocking_assign_in_seq_block # [E017]
lint on non_blocking_assign_in_combo_block # [E017]
lint report check -severity error non_blocking_assign_in_combo_block # [E017]
lint on nonblocking_assign_and_delay_in_always  # [E017]
lint report check -severity error nonblocking_assign_and_delay_in_always  # [E017]
# [E018]

lint on line_char_large # [W001]
lint preference -ignore_comment_length # [W001]
lint preference -tab_width 2 [W001]
lint preference limit -max_char_length 132 # [W001]
lint report check -severity warning line_char_large # [W001]
lint on clock_gated # [W002]
lint report check -severity warning clock_gated # [W002]
lint on latch_inferred # [W003]
lint report check -severity error latch_inferred # [W003]
lint on module_output_not_registered # [W004]
lint preference -report_all_modules_outputs # [W004]
lint report check -severity warning module_output_not_registered # [W004]
lint on var_set_not_read # [W005]
lint report check -severity warning var_set_not_read # [W005]
lint on reset_port_connection_static # [W006]
lint report check -severity warning reset_port_connection_static # [W006]
lint on const_latch_enable # [W006]
lint report check -severity warning const_latch_enable # [W006]
lint on seq_block_has_multi_clks # [W007]
lint report check -severity error seq_block_has_multi_clks # [W007]
lint on undriven_unloaded_signal # [W010]
lint report check -severity warning undriven_unloaded_signal # [W010]
# [W011]
lint on ordered_port_connection 
lint report check -alias OC_W011 -severity warning ordered_port_connection
# [W016]
lint on always_comb_recommended always_ff_recommended always_latch_recommended 
lint report check -alias OC_W016 -severity warning always_comb_recommended always_ff_recommended always_latch_recommended
# [W017]
lint on task_in_seq_block task_in_combo_block 
lint report check -alias OC_W017 -severity warning task_in_combo_block task_in_seq_block


lint on include_path_not_relative
lint report check -severity warning include_path_not_relative
# [H001]
lint on design_file_line_limit 
lint preference limit -check design_file_line_limit -max_file_lines 500 
lint report check -severity info -alias OC_H001 design_file_line_limit
# H002
lint on procedure_exceeds_line_limit func_exceeds_line_limit process_exceeds_line_limit always_exceeds_line_limit
lint preference limit -check procedure_exceeds_line_limit -max_procedure_lines 100
lint preference limit -check func_exceeds_line_limit -max_func_lines 100
lint preference limit -check process_exceeds_line_limit -max_process_lines 100
lint preference limit -check always_exceeds_line_limit -max_always_lines 100
lint report check -alias OC_H002 -severity info procedure_exceeds_line_limit func_exceeds_line_limit process_exceeds_line_limit always_exceeds_line_limit
# [H008]
lint on clock_with_both_edges 
lint report check -alias OC_H008 -severity warning clock_with_both_edges
# [H013]
lint on case_nested 
lint preference limit -case_nested_depth 4 
lint report check -alias OC_H013 -severity warning case_nested
# [H020]
lint on expr_operands_width_mismatch comparison_width_mismatch 
lint report check -alias OC_H020 -severity warning expr_operands_width_mismatch comparison_width_mismatch
# [H028]
lint on start_label_missing 
lint preference -check start_label_missing -start_label_construct verilog_generate 
lint report check -alias OC_H028 -severity warning start_label_missing
# [H029]
lint on space_missing 
lint report check -alias OC_H029 -severity warning space_missing
# [H031]
lint on bit_order_reversed 
lint preference -check bit_order_reversed -array_order_recommended ascending
lint report check -alias OC_H031 -severity warning bit_order_reversed 


# Enable the lint report checks
lint report check -severity warning -alias OC_G004 interface_modport_unused
lint report check -severity info -alias OC_G007 design_element_has_std_word
lint report check -severity warning -alias OC_G024 reserved_keyword
lint report check -severity info -alias OC_G008.input input_port_name_not_standard
lint report check -severity info -alias OC_G008.constant const_name_not_standard
lint report check -severity warning -alias OC_G008.clock clock_name_not_standard
lint report check -severity warning -alias OC_G008.reset 
lint report check -severity warning -alias OC_G011 file_name_not_standard
lint report check -severity warning -alias OC_G013 file_header_template_mismatch
lint report check -severity info -alias OC_G028 macro_defines_numeric_constant
lint report check -severity info -alias OC_G029a file_extension_not_standard 
lint report check -severity warning -alias OC_G029b include_file_construct_disallowed 
lint report check -severity warning -alias OC_G030 const_output
lint report check -severity warning -alias OC_G031 inst_name_not_standard