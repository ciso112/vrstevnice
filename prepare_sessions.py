import pandas as pd
from numpy import timedelta64 as td
import numpy as np

first_day = pd.Timestamp('26-04-2017')
last_day = pd.Timestamp('2017-06-05')
days = pd.date_range(first_day, last_day)
number_of_days = len(days)

sessions_list = []
columns = ['date', 'session_start', 'session_end', 'session_length']

for day in days:
    date = day.date()
    print('Preparing day', date)

    start = day + td(9, 'h')
    end = day + td(18, 'h')

    points_filename = '%s.%s\max_values_%s-%s.txt' % (day.day, day.month, day.day, day.month)
    points = pd.read_csv(points_filename, header=None, names=['overpoints', 'timestamp'], parse_dates=[1])
    if points.empty:
        continue
    points['time'] = points.timestamp.apply(pd.Timestamp.time)
    points = points[(points.time >= start.time()) & (points.time <= end.time())]
    points['previous_timestamp'] = points.timestamp.shift()
    points['difference'] = (points.timestamp - points.previous_timestamp).fillna(0)
    points['difference_seconds'] = points['difference'].apply(lambda x: x.seconds)

    s_start = points.head(1).time.item()
    p_time = s_start

    for i, row in points.iterrows():
        if row.difference > td(3, 's'):

            sessions_list.append([date, s_start, p_time,
                                  (pd.Timestamp.combine(date, p_time) - pd.Timestamp.combine(date, s_start)).seconds+1])
            s_start = row.time
        p_time = row.time

sessions = pd.DataFrame(data=sessions_list, columns=columns)

sessions.to_csv('sessions_continue.csv', index_label='id')