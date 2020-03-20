import tables as tb
import pandas as pd

import invisible_cities.core.system_of_units  as units

from typing import List
from typing import Optional
from typing import Union


def load_mchits_df(file_name : str) -> pd.DataFrame:
    hits = pd.read_hdf(file_name, 'MC/hits')
    hits.set_index(['event_id', 'particle_id', 'hit_id'],
                    inplace=True)
    return hits


def load_mcparticles_df(file_name: str) -> pd.DataFrame:
    particles = pd.read_hdf(file_name, 'MC/particles')
    particles.primary = particles.primary.astype('bool')
    particles.set_index(['event_id', 'particle_id'], inplace=True)
    return particles


def get_sensor_binning(file_name : str) -> pd.DataFrame:
    config = pd.read_hdf(file_name, 'MC/configuration').set_index('param_key')
    sns_names    = pd.read_hdf(file_name, 'MC/sns_positions').sensor_name
    sns_binnings = [nm + '_binning' for nm in sns_names.unique()]
    bins         = config.loc[sns_binnings].copy()
    bins.columns = ['bin_width']
    bins.index   = bins.index.rename('sns_name')
    bins.index   = bins.index.str.strip('_binning')
    bins.bin_width = bins.bin_width.str.split(expand=True).apply(
        lambda x: float(x[0]) * getattr(units, x[1]), axis=1)
    return bins


def get_sensor_types(file_name : str) -> pd.DataFrame:
    """
    returns a DataFrame linking sensor_ids to
    sensor type names.
    file_name : str
                name of the file with nexus sensor info.
    """
    sns_pos = pd.read_hdf(file_name, 'MC/sns_positions').copy()
    sns_pos.drop(['x', 'y', 'z'], axis=1, inplace=True)
    return sns_pos


def get_sensor_positions(file_name : str) -> pd.DataFrame:
    get_sensor_positions
    """
    returns a DataFrame with sensor positions.
    file_name : str
                name of the file with nexus sensor info.
    """
    sns_pos = pd.read_hdf(file_name, 'MC/sns_positions').copy()
    return sns_pos


def load_mcsensor_response_df(file_name : str                 ,
                              sns_name  : Optional[Union[str, List[str]]] = None
                              ) -> pd.DataFrame:
    """
    A reader for the MC sensor output based
    on pandas DataFrames.

    file_name: string
               Name of the file to be read
    db_file  : string
               Name of the detector database to be accessed
    run_no   : int
               Run number for database access
    sns_name : str or list[str]
               Sensor name of the data to be returned
               Default: return for every sensor
    """
    sns       = pd.read_hdf(file_name,  'MC/sns_response')
    sns_bins  = get_sensor_binning(file_name)
    sns_pos   = pd.read_hdf(file_name, 'MC/sns_positions')
    sns_pos.set_index('sensor_name', inplace=True)
    if sns_name:
        sns_pos = sns_pos.loc[sns_name]

    sns_merge = sns.merge(sns_pos.join(sns_bins), on='sensor_id')
    sns_merge['time'] = sns_merge.bin_width * sns_merge.time_bin
    sns_merge.drop(['x', 'y', 'z', 'time_bin', 'bin_width'],
                   axis=1, inplace=True)
    sns_merge.set_index(['event_id', 'sensor_id'], inplace = True)
    return sns_merge


