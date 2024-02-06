#!/usr/bin/env python
# coding: utf-8

import os

import pandas as pd
import matplotlib.pyplot as plt
plt.rcParams['font.size'] = 14
import glob
from matplotlib.dates import DateFormatter
import datetime as dt

''' Set paths here:
Input: "filedir" is the jsons folder that is created from downloading personal data from Samsung Health app
Output: "outdir" is where the plots are saved
'''
filedir = '/home/davidhersh/Dropbox/Health/Heart_rate/jsons'
outdir = '/home/davidhersh/Dropbox/Health/Heart_rate/plots'

if not os.path.exists(outdir):
    os.mkdir(outdir)

#---------------------------------------------------------------------------------------------------------

# Heart rate data
dfs = []
for file in glob.glob(filedir+'*/com.samsung.shealth.tracker.heart_rate/*/*'):
    df = pd.read_json(file)
    dfs.append(df)
heart_rate = pd.concat(dfs)
heart_rate.sort_values(by='start_time', inplace=True)

# For some reason, the data is ahead 1 hour, so I add an extra hour to the time column
heart_rate['start_time'] = heart_rate['start_time'] + dt.timedelta(hours=1)

heart_rate['day'] = heart_rate['start_time'].dt.strftime('%B %d, %Y')

# Add in exercise to plot
dfs = []
for file in glob.glob(filedir+'*/com.samsung.shealth.exercise/*/*live_data.json'):
    df = pd.read_json(file)
    dfs.append(df)
workouts = pd.concat(dfs)
workouts.sort_values('start_time', inplace=True)
workouts['start_time'] = workouts['start_time'] + dt.timedelta(hours=1)
workouts = workouts[workouts.speed > 0]
workouts['day'] = workouts['start_time'].dt.strftime('%B %d, %Y')

# Manual workouts have sub-minute sampling. To draw vlines that don't overlap, I only want one row per minute
# Auto workouts already have one row per minute
workouts['minute'] = workouts['start_time'].dt.floor('T')
workouts = workouts.groupby('minute').first().reset_index()

for day in heart_rate.day.unique():
    data = heart_rate[heart_rate.day == day]
    workout_data = workouts[workouts.day == day]
    print(f'Creating heart rate plot for {day}')

    fig, ax = plt.subplots(1, 1, figsize=(20, 7))

    ax.plot(data.start_time, data.heart_rate, label='Heart rate')
    ax.fill_between(data.start_time,
                    data.heart_rate_min,
                    data.heart_rate_max,
                    color='gray',
                    alpha=0.5,
                    label='Min/Max')
    ax.set_ylabel('Heart rate (bpm)')
    ax.set_xlabel('Time of day')

    date_format = DateFormatter('%H:%M')

    # Shade along the x-axis for workout data
    full_ymin, full_ymax = plt.gca().get_ylim()
    ax.vlines(workout_data.start_time, full_ymin, full_ymax, color='g', alpha=.3, label='Exercise')

    plt.gca().xaxis.set_major_formatter(date_format)
    plt.title(day)
    plt.legend()
    plt.grid(alpha=.45)
    print(f'Saving plot in {outdir}')
    print('--'*40)
    plt.savefig(os.path.join(outdir, f'{day}_heart_rate.svg'), bbox_inches='tight')


