#!/usr/bin/env python
# coding: utf-8

# # Plotting VLF Live Data 
# 
# - The following code takes the live NAA Birr VLF data and plots it.
# 
# 0. Import necessary libraries
# 1. Read in the most recent NAA csv file from https://vlf.ap.dias.ie/data/birr/live/ as a `pandas` dataframe
# 2. Convert the time data into the necessary format (`datetime` objects) for plotting
# 3. Convert the signal data to <i>dB</i> using $dB = 20 \times log_{10}(signal strength)$
# 4. Use `matplotlib` to plot the data as a timeseries


# all matplotlib imports
import matplotlib.pyplot as plt
from matplotlib import dates
import matplotlib.dates as mdates

# Make sharp, nice plots, mainly for jupyter
#from IPython.display import HTML
#get_ipython().run_line_magic('config', "InlineBackend.figure_format ='retina'")

from datetime import datetime, timedelta
import numpy as np
import pandas as pd

import scipy as sp
from scipy import signal

# Astral is used to get sunrise and sunset times, needs to be installed using pip.
# You can leave this package commented for now, or if you want to install it let me know and I can help!
#from astral.sun import sun
#from astral import LocationInfo


# ## 1. Reading the Data


# The line below uses pandas read csv to read the live csv for the NAA frequency received by the Birr VLF. 
# The read_csv function uses 'skiprows' skips the first 16 rows of the csv which contain header information on the station ID, start time, etc. 
# The argument delimiter=',' is used to know what value is used for separating each part of the data
# The two columns in the csv are manually named with this function.
vlf_naa_data  = pd.read_csv('https://vlf.ap.dias.ie/data/birr/super_sid/2023/06/22/csv/Birr_DHO38_2023-06-22_000000.csv', skiprows=16, delimiter=',', skipinitialspace=True, names=['datetimes', 'NAA'])

# check the first 5 rows of the vlf_naa_data pandas dataframe
vlf_naa_data.head()


# ## 2. Converting the Time Data



# Converting the VLF time data to datetime object
# Create a new list
time_naa = []
# For each time value in the datetimes column of the vlf data, convert it to 
# a datetime object and append it to the new list (time_naa)
for i in vlf_naa_data['datetimes']:
    time_naa.append(datetime.strptime(i, '%Y-%m-%d %H:%M:%S'))


# ## 3. Converting and Cleaning the Signal Data

# Convert the VLF signal to dB and clean data by replacing infinite values with nans (makes for better plotting)
vlf_naa_dB = 20*np.log10(vlf_naa_data['NAA'])
vlf_naa_dB[vlf_naa_dB == -np.inf] = np.nan
vlf_naa_dB[vlf_naa_dB == +np.inf] = np.nan

# Can ignore if it prints a warning about divide by zero, will still run fine.


# ## 4. Plotting the data


# Create a figure
fig = plt.figure(figsize=(12,4))

ax = plt.gca()

# Plot the raw data (looks quite noisy)
ax.plot(time_naa, vlf_naa_dB, color='k', lw=1, ls='-', label='VLF NAA', alpha=1)

# Set the x label to be the current date in the first time object 
ax.set_xlabel(str(time_naa[0].strftime("%d/%m/%Y"))+ ' [UTC]', fontsize=14)
# Set y-value to string below.
ax.set_ylabel('VLF Signal [dB]', fontsize=14)

# Set x-axis limit to be start time with a window of 1 day
ax.set_xlim(time_naa[0], time_naa[0]+timedelta(days=1))
# Set y-axis limit to be 80 dB to the max recorded dB in the data +5 dB
ax.set_ylim(80, int(np.max(vlf_naa_dB)+5))

# Make the x-axis appear in time format (Hours:mins)
date_format = mdates.DateFormatter('%H:%M')
ax.xaxis_date()
ax.xaxis.set_major_formatter(date_format)

ax.tick_params(axis='both', which='major', labelsize=12)
ax.tick_params(bottom=True, top=True, left=True, right=True,direction="in")

# save figure as png
#plt.savefig('vlf_current.png')

# plot a grid
plt.grid(alpha=0.4, ls='dotted')

plt.show()







