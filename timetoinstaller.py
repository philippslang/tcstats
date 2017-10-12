import sys, logging
import common
import datetime
import pandas as pd
import collections
import bisect
import matplotlib
import matplotlib.pyplot as plt
matplotlib.style.use('ggplot')

#logging.basicConfig(level=logging.DEBUG)
#logging.basicConfig(level=logging.INFO)

TC_TIME_FORMAT = '%Y%m%dT%H%M%S+0100'

min_date = datetime.datetime.now() - datetime.timedelta(days=62)
min_date_submitted = datetime.datetime.now() - datetime.timedelta(days=58)

published = {}
rdata = common.get_tc('/app/rest/latest/buildTypes/id:IntersectMain_P7d11PublishTestedDvdWorkInProgress/builds/')
def for_each_build_page(page_data):
    for build in page_data['build']:
        data = common.get_tc(build['href'])
        start = datetime.datetime.strptime(data['startDate'], TC_TIME_FORMAT)
        if start < min_date:
            return False
        print('{0}: {1}'.format(data['number'], str(start)))
        published[int(data['number'])] = start
    return True

common.traverse_linked_pages_tc(rdata['href'], for_each_build_page)


submitted = {}
with open('cl.txt', 'r') as file:
    for line in file: 
        tokens = line.split()
        cl = int(tokens[1])
        datestamp = 'T'.join(tokens[3:5])
        date = datetime.datetime.strptime(datestamp, r'%Y/%m/%dT%H:%M:%S')
        if date > min_date_submitted:
            submitted[cl] = date

time_to_publish = []
for cl_submitted in submitted:
    cl_published_closest = 0
    cl_diff_closest = 100000
    for cl_published in published:
        cl_diff = cl_published - cl_submitted
        if cl_diff >= 0:
            if cl_diff_closest > cl_diff:
                cl_diff_closest = cl_diff
                cl_published_closest = cl_published
    #print(cl_submitted, cl_published_closest)    
    try:
        date_published = published[cl_published_closest]
        time_to_publish += [(date_published - submitted[cl_submitted]).total_seconds()/60**2]
    except:
        pass



d = {'time to publish': time_to_publish}
df = pd.DataFrame(data=d)
df['time to publish'].plot.hist(alpha=0.5, bins=60, xlim=(0,40))
print('mean', df['time to publish'].mean())
#print('50 quantile', df['time to publish'].quantile(0.5))
#print('75 quantile', df['time to publish'].quantile(0.75))
plt.xlabel('Hours')
plt.savefig('data_tmp/timetopublish.png', dpi=600)
plt.show()