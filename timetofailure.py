import common, fetchresults
import logging, sys
import datetime
import numpy as np
import pickle
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
matplotlib.style.use('ggplot')

logging.basicConfig(level=logging.INFO)
#logging.basicConfig(level=logging.DEBUG)

if 0:
    results = fetchresults.get_all_with_status()
    pickle.dump(results, open(r'data_tmp\latestall', 'wb'))
else:
    results = pickle.load(open(r'data_tmp\latestall', 'rb'))


submitted = {}
with open('cl.txt', 'r') as file:
    for line in file: 
        tokens = line.split()
        cl = int(tokens[1])
        datestamp = 'T'.join(tokens[3:5])
        date = datetime.datetime.strptime(datestamp, common.P4_TIME_FORMAT)
        submitted[cl] = date


failure = {}
min_date = datetime.datetime.now()
for result in results:
    statii = common.make_int_array(result['status'])
    if any(status is not 0 for status in statii):
        try:
            cl = int(result['cl'])
        except:
            cl = 0
        if cl is not 0:
            if any(nogo in result['tests'] for nogo in ['TENGIZ-STC', 'GORGON', 'Gullfaks-HM']):
                continue
            # TODO instead of posted time, which is the end of all tests in that suite, we should
            # use posted - suite_duration/2
            date = datetime.datetime.strptime(result['posted'], "%Y-%m-%dT%H:%M:%S.%fZ")
            if date < min_date:
                min_date = date
            if cl not in failure:
                failure[cl] = date
            else:
                if failure[cl] < date:
                    failure[cl] = date
    
changelists = []
time_to_failure = []
for cl in failure:
    if cl in submitted:
        changelists += [cl]
        time_to_failure += [(failure[cl] - submitted[cl]).total_seconds()/60**2]

d = {'cl': changelists, 'time to failure': time_to_failure}
df = pd.DataFrame(data=d)
df['time to failure'].plot.hist(alpha=0.5, bins=160, xlim=(0,50))
print('mean', df['time to failure'].mean())
print('median', df['time to failure'].median())
print('50 quantile', df['time to failure'].quantile(0.5))
print('75 quantile', df['time to failure'].quantile(0.75))
plt.xlabel('Hours')
plt.savefig('data_tmp/timetofailure.png', dpi=600)
plt.show()