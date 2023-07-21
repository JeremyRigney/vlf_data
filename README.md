# vlf_data
Accessing and plotting VLF data from Irish receivers

The <code>vlf_get_data.py</code> file accesses _.csv_ files from the <a href='vlf.ap.dias.ie'>vlf.ap.dias.ie</a> archive for Irish VLF receivers  (Birr and Dunsink), converts the signals to dB and plots the 24 hour data.

A sample plot from running this script looks like the following:

![image](https://github.com/JeremyRigney/vlf_data/assets/11720251/561ab3be-d082-41a4-8ccd-ccd800347b8f)

***

The <code>vlf_live_data.py</code> file contains a function to get vlf data from a selected station over a given date range. The relevant csv files are then downloaded from <a href='vlf.ap.dias.ie'>vlf.ap.dias.ie</a> and plotted along with the GOES x-ray data from the same date range. Sunrise, sunset and solar noon times are included in the plot. A Savitsky-Golay filter is applied to the VLF data to smooth noise, but the script does not check for bad data. the <code>y_min</code> axis limit must still be applied manually. Functionality for including flare times during the specified date range will be implemented fully at a later date. An example plot from this script looks like this:

![image](https://github.com/JeremyRigney/vlf_data/assets/11720251/117ab95f-c5ef-44f9-81fe-30f75f585cdb)
