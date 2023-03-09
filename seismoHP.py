from obspy import UTCDateTime
from obspy.clients.seedlink import Client
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import butter, lfilter
from scipy.io import wavfile
from playsound import playsound

# Set up the Seedlink client
client = Client("geofon.gfz-potsdam.de", 18000)

# Set the start and end times for the plot
endtime = UTCDateTime.now()  # now
starttime = endtime - 60  # 60 seconds ago

# Set the size of the buffer (in seconds)
buffer_size = 10

# Set the filter parameters
nyquist_freq = 0.5 * 100.0  # half of the sampling frequency
cutoff_freq = 1.0  # in Hz
filter_order = 5

# Create the filter coefficients
b, a = butter(filter_order, cutoff_freq/nyquist_freq, btype='highpass')

# Initialize an empty buffer
buffer = []

# Create an empty plot to use for updating
fig, ax = plt.subplots()
line, = ax.plot([], color='black')

# Continuously update the plot with new data
while True:
    # If the buffer is empty or the endtime is greater than the last buffered time, get new data
    if len(buffer) == 0 or endtime > buffer[-1].stats.endtime:
        # Get the waveform data
        st = client.get_waveforms("RO", "MLR", "", "HHZ", starttime, endtime)

        # Filter the waveform data
        st_filt = st.copy()
        for tr in st_filt:
            tr.data = lfilter(b, a, tr.data)

        # Append the new data to the buffer
        buffer.append(st_filt[0])
        
        # If the buffer has grown larger than the buffer size, remove the oldest data
        if len(buffer) > buffer_size:
            buffer.pop(0)

    # Combine the data from the buffer into a single trace
    trace = buffer[0]
    for i in range(1, len(buffer)):
        trace += buffer[i]

    # Update the plot with the new data
    line.set_data(trace.times(), trace.data)
    ax.relim()
    ax.autoscale_view()
    #set the signal amp
    ax.set_ylim(-20, 20)


    # Check if the maximum amplitude of the trace exceeds 6000 units
    if np.max(np.abs(trace.data)) > 6000:
        # Play the sound file
        playsound('alert.wav')

    # Pause for a short time before getting new data
    plt.pause(0.1)

    # Update the start and end times for the next iteration
    endtime = UTCDateTime.now()
    starttime = endtime - 60  # 60 seconds ago

