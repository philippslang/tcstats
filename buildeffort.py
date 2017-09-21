import sys, logging
import common
import datetime
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
matplotlib.style.use('ggplot')

#logging.basicConfig(level=logging.DEBUG)
#logging.basicConfig(level=logging.INFO)

TC_TIME_FORMAT = '%Y%m%dT%H%M%S+0100'

min_date = datetime.datetime.now() - datetime.timedelta(hours=24)
builds = {}
nmax_build_pages = 1

frames = []
rdata = common.get_tc('/projects/id:IntersectMain_RollingBuilds_Builds')
for build_type in rdata['buildTypes']['buildType']:
    build_data = common.get_tc(build_type['href'])
    build_name = build_type['id']
    ibuild_name_begin = build_name.rfind('Rolling')+7
    bname = build_name[ibuild_name_begin:]
    builds[bname] = []
    tmp_start = []
    tmp_duration = []
    def for_each_build_page(page_data):
        for build in page_data['build']:
            data = common.get_tc(build['href'])
            start = datetime.datetime.strptime(data['startDate'], TC_TIME_FORMAT)
            if start < min_date:
                break
            end = datetime.datetime.strptime(data['finishDate'], TC_TIME_FORMAT)
            duration_seconds = int((end-start).total_seconds())
            print('  {0}: {1}-{2} = {3:d}s'.format(data['number'], str(start), str(end), duration_seconds))
            builds[bname].append((start, duration_seconds))
            tmp_start.append(start)
            tmp_duration.append(duration_seconds)

    common.traverse_linked_pages_tc(build_data['builds']['href'], for_each_build_page, 
      num_max_pages=nmax_build_pages)
    
    date = pd.to_datetime(pd.Series(tmp_start))
    series = pd.Series(tmp_duration, index=date)
    frame = pd.DataFrame({bname:series.groupby(series.index.hour).sum()})
    index = [i for i in range(24)]
    frame = frame.reindex(index, fill_value=0)
    frames.append(frame)

frame = pd.concat(frames, axis=1)
ax = frame.plot.bar(stacked='bar')
ax.set_ylabel('Duration')
ax.set_xlabel('Time')
plt.show()