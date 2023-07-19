################################################################################
# Automatically-generated file. Do not edit!
################################################################################

SHELL = cmd.exe

# Each subdirectory must supply rules for building sources it contributes
%.obj: ../%.c $(GEN_OPTS) | $(GEN_FILES) $(GEN_MISC_FILES)
	@echo 'Building file: "$<"'
	@echo 'Invoking: Arm Compiler'
	"C:/ti/ccs1220/ccs/tools/compiler/ti-cgt-arm_20.2.7.LTS/bin/armcl" -mv7M4 --code_state=16 --float_support=none -me -O0 --include_path="C:/Users/nniro/workspace_v12/ethernet_ipc_ex1_basic_cm_superloop" --include_path="C:/Users/nniro/workspace_v12/ethernet_ipc_ex1_basic_cm_superloop/device" --include_path="C:/ti/c2000/C2000Ware_4_02_00_00/driverlib/f2838x/driverlib_cm" --include_path="C:/ti/ccs1220/ccs/tools/compiler/ti-cgt-arm_20.2.7.LTS/include" --define=DEBUG --diag_warning=225 --diag_wrap=off --display_error_number --gen_func_subsections=on --preproc_with_compile --preproc_dependency="$(basename $(<F)).d_raw" $(GEN_OPTS__FLAG) "$<"
	@echo 'Finished building: "$<"'
	@echo ' '


