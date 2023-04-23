def split_recursively(list_or_str, *args,  ok_if_not_string=True,delete_empty_string=True, **kwargs):
    """
    Apply a split to a list recursively
    INPUT:
        - list_or_str is a list of elts or a single elt (supposed to be a string)
        - ok_if_not_string : If True, do not raise error if we meet a non list or non string value
    OUTPUT: the splitted output
    """
    if type(list_or_str) == list:
        return [split_recursively(elt) for elt in list_or_str]
    else:
        if ok_if_not_string and type(list_or_str ) != str:
            return list_or_str
        return list(filter(lambda x :x !='', list_or_str.split(*args, **kwargs) )) if delete_empty_string else list_or_str.split(*args, **kwargs)

def flatten_list(list_or_elt):
    """
    Flatten a list
    """
    return_value = []
    for elt in list_or_elt:
        if type(elt) == list:
            return_value += flatten_list(elt)
        else: 
            return_value.append(elt)
    return return_value

def are_all_str_in_list(list1, list2, accept_substr=True, break_on_first_fail = True):
    """
    check if all str in list1 are str (substr if accept_substr) of list2
    return ondices that are not
    INPUT: - list1 : list[str]
           - list2: list[str] 
    """
    returned_value = []
    for i in range(len(list1)):
        elt_found = False
        if accept_substr:
            for elt in list2:
                if list1[i] in list2:
                    elt_found = True
                    break
        else:
            for elt in list2:
                if list1[i] == list2:
                    elt_found = True
                    break
        if not(elt_found):
            if break_on_first_fail:
                return [i]
            else:
                returned_value.append(i)
    return returned_value

def has_value_been_cliped(value, min_val=0, max_val=1):
    """
    Clip value, and return True if the value has indeed been affected
    """
    if value < min_val:
        return min_val, True
    if value > max_val:
        return max_val, True
    return value, False

def cpu_full_afinity():
    import psutil
    import multiprocessing
    kernel_list = generate_filters_list()
    p = psutil.Process(os.getpid())
    print(p.cpu_affinity())
    p.cpu_affinity(range(multiprocessing.cpu_count()))
    print(p.cpu_affinity())
