import numpy as np
from tqdm import tqdm
import gc 

class RandomMatrixIterator:
    def __init__(self, rows_boudaries, cols_boundaries, num_matrices, seed=None):
        
        self.rows_min, self.rows_max = rows_boudaries
        self.cols_min, self.cols_max = cols_boundaries
        self.num_matrices = num_matrices
        self.current = 0
        self.random_state = np.random.RandomState(seed) if seed is not None else np.random

    def __iter__(self):
        return self

    def __next__(self):
        rows = np.random.randint(self.rows_min, self.rows_max)
        cols =  np.random.randint(self.cols_min, self.cols_max)
        if self.current < self.num_matrices:
            self.current += 1
            return self.random_state.random((rows, cols))
        else:
            raise StopIteration
    def __length__(self):
        return self.num_matrices
    
class RandomMaskedMatrixIterator:
    def __init__(self, rows_boudaries, cols_boundaries, num_matrices,zero_proportion=0.5, seed=42):
        
        self.rows_min, self.rows_max = rows_boudaries
        self.cols_min, self.cols_max = cols_boundaries
        self.num_matrices = num_matrices
        self.current = 0
        self.random_state = np.random.RandomState(seed) if seed is not None else np.random
        self.zero_proportion = zero_proportion

    def __iter__(self):
        return self

    def __next__(self):
        rows = np.random.randint(self.rows_min, self.rows_max)
        cols =  np.random.randint(self.cols_min, self.cols_max)
        if self.current < self.num_matrices:
            self.current += 1
            mask = self.random_state.choice([0, 1], size=(rows, cols), p=[self.zero_proportion, 1-self.zero_proportion])

            return np.float64(self.random_state.random((rows, cols)) * mask)
        else:
            raise StopIteration
    def __len__(self):
        return self.num_matrices
        

def test_function(tested_func, ground_truth_func,comparison_func, input_iterator):
    for input in tqdm(input_iterator, total=len(input_iterator)):
        gt = ground_truth_func(input)

        tested_output = tested_func(input)
        gc.collect()
        gc.collect()
        compare_output = comparison_func(tested_output, gt)
        gc.collect()
        if compare_output is not None:
            print(compare_output)
        

        
