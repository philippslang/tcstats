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

num_max_vCPU_ix_all = 0
num_max_vCPU_ix_count = {}
num_user_calls = 0
num_tc_calls = 0
vCPU_min_user = 0.
vCPU_min_tc = 0.
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
    num_processes_ix[num_processes_ix == 0] = 1 # hack for now, this has been checked
    platform = result['platform']
    num_threads_ix = common.make_int_array(result['num_threads_ix']) 
    num_vCPU_ix = num_threads_ix * num_processes_ix
    thread_seconds = np.sum(duration_ix * num_vCPU_ix + duration_ecl2ix)
    total_seconds = np.sum(duration_ix + duration_ecl2ix)
    num_max_vCPU_ix = np.max(num_vCPU_ix)
    if num_max_vCPU_ix in num_max_vCPU_ix_count:
        num_max_vCPU_ix_count[num_max_vCPU_ix] = num_max_vCPU_ix_count[num_max_vCPU_ix] + 1
    else:
        num_max_vCPU_ix_count[num_max_vCPU_ix] = 1
    num_max_vCPU_ix_all = max(num_max_vCPU_ix, num_max_vCPU_ix_all)
    # TODO group CL, platform
    cost_24hrs += cost.google_compute(total_seconds, thread_seconds, num_max_vCPU_ix, platform)
    thread_min = np.ceil(thread_seconds/60)
    if 'tc' in result['origin']:
        vCPU_min_tc += thread_min
    else:
        vCPU_min_user += thread_min


fig, all_axes = plt.subplots(2, 2, figsize=(12, 8))

axes = all_axes[0, 0]
numbers = np.array([num_tc_calls, num_user_calls], dtype=np.int16)
axes.set_title('{:d} posts'.format(numbers.sum()))
labels = 'TeamCity', 'Workstation'
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
timings = np.array([vCPU_min_tc, vCPU_min_user], dtype=np.int32)
axes.set_title('{:d} vCPU minutes'.format(timings.sum()))
labels = 'TeamCity', 'Workstation'
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
labels = [vCPU for vCPU in num_max_vCPU_ix_count.keys()]
#labels = num_max_vCPU_ix_count.keys()
counts = [num_max_vCPU_ix_count[count] for count in labels]
axes.bar(labels, counts)
axes.set_xlabel('vCPU')
axes.set_ylabel('# tests')
axes.text(0.5, 0.5, '({0:d},{1:d})'.format(np.min(labels), np.max(labels)),horizontalalignment='center',
 verticalalignment='center', transform=axes.transAxes)
#axes.pie(counts, labels=labels, shadow=True, startangle=45)#, autopct=make_autopct(counts))
#axes.axis('equal')

plt.show()











