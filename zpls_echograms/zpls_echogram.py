#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import cmocean
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import os
import warnings

from calendar import monthrange
from datetime import datetime, date, timedelta
from echopype.convert import Convert
from echopype.process import Process
from pandas.plotting import register_matplotlib_converters

register_matplotlib_converters()
subsite_config = {
    'CE01ISSM': {
        'long_name': 'Oregon Inshore Surface Mooring',
        'tilt_correction': 15,
        'colorbar_range': [-90, -50],
        'vertical_range': [0, 25],
        'deployed_depth': 25
    },
    'CE06ISSM': {
        'long_name': 'Washington Inshore Surface Mooring',
        'tilt_correction': 15,
        'colorbar_range': [-90, -50],
        'vertical_range': [0, 30],
        'deployed_depth': 29
    },
    'CE07SHSM': {
        'long_name': 'Washington Shelf Surface Mooring',
        'tilt_correction': 15,
        'colorbar_range': [-90, -50],
        'vertical_range': [0, 87],
        'deployed_depth': 87
    },
    'CE09OSSM': {
        'long_name': 'Washington Offshore Surface Mooring',
        'tilt_correction': 15,
        'colorbar_range': [-90, -50],
        'vertical_range': [0, 540],
        'deployed_depth': 542
    },
    'CP04OSSM': {
        'long_name': 'Offshore Surface Mooring',
        'tilt_correction': 15,
        'colorbar_range': [-150, 0],
        'vertical_range': [0, 450],
        'deployed_depth': 450
    },
    'CP03ISSM': {
        'long_name': 'Inshore Surface Mooring',
        'tilt_correction': 15,
        'colorbar_range': [-150, 0],
        'vertical_range': [0, 90],
        'deployed_depth': 90
    },
    'CP01CNSM': {
        'long_name': 'Central Surface Mooring',
        'tilt_correction': 15,
        'colorbar_range': [-150, 0],
        'vertical_range': [0, 130],
        'deployed_depth': 130
    },
    'GI02HYPM_Upper': {
        'long_name': 'Apex Profiler Mooring, Upward Looking',
        'tilt_correction': 15,
        'colorbar_range': [-150, 0],
        'vertical_range': [0, 150],
        'deployed_depth': 150
    },
    'GI02HYPM_Lower': {
        'long_name': 'Apex Profiler Mooring, Downward Looking',
        'tilt_correction': 15,
        'colorbar_range': [-150, 0],
        'vertical_range': [150, 300],
        'deployed_depth': 150
    },
    'GP02HYPM_Upper': {
        'long_name': 'Apex Profiler Mooring, Upward Looking',
        'tilt_correction': 15,
        'colorbar_range': [-150, 0],
        'vertical_range': [0, 150],
        'deployed_depth': 150},
    'GP02HYPM_Lower': {
        'long_name': 'Apex Profiler Mooring, Downward Looking',
        'tilt_correction': 15,
        'colorbar_range': [-150, 0],
        'vertical_range': [150, 300],
        'deployed_depth': 150
    }
}


def set_file_name(serial_number, dates, subsite, deployment_number):
    """
    Create the file name for the echogram based on the mooring site name,
    deployment number, instrument serial number and date range plotted.

    :param serial_number: instrument serial number
    :param dates: date range shown in the plot
    :param subsite: mooring site name
    :param deployment_number: sequential mooring deployment number
    :return file_name: file name as a string created from the inputs
    """
    serial_number = 'SN' + str(serial_number) + '_'
    if subsite is None:
        subsite = ''
    else:
        subsite = subsite + '_'
    if deployment_number is None:
        deployment_number = ''
    else:
        deployment_number = 'R' + deployment_number + '_'
    file_name = subsite + deployment_number + serial_number + dates[0] + '-' + dates[1]
    return file_name


def ax_config(ax, upward, frequency):
    """
    Configure axis elements for the echogram, setting title, date formatting
    and direction of the y-axis

    :param ax: graphics handle to the axis object
    :param upward: boolean flag to set whether this is an upward or downward
        looking instrument, y-axis direction set accordingly
    :param frequency: acoustic frequency of the data plotted in this axis
    :return None:
    """
    title = '%.0f kHz' % (frequency / 1000)
    ax.set_title(title)
    ax.grid(False)

    ax.set_ylabel('Vertical Range (m)')
    if not upward:  # plot depth increasing down the y-axis
        ax.invert_yaxis()
    x_fmt = mdates.DateFormatter('%b-%d')
    ax.xaxis.set_major_formatter(x_fmt)
    ax.set_xlabel('')


def generate_echogram(data, subsite, long_name, deployment_number, deployed_depth, output_dir, file_name,
                      dates, vertical_range=None, colorbar_range=None):
    """
    Generates and saves to disk an echogram of the acoustic volume backscatter
    for each of the frequencies.

    :param data: xarray dataset containing the acoustic volume backscatter data
    :param subsite: 8 letter OOI code (e.g. CP01CNSM) name of the mooring
    :param long_name: Full descriptive name of the mooring
    :param deployment_number: OOI sequential deployment number
    :param deployed_depth: nominal instrument depth in meters
    :param output_dir: directory to save the echogram plot to
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
        'font.size': 12,
        'axes.linewidth': 1.0,
        'axes.titlelocation': 'right',
        'figure.figsize': [17, 11],
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

    # set the color map to "balance" from CMOCEAN and set the c_min and c_max from the colorbar range
    my_cmap = cmocean.cm.balance
    if not colorbar_range:
        v_min = None  # colorbar range will be set by the range in the data
        v_max = None
    else:
        v_min = colorbar_range[0]
        v_max = colorbar_range[1]

    # if upward looking, increase y-axis from bottom to top, otherwise increase from the top to the bottom
    if subsite in ['GP02HYPM_Lower', 'GI02HYPM_Lower']:
        upward = False
    else:
        upward = True

    # initialize the echogram figure and set the title
    fig, ax = plt.subplots(nrows=len(frequency_list), sharex='all', sharey='all')
    ht = fig.suptitle('{} ({}-{}), {} m nominal depth, {} to {} UTC'.format(long_name, subsite, deployment_number,
                                                                            deployed_depth, start_date, stop_date))
    ht.set_horizontalalignment('left')
    ht.set_position([0.125, 0.9025])  # position title to the left

    # populate the subplots
    im = []
    for index in range(len(frequency_list)):
        im.append(data.isel(frequency=index).Sv.plot(x='ping_time', y='range', vmin=v_min, vmax=v_max, ax=ax[index],
                                                     cmap=my_cmap, add_colorbar=False))
        ax_config(ax[index], upward, frequency_list[index])

    # set a common x- and y-axis, label the x-axis and create space for a shared colorbar
    ax[0].set_xlim([date.fromisoformat(start_date), date.fromisoformat(stop_date)])
    ax[0].set_ylim([y_min, y_max])
    plt.xlabel('Date (UTC)')
    fig.subplots_adjust(right=0.89)
    cbar = fig.add_axes([0.91, 0.30, 0.012, 0.40])
    fig.colorbar(im[0], cax=cbar, label='Sv (dB)')

    # save the echogram
    echogram_name = file_name + '.png'
    plt.savefig(os.path.join(output_dir, echogram_name), bbox_inches='tight', dpi=150)


def range_correction(data, tilt_correction):
    """
    Apply a correction to the calculated range using the supplied tilt
    correction value instead of the instrument's measured tilt/roll values.

    :param data: xarray dataset with the calculated range
    :param tilt_correction: tilt correction value in degrees to use
    :return None: adjusts the range variable in the xarray object directly
    """
    data['range'] = data.range * np.cos(np.deg2rad(tilt_correction))


def file_path_generator(data_directory, dates):
    """
    Generate a list of file paths pointing to the .01A files that contain the
    dates the user has requested.

    :param data_directory: path to directory with the AZFP .01A files
    :param dates: starting and ending dates to use in generating the file list
    :return file_list: list of potential .01A file names, including full path
    """
    if len(dates) == 1 and len(dates[0]) == 8:
        dates += [dates[0]]
    else:
        if len(dates) == 1:
            dates += [(dates[0] + str(monthrange(int(dates[0][:4]), int(dates[0][4:6]))[1]))[:8]]
        else:
            dates[1] = (dates[1] + str(monthrange(int(dates[1][:4]), int(dates[1][4:6]))[1]))[:8]
        dates[0] = (dates[0]+'01')[:8]
    sdate = date(int(dates[0][:4]), int(dates[0][4:6]), int(dates[0][6:8]))
    edate = date(int(dates[1][:4]), int(dates[1][4:6]), int(dates[1][6:8]))
    delta = edate - sdate
    file_list = []
    for i in range(delta.days + 1):
        day = sdate + timedelta(days=i)
        for hr in range(24):
            file_list.append(os.path.join(data_directory, day.strftime('%Y%m'), day.strftime('%y%m%d') +
                                          str(hr).zfill(2) + '.01A'))
    return file_list


def main(argv=None):
    # Creating an argparse object
    parser = argparse.ArgumentParser(description='ZPLSC/G echogram generator')

    # Creating input arguments
    parser.add_argument('-tc', '--tilt_correction', dest='tilt_correction', type=int,
                        help='Apply tilt correction in degree(s)')
    # parser.add_argument('-s', '--site', choice=['endurance','pioneer','global'],
    #                     help='"endurance", "pioneer", or "global" array')
    parser.add_argument('-ss', '--subsite', dest='subsite', type=str, help=('The subsite where the ZPLSC/G is '
                                                                            'located. Ex: CP03ISSM, GI02HYPM_Upper, '
                                                                            'or GP02HYPM_Lower'))
    parser.add_argument('-dn', '--deployment_number', dest='deployment_number', type=str, help='Deployment number.')
    parser.add_argument('-dd', '--deployed_depth', dest='deployed_depth', type=int,
                        help='The depth where the ZPLSC/G is located at')
    parser.add_argument('-cr', '--colorbar_range', dest='colorbar_range', type=int, nargs=2,
                        help='Set colorbar range. Usage: "min" "max"')
    parser.add_argument('-dr', '--vertical_range', dest='vertical_range', type=int, nargs=2,
                        help='Set the range for the y-axis. Usage: "min" "max"')
    parser.add_argument('data_directory', type=str, help=('The path to /DATA directory, where the .01A files '
                                                          'are stored'))
    parser.add_argument('xml_file', type=str, help='The path to .xml file')
    parser.add_argument('dates', type=str, nargs='+', help='YYYYMM or YYYYMMDD')
    parser.add_argument('output_dir', type=str, help='The path where .nc file and .png plot is being saved')

    # parse the input arguments
    args = parser.parse_args(argv)
    tilt_correction = args.tilt_correction
    subsite = args.subsite
    deployment_number = args.deployment_number
    colorbar_range = args.colorbar_range
    vertical_range = args.vertical_range
    data_directory = os.path.abspath(args.data_directory)
    xml_file = args.xml_file
    dates = args.dates
    output_dir = os.path.abspath(args.output_dir)
    deployed_depth = args.deployed_depth

    # make sure the output directory exists. if not, create it
    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)

    # assign per subsite variables
    if subsite in subsite_config:
        # if tilt_correction flag is not set, set the tilt correction from the subsite configuration
        if tilt_correction is None:
            tilt_correction = subsite_config[subsite]['tilt_correction']
        # if deployed_depth flag is not set, set the deployed_depth from the subsite configuration
        if deployed_depth is None:
            deployed_depth = subsite_config[subsite]['deployed_depth']
        # if colorbar_range flag is not set, set the colorbar_range from the subsite configuration
        if colorbar_range is None:
            colorbar_range = subsite_config[subsite]['colorbar_range']
        # if vertical_range flag is not set, set the vertical_range from the subsite configuration
        if vertical_range is None:
            vertical_range = subsite_config[subsite]['vertical_range']
    elif subsite is not None:
        raise parser.error('Subsite not found')

    # set other metadata attributes from the subsite dictionary
    long_name = subsite_config[subsite]['long_name']

    # generate a list of possible data files given input dates and check to see if they exist
    file_list = file_path_generator(data_directory, dates)
    file_list = [file for file in file_list if os.path.isfile(file)]
    if not file_list:
        # if there are no files to process, exit cleanly
        return None

    # convert the list of .01A files using echopype and save the output as a .zarr file to output_dir
    dc = Convert(file_list, xml_file)
    dc.platform_name = subsite      # OOI site name
    dc.platform_type = 'Mooring'    # ICES platform type
    dc.platform_code_ICES = '48'    # ICES code: tethered collection of instruments at a fixed location that may
                                    # include seafloor, mid-water or surface components
    serial_number = (dc.parameters['serial_number'])
    file_name = set_file_name(serial_number, dates, subsite, deployment_number)
    dc.raw2zarr(combine_opt=True, save_path=os.path.join(output_dir, file_name + '.zarr'), overwrite=True)

    # process the data, applying calibration coefficients and calculating the depth with a tilt correction
    tmp_echo = Process(os.path.join(output_dir, file_name + '.zarr'))
    tmp_echo.salinity = 33                                 # nominal salinity in PSU
    tmp_echo.pressure = deployed_depth                     # nominal site depth in dbar
    tmp_echo.recalculate_environment()                     # recalculate related parameters
    tmp_echo.calibrate()                                   # calculate Sv
    v_range = tmp_echo.calc_range(tilt_corrected=False)    # extract the range
    data = tmp_echo.Sv.assign_coords(range=v_range)        # add to the dateset as a coordinate variable
    if tilt_correction:
        range_correction(data, tilt_correction)            # apply tilt correction, if applicable

    # resample the data to a 15 minute burst averaged time-series
    warnings.filterwarnings('ignore', category=FutureWarning)
    burst = data.resample({'ping_time': '15Min'}, keep_attrs=True).median()

    # generate the echogram
    generate_echogram(burst, subsite, long_name, deployment_number, deployed_depth, output_dir, file_name,
                      dates, vertical_range, colorbar_range)


if __name__ == '__main__':
    main()
