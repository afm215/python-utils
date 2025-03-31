import numpy as np
from scipy.sparse import coo_matrix, csr_matrix, vstack
from tqdm import tqdm
from functools import partial
import gc
import time
import os
from torch.utils.data import DataLoader, Dataset
## CHATPGT generated
def dense_chunk_to_coo(dense_chunk, idx_dtype, data_type):
    """Convert a chunk of a dense matrix to a COO matrix with given offsets."""
    non_zero_indices = np.nonzero(dense_chunk)
    non_zero_values = np.asarray(dense_chunk[non_zero_indices], dtype=data_type)
    rows = np.asarray(non_zero_indices[0], dtype=idx_dtype)
    cols = np.asarray(non_zero_indices[1], dtype=idx_dtype)
    return coo_matrix((non_zero_values, (rows, cols)), shape=(dense_chunk.shape[0], dense_chunk.shape[1]))

def dense_to_csr_in_stack_chunks(dense_matrix, chunk_size, idx_dtype = np.int32, data_type=np.float32, all_in_once=True):
    rows, cols = dense_matrix.shape
    print("create sparse matrix through chunk", flush=True)
    combined_csr = None
    if not(all_in_once):
        for row_start in tqdm(range(0, rows, chunk_size)):
            row_end = min(row_start + chunk_size, rows)
            chunk = dense_matrix[row_start:row_end]
            coo = dense_chunk_to_coo(chunk, idx_dtype=idx_dtype,data_type=data_type)
            csr_chunk = coo.tocsr()
            if combined_csr is None:
                combined_csr = csr_chunk
            else:
                combined_csr = vstack([combined_csr, csr_chunk]) 
            gc.collect()
    else:
        chunk_list = []
        print("computing all csr chunk", flush=True)
        for row_start in tqdm(range(0, rows, chunk_size)):
            row_end = min(row_start + chunk_size, rows)
            chunk = dense_matrix[row_start:row_end]
            coo = dense_chunk_to_coo(chunk, idx_dtype=idx_dtype,data_type=data_type)
            csr_chunk = coo.tocsr()
            chunk_list.append(csr_chunk)
            gc.collect()
        print("stacking chunks", flush=True)
        combined_csr =  vstack(chunk_list) 


    print("resulting indices dtype", combined_csr.indices.dtype, flush=True)
    print("resulting data dtype", combined_csr.data.dtype, flush=True)
    print("resulting data shape", combined_csr.shape, flush=True)
    # Combine CSR matrices
    return combined_csr

class RowsSet(Dataset):
    def __init__(self, non_zeros_row: np.array, rows:int):
        self.non_zeros_row = non_zeros_row
        self.rows = rows
        self.rows_list = np.arange(0, self.rows)
        self.current_iter_index=0
    def __len__(self):
        return len(self.rows_list)

    def __getitem__(self, idx):
        row = self.rows_list[idx]
        row_mask =  self.non_zeros_row == row
        row_count = np.sum(row_mask)
        return row_count, idx

    def __next__(self):
        if self.current_iter_index == self.len():
            raise StopIteration
        self.current_iter_index += 1
        return self[self.current_iter_index - 1]
    
class ChunkSet(Dataset):
    def __init__(self, over_chunk: np.array, chunk_length=500,  idx_dtype = np.int32, data_type=np.float32):
        self.over_chunk = over_chunk
        self.row_starts = np.arange(0, len(over_chunk), chunk_length)
        self.chunk_length = chunk_length
        self.current_iter_index=0
        self.idx_type = idx_dtype
        self.data_type = data_type
    def __len__(self):
        return len(self.row_starts)
    def __getitem__(self, idx):

        row_start = self.row_starts[idx]
        row_end = min(row_start + self.chunk_length, len(self.over_chunk))
        chunk = self.over_chunk[row_start:row_end]
        return dense_to_csr_tuple(chunk, idx_dtype= self.idx_type, data_type=self.data_type, process_idx=idx)

    def __next__(self):
        if self.current_iter_index == self.len():
            raise StopIteration
        self.current_iter_index += 1
        return self[self.current_iter_index - 1]


def dense_to_csr_tuple(dense_matrix, idx_dtype = np.int32, data_type=np.float32, num_workers=0, prefetch_factor=2, process_idx = 0):
    rows, cols = dense_matrix.shape

    non_zeros =  np.nonzero(dense_matrix)
    non_zeros = (np.asarray(non_zeros[0], dtype=idx_dtype), np.asarray(non_zeros[1], dtype=idx_dtype))
    gc.collect()
    nb_non_zeros = len(non_zeros[0])

    indptr = np.zeros(rows + 1, dtype=idx_dtype)
    data = np.asarray(dense_matrix[non_zeros[0], non_zeros[1]], dtype=data_type)
    indices = np.empty(nb_non_zeros, dtype=idx_dtype)
    
    indptdr_idx = 1
    indices_idx = 0
    iterator = range(rows)
    if num_workers > 0:
        iterator = DataLoader(RowsSet(non_zeros[0], rows), num_workers=num_workers,prefetch_factor=prefetch_factor)
    if process_idx == 0:
        iterator = tqdm(iterator, position=1)
    for item in iterator:
        if type(item) is int: 
            row = item
            row_mask =  non_zeros[0] == row
            cols_indices = non_zeros[1][row_mask]
            row_count = len(cols_indices)
        else:
            row_count, row = item
            row_count = row_count.item()
            row = row.item()
            row_mask =  non_zeros[0] == row


        if row_count > 0:
            indptr[indptdr_idx] = indptr[indptdr_idx - 1] + row_count
            
            indices[indices_idx: indices_idx + len(cols_indices)] = cols_indices
            indices_idx += len(cols_indices)

        else:
            indptr[indptdr_idx] = indptr[indptdr_idx - 1]
        indptdr_idx += 1
    if process_idx == 0:
        iterator.close()
    
    assert indices_idx == nb_non_zeros, f" expected {nb_non_zeros} but got {indices_idx}"
    assert len(indices) == len(data), f"data size with {len(data)} should be the same as indices_idx size with {len(indices_idx)}"
    return data, indices, indptr

def dense_to_csr_in_chunks(dense_matrix, chunk_size, idx_dtype = np.int32, data_type=np.float32, convert_to_csr=False,sub_chunk_size=500, num_workers = 0,prefetch_factor=2):
    
    rows, cols = dense_matrix.shape
    save_path = "/lus/scratch/CT10/cin4694/amfournier/COREDIR/mid_checkpoint.pnz"
    adastra_cluster=False
    if os.path.exists(os.path.dirname(save_path)):
        adastra_cluster = True
        if os.path.exists(save_path):
            print("loading mid checkpoint", flush=True)
            floaded = np.load(save_path)
            return  floaded["data"],floaded["indices"], floaded["indptr"]
    print("getting nb non zero", flush=True)
    nb_non_zeros = np.count_nonzero(dense_matrix)
    print("done, found", nb_non_zeros, " elts", flush=True)
    indptr = np.zeros(rows + 1, dtype=np.int64)
    data = np.empty(nb_non_zeros, dtype=data_type)
    indices = np.empty(nb_non_zeros, dtype=idx_dtype)
    
    data_idx = 0
    indptdr_idx = 1

    for row_start in tqdm(range(0, rows, chunk_size), position=0):
        # for loop here
        row_end = min(row_start + chunk_size, rows)

        over_chunk = dense_matrix[row_start:row_end]
        if sub_chunk_size == 0:
            iterator = [dense_to_csr_tuple(over_chunk, idx_dtype=idx_dtype, data_type=data_type, num_workers=num_workers, prefetch_factor=prefetch_factor)]
        else:
            chunk_dataset = ChunkSet(over_chunk=over_chunk, chunk_length=sub_chunk_size,idx_dtype=idx_dtype, data_type=data_type)
            iterator = DataLoader(chunk_dataset, num_workers=len(chunk_dataset), prefetch_factor=1)
        for elt in iterator:
            chunk_data, chunk_indices, chunk_indptr = elt
            if type(iterator) is DataLoader:
                chunk_data = chunk_data.squeeze().numpy()
                chunk_indices = chunk_indices.squeeze().numpy()
                chunk_indptr = chunk_indptr.squeeze().numpy()
        
            chunk_data_length = len(chunk_data)
            chunk_chunk_indptr_length = len(chunk_indptr) 
            assert chunk_data_length >= np.max(chunk_indptr), f"{chunk_data_length} vs {np.max(chunk_indptr)}"

            data[data_idx: data_idx + chunk_data_length] = chunk_data
            indices[data_idx: data_idx + chunk_data_length] = chunk_indices
            indptr[indptdr_idx: indptdr_idx + chunk_chunk_indptr_length - 1 ] = chunk_indptr[1:] + indptr[indptdr_idx - 1]
            data_idx+=chunk_data_length
            indptdr_idx+= chunk_chunk_indptr_length-1
            assert data_idx >= indptr[indptdr_idx - 1]
        gc.collect()
    indptr = indptr[:indptdr_idx]
    if adastra_cluster:
        np.savez(save_path, data=data, indices=indices, indptr=indptr)
    if convert_to_csr:
        return csr_matrix((data, indices, indptr), shape=dense_matrix.shape)
    return data, indices, indptdr_idx

    print("resulting indices dtype", combined_csr.indices.dtype, flush=True)
    print("resulting data dtype", combined_csr.data.dtype, flush=True)
    print("resulting data shape", combined_csr.shape, flush=True)
    # Combine CSR matrices
    return combined_csr

if __name__ == "__main__":
    from test import RandomMaskedMatrixIterator, test_function

    # Example usage

    # dense_matrix = np.random.random((10000, 10000))  # Example large dense matrix
    # #dense_matrix[dense_matrix < 0.99] = 0  # Sparsify the matrix
    chunk_size = 555  # Define chunk size

    # csr_matrix_ = dense_to_csr_in_chunks(dense_matrix, chunk_size)

    # ground_truth = csr_matrix(dense_matrix)
    

    nb_trial = 10
    print("running ", nb_trial, " trials")
    inputs = RandomMaskedMatrixIterator((10000, 20000), (10000, 20000), nb_trial, 0.2, 42)
    # inputs = RandomMaskedMatrixIterator((100, 1000), (1000000, 2000000), nb_trial, 0, 42)
    #inputs = RandomMaskedMatrixIterator((1000, 2000), (1000, 2000), nb_trial, 0.5, 42)
    
    def comparison_func (I1, I2):
        import time

        print("test dtype is ", I1.dtype)
        print("check type is ", I2.dtype)
        print("idptr test dtyp ", I1.indptr.dtype)
        print("idptr target dtyp ", I2.indptr.dtype)
        assert np.max(I1.indptr) == len(I1.data)
        diff = I1 - I2
        print(diff.multiply(diff).sum())
    test_function(partial(dense_to_csr_in_chunks, chunk_size=chunk_size,convert_to_csr=True,sub_chunk_size=200, num_workers=0, prefetch_factor=12 ),csr_matrix, comparison_func, inputs)

