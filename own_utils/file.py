def extract_file_lines_to_list(file_path:str, skip_blank_line=True):
    """
    Extract each lines of a file into a list and ignore \n
    INPUT:
        - file path : the path of the file to be considered
        - skip_blank_line : if set to True, remove the blank lines
    """
    file = open(file_path, 'r')
    raw_lines = file.readlines() 
    result = ''.join(raw_lines).split('\n')
    if skip_blank_line:
        result = list(filter(lambda elt: elt!='', result))
    return result