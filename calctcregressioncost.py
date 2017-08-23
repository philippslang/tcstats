import common, cost, fetchresults
import logging, csv, math, sys
import numpy as np


logging.basicConfig(level=logging.INFO)
#logging.basicConfig(level=logging.DEBUG)


results = fetchresults.get_last_24hrs()
cost_24hrs = np.zeros((4,))
num_max_processes_all = 0
for result in results:
    if not result['duration_ix'] or result['duration_ix'] == 'NA':
            continue
    duration_ix = common.make_int_array(result['duration_ix'])
    duration_ecl2ix = common.make_int_array(result['duration_ecl2ix'])
    num_processes_ix = common.make_int_array(result['num_processes_ix'])
    process_seconds = np.sum(duration_ix * num_processes_ix + duration_ecl2ix)
    total_seconds = np.sum(duration_ix + duration_ecl2ix)
    num_max_processes = np.max(num_processes_ix)
    num_max_processes_all = max(num_max_processes, num_max_processes_all)
    cost_24hrs += cost.google_compute(total_seconds, process_seconds, num_max_processes)

print(cost_24hrs)
print(num_max_processes_all)
sys.exit()










