import pandas as pd
from utility_functions import data_subfolder
import os


def TS_input():
    df_solar_raw = pd.read_csv(os.path.join(data_subfolder(), 'solar_data-530_-710_2019.csv'))
    df_wind_raw = pd.read_csv(os.path.join(data_subfolder(), 'wind_data-530_-710_2019.csv'))

    df_wind = df_wind_raw[['local_time', 'electricity']].rename(columns={'local_time': 't', 'electricity': 'CFgen'})
    df_solar = df_solar_raw[['local_time', 'electricity']].rename(columns={'local_time': 't', 'electricity': 'CFgen'})

    df_wind['t'] = pd.to_datetime(df_wind['t'])
    df_solar['t'] = pd.to_datetime(df_solar['t'])

    df_wind.set_index('t', inplace=True)
    df_solar.set_index('t', inplace=True)
    return df_wind, df_solar

