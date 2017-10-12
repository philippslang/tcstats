import common
import logging, sys
import datetime
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
matplotlib.style.use('ggplot')

logging.basicConfig(level=logging.INFO)
#logging.basicConfig(level=logging.DEBUG)



change_lists, submitted = [], []
with open('cl.txt', 'r') as file:
    for line in file: 
        tokens = line.split()
        cl = int(tokens[1])
        datestamp = 'T'.join(tokens[3:5])
        date = datetime.datetime.strptime(datestamp, common.P4_TIME_FORMAT)
        submitted += [date]
        change_lists += [cl]

submitted = pd.to_datetime(pd.Series(submitted))
change_lists = pd.DataFrame(change_lists, index=submitted)
change_lists_per_day = change_lists.groupby(change_lists.index.date).count()
print(change_lists_per_day.mean())
ax = change_lists_per_day.plot(kind='bar', alpha=0.5)
ax.set_ylabel('CLs')
ax.legend_.remove()
#plt.savefig('data_tmp/clperday.png', dpi=600)
plt.show()