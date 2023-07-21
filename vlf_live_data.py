# all matplotlib imports
import matplotlib.pyplot as plt
from matplotlib import dates
import matplotlib.dates as mdates
from mpl_toolkits.axes_grid1 import make_axes_locatable


from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import os
import json
import requests
from tqdm import tqdm
import scipy as sp
from scipy import signal

from sunpy.net import Fido
from sunpy.net import attrs as a
from sunpy.time import parse_time
import netCDF4

# Astral is used to get sunrise and sunset times, may need to be pip installed
from astral.sun import sun
from astral import LocationInfo


#%matplotlib inline
#%config InlineBackend.figure_format ='retina'


# Reading in the last 7 days of GOES x-ray data in json format
def load_goes(date, daterange):
    
    if (datetime.today()-date).days < 7:
        goes_xray = json.loads(requests.get('https://services.swpc.noaa.gov/json/goes/primary/xrays-7-day.json').text)
        
        # Parsing the GOES x-ray data
        goes_timestamps = []
        goes_short = []
        goes_long = []
        
        for i in goes_xray:
            if i['energy'] == '0.05-0.4nm':
                goes_timestamps.append(i['time_tag'])
                goes_short.append(i['observed_flux'])
            if i['energy'] == '0.1-0.8nm':
                goes_long.append(i['observed_flux'])
        
        # Creating datetime objects for GOES timeseries subplot
        goes_times = []
        for i in goes_timestamps:
            goes_times.append(datetime.strptime(i, '%Y-%m-%dT%H:%M:%SZ'))
        
        return(goes_times, goes_short, goes_long)
    
    # need to update the else statement to access older data with the new sunpy 5.0.0 query    
    else:
        tstart = date
        tend = date + timedelta(days=daterange)
        result = Fido.search(a.Time(tstart, tend), a.goes.SatelliteNumber(16), a.Instrument("XRS"))
        file_goes = Fido.fetch(result)
        times_goes = []
        goes_short_test = []
        goes_long_test = []

        for day in file_goes:
            nc = netCDF4.Dataset(day)
            for i in nc['time']:
                t2 = datetime.strptime('01/01/2000 12:00:00', '%d/%m/%Y %H:%M:%S') + timedelta(seconds=i)
                times_goes.append(t2)

            if goes_long_test:
                goes_long_test = goes_long_test + nc['xrsb_flux']
                goes_short_test = goes_short_test + nc['xrsa_flux']
            else:
                goes_long_test = nc['xrsb_flux']
                goes_short_test = nc['xrsa_flux']



        # Returns the GOES times, short and long data
        #return(goes_times, goes_short, goes_long)
        return(times_goes,goes_short_test,goes_long_test)


def load_vlf(rec, tra, dt, daterange):
    print(dt, daterange)
    # This line uses pandas read csv to read the live csv for the NAA frequency received by the Birr VLF. 
    # The read_csv function uses 'skiprows' skips the first 16 rows of the csv which contain header information on the station ID, start time, etc. 
    # The argument delimiter=',' is used to know what value is used for separating each part of the data
    # The two columns in the csv are manually named with this function.
    time_vlf = []
    vlf_sig_dB_total = []
    
    for i in range(0, daterange):
        dt1 = dt + timedelta(days=i)
        print('Checking', dt1)
        vlf_data = []
        for i in range(23):
            try:
                vlffile = 'https://vlf.ap.dias.ie/data/'+rec.lower()+'/super_sid/'+dt1.strftime('%Y/%m/%d')+'/csv/'+rec.title()+'_'+tra.upper()+'_'+dt1.strftime('%Y-%m-%d')+'.csv' #+'_'+str(i).zfill(2)+'0000.
                #print(dt, vlffile)
                
                #vlffile = 'https://vlf.ap.dias.ie/data/birr/super_sid/2023/06/20/csv/Birr_DHO38_2023-06-20_000000.csv'   
                vlf_data  = pd.read_csv(vlffile, skiprows=16, delimiter=',', skipinitialspace=True, names=['datetimes', 'signal'])
                #display(vlf_data.head())
                # Converting the VLF time data to datetime object
                # Create a new list
            except:
                print('No file available for that date.')
                continue
        
        # For each time value in the datetimes column of the vlf data, convert it to 
        # a datetime object and append it to the new list (time_naa)
        for i in vlf_data['datetimes']:
            time_vlf.append(datetime.strptime(i, '%Y-%m-%d %H:%M:%S.%f'))
        
        # Converting the VLF signal to dB and cleaning data by replacing infinite values with nans (makes for better plotting)
        vlf_sig_dB = 20*np.log10(vlf_data['signal'])
        vlf_sig_dB[vlf_sig_dB == -np.inf] = np.nan
        vlf_sig_dB[vlf_sig_dB == +np.inf] = np.nan
        vlf_sig_dB_total.extend(vlf_sig_dB)
            
    # Returns the time and vlf dB data
    return(time_vlf, vlf_sig_dB_total)

def get_sun_info(date):
        
    # Getting sunrise, sunset data etc.
    city = LocationInfo("Dublin", "Ireland", "Europe", 53.3871, -6.3375)
    #print((
    #    f"Information for {city.name}/{city.region}\n"
    #    f"Timezone: {city.timezone}\n"
    #    f"Latitude: {city.latitude:.02f}; Longitude: {city.longitude:.02f}\n"
    #))
    s = sun(city.observer, date= date)
    #print((
    #    f'Dawn:    {s["dawn"]}\n'
    #    f'Sunrise: {s["sunrise"]}\n'
    #    f'Noon:    {s["noon"]}\n'
    #    f'Sunset:  {s["sunset"]}\n'
    #    f'Dusk:    {s["dusk"]}\n'
    #))
    return s


def plot_live_vlf(receiver, transmitter, date, daterange):
    vlf_time, vlf_sig_dB = load_vlf(receiver, transmitter, date, daterange)
    
    goes_times, goes_short, goes_long = load_goes(date, daterange)
    
    
    # Color values to change for vertical lines in the plot
    verticallinecolor = '#740A04'
    
    
    # Print just the header data
    #vlf_naa_header  = pd.read_csv(vlffile, nrows=16, delimiter=',', skipinitialspace=True, names=['header', 'nan'])
    #display(vlf_naa_header)
    
    
    # check the first 5 rows of the vlf_naa_data pandas dataframe
    #vlf_naa_data.head()
    

    
    
    # Getting all flares above C6 class from GOES to overplot
    # Latest flares, has more recent flares than sunpy
    goes_flares = json.loads(requests.get('https://services.swpc.noaa.gov/json/goes/primary/xray-flares-latest.json').text)
    
    filtered_flare_results = []
    # Using sunpy package to query GOES flare list (sometimes doesn't have most recent flare)
    try:
        event_type = "FL"
        tstart = vlf_time[0]
        tend = vlf_time[0]+timedelta(days=daterange)
        print(tstart, tend)
        event_type = "FL"
        result = Fido.search(a.Time(tstart, tend), a.hek.EventType(event_type), a.hek.FL.GOESCls > "C6.0", a.hek.OBS.Observatory == "GOES")
        hek_results = result["hek"]
        filtered_flare_results = hek_results["event_starttime", "event_peaktime", "event_endtime", "fl_goescls", "ar_noaanum"]

    except:
        print('Query failed, site may be temporarily unreachable.')
        filtered_flare_results = []
    
    
    # Plotting
    date_format = mdates.DateFormatter('%H:%M')
    
    fig, ax = plt.subplots(nrows=2, ncols=1, gridspec_kw={'height_ratios': [1,2]},figsize=(12,6), facecolor=('#FBFBFB'), sharex=True)
    
    #plt.rc("font", family='Source Han Sans TW')
    plt.rc("xtick", labelsize="large")
    plt.rc("ytick", labelsize="large")
    
    
    ax[1].set_facecolor('#FBFBFB')
    
    min_signal = 30
    for day in range(daterange):
        s = get_sun_info(date + timedelta(days=day))
        ax[1].axvline(s["dawn"], ls='dotted', lw=1, alpha=0.7, color=verticallinecolor)
        ax[1].axvline(s["noon"], ls='--', lw=1, alpha=0.7, color=verticallinecolor)
        ax[1].axvline(s["sunrise"], ls='--', lw=1, alpha=0.7, color=verticallinecolor)
        ax[1].axvline(s["sunset"], ls='--', lw=1, alpha=0.7, color=verticallinecolor)
        ax[1].axvline(s["dusk"], ls='dotted', lw=1, alpha=0.7, color=verticallinecolor)
            
        text = ax[1].annotate( 'Dawn', xy=(s["dawn"], min_signal+1), xycoords="data", xytext=(-8, 0), textcoords="offset points", ha="center", color=verticallinecolor, size=10, rotation=90)
        text = ax[1].annotate( 'Sunrise', xy=(s["sunrise"], min_signal+1), xycoords="data", xytext=(-8, 0), textcoords="offset points", ha="center", color=verticallinecolor, size=12, rotation=90)
        text = ax[1].annotate( 'Solar Noon', xy=(s["noon"], min_signal+1), xycoords="data", xytext=(-8, 0), textcoords="offset points", ha="center", color=verticallinecolor, size=10, rotation=90)
        text = ax[1].annotate( 'Sunset', xy=(s["sunset"], min_signal+1), xycoords="data", xytext=(-8, 0), textcoords="offset points", ha="center", color=verticallinecolor, size=12, rotation=90)
        text = ax[1].annotate( 'Dusk', xy=(s["dusk"], min_signal+1), xycoords="data", xytext=(-8, 0), textcoords="offset points", ha="center", color=verticallinecolor, size=10, rotation=90)
        
        ax[0].axvline(s["dawn"], ls='dotted', lw=1, alpha=0.7, color=verticallinecolor)
        ax[0].axvline(s["noon"], ls='--', lw=1, alpha=0.7, color=verticallinecolor)
        ax[0].axvline(s["sunrise"], ls='--', lw=1, alpha=0.7, color=verticallinecolor)
        ax[0].axvline(s["sunset"], ls='--', lw=1, alpha=0.7, color=verticallinecolor)
        ax[0].axvline(s["dusk"], ls='dotted', lw=1, alpha=0.7, color=verticallinecolor)
    
    
    # Plotting flares
    for flare in filtered_flare_results:
        the_flare_datetime = datetime.strptime(str(flare['event_starttime']), '%Y-%m-%d %H:%M:%S.%f')
        ax[0].axvline(the_flare_datetime, ls='-', lw=3, alpha=0.1, color='gray')
        ax[1].axvline(the_flare_datetime, ls='-', lw=3, alpha=0.1, color='gray')
        text = ax[0].annotate(
        flare['fl_goescls'],
        xy=(datetime.strptime(str(flare['event_starttime']), '%Y-%m-%d %H:%M:%S.%f'), 2e-4),
        xycoords="data",
        xytext=(-3, 0),
        textcoords="offset points",
        ha="center",
        color='gray',
        size=8,
        rotation=90
    )
    for flare in goes_flares:
        the_flare_datetime = datetime.strptime(str(flare['begin_time']), '%Y-%m-%dT%H:%M:%SZ')
        ax[0].axvline(the_flare_datetime, ls='-', lw=3, alpha=0.1, color='gray')
        ax[1].axvline(the_flare_datetime, ls='-', lw=3, alpha=0.1, color='gray')
    
    ax[1].plot(vlf_time, vlf_sig_dB, color='#494949', lw=1, ls='-', label='VLF (Raw Data)', alpha=0.3)
    
    vlf_dB_savgol = signal.savgol_filter(vlf_sig_dB, window_length=601, polyorder=3, mode="nearest")
    ax[1].plot(vlf_time, vlf_dB_savgol, '-k' , lw=2, label='VLF Running Mean')
    
    
    ax[1].set_xlabel(str(vlf_time[0].strftime("%d/%m/%Y"))+ ' [UTC]',fontsize=14)
    ax[1].set_ylabel('VLF Signal [dB]', fontsize=14)
    
    ax[1].set_yticks([85, 90, 95, 100, 105, 110, 115])
    
    
    ax[1].set_xlim(vlf_time[0], vlf_time[0]+timedelta(days=daterange))
    ax[1].set_ylim(min_signal, np.nanmax(vlf_sig_dB)+3)
    
    

    #ax[0,1].xaxis_date()
    ax[1].xaxis.set_major_formatter(date_format)
    ax[1].xaxis.set_major_locator(mdates.HourLocator(interval=3)) # to get a tick every 2 hours
    
    ax[1].tick_params(axis='both', which='major', labelsize=14)
    
    
    #adjust_spines(ax, ['left', 'bottom'])
    for loc, spine in ax[1].spines.items():
        if loc in ['left', 'bottom']:
            spine.set_position(('outward', 10))  # outward by 10 points
            #spine.set_smart_bounds(True)
        else:
            spine.set_color('none')
    
    
    ax[0].set_facecolor('#FBFBFB')
    ax[0].plot(goes_times, goes_short, color='#1D4890', lw=2, ls='-', label='GOES 0.05 - 0.4 nm', alpha=1)
    
    ax[0].plot(goes_times, goes_long, color='#D9761A', lw=2, ls='-', label='GOES 0.1 - 0.8 nm', alpha=1)


    ax[0].set_xlim(vlf_time[0], vlf_time[0]+timedelta(days=daterange))
    ax[0].set_ylabel('GOES [W$^{-2}$]', fontsize=14)
    
    
    for loc, spine in ax[0].spines.items():
        if loc in ['left']:
            spine.set_position(('outward', 10))  # outward by 10 points
            #spine.set_smart_bounds(True)
        else:
            spine.set_color('none')
    
    ax[0].xaxis_date()
    ax[0].xaxis.set_major_formatter(date_format)
    ax[0].xaxis.set_major_locator(mdates.HourLocator(interval=3)) # to get a tick every 2 hours
    
    ax[0].tick_params(axis='y', which='major', labelsize=14)
    ax[0].tick_params('x', labelbottom=False)
    ax[0].set_yscale('log')
    ax[0].tick_params('x',length=0)
    ax[0].set_yticks([1e-8, 1e-7, 1e-6, 1e-5, 1e-4, 1e-3])
    
    ax[0].set_ylim(1e-8, 1e-3)
    
    ax2 = ax[0].twinx()
    mn, mx = ax[0].get_ylim()
    ax2.set_ylim(mn, mx)
    ax2.set_yscale('log')
    ax2.set_ylabel('Flare Class', fontsize=14)
    ax2.set_yticks([1e-8, 1e-7, 1e-6, 1e-5, 1e-4])
    ax2.set_yticklabels(['A','B','C','M','X'])
    ax2.tick_params(axis='both', which='both', labelsize=14)
    #ax2.set_xticks([])
    for loc, spine in ax2.spines.items():
        if loc in ['right']:
            spine.set_position(('outward', 10))  # outward by 10 points
            #spine.set_smart_bounds(True)
        else:
            spine.set_color('none')
            
    
    #plt.subplots_adjust(bottom=0.15, left=0.2)
    
    #plt.savefig('vlf_current.png')# , dpi=1200)
    
    ax[1].grid(alpha=0.3, ls='dotted')
    ax[0].grid(alpha=0.3, ls='dotted')
    
    
    ax[1].legend(loc='upper center', bbox_to_anchor=(0.76, 1.65), ncol=2, facecolor='gray', fontsize=12, frameon=False)
    ax[0].legend(loc='upper center', bbox_to_anchor=(0.24, 1.25), ncol=2, facecolor='gray', fontsize=12, frameon=False)
    
    plt.subplots_adjust(hspace=0.03)
    
    #plt.title('SuperSid Birr, Ireland - NAA (Maine, USA 24 kHz)', fontsize=16, pad=40, color='#252525')
    plt.title('SuperSid '+receiver.title()+', Ireland - '+transmitter.upper(), fontsize=16, pad=40, color='#252525')
    plt.savefig('birr_dho_vlf_live.png', dpi=300)
    #plt.show()
    return fig



# plot_live_vlf('receiver', 'transmitter', datetime object, day range)
dt = datetime.today()-timedelta(days=2)

#birr or dunsink
# naa, dho38, hwu1, hwu2, nrk
test = plot_live_vlf('dunsink', 'dho38', dt, 1)
