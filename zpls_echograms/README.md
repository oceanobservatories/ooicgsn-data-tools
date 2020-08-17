ZPLSC/G Echogram Code & Instructions

Note: The preset colorbar ranges are the same for every array. Feel free to change it in the code.

Optional flags:
-tc     --tilt_correction                Apply tilt correction in degree(s)
-ss     --subsite                          The subsite where the ZPLSC/G is located. Ex: "CP03ISSM", "GI02HYPM_Upper", or "GP02HYPM_Lower"
-dn    --deployment_number      Deployment number
-dd    --deployed_depth             The depth where the ZPLSC/G is located at
-cr    --colorbar_range                Set colorbar range. Useage: "min max"

Required Input:
data_directory                              The path to /DATA directory, where the .01A files are stored
xml_file                                        The path to .xml file
dates                                            The date range to be plotted. Ex: "20200118" will plot the day (01/18/2020),
                                                                                                        "202001" will plot the whole month (01/01/2020 to 01/31/2020),
                                                                                                        "202001 202002" will plot (01/01/2020 to 02/29/2020),
                                                                                                        "20200115 20200216" will plot (01/15/2020 to 02/16/2020)
output_dir                                    The path where .nc file and .png plot is being saved

Usage:
python3    zpls_echogram.py    [data_directory]    [xml_file]    [dates]    [output_dir]

ZPLS raw data folder structure (This is how the instrument stores the data):
./GI/ZPLSG_sn55067/DATA/201610
        ./GI/ZPLSG_sn55067/DATA/201610/16101401.01A
        ./GI/ZPLSG_sn55067/DATA/201610/16101402.01A
        ./GI/ZPLSG_sn55067/DATA/201610/16101403.01A
        ./GI/ZPLSG_sn55067/DATA/201610/*.01A
        ./GI/ZPLSG_sn55067/DATA/201610/16101417.XML
./GI/ZPLSG_sn55067/DATA/201611
        ./GI/ZPLSG_sn55067/DATA/201611/16111401.01A
        ./GI/ZPLSG_sn55067/DATA/201611/16111402.01A
        ./GI/ZPLSG_sn55067/DATA/201611/16111403.01A
        ./GI/ZPLSG_sn55067/DATA/201611/*.01A

Example 1:
python3    zpls_echogram.py    ./GI/ZPLSG_sn55067/DATA    ./GI/ZPLSG_sn55067/DATA/201610/16101417.XML    20161115    20161116    ./processed_folder

The code will process the data from 11/15/2016 to 11/16/2016. The .nc file and .png plot will be stored at ./processed_folder.

Example 2:
python3    zpls_echogram.py    ./GI/ZPLSG_sn55067/DATA    ./GI/ZPLSG_sn55067/DATA/201610/16101417.XML    201611    ./processed_folder

The code will process the data from 11/01/2016 to 11/30/2016. The .nc file and .png plot will be stored at ./processed_folder.

Example 3:
python3    zpls_echogram.py    ./GI/ZPLSG_sn55067/DATA    ./GI/ZPLSG_sn55067/DATA/201610/16101417.XML    201611    ./processed_folder    -ss    GI02HYPM_Upper

Once a subsite is specified, the code will look at the mooring configuration and apply the corrected tilt angle (15degrees for GI02HYPM_Upper) and the theoretical depth (150m for GI02HYPM_Upper).

Example 4:
python3    zpls_echogram.py    ./GI/ZPLSG_sn55067/DATA    ./GI/ZPLSG_sn55067/DATA/201610/16101417.XML    201611    ./processed_folder    -ss    GI02HYPM_Upper    -dd    160

If the instrument is deployed at 160m instead of the the theoretical depth of 150m. The optional flag -dd 160 will overwrite the mooring configuration.

Example 5:
python3    zpls_echogram.py    ./GI/ZPLSG_sn55067/DATA    ./GI/ZPLSG_sn55067/DATA/201610/16101417.XML    201611    ./processed_folder    -ss    GI02HYPM_Upper    -cr    -120    -20    -dd    160

The optional flag -cr will set the colorbar range from -120 to -20.

Output Naming Convention:
The naming convention is:

subsite + deployment_number + serial_number + date

If subsite and deployment_number is not specified, the output file name will become:

serial_number + date

Example 6:
python3    zpls_echogram.py    ./GI/ZPLSG_sn55067/DATA    ./GI/ZPLSG_sn55067/DATA/201610/16101417.XML    201611    ./processed_folder

The code will create ./processed_folder/SN55067-20161101-20161130.nc and ./processed_folder/SN55067-20161101-20161130.png

Example 7:
python3    zpls_echogram.py    ./GI/ZPLSG_sn55067/DATA    ./GI/ZPLSG_sn55067/DATA/201610/16101417.XML    201611    ./processed_folder    -ss    GI02HYPM_Upper

The code will create ./processed_folder/GI02HYPM_Upper_SN55067-20161101-20161130.nc and ./processed_folder/GI02HYPM_Upper_SN55067-20161101-20161130.png

Example 8:
python3    zpls_echogram.py    ./GI/ZPLSG_sn55067/DATA    ./GI/ZPLSG_sn55067/DATA/201610/16101417.XML    201611    ./processed_folder    -ss    GI02HYPM_Upper    -dn    4

The code will create ./processed_folder/GI02HYPM_Upper_R4_SN55067-20161101-20161130.nc and ./processed_folder/GI02HYPM_Upper_R4_SN55067-20161101-20161130.png


