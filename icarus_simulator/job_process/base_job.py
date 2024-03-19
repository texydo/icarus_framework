#  2020 Tommaso Ciussani and Giacomo Giuliari

class BaseJob:
    def __init__(self):
        self.num_procs = 128 # TODO
        self.num_batches = 10 # TODO
    
    def run_multiprocessor(data_path, process_params_path, output_path):
        raise NotImplementedError