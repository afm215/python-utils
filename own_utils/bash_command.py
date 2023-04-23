import subprocess
from . import basics
COMMAND_OUTPUT_IN_STDERR = ["ssh", "bash"]

def run(cmd: str)-> str:
    # split_cmd = list(filter(lambda x: x != '', cmd.split(' ')))
    split_cmd = "source /etc/bashrc && " + cmd
    split_cmd = ['bash', '-c'] +  [split_cmd]
    cmd_return = subprocess.run(split_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    std_out = cmd_return.stdout.decode('UTF-8')
    std_err = cmd_return.stderr.decode('UTF-8')
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
        return_value = return_value[1:]
    if split_on_linebreak:
        return_value = return_value.split('\n')
    if split_on_spaces:
        return_value = basics.flatten_list(basics.split_recursively(return_value, ' '))
    return return_value
    