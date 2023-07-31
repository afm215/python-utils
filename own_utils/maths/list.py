from enum import Enum
import time
class _SortMode(Enum):
    DEFAULT=0
    INDEX = 1 
    KEY = 2

class OrderedList:

    def _dichotomy_insert(self, list_: list, new_elt, new_elt_sort_value) -> list:
        if len(list_) == 0:
            return [new_elt]
        elt = list_[0]
        elt_sort_value = elt if self.sort_mode == _SortMode.DEFAULT else elt[self.sort_on]
        if elt_sort_value > new_elt_sort_value:
            return [new_elt] + list_
        if len(list_) == 1:
            return [elt, new_elt]

        half_list_length = len(list_) // 2
        splited_list_1, splited_list_2 = list_[:half_list_length], list_[half_list_length:]
        elt = splited_list_2[0]
        elt_sort_value = elt if self.sort_mode == _SortMode.DEFAULT else elt[self.sort_on]   
        if new_elt_sort_value< elt_sort_value:
            return self._dichotomy_insert(splited_list_1, new_elt, new_elt_sort_value) + splited_list_2
        return splited_list_1 + self._dichotomy_insert(splited_list_2, new_elt, new_elt_sort_value)

    
    def append(self, new_elt, verbose=0):
        new_elt_sort_value = new_elt if self.sort_mode == _SortMode.DEFAULT else new_elt[self.sort_on]
        if verbose > 0:
            begin = time.perf_counter()
        if self.insert_mode == "dichotomy":
            if verbose > 0:
                print("using dichotomy", flush=True)
            self.list_ = self._dichotomy_insert(self.list_, new_elt, new_elt_sort_value)
            if verbose > 0:
                end = time.perf_counter()
                print("list insertion done in ", end - begin , flush=True)
            return

        for i, elt in enumerate(self.list_):
            elt_sort_value = elt if self.sort_mode == _SortMode.DEFAULT else elt[self.sort_on]   
            if new_elt_sort_value< elt_sort_value:
                self.list_.insert(i, new_elt) 
                if verbose > 0:
                    end = time.perf_counter()
                    print("list insertion done in ", end - begin , flush=True)
                return
        self.list_.append(new_elt)
        if verbose > 0:
            end = time.perf_counter()
            print("list insertion done in ", end - begin , flush=True)
        return


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
            returned_value = OrderedList()
            returned_value.list_ = self.list_[index]
            return returned_value
        return self.list_[index]

    def __str__(self) -> str:
        return str(self.list_)
    def __len__(self):
        return len(self.list_)