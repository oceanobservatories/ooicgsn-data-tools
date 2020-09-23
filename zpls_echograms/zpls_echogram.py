#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import matplotlib.pyplot as plt
import numpy as np
import os

from calendar import monthrange
from datetime import date, timedelta
from echopype.convert import Convert
from echopype.process import Process
from pandas.plotting import register_matplotlib_converters

register_matplotlib_converters()
subsite_config = {
    'CP04OSSM': {
        'tilt_correction': 15,
        'colorbar_range': [-150, 0],
        'deployed_depth': 450
    },
    'CP03ISSM': {
        'tilt_correction': 15,
        'colorbar_range': [-150, 0],
        'deployed_depth': 90
    },
    'CP01CNSM': {
        'tilt_correction': 15,
        'colorbar_range': [-150, 0],
        'deployed_depth': 130
    },
    'GI02HYPM_Upper': {
        'tilt_correction': 15,
        'colorbar_range': [-150, 0],
        'deployed_depth': 150
    },
    'GI02HYPM_Lower': {
        'tilt_correction': 15,
        'colorbar_range': [-150, 0],
        'deployed_depth': 150
    },
    'GP02HYPM_Upper': {
        'tilt_correction': 15,
        'colorbar_range': [-150, 0],
        'deployed_depth': 150},
    'GP02HYPM_Lower': {
        'tilt_correction': 15,
        'colorbar_range': [-150, 0],
        'deployed_depth': 150
    }
}


def set_file_name(serial_number, dates, subsite, deployment_number):
    """
    TODO: Add function description and variable definitions

    :param serial_number:
    :param dates:
    :param subsite:
    :param deployment_number:
    :return:
    """
    serial_number = 'SN'+str(serial_number)+'_'
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


def ax_config(ax, frequency, y_min, y_max):
    """
    TODO: Add function description and variable definitions

    :param ax:
    :param frequency:
    :param y_min:
    :param y_max:
    :return:
    """
    font_size_small = 14
    font_size_large = 18

    title = 'Volume Backscatter (Sv): Frequency: %.0f kHz' % (frequency / 1000)
    ax.set_title(title, fontsize=font_size_large)
    ax.grid(False)

    ax.set_ylabel('depth (m)', fontsize=font_size_small)
    ax.set_ylim([y_min, y_max])
    ax.invert_yaxis()

    ax.tick_params(axis="both", labelcolor="k", pad=4, direction='out', length=5, width=2)

    ax.spines['top'].set_visible(True)
    ax.spines['right'].set_visible(True)
    ax.spines['bottom'].set_visible(True)
    ax.spines['left'].set_visible(True)


def generate_echogram(data, output_dir, file_name, v_min=None, v_max=None):
    """
    TODO: Add function description and variable definitions

    :param data:
    :param output_dir:
    :param file_name:
    :param v_min:
    :param v_max:
    :return:
    """
    interplot_spacing = 0.1
    frequency_list = data.frequency.values
    y_min = 0
    y_max = np.amax(data.depth)

    fig, ax = plt.subplots(nrows=len(frequency_list), sharex='all', sharey='all')
    fig.subplots_adjust(hspace=interplot_spacing)
    fig.set_size_inches(40, 19)

    for index in range(len(frequency_list)):
        data.isel(frequency=index).swap_dims({'range_bin': 'depth'}).Sv.plot(x='ping_time', y='depth', vmin=v_min,
                                                                             vmax=v_max, ax=ax[index])
        ax_config(ax[index], frequency_list[index], y_min, y_max)

    fig.tight_layout(rect=[0, 0.0, 0.97, 1.0])
    echogram_name = file_name+'.png'
    # plt.cm.get_cmap(viridis)
    # sc = plot.scatter()
    plt.savefig(os.path.join(output_dir, echogram_name))


def depth_correction(data, tilt_correction, deployed_depth, subsite):
    """
    TODO: Add function description and variable definitions

    :param data:
    :param tilt_correction:
    :param deployed_depth:
    :param subsite:
    :return:
    """
    if subsite in ['GP02HYPM_Lower', 'GI02HYPM_Lower']:
        if tilt_correction is not None:
            data['depth'] = data.depth * np.cos(np.deg2rad(tilt_correction))
        data['depth'] = data.depth + deployed_depth
    else:
        if tilt_correction is not None:
            data['depth'] = data.depth * np.cos(np.deg2rad(tilt_correction))
        data['depth'] = data.depth.max() - data.depth  # Reverse y-axis values
        if deployed_depth is not None:
            data['depth'] = data.depth - (data.depth.max() - deployed_depth)


def file_path_generator(data_directory, dates):
    """
    generate a list of file paths pointing to the .01A files that contain the dates user has requested

    :param data_directory:
    :param dates:
    :return:
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
    parser.add_argument('data_directory', type=str, help=('The path to /DATA directory, where the .01A files '
                                                          'are stored'))
    parser.add_argument('xml_file', type=str, help='The path to .xml file')
    parser.add_argument('dates', type=str, nargs='+', help='YYYYMM or YYYYMMDD')
    parser.add_argument('output_dir', type=str, help='The path where .nc file and .png plot is being saved')

    # parse the input arguments and create a parser object
    args = parser.parse_args(argv)
    tilt_correction = args.tilt_correction
    subsite = args.subsite
    deployment_number = args.deployment_number
    colorbar_range = args.colorbar_range
    data_directory = os.path.abspath(args.data_directory)
    xml_file = args.xml_file
    dates = args.dates
    output_dir = os.path.abspath(args.output_dir)
    deployed_depth = args.deployed_depth

    # make sure the output directory exists. if not, create it
    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)

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
    elif subsite is not None:
        raise parser.error('Subsite not found')

    if colorbar_range is not None:
        v_min = colorbar_range[0]
        v_max = colorbar_range[1]
    else:
        v_min = None
        v_max = None

    # convert the list of .01A files using echopype and save the output .nc file to output_dir
    file_list = file_path_generator(data_directory, dates)
    dc = Convert(file_list, xml_file)

    serial_number = (dc.parameters['serial_number'])
    file_name = set_file_name(serial_number, dates, subsite, deployment_number)

    dc.raw2nc(combine_opt=True, save_path=os.path.join(output_dir, file_name+'.nc'))
    tmp_echo = Process(os.path.join(output_dir, file_name+'.nc'))
    tmp_echo.calibrate(save=False)  # Sv data
    depth = tmp_echo.calc_range(tilt_corrected=False)
    data = tmp_echo.Sv.assign_coords(depth=depth)

    depth_correction(data, tilt_correction, deployed_depth, subsite)
    generate_echogram(data, output_dir, file_name, v_min, v_max)


if __name__ == '__main__':
    main()
