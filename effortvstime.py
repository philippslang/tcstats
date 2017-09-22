import common, cost, fetchresults
import logging, sys, datetime
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
matplotlib.style.use('ggplot')
import pickle

logging.basicConfig(level=logging.INFO)
#logging.basicConfig(level=logging.DEBUG)

if 0:
    results = fetchresults.get_all_with_status()
    pickle.dump(results, open(r'data_tmp\effortvstime', 'wb'))
else:
    results = pickle.load(open(r'data_tmp\effortvstime', 'rb'))


date_all = []
compute_hours_all = []

for result in results:
    duration_ix = common.make_int_array(result['duration_ix'])
    duration_ecl2ix = common.make_int_array(result['duration_ecl2ix'])
    nprocesses_ix = common.make_int_array(result['num_processes_ix'])
    nprocesses_ix[nprocesses_ix == 0] = 1 # hack for now, this has been checked
    nthreads_ix = common.make_int_array(result['num_threads_ix']) 
    nvcpu_ix = nthreads_ix * nprocesses_ix
    compute_seconds = np.sum(duration_ix * nvcpu_ix + duration_ecl2ix)
    compute_hours = compute_seconds/60**2
    date_all += [result['posted']]
    compute_hours_all += [compute_hours]

date = pd.to_datetime(pd.Series(date_all))
compute_hours = pd.DataFrame(compute_hours_all, index=date)
date_from_incl = datetime.datetime(2017, 8, 28, 0, 0) #
date_mask = (compute_hours.index >= date_from_incl)
dates = compute_hours.index[date_mask]
compute_hours = compute_hours.ix[dates]

if 0:
    date_to_incl = datetime.datetime(2017, 9, 11, 0, 0) 
    date_mask = (compute_hours.index <= date_to_incl)
    dates = compute_hours.index[date_mask]
    compute_hours = compute_hours.ix[dates]

compute_hours_per_day = compute_hours.groupby(lambda x: x.date()).aggregate(lambda x: sum(x))
print(compute_hours_per_day)
ax = compute_hours_per_day.plot(kind='bar', alpha=0.5)
ax.set_ylabel('Compute Hours')
ax.legend_.remove()
plt.savefig('data_tmp/testeffort.png', dpi=600)
plt.show()








