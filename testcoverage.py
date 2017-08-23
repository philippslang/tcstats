import common, cost, fetchresults
import logging, sys
import numpy as np
import pickle
import pandas as pd
import matplotlib.pyplot as plt
from adjustText import adjust_text

logging.basicConfig(level=logging.INFO)
#logging.basicConfig(level=logging.DEBUG)

if 1:
    results = fetchresults.get_all_with_status()
    pickle.dump(results, open(r'data_tmp\resultsstatus', 'wb'))
else:
    results = pickle.load(open(r'data_tmp\resultsstatus', 'rb'))


failures = {}
vcpu_seconds = {}
for result in results:
    status = common.make_int_array(result['status'])
    duration_ix = common.make_int_array(result['duration_ix'])
    duration_ecl2ix = common.make_int_array(result['duration_ecl2ix'])
    num_processes_ix = common.make_int_array(result['num_processes_ix'])
    num_threads_ix = common.make_int_array(result['num_threads_ix'])
    vcpu_seconds_tests = num_threads_ix*num_processes_ix*duration_ix + duration_ecl2ix
    tests = result['tests'].split(',')
    cl = int(result['cl'])
    for i, test in enumerate(tests):
        if status[i] > 0: # TODO outsource to failed method, or better, make test type
            if test in failures:
                failures[test] += [cl]
                vcpu_seconds[test] += [vcpu_seconds_tests[i]]
            else:
                failures[test] = [cl]
                vcpu_seconds[test] = [vcpu_seconds_tests[i]]

coverage = []           
vcpusecs = []           
name = []           
for test in vcpu_seconds:
    name += [test]
    coverage += [len(failures[test])]
    vcpusecs += [max(1, np.mean(vcpu_seconds[test]))]

efficiency = np.array(coverage) / np.array(vcpusecs)
summary = {'test': name, 'coverage': coverage, 'vCPU seconds': vcpusecs, 'efficiency': efficiency}
summary = pd.DataFrame(summary)
summary = summary.sort_values('efficiency', ascending=False)
print(summary)


fig, axes = plt.subplots(figsize=(8, 8))
x = summary['vCPU seconds']
y = summary['coverage']
axes.scatter(x, y, s=summary['efficiency']*750, alpha=0.5, c=np.random.rand(len(x)))
axes.set_xlabel('vCPU seconds')
axes.set_ylabel('Coverage')
ts = []
for i, test in enumerate(summary['test']):
    ts.append(plt.text(x[i], y[i], test))
adjust_text(ts, x=x, y=y, force_points=0.1, arrowprops=dict(arrowstyle='->', 
  color='red'))
plt.show()













