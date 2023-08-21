__package__="own_utils"

import math 

def split_recursively(list_or_str, *args,  ok_if_not_string=True,delete_empty_string=True, **kwargs):
    """
    Apply a split to a list recursively
    INPUT:
        - list_or_str is a list of elts or a single elt (supposed to be a string)
        - ok_if_not_string : If True, do not raise error if we meet a non list or non string value
    OUTPUT: the splitted output
    """
    if type(list_or_str) == list:
        return [split_recursively(elt, *args,  ok_if_not_string = ok_if_not_string,delete_empty_string = delete_empty_string, **kwargs) for elt in list_or_str]
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

def format_number(input, max_int_length = None,max_decimal_length = None):
    """
    convert a number to str and format it so that the integer part doesn't exceed  max_int_length and the decimal part doesn't exceed max_decimal_length
    """
    output = str(input)
    if not(max_decimal_length is None) and (max_int_length is None):
        return ("{:." + str(max_decimal_length) + "f}").format(input)
    if not(max_int_length is None):
        ten_power = int(math.log(input)/ math.log(10))
        output = input /(10**(ten_power +1 - max_int_length))
        if not(max_decimal_length is None):
            return ("{:." + str(max_decimal_length) + "f}").format(output) + " + 1e" + str(ten_power +1 - max_int_length)
        return str(output) + " + 1e" + str(ten_power +1 - max_int_length)
    return output
class Irange:
    # heavily inspired from https://codereview.stackexchange.com/questions/17543/iterator-and-generator-versions-of-pythons-range
    """
    Create an iterator that takes exaclty the same properties as range on initialization.
    Alterantiveto the range function. This class behaves as an Iterator whereas range generates a sequence
    """
    def __init__(self, start_element, end_element=None, step=1):
        if step == 0:
            raise ValueError('Irange() step argument must not be zero')
        if((type(start_element) is str) or (type(end_element) is str) 
        or (type(step) is str)):
            raise TypeError('Irange() integer expected, got str')
        self.start_element = start_element
        self.item = start_element
        self.end_element = end_element
        self.step = step

        if end_element is None:
            self.start_element = 0
            self.item = 0
            self.end_element = start_element
    def __iter__(self):
        return self
    def __len__(self)-> int:
        return (self.end_element - self.start_element) // self.step
    def __next__(self):
        if self.step > 0:
            if self.item >= self.end_element:
                raise StopIteration
        elif self.step < 0:
            if self.item <= self.end_element:
                raise StopIteration
        returned_item = self.item
        self.item = self.item + self.step
        return returned_item

def cpu_full_afinity():
    import psutil
    import multiprocessing
    p = psutil.Process(os.getpid())
    print(p.cpu_affinity())
    p.cpu_affinity(range(multiprocessing.cpu_count()))
    print(p.cpu_affinity())
