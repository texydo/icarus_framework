#  2020 Tommaso Ciussani and Giacomo Giuliari
"""
This class defines the abstraction for a computation phase, passed to the IcarusSimulator class to be executed.
This class is open for custom extension, in order to create different phases.

The input and output parameters are identified in IcarusSimulator by string identifiers, which the phase should provide.
The _compute() method, which accepts any parameter in any number, contains the computation logic. Always returns tuple.
    _compute() is intended as a skeleton, where interchangeable steps are determined by BaseStrategy objects
The methods name() and strategies() are used by IcarusSimulator to manage inter-phase dependencies and filenames.
Moreover, this base class provides some basic logs and the resultfile dumping logic.

For an extension example, see any provided phase class. All files in this directory are library-provided phases.
"""

class BaseJob:
    def __init__(self):
        self.num_procs = 128 # TODO
        self.num_batches = 10 # TODO
    
    def run_multiprocessor(data_path, process_params_path, output_path):
        raise NotImplementedError