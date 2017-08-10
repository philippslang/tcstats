import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
plt.style.use('ggplot')
import common

HOST = 'http://slb-2cgbj32.dir.slb.com:8000'
API = '/devdiff/latest'
ENDPOINT = '/results/?page=1'


posted_tc = []
posted_user = []

def for_each_results_page(rdata):
    for result in rdata['results']:
        if 'tc' in result['origin']:
            posted_tc.append(result['posted'])
        else:
            posted_user.append(result['posted'])            
    
 
first_page = HOST + API + ENDPOINT
num_max_pages = None

common.traverse_linked_pages(first_page, for_each_results_page, verbose=1, num_max_pages=num_max_pages)

df = pd.DataFrame(pd.to_datetime(pd.Series(posted_tc)), columns=['posted'])
print(df.head())
print(df.tail())

df.groupby([df['posted'].dt.month, df['posted'].dt.day, df['posted'].dt.hour]).count().plot(kind='bar')
plt.show()






