import common, cost, fetchresults
import logging, sys
import numpy as np
import matplotlib.pyplot as plt
import pickle

logging.basicConfig(level=logging.INFO)
#logging.basicConfig(level=logging.DEBUG)

if 1:
    results = fetchresults.get_last_24hrs()
    pickle.dump(results, open(r'data_tmp\results24', 'wb'))
else:
    results = pickle.load(open(r'data_tmp\results24', 'rb'))

cost_24hrs = np.zeros((4,))

num_max_processes_all = 0
num_max_processes_count = {}
num_user_calls = 0
num_tc_calls = 0
threadtime_min_user = 0.
threadtime_min_tc = 0.
for result in results:
    if 'tc' in result['origin']:
        num_tc_calls += 1
    else:
        num_user_calls += 1
    if not result['duration_ix'] or result['duration_ix'] == 'NA':
            continue
    duration_ix = common.make_int_array(result['duration_ix'])
    duration_ecl2ix = common.make_int_array(result['duration_ecl2ix'])
    num_processes_ix = common.make_int_array(result['num_processes_ix'])
    platform = result['platform']
    num_threads_ix = common.make_int_array(result['num_threads_ix'])   
    thread_seconds = np.sum(duration_ix * num_processes_ix * num_threads_ix + duration_ecl2ix)
    total_seconds = np.sum(duration_ix + duration_ecl2ix)
    num_max_processes = np.max(num_processes_ix)
    if num_max_processes in num_max_processes_count:
        num_max_processes_count[num_max_processes] = num_max_processes_count[num_max_processes] + 1
    else:
        num_max_processes_count[num_max_processes] = 1
    num_max_processes_all = max(num_max_processes, num_max_processes_all)
    cost_24hrs += cost.google_compute(total_seconds, thread_seconds, num_max_processes, platform)
    thread_min = np.ceil(thread_seconds/60.)
    if 'tc' in result['origin']:
        threadtime_min_tc += thread_min
    else:
        threadtime_min_user += thread_min


fig, all_axes = plt.subplots(2, 2, figsize=(12, 8))

axes = all_axes[0, 0]
axes.set_title('Calls')
labels = 'TeamCity', 'Workstation'
numbers = [num_tc_calls, num_user_calls]
explode = (0, 0.1) 
def make_autopct(numbers):
    def absolut_number(pct):
        total = np.sum(numbers)
        val = int(round(pct*total/100.0))
        return '{:d}'.format(val)
    return absolut_number 
axes.pie(numbers, explode=explode, labels=labels, autopct=make_autopct(numbers),
        shadow=True, startangle=45)
axes.axis('equal')

axes = all_axes[0, 1]
axes.set_title('vCPU minutes')
labels = 'TeamCity', 'Workstation'
timings = np.array([threadtime_min_tc, threadtime_min_user])
explode = (0, 0.1) 
axes.pie(timings, explode=explode, labels=labels, autopct=make_autopct(timings),
        shadow=True, startangle=45)
axes.axis('equal')


axes = all_axes[1, 0]
axes.set_title('Dynamic cost estimate')
axes.boxplot(cost_24hrs)
axes.set_ylabel('USD')


axes = all_axes[1, 1]
axes.set_title('vCPU required')
labels = num_max_processes_count.keys()
counts = [num_max_processes_count[count] for count in labels]
axes.pie(counts, labels=labels, shadow=True, startangle=90)#, autopct=make_autopct(counts))
axes.axis('equal')

plt.show()











