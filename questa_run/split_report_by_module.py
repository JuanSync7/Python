#!/usr/bin/env python3
import re
def split_file_by_regex(input_file, regex_pattern, output_prefix):
    with open(input_file, 'r') as file:
        content = file.read()
    
    pattern = re.compile(regex_pattern)
        
    x = re.split("Module [0-9]:*", content)
    
    # Find all the Module 
    module_name_list = re.findall("Module [0-9]: [a-zA-Z]*\n",content)
    module_name_list = [re.sub("Module [0-9]: ", "",i) for i in module_name_list]
    module_name_list = [re.sub("\n","",i) for i in module_name_list]
    
    print(module_name_list)

    prefix = "Module: "
    new_x = []
    for item in x:
        new_x.append(prefix + item)
    
    for i,item in enumerate(new_x):
        if i == 0:
            output_file = f'lint_summary.rpt'
        else:
            output_file = f'report/{module_name_list[i]}.rpt'
        with open(output_file, 'w') as file:
            file.write(item)
        print(f"{output_file}: file created")

def walk_directory(directory):
    sub_directory = os.walk(directory)
    return sub_directory
       
def main():
    c = 1
if __name__ == '__main__':
    
    split_file_by_regex('/ln/proj/va_10/a0/workareas/z2jkok/questa_febuild/workdir/VtCcb/lint/Results/report/lint_full.rpt',"^(Module"+" "+"[0-9]"+":*)",'a')
    main()
    