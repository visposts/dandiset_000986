import sys
import pynwb
import h5py
import remfile
import numpy as np
import figpack.views as fp
import figpack_spike_sorting.views as fpss
from figpack.utils import read_script
from dandi.dandiapi import DandiAPIClient

asset_path = None
if len(sys.argv) > 1:
    asset_path = sys.argv[1]

output_file = None
if len(sys.argv) > 2:
    output_file = sys.argv[2]

if asset_path is None:
    raise ValueError(
        "Please provide the asset path as the first argument. For example: sub-LA11/sub-LA11_ses-2_behavior.nwb"
    )

if output_file is not None:
    print(f"Output file specified: {output_file}")

# Initialize Dandi client and load NWB file
print("Connecting to DANDI API...")
client = DandiAPIClient()
dandiset = client.get_dandiset("000986", "draft")
nwb_file_url = dandiset.get_asset_by_path(asset_path).download_url

print("Loading NWB file...")
# Open the remote file with disk cache
disk_cache = remfile.DiskCache("./cache")
remote_file = remfile.File(nwb_file_url, disk_cache=disk_cache)
h5_file = h5py.File(remote_file)
nwb_io = pynwb.NWBHDF5IO(file=h5_file)
nwb = nwb_io.read()
print("NWB file loaded successfully")

# Extract pupil diameter data
print("\nExtracting pupil diameter data...")
pupil = (
    nwb.processing["behavior"]
    .data_interfaces["PupilTracking"]
    .time_series["pupil_diameter"]
)
pupil_data = pupil.data[:]
pupil_timestamps = pupil.timestamps[:]
print(f"Pupil data: {len(pupil_data)} samples")

# Create pupil diameter time series graph
print("Creating pupil diameter graph...")
pupil_graph = fp.TimeseriesGraph(hide_nav_toolbar=True)
pupil_graph.add_uniform_series(
    name="pupil",
    start_time_sec=pupil_timestamps[0],
    sampling_frequency_hz=1 / (pupil_timestamps[1] - pupil_timestamps[0]),
    data=pupil_data,
    timestamps_for_inserting_nans=pupil_timestamps,
)


# Extract running speed data
print("\nExtracting running speed data...")
running_speed = nwb.processing["behavior"].data_interfaces["running_speed"]
running_speed_data = running_speed.data[:]
running_speed_timestamps = running_speed.timestamps[:]
print(f"Running speed data: {len(running_speed_data)} samples")

# Create running speed time series graph
print("Creating running speed graph...")
running_speed_graph = fp.TimeseriesGraph(hide_nav_toolbar=True)
running_speed_graph.add_uniform_series(
    name="running_speed",
    start_time_sec=running_speed_timestamps[0],
    sampling_frequency_hz=1
    / (running_speed_timestamps[1] - running_speed_timestamps[0]),
    data=running_speed_data,
    timestamps_for_inserting_nans=running_speed_timestamps,
)


# Extract interval data
print("\nExtracting interval data...")
spontaneous_blocks = nwb.intervals["spontaneous_blocks"]
spontaneous_start = spontaneous_blocks["start_time"][:]
spontaneous_stop = spontaneous_blocks["stop_time"][:]
print(f"Spontaneous blocks: {len(spontaneous_start)} intervals")

trials = nwb.intervals["trials"]
trials_start = trials["start_time"][:]
trials_stop = trials["stop_time"][:]
print(f"Trials: {len(trials_start)} intervals")

# Create trials interval graph
print("Creating trials interval graph...")
trials_graph = fp.TimeseriesGraph(hide_nav_toolbar=True)
trials_graph.add_interval_series(
    name="trials",
    t_start=trials_start,
    t_end=trials_stop,
    color="lightblue",
    # alpha=0.5
)

# Create spontaneous blocks interval graph
print("Creating spontaneous blocks interval graph...")
spontaneous_graph = fp.TimeseriesGraph(hide_nav_toolbar=True)
print(spontaneous_start)
print(spontaneous_stop)
spontaneous_graph.add_interval_series(
    name="spontaneous_blocks",
    t_start=spontaneous_start,
    t_end=spontaneous_stop,
    color="lightcoral",
    alpha=0.5,
)

# Create raster plot of neural units
print("\nExtracting neural units data...")
units = nwb.units
num_units = len(units.id)
print(f"Number of units: {num_units}")

print("Creating raster plot...")
raster_plot_items = [
    fpss.RasterPlotItem(
        unit_id=str(units.id[i]), spike_times_sec=units.spike_times_index[i]
    )
    for i in range(num_units)
]

raster_start_time = 0
raster_end_time = np.max(units.spike_times_index[num_units - 1]) + 10

raster_plot = fpss.RasterPlot(
    start_time_sec=raster_start_time,
    end_time_sec=raster_end_time,
    plots=raster_plot_items,
)

# Create combined visualization
print("\nCreating combined visualization...")
combined_view = fp.Box(
    direction="vertical",
    items=[
        fp.LayoutItem(
            view=trials_graph, title="Trials", stretch=1, max_size=80, collapsible=True
        ),
        fp.LayoutItem(
            view=spontaneous_graph,
            title="Spontaneous Blocks",
            stretch=1,
            max_size=80,
            collapsible=True,
        ),
        fp.LayoutItem(
            view=pupil_graph,
            title="Pupil Diameter",
            min_size=100,
            stretch=1,
            collapsible=True,
        ),
        fp.LayoutItem(
            view=running_speed_graph,
            title="Running Speed",
            min_size=100,
            stretch=1,
            collapsible=True,
        ),
        fp.LayoutItem(
            view=raster_plot,
            title="Spike Raster Plot",
            min_size=100,
            stretch=2,
            collapsible=True,
        ),
    ],
    show_titles=True,
)
# Display combined view
print("Displaying combined view...")
this_script = read_script(__file__, _this_script_contains_no_sensitive_info=True)
url = combined_view.show(
    title=f'DANDI:000986/{asset_path}',
    description="Test description",
    script=this_script,
    wait_for_input=False if output_file is not None else True,
    upload=True if output_file is not None else False,
)

if output_file is not None:
    print(f"Figure URL: {url}")
    print(f"Writing figure URL to {output_file}...")
    with open(output_file, "w") as f:
        f.write(url)
