import subprocess
from . import basics
COMMAND_OUTPUT_IN_STDERR = ["ssh", "bash"]

def run(cmd: str, launch_cmd_using_sys_env = True, do_not_split = True, use_shell=False)-> str:
    """
    Launch bash command and return the output
    INPUT: - cmd is the str of the command you want to launch, ex: "cd /home/test && ls -l"
           - launch_cmd_using_sys_env is a boolean. If set to True, the command will be launch with /etc/bashrc allowing to use the function defined in it
           - do_not_split=if set to True, the command will be launch in a subprocess as is. If False, the command will be split on space char
           - use shell, not recommended, do it if your command is a succession of bash commands
    """
    split_cmd = ''

    if launch_cmd_using_sys_env:
        split_cmd = "source /etc/bashrc && " + cmd
        split_cmd = ['bash', '-c'] +  [split_cmd]
    else:
        if do_not_split:
            split_cmd = [cmd]
        else:
            split_cmd = list(filter(lambda x: x != '', cmd.split(' ')))
    if launch_cmd_using_sys_env:
        ## bash -c doesn't work with subprocess.Popen
        cmd_return = subprocess.run(split_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=use_shell)
        std_out = cmd_return.stdout.decode('UTF-8')
        std_err = cmd_return.stderr.decode('UTF-8')
    else:
        p = subprocess.Popen(split_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=use_shell)
        std_out=''
        std_err=''
        while True:
            line_err=p.stderr.readline().decode('UTF-8')
            line_std = p.stdout.readline().decode('UTF-8')
            if not line_std and not line_std:
                break
            std_out+=line_std
            std_err+= line_err
    if split_cmd[0] in COMMAND_OUTPUT_IN_STDERR:
        return std_err
    else:
        if (len(std_err) > 0):
            raise Exception(std_err)
        else:
            return std_out

def convert_output_to_elts_list(output:str, split_on_linebreak=True, split_on_spaces=True, remove_header=True)->list:
    return_value = output
    if remove_header:
        return_value = "\n".join(return_value.split('\n')[1:])
    if split_on_linebreak:
        return_value = return_value.split('\n')
    if split_on_spaces:
        return_value = basics.flatten_list(basics.split_recursively(return_value, ' '))
    return return_value
    
