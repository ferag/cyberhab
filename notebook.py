#import APIs
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import numpy as np

#import satellite submodules
from wq_modules import sentinel
from wq_modules import landsat
from wq_modules import water
from wq_modules import clouds

#import meteo submodules
from wq_modules import meteo

#import general submodules
from wq_modules import utils
from wq_modules import config

#widget
import ipywidgets as widgets
from ipywidgets import HBox, VBox
from IPython.display import display
from IPython.display import clear_output

def plot_meteo(region_buttons, ini_date, end_date, actions):
    region = region_buttons.value
    sd = ini_date.value
    #datetime.strptime(ini_date.value, "%m-%d-%Y")
    ed = end_date.value
    m = meteo.Meteo(sd, ed, region)
    meteo_output = m.get_meteo()
    data = pd.read_csv(meteo_output['output'],delimiter=',',decimal=',')
    data['Date'] = pd.to_datetime(data['Date'])
    #data["Temp"] = float(data["Temp"])
    data
    data.plot(x='Date', y='Temp')
    plt.show()



def plot_satellite(region_buttons, ini_date, end_date, actions):

    #Check the format date and if end_date > start_date
    st_date = ini_date.value
    ed_date = end_date.value
    sd, ed = utils.valid_date(st_date, ed_date)

    #chek the region to attach coordinates
    region = region_buttons.value
    utils.valid_region(region)

    #check if the action exist in the Keywords list of config file
    act = actions.value[0]
    utils.valid_action(act)

    #Configure the tree of the temporal datasets path. Create the folder and the downloaded_files file
    onedata_mode = config.onedata_mode
    utils.path_configurations(onedata_mode)

    #Action management
    if act is not None:

        #download sentinel files
        s = sentinel.Sentinel(sd, ed, region, act)
        s.download()
        sentinel_files = s.__dict__['output']

        #download landsat files
        l = landsat.Landsat(sd, ed, region, act)
        l.download()
        landsat_files = l.__dict__['output']

        if onedata_mode == 1:
            utils.to_onedata(sentinel_files, landsat_files, region)
            utils.clean_temporal_path()

        if act == 'water_mask' or act == 'water_surface':

            water.main_water(sentinel_files, landsat_files, region, act)

        elif act == 'cloud_mask' or act == 'cloud_coverage':

            clouds.main_cloud(sentinel_files, landsat_files, region, act)

region_buttons = widgets.ToggleButtons(
    options=['CdP', 'Santabria', 'Cogotas'],
    description='Region:',
)
ini_date = widgets.DatePicker(
    description='Initial Date',
    disabled=False
)
end_date = widgets.DatePicker(
    description='End Date',
    disabled=False
)
actions = widgets.SelectMultiple(
    options=['meteo', 'water_mask', 'water_surface', 'cloud_mask', 'cloud_coverage'],
    value=['meteo'],
    #rows=10,
    description='Actions',
    disabled=False
)
tab = VBox(children=[region_buttons, ini_date, end_date, actions])

button = widgets.Button(
    description='Plot',
)

out = widgets.Output()
@button.on_click
def plot_on_click(b):
    with out:
        clear_output()
        if actions.value[0] == 'meteo':
            plot_meteo()
        else:
            plot_satellite()

VBox(children=[tab,button,out])
