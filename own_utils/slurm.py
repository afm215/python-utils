import time
from .bash_command import run
import numpy as np
import os
def get_slurm_file_name():
  return run("scontrol show job $SLURM_JOB_ID | grep Command | cut -d'=' -f2",  False, True, True).strip()
def slurm_get_time_left():
    time_left = run("squeue -j $SLURM_JOB_ID -h --Format TimeLeft", False, True, True).strip()
    if "-" in time_left:
        days, rest = time_left.split("-")
        days = int(days)
    else:
        days = 0
        rest = time_left
    rest_splited = rest.split(":") 
    hours = 0
    minutes = 0
    if len(rest_splited) ==3:
        hours = int(rest_splited[-3])
    if len(rest) >=2:
        minutes = int(rest_splited[-2])
    seconds = int(rest_splited[-1])
    time_left_sec = (hours + days * 24) * 3600 + 60 * minutes + seconds
    return time_left_sec
class TimeLeftWatcher:
    def __init__(self, logging = True):
        self.time_left = slurm_get_time_left()
        self.begin = time.perf_counter()
        self.recored_cycle_times= []
        self.logging = logging
    def _get_time_left(self):
        timestamp = time.perf_counter()
        ellapsed_time = timestamp - self.begin
        return self.time_left - ellapsed_time
    
    def relauch_job_or_continue(self, cycle_time, additional_log_path=None, offset = 300, limit_mem=None):
        
        self.recored_cycle_times.append(cycle_time)
        if limit_mem is not None and len( self.recored_cycle_times) > limit_mem:
            self.recored_cycle_times = self.recored_cycle_times[-limit_mem:]
        time_left = self._get_time_left()
        if self.logging:
            print("time left ", time_left, " last iteration duraction ", cycle_time, " mean iteration time", np.mean(self.recored_cycle_times), "standard deviation", np.std(self.recored_cycle_times), flush=True)
        if np.mean(self.recored_cycle_times) + np.std(self.recored_cycle_times) + offset >= time_left:
            print(" Not enough time leftn resubmitting", flush=True)
            

            resubmit_file = os.path.join(os.getcwd(), os.environ["SLURM_JOB_ID"]+ "_resubmit") #get_slurm_file_name() + "_resubmit"
            print("sasving file in ", resubmit_file, flush=True)
            with open(resubmit_file, "w"):
                pass
            if additional_log_path:
                with open(additional_log_path, "w"):
                    pass

            raise Exception("Not enough time shutdown job")




