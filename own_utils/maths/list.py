from enum import Enum
import time
class _SortMode(Enum):
    DEFAULT=0
    INDEX = 1 
    KEY = 2

class OrderedList:

    def _dichotomy_insert(self, list_: list, new_elt, new_elt_sort_value) -> 'tuple[list, int]':
        if len(list_) == 0:
            return [new_elt], 0
        elt = list_[0]
        elt_sort_value = elt if self.sort_mode == _SortMode.DEFAULT else elt[self.sort_on]
        if elt_sort_value > new_elt_sort_value:
            return [new_elt] + list_, 0
        if len(list_) == 1:
            return [elt, new_elt], 1

        half_list_length = len(list_) // 2
        splited_list_1, splited_list_2 = list_[:half_list_length], list_[half_list_length:]
        elt = splited_list_2[0]
        elt_sort_value = elt if self.sort_mode == _SortMode.DEFAULT else elt[self.sort_on]   
        if new_elt_sort_value< elt_sort_value:
            dichotomy_result, insertion_index = self._dichotomy_insert(splited_list_1, new_elt, new_elt_sort_value)
            return dichotomy_result + splited_list_2, insertion_index
        dichotomy_result, insertion_index = self._dichotomy_insert(splited_list_2, new_elt, new_elt_sort_value)
        return splited_list_1 + dichotomy_result, insertion_index + len(splited_list_1)

    
    def append(self, new_elt, verbose=0) -> int:
        new_elt_sort_value = new_elt if self.sort_mode == _SortMode.DEFAULT else new_elt[self.sort_on]
        if verbose > 0:
            begin = time.perf_counter()
        if self.insert_mode == "dichotomy":
            if verbose > 0:
                print("using dichotomy", flush=True)
            self.list_, insertion_index = self._dichotomy_insert(self.list_, new_elt, new_elt_sort_value)
            if verbose > 0:
                end = time.perf_counter()
                print("list insertion done in ", end - begin , flush=True)
                if not(self.sort_mode == _SortMode.DEFAULT):
                    for i, elt in  enumerate(self.list_[1:]):
                        assert elt[self.sort_on] >= self.list_[i][self.sort_on], f"sorting error {elt} vs {self.list_[i]}"
            return insertion_index

        for i, elt in enumerate(self.list_):
            elt_sort_value = elt if self.sort_mode == _SortMode.DEFAULT else elt[self.sort_on]   
            if new_elt_sort_value< elt_sort_value:
                self.list_.insert(i, new_elt) 
                if verbose > 0:
                    end = time.perf_counter()
                    print("list insertion done in ", end - begin , flush=True)
                return i
        insertion_index = len(self)
        self.list_.append(new_elt)
        if verbose > 0:
            end = time.perf_counter()
            print("list insertion done in ", end - begin , flush=True)
        return insertion_index


    def __init__(self, init_list: 'list | None' = None, sort_on: 'int | None | str'= None, insert_mode: 'str | None' = "dichotomy"):
        self.list_ = []
        self.insert_mode = insert_mode
        self.current_index = 0
        if sort_on is None:
            self.sort_mode = _SortMode.DEFAULT
        elif type(sort_on) == int:
            self.sort_mode = _SortMode.INDEX
            self.sort_on = sort_on
        elif type(sort_on) == str:
            self.sort_mode = _SortMode.KEY
            self.sort_on = sort_on
        else:
            raise TypeError("Type Error on sort_on")
        if not(init_list is None):
            for elt in init_list:
                self.append(elt)
        
    def __iter__(self):
        return self
    
    def __next__(self):
      if self.current_index < len(self.list_):
          self.current_index += 1
          return self.list_[self.current_index - 1] 
      else:
          self.current_index = 0
          raise StopIteration
    def __getitem__(self, index):
        if isinstance(index, slice):
            returned_value = OrderedList(sort_on=self.sort_on, insert_mode=self.insert_mode)
            returned_value.list_ = self.list_[index]
            return returned_value
        return self.list_[index]
    
    def __delitem__(self, index):
        del self.list_[index]

    def __str__(self) -> str:
        return str(self.list_)
    def __repr__(self) -> str:
        return f"OrderedList object : {str(self)}"
    def __len__(self):
        return len(self.list_)