import common, fetchresults
import logging, sys
import numpy as np
import pickle
import pandas as pd
import matplotlib.pyplot as plt
from adjustText import adjust_text

logging.basicConfig(level=logging.INFO)
#logging.basicConfig(level=logging.DEBUG)

if 0:
    results = fetchresults.get_all_with_status()
    pickle.dump(results, open(r'data_tmp\resultsstatus', 'wb'))
else:
    results = pickle.load(open(r'data_tmp\resultsstatus', 'rb'))


failures = {}
changelists = set()
vcpu_seconds = {}
for result in results:
    status = common.make_int_array(result['status'])
    duration_ix = common.make_int_array(result['duration_ix'])
    duration_ecl2ix = common.make_int_array(result['duration_ecl2ix'])
    num_processes_ix = common.make_int_array(result['num_processes_ix'])
    num_threads_ix = common.make_int_array(result['num_threads_ix'])
    vcpu_seconds_tests = num_threads_ix*num_processes_ix*duration_ix + duration_ecl2ix
    tests = result['tests'].split(',')
    try:
        cl = int(result['cl'])
    except:
        cl = 0
    if cl is not 0:
        for i, test in enumerate(tests):
            if status[i] > 0: # TODO outsource to failed method, or better, make test type
                changelists.add(cl)
                if test in failures:
                    failures[test] += [cl]
                    vcpu_seconds[test] += [vcpu_seconds_tests[i]]
                else:
                    failures[test] = [cl]
                    vcpu_seconds[test] = [vcpu_seconds_tests[i]]

changelists = list(changelists)
test_fauilures = {}
for test in failures:
    failed_cls = [0]*len(changelists)
    for failed_cl in failures[test]:
        failed_cls[changelists.index(failed_cl)] = 1
    test_fauilures[test] = failed_cls
test_coverage = pd.DataFrame(test_fauilures, index=changelists)

test_coverage.to_csv('data_tmp/test_coverage.csv')
sys.exit()
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
y = summary['coverage'] / np.max(summary['coverage'])
axes.scatter(x, y, s=summary['efficiency']*750, alpha=0.5, c=np.random.rand(len(x)))
axes.set_xlabel('vCPU seconds')
axes.set_ylabel('Coverage')
axes.set_xlim(0, 1000)
if 0:
    ts = []
    for i, test in enumerate(summary['test']):
        ts.append(plt.text(x[i], y[i], test))
    adjust_text(ts, x=x, y=y, force_points=0.1, arrowprops=dict(arrowstyle='->', 
    color='red'))
plt.show()













