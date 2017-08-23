import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import collections
import pickle, time, datetime
plt.style.use('ggplot')
import common, logging

HOST = 'http://slb-2cgbj32.dir.slb.com:8000'
API = '/devdiff/latest'
ENDPOINT = '/results/?page=1'
FNAME_DATA = 'data_tmp/evaldevdiffserv_data'

logging.basicConfig(level=logging.INFO)


LoadedData = collections.namedtuple('LoadedData', 'queried tc user')

if 1: # query api
    first_page = HOST + API + ENDPOINT
    num_max_pages = None
    
    data = LoadedData(time.localtime(time.time()), [], [])

    def for_each_results_page(rdata):
        for result in rdata['results']:
            if 'tc' in result['origin']:
                data.tc.append(result['posted'])
            else:
                data.user.append(result['posted'])            

    common.traverse_linked_pages(first_page, for_each_results_page, num_max_pages=num_max_pages)
    pickle.dump(data, open(FNAME_DATA, 'wb'))

else: # load last saved
    data = pickle.load(open(FNAME_DATA, 'rb'))
    print('\nLoaded data from {:}'.format(time.asctime(data.queried)))

if 1:
    df = pd.DataFrame(pd.to_datetime(pd.Series(data.user)), columns=['posted'])
    title = 'Users'
else:
    df = pd.DataFrame(pd.to_datetime(pd.Series(data.tc)), columns=['posted'])
    title = 'TC'

print('\nDataset start\n', df.tail())
print('\nMost recent\n', df.head())


date_from_incl = datetime.date(year=2017, month=8, day=21) # monday after p4user triggered teamcity tag made it through
#date_from_incl = datetime.date(year=2017, month=8, day=14) # monday after teamcity tag made it through
df = df[df['posted'] >= date_from_incl]

#df.groupby([df['posted'].dt.month, df['posted'].dt.day, df['posted'].dt.hour]).count().plot(kind='bar')
df.groupby([df['posted'].dt.month, df['posted'].dt.day]).count().plot(kind='bar')
plt.title(title)
plt.show()






