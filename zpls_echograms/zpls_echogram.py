#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import cmocean
import dateutil.parser as dparser
import glob
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import os
import warnings
import xarray as xr

from calendar import monthrange
from datetime import datetime, date, timedelta
from echopype.convert import Convert
from echopype.process import Process
from pandas.plotting import register_matplotlib_converters
from PIL import Image

warnings.filterwarnings('ignore', category=FutureWarning)
register_matplotlib_converters()
site_config = {
    'CE01ISSM': {
        'long_name': 'Coastal Endurance, Oregon Inshore Surface Mooring',
        'tilt_correction': 15,
        'colorbar_range': [-90, -50],
        'vertical_range': [0, 25],
        'deployed_depth': 25,
        'instrument_orientation': 'up'
    },
    'CE02SHBP': {
        'long_name': 'Coastal Endurance, Oregon Shelf Cabled Benthic Experiment Package',
        'tilt_correction': 0,
        'colorbar_range': [-90, -50],
        'vertical_range': [0, 80],
        'deployed_depth': 80,
        'instrument_orientation': 'up'
    },
    'CE04OSPS': {
        'long_name': 'Coastal Endurance, Oregon Offshore Cabled Shallow Profiler Mooring',
        'tilt_correction': 0,
        'colorbar_range': [-90, -50],
        'vertical_range': [0, 200],
        'deployed_depth': 200,
        'instrument_orientation': 'up'
    },
    'CE06ISSM': {
        'long_name': 'Coastal Endurance, Washington Inshore Surface Mooring',
        'tilt_correction': 15,
        'colorbar_range': [-90, -50],
        'vertical_range': [0, 30],
        'deployed_depth': 29,
        'instrument_orientation': 'up'
    },
    'CE07SHSM': {
        'long_name': 'Coastal Endurance, Washington Shelf Surface Mooring',
        'tilt_correction': 15,
        'colorbar_range': [-90, -50],
        'vertical_range': [0, 87],
        'deployed_depth': 87,
        'instrument_orientation': 'up'
    },
    'CE09OSSM': {
        'long_name': 'Coastal Endurance, Washington Offshore Surface Mooring',
        'tilt_correction': 15,
        'colorbar_range': [-90, -50],
        'vertical_range': [0, 540],
        'deployed_depth': 542,
        'instrument_orientation': 'up'
    },
    'CP04OSSM': {
        'long_name': 'Coastal Pioneer, Offshore Surface Mooring',
        'tilt_correction': 15,
        'colorbar_range': [-90, -50],
        'vertical_range': [0, 460],
        'deployed_depth': 450,
        'instrument_orientation': 'up'
    },
    'CP03ISSM': {
        'long_name': 'Coastal Pioneer, Inshore Surface Mooring',
        'tilt_correction': 15,
        'colorbar_range': [-90, -50],
        'vertical_range': [0, 100],
        'deployed_depth': 95,
        'instrument_orientation': 'up'
    },
    'CP01CNSM': {
        'long_name': 'Coastal Pioneer, Central Surface Mooring',
        'tilt_correction': 15,
        'colorbar_range': [-90, -50],
        'vertical_range': [0, 140],
        'deployed_depth': 135,
        'instrument_orientation': 'up'
    },
    'GI02HYPM_UPPER': {
        'long_name': 'Global Irminger Sea, Apex Profiler Mooring, Upward Looking',
        'tilt_correction': 15,
        'colorbar_range': [-95, -65],
        'vertical_range': [0, 200],
        'deployed_depth': 150,
        'instrument_orientation': 'up'
    },
    'GI02HYPM_LOWER': {
        'long_name': 'Global Irminger Sea, Apex Profiler Mooring, Downward Looking',
        'tilt_correction': 15,
        'colorbar_range': [-95, -65],
        'vertical_range': [0, 400],
        'deployed_depth': 150,
        'instrument_orientation': 'down'
    },
    'GP02HYPM_UPPER': {
        'long_name': 'Global Station Papa, Apex Profiler Mooring, Upward Looking',
        'tilt_correction': 15,
        'colorbar_range': [-95, -65],
        'vertical_range': [0, 200],
        'deployed_depth': 150,
        'instrument_orientation': 'up'
    },
    'GP02HYPM_LOWER': {
        'long_name': 'Global Station Papa, Apex Profiler Mooring, Downward Looking',
        'tilt_correction': 15,
        'colorbar_range': [-95, -65],
        'vertical_range': [0, 400],
        'deployed_depth': 150,
        'instrument_orientation': 'down'
    },
    'GA02HYPM_UPPER': {
        'long_name': 'Global Argentine Basin, Apex Profiler Mooring, Upward Looking',
        'tilt_correction': 15,
        'colorbar_range': [-95, -65],
        'vertical_range': [0, 200],
        'deployed_depth': 150,
        'instrument_orientation': 'up'
    },
    'GA02HYPM_LOWER': {
        'long_name': 'Global Argentine Basin, Apex Profiler Mooring, Downward Looking',
        'tilt_correction': 15,
        'colorbar_range': [-95, -65],
        'vertical_range': [0, 400],
        'deployed_depth': 150,
        'instrument_orientation': 'down'
    },
    'GS02HYPM_UPPER': {
        'long_name': 'Global Southern Ocean, Apex Profiler Mooring, Upward Looking',
        'tilt_correction': 15,
        'colorbar_range': [-95, -65],
        'vertical_range': [0, 200],
        'deployed_depth': 150,
        'instrument_orientation': 'up'
    },
    'GS02HYPM_LOWER': {
        'long_name': 'Global Southern Ocean, Apex Profiler Mooring, Downward Looking',
        'tilt_correction': 15,
        'colorbar_range': [-95, -65],
        'vertical_range': [0, 400],
        'deployed_depth': 150,
        'instrument_orientation': 'down'
    }
}

attributes = {
    # attributes for the variables in the NetCDF files
    'global': {
        'title': 'Measurements of the Volume Acoustic Backscatter Strength',
        'summary': ('Volume acoustic backscatter strength measurements collected by bioacoustic sonar sensors '
                    'deployed on moorings and seafloor platforms as part of the Ocean Observatories Initiative '
                    'project funded by the National Science Foundation. Data was converted and processed from raw '
                    'instrument files to this processed dataset using the open-source package echopype '
                    '(https://echopype.readthedocs.io/en/latest/)'),
        'project': 'Ocean Observatories Initiative',
        'acknowledgement': 'National Science Foundation',
        'references': 'http://oceanobservatories.org',
        'creator_name': 'Ocean Observatories Initiative',
        'creator_email': 'helpdesk@oceanobservatories.org',
        'creator_url': 'http://oceanobservatories.org',
        'featureType': 'timeSeries',
        'cdm_data_type': 'Station',
        'Conventions': 'CF-1.6'
    },
    'frequency': {
        'long_name': 'Acoustic Frequency',
        'standard_name': 'sound_frequency',
        'units': 'Hz'
    },
    'ping_time': {
        'long_name': 'Time of Each Ping',
        'standard_name': 'time',
        'units': 'seconds since 1970-01-01 00:00:00.0000000',
        'calendar': 'gregorian',
        'comment': ('Derived from the instrument internal clock. Instrument clocks are subject to drift. The data '
                    'should be checked against other sensors to determine if drift and offset corrections are '
                    'applicable.')
    },
    'range_bin': {
        'long_name': 'Vertical Range Bin Number',
        'comment': 'Bin number starting with 0 at the sensor face, used to derive the vertical range.',
        # 'units': ''    # deliberately left blank, no units for this value
    },
    'range': {
        'long_name': 'Vertical Range',
        'units': 'm',
        'comment': 'Vertical range from the sensor face, corrected for sensor tilt where applicable.',
    },
    'Sv': {
        'long_name': 'Volume Acoustic Backscatter Strength',
        'units': 'dB',
        'comments': ('Initial estimate of the volume acoustic backscatter strength derived from the raw instrument '
                     'data using echopype to convert and process the data.'),
        'references': 'https://echopype.readthedocs.io/en/latest/'
    }
}


def set_file_name(site, dates):
    """
    Create the file name for the echogram based on the mooring site name,
    and the date range plotted.

    :param site: mooring site name
    :param dates: date range shown in the plot
    :return file_name: file name as a string created from the inputs
    """
    file_name = site + '_Bioacoustic_Echogram_' + dates[0] + '-' + dates[1] + '_Calibrated_Sv'
    return file_name


def ax_config(ax, frequency):
    """
    Configure axis elements for the echogram, setting title, date formatting
    and direction of the y-axis

    :param ax: graphics handle to the axis object
    :param frequency: acoustic frequency of the data plotted in this axis
    :return None:
    """
    title = '%.0f kHz' % (frequency / 1000)
    ax.set_title(title)
    ax.grid(False)

    ax.set_ylabel('Vertical Range (m)')
    x_fmt = mdates.DateFormatter('%b-%d')
    ax.xaxis.set_major_formatter(x_fmt)
    ax.set_xlabel('')


def generate_echogram(data, site, long_name, deployed_depth, output_directory, file_name, dates,
                      vertical_range=None, colorbar_range=None):
    """
    Generates and saves to disk an echogram of the acoustic volume backscatter
    for each of the frequencies.

    :param data: xarray dataset containing the acoustic volume backscatter data
    :param site: 8 letter OOI code (e.g. CP01CNSM) name of the mooring
    :param long_name: Full descriptive name of the mooring
    :param deployed_depth: nominal instrument depth in meters
    :param output_directory: directory to save the echogram plot to
    :param file_name: file name to use for the echogram
    :param dates: date range to plot, sets the x-axis
    :param vertical_range: vertical range to plot, sets the y-axis
    :param colorbar_range: colorbar range to plot, sets the colormap
    :return None: generates and saves an echogram to disk
    """
    # setup defaults based on inputs
    frequency_list = data.frequency.values
    t = datetime.strptime(dates[0], '%Y%m%d')
    start_date = datetime.strftime(t, '%Y-%m-%d')
    t = datetime.strptime(dates[1], '%Y%m%d')
    stop_date = datetime.strftime(t, '%Y-%m-%d')
    params = {
        'font.size': 11,
        'axes.linewidth': 1.0,
        'axes.titlelocation': 'right',
        'figure.figsize': [17, 11],
        'figure.dpi': 100,
        'xtick.major.size': 4,
        'xtick.major.pad': 4,
        'xtick.major.width': 1.0,
        'ytick.major.size': 4,
        'ytick.major.pad': 4,
        'ytick.major.width': 1.0
    }
    plt.rcParams.update(params)

    # set the y_min and y_max from the vertical range
    if not vertical_range:
        y_min = 0
        y_max = np.amax(data.range.values)
    else:
        y_min = vertical_range[0]
        y_max = vertical_range[1]

    # set the color map to "balance" from cmocean and set the c_min and c_max from the colorbar range
    my_cmap = cmocean.cm.balance
    if not colorbar_range:
        v_min = None  # colorbar range will be set by the range in the data
        v_max = None
    else:
        v_min = colorbar_range[0]
        v_max = colorbar_range[1]

    # determine if this is an upward or downward looking sensor
    if 'LOWER' in site:
        upward = False
    else:
        upward = True

    # initialize the echogram figure and set the title
    fig, ax = plt.subplots(nrows=len(frequency_list), sharex='all', sharey='all')
    ht = fig.suptitle('{} ({})\n{} to {} UTC\n{} m nominal deployment depth'.format(long_name, site[:8], start_date,
                                                                                    stop_date, deployed_depth))
    ht.set_horizontalalignment('left')
    ht.set_position([0.301, 0.94])  # position title to the left

    # populate the subplots
    im = []
    for index in range(len(frequency_list)):
        im.append(data.isel(frequency=index).Sv.plot(x='ping_time', y='range', vmin=v_min, vmax=v_max, ax=ax[index],
                                                     cmap=my_cmap, add_colorbar=False))
        ax_config(ax[index], frequency_list[index])

    # set a common x- and y-axis, label the x-axis and create space for a shared colorbar
    ax[0].set_xlim([date.fromisoformat(start_date), date.fromisoformat(stop_date)])
    # if upward looking, increase y-axis from bottom to top, otherwise increase from the top to the bottom
    if upward:
        ax[0].set_ylim([y_min, y_max])
    else:
        ax[0].set_ylim([y_max, y_min])

    fig.subplots_adjust(right=0.89)
    cbar = fig.add_axes([0.91, 0.30, 0.012, 0.40])
    fig.colorbar(im[0], cax=cbar, label='Sv (dB)')

    # save the echogram
    echogram_name = file_name + '.png'
    plt.savefig(os.path.join(output_directory, echogram_name), dpi=150, bbox_inches='tight')


def range_correction(data, tilt_correction):
    """
    Apply a correction to the calculated range using the supplied tilt
    correction value instead of the instrument's measured tilt/roll values.

    :param data: xarray dataset with the calculated range
    :param tilt_correction: tilt correction value in degrees to use
    :return None: adjusts the range variable in the xarray object directly
    """
    data['range'] = data.range * np.cos(np.deg2rad(tilt_correction))


def calc_range(data, thickness, correction_factor):
    """
    Pulled from the echopype code to recalculate the range for EK60 data in
    order to address issues with exporting the data to an xarray dataset and
    then resampling.

    :param data:
    :param thickness:
    :param correction_factor:
    :return range_meter:
    """
    range_bin = np.atleast_2d(data.range_bin.values)
    thickness = np.tile(thickness, [range_bin.shape[1], 1])
    range_meter = thickness.T * range_bin - correction_factor * thickness.T
    range_meter = np.where(range_meter > 0, range_meter, 0)
    return range_meter


def azfp_file_list(data_directory, dates):
    """
    Generate a list of file paths pointing to the .01A files that contain the
    dates the user has requested.

    :param data_directory: path to directory with the AZFP .01A files
    :param dates: starting and ending dates to use in generating the file list
    :return file_list: list of potential .01A file names, including full path
    """
    if len(dates) == 1:
        dates += [dates[0]]

    if len(dates[0]) == 6:
        dates[0] = dates[0] + '01'
        dates[1] = dates[1] + str(monthrange(int(dates[1][:4]), int(dates[1][4:]))[1])

    sdate = dparser.parse(dates[0])
    edate = dparser.parse(dates[1]) - timedelta(days=1)
    delta = edate - sdate

    file_list = []
    for i in range(delta.days + 1):
        day = sdate + timedelta(days=i)
        files = glob.glob(os.path.join(data_directory, day.strftime('%Y%m')) + '/' + day.strftime('%y%m%d') + '*.01A')
        file_list.append(files)

    return file_list


def ek60_file_list(data_directory, dates):
    """
    Generate a list of file paths pointing to the .raw files that contain the
    dates the user has requested.

    :param data_directory: path to directory with the AZFP .01A files
    :param dates: starting and ending dates to use in generating the file list
    :return file_list: list of potential .01A file names, including full path
    """
    if len(dates) == 1:
        dates += [dates[0]]

    if len(dates[0]) == 6:
        dates[0] = dates[0] + '01'
        dates[1] = dates[1] + str(monthrange(int(dates[1][:4]), int(dates[1][4:]))[1])

    sdate = dparser.parse(dates[0])
    edate = dparser.parse(dates[1]) - timedelta(days=1)
    delta = edate - sdate

    file_list = []
    for i in range(delta.days + 1):
        day = sdate + timedelta(days=i)
        files = glob.glob(os.path.join(data_directory, day.strftime('%m'), day.strftime('%d')) + '/*.raw')
        file_list.append(files)

    return file_list


def process_azfp(site, data_directory, xml_file, output_directory, dates, tilt_correction):
    """
    Use echopype to convert and process the ASL AZFP bio-acoustic sonar data
    (in *.01A files) to generate echograms for use by the community

    :param site:
    :param data_directory:
    :param xml_file:
    :param output_directory:
    :param dates:
    :param tilt_correction:
    :return data:
    """
    # generate a list of data files given the input dates
    file_list = azfp_file_list(data_directory, dates)

    # reset the file_list to a single index
    file_list = [file for sub in file_list for file in sub]
    if not file_list:
        # if there are no files to process, exit cleanly
        return None

    # make sure the data output directory exists
    output_directory = os.path.join(output_directory, dates[0] + '-' + dates[1])
    if not os.path.isdir(output_directory):
        os.mkdir(output_directory)

    # convert the list of .01A files using echopype and save the output as NetCDF files
    dc = Convert(file_list, xml_file)
    dc.platform_name = site         # OOI site name
    dc.platform_type = 'Mooring'    # ICES platform type
    dc.platform_code_ICES = '48'    # ICES code: tethered collection of instruments at a fixed location that may
                                    # include seafloor, mid-water or surface components
    dc.raw2nc(save_path=output_directory)

    # process the data, calculating the volume acoustic backscatter strength and the vertical range
    echo = []
    nc_files = glob.glob(output_directory + '/[12]???????.nc')
    for nc in nc_files:
        tmp_echo = Process(nc)
        tmp_echo.calibrate()                                   # calculate Sv
        data = tmp_echo.Sv                                     # extract the Sv dataset
        echo.append(data.sortby('ping_time'))                  # append to the echogram list

    # concatenate the data into a single dataset
    data = xr.concat(echo, dim='ping_time', join='outer')
    data = data.sortby(['frequency', 'ping_time'])
    data['frequency'] = data['frequency'].astype(np.float32)
    data['range_bin'] = data['range_bin'].astype(np.int32)
    data['range'] = data['range'].sel(ping_time=data.ping_time[0], drop=True)
    data = data.set_coords('range')

    if tilt_correction:
        range_correction(data, tilt_correction)  # apply a tilt correction, if applicable

    # pass the Sv data back for further processing
    return data


def process_ek60(site, data_directory, output_directory, dates, tilt_correction):
    """

    :param site:
    :param data_directory:
    :param output_directory:
    :param dates:
    :param tilt_correction:
    :return data:
    """
    # generate a list of data files given the input dates
    file_list = ek60_file_list(data_directory, dates)

    # reset the file_list to a single index
    file_list = [file for sub in file_list for file in sub]
    if not file_list:
        # if there are no files to process, exit cleanly
        return None

    # make sure the data output directory exists
    output_directory = os.path.join(output_directory, dates[0] + '-' + dates[1])
    if not os.path.isdir(output_directory):
        os.mkdir(output_directory)

    # convert the list of .raw files using echopype and save the output as NetCDF files
    dc = Convert(file_list)
    dc.platform_name = site      # OOI site name
    if site == 'CE02SHBP':
        dc.platform_type = 'Fixed Benthic Node'    # ICES platform type
        dc.platform_code_ICES = '11'               # ICES code
    else:
        dc.platform_type = 'Mooring'    # ICES platform type
        dc.platform_code_ICES = '48'    # ICES code: tethered collection of instruments at a fixed location that may
                                        # include seafloor, mid-water or surface components
    dc.raw2nc(save_path=output_directory)

    # process the data, calculating the volume acoustic backscatter strength and the vertical range
    echo = []
    sample_thickness = []
    tvg_correction_factor = []
    nc_files = glob.glob(output_directory + '/*OOI-D*.nc')
    for nc in nc_files:
        tmp_echo = Process(nc)
        tmp_echo.calibrate()                                   # calculate Sv
        data = tmp_echo.Sv                                     # extract the Sv dataset
        echo.append(data.sortby('ping_time'))                  # append to the echogram list
        sample_thickness.append(tmp_echo.sample_thickness.values)
        tvg_correction_factor.append(tmp_echo.tvg_correction_factor)

    # concatenate the data into a single dataset
    data = xr.concat(echo, dim='ping_time', join='outer')
    data = data.sortby(['frequency', 'ping_time'])
    data['range_bin'] = data['range_bin'].astype(np.int32)
    data['range'] = data['range'].sel(ping_time=data.ping_time[0], drop=True)
    data = data.set_coords('range')

    # recalculate the range to deal with some discrepancies caused by the xarray concat
    thickness = np.max(np.array(sample_thickness), 0)
    correction_factor = np.max(tvg_correction_factor)
    range_meter = calc_range(data, thickness, correction_factor)
    data['range'] = data['range'].fillna(range_meter)

    if tilt_correction:
        range_correction(data, tilt_correction)  # apply a tilt correction, if applicable

    # pass the Sv data back for further processing
    return data


def main(argv=None):
    # Creating an argparse object
    parser = argparse.ArgumentParser(description='ZPLSC/G echogram generator')

    # Creating input arguments
    parser.add_argument('-s', '--site', dest='site', type=str, required=True,
                        help='The OOI 8-letter site name for where the ZPLSC/G is located.')
    parser.add_argument('-d', '--data_directory', dest='data_directory', type=str, required=True,
                        help='The path to the root directory below which the .01A or .raw files may be found.')
    parser.add_argument('-o', '--output_directory', dest='output_directory', type=str, required=True,
                        help='The path to the root directory below which the .nc file(s) and .png plot will be saved.')
    parser.add_argument('-dr', '--date_range', dest='dates', type=str, nargs='+', required=True,
                        help=('Date range to plot as either YYYYMM or YYYYMMDD. Specifying an end date is optional, '
                              'it will be assumed to be 1 month or 1 day depending on input.'))
    parser.add_argument('-zm', '--zpls_model', dest='zpls_model', type=str, required=True,
                        help='Specifies the ZPLS instrument model, either AZFP or EK60.')
    parser.add_argument('-xf', '--xml_file', dest='xml_file', type=str, required=False,
                        help='The path to .XML file used to process the AZFP data in the .01A files')
    parser.add_argument('-tc', '--tilt_correction', dest='tilt_correction', type=int, required=False,
                        help='Apply tilt correction in degree(s)')
    parser.add_argument('-dd', '--deployed_depth', dest='deployed_depth', type=int, required=False,
                        help='The depth where the ZPLSC/G is located at')
    parser.add_argument('-cr', '--colorbar_range', dest='colorbar_range', type=int, nargs=2, required=False,
                        help='Set colorbar range. Usage: "min" "max"')
    parser.add_argument('-vr', '--vertical_range', dest='vertical_range', type=int, nargs=2, required=False,
                        help='Set the range for the y-axis. Usage: "min" "max"')

    # parse the input arguments
    args = parser.parse_args(argv)
    site = args.site.upper()
    data_directory = os.path.abspath(args.data_directory)
    output_directory = os.path.abspath(args.output_directory)
    dates = args.dates
    zpls_model = args.zpls_model.upper()
    tilt_correction = args.tilt_correction
    deployed_depth = args.deployed_depth
    colorbar_range = args.colorbar_range
    vertical_range = args.vertical_range
    xml_file = args.xml_file
    if xml_file:
        xml_file = os.path.abspath(xml_file)

    # assign per site variables
    if site in site_config:
        # if tilt_correction flag is not set, set the tilt correction from the site configuration
        if tilt_correction is None:
            tilt_correction = site_config[site]['tilt_correction']
        # if deployed_depth flag is not set, set the deployed_depth from the site configuration
        if deployed_depth is None:
            deployed_depth = site_config[site]['deployed_depth']
        # if colorbar_range flag is not set, set the colorbar_range from the site configuration
        if colorbar_range is None:
            colorbar_range = site_config[site]['colorbar_range']
        # if vertical_range flag is not set, set the vertical_range from the site configuration
        if vertical_range is None:
            vertical_range = site_config[site]['vertical_range']
    elif site is not None:
        raise parser.error('The site name was not found in the configuration dictionary.')

    # make sure the root output directory exists
    if not os.path.isdir(output_directory):
        os.mkdir(output_directory)

    # use the ZPLS model to determine how to process the data
    data = None
    if zpls_model not in ['AZFP', 'EK60']:
        raise ValueError('The ZPLS model must be set as either AZFP or EK60 (case insensitive)')
    else:
        if zpls_model == 'AZFP':
            data = process_azfp(site, data_directory, xml_file, output_directory, dates, tilt_correction)

        if zpls_model == 'EK60':
            data = process_ek60(site, data_directory, output_directory, dates, tilt_correction)

    # test to see if we have any data from the processing
    if not data:
        return None

    # save the full resolution data to daily NetCDF files
    file_name = set_file_name(site, dates)
    output_directory = os.path.join(output_directory, dates[0] + '-' + dates[1])

    # reset a couple data types (helps to control size of NetCDF files)
    data['range'] = data['range'].astype(np.float32)
    data['Sv'] = data['Sv'].astype(np.float32)

    # split the data into daily records
    days, datasets = zip(*data.groupby("ping_time.day"))

    # create a list of file names based on the day of the record
    start = datetime.strptime(dates[0], '%Y%m%d')
    stop = datetime.strptime(dates[1], '%Y%m%d')
    date_list = [start + timedelta(days=x) for x in range(0, (stop - start).days)]
    nc_file = os.path.join(output_directory, file_name)
    nc_files = []
    for day in days:
        for dt in date_list:
            if dt.day == day:
                nc_files.append(nc_file + "_Full_%s.nc" % dt.strftime('%Y%m%d'))

    # convert ping_time from a datetime64[ns] object to a float (seconds since 1970) and update the attributes
    for dataset in datasets:
        dataset['ping_time'] = dataset['ping_time'].values.astype(np.float64) / 10.0 ** 9
        dataset.attrs = attributes['global']
        dataset.attrs['instrument_orientation'] = site_config[site]['instrument_orientation']

        for v in dataset.variables:
            dataset[v].attrs = attributes[v]

    # save the daily files
    xr.save_mfdataset(datasets, nc_files, mode='w', format='NETCDF4', engine='h5netcdf')

    # if a global mooring, create hourly averaged data records, otherwise create 15 minute records
    if 'HYPM' in site:
        # resample the data into a 60 minute, median averaged record, filling gaps less than 180 minutes
        avg = data.resample(ping_time='60Min').mean()
        avg = avg.interpolate_na(dim='ping_time', max_gap='180Min')
    else:
        # resample the data into a 15 minute, median averaged record, filling gaps less than 45 minutes
        avg = data.resample(ping_time='15Min').median()
        avg = avg.interpolate_na(dim='ping_time', max_gap='45Min')

    # generate the echogram
    long_name = site_config[site]['long_name']
    generate_echogram(avg, site, long_name, deployed_depth, output_directory, file_name, dates,
                      vertical_range=vertical_range, colorbar_range=colorbar_range)

    # add the OOI logo as a watermark
    echogram = os.path.join(output_directory, file_name + '.png')
    echo_image = Image.open(echogram)
    ooi_image = Image.open('ooi-logo.png')
    width, height = echo_image.size
    transparent = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    transparent.paste(echo_image, (0, 0))
    if max(vertical_range) > 99:
        transparent.paste(ooi_image, (96, 15), mask=ooi_image)
    else:
        transparent.paste(ooi_image, (80, 15), mask=ooi_image)

    # re-save the echogram with the added logo
    transparent.save(echogram)

    # save the averaged data
    avg['ping_time'] = avg['ping_time'].values.astype(np.float64) / 10.0 ** 9
    avg.attrs = attributes['global']
    avg.attrs['instrument_orientation'] = site_config[site]['instrument_orientation']
    for v in avg.variables:
        avg[v].attrs = attributes[v]

    avg_file = nc_file + '_Averaged.nc'
    avg.to_netcdf(avg_file, mode='w', format='NETCDF4', engine='h5netcdf')


if __name__ == '__main__':
    main()
