"""Contains functions which provide corresponding name and remedy of ICP numbers."""
from collections import namedtuple
from importlib.resources import files
from pathlib import PurePath
from functools import lru_cache
import csv
from edcon.utils.logging import Logging


@lru_cache
def read_icp_map_file(icp_map_file: str = None):
    """Creates a dict based on a provided ICP name map file

    Parameters:
        icp_map_file (str): Optional file to use for mapping. 
                                 If nothing provided try to load mapping shipped with package.
    Returns:
        dict: With the first column values as keys and namedtuple values
    """
    if not icp_map_file:
        icp_map_file = PurePath(files('edcon') / 'edrive' / 'data' / 'icp_map.csv')

    with open(icp_map_file, encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        # Define a namedtuple where the header row determines the field names
        icp_item = namedtuple('icp_item', next(reader, None))
        # Create a dict where the first column determines the key
        icp_name_dict = {int(row[0]): icp_item(*row) for row in reader}
    return icp_name_dict


def diagnosis_name(icp_number: int, icp_map_file: str = None) -> str:
    """Determines the corresponding name to a provided icp_number, can be 
       determined either via a provided icp_map_file or 
       by the icp_map_file shipped with the package.

    Parameters:
        icp_number (int): ICP number whose name should be determined.
        icp_map_file (str): Optional file name for icp_map. 
                                 By default installed icp_map file is used.
    Returns:
        value: Name of corresponding ICP
    """
    icp_map = read_icp_map_file(icp_map_file)
    if not icp_number in icp_map.keys():
        Logging.logger.error(f'No entry for ICP {icp_number}')
    return icp_map[icp_number].name


def diagnosis_remedy(icp_number: int, icp_map_file: str = None) -> list:
    """Determines the corresponding remedies to a provided icp_number, can be 
       determined either via a provided icp_map_file or 
       by the icp_map_file shipped with the package.

    Parameters:
        icp_number (int): ICP number whose remedy should be determined.
        icp_map_file (str): Optional file name for icp_map. 
                                 By default installed icp_map file is used.
    Returns:
        value: List of str containing potential remedies for the corresponding ICP
    """
    icp_map = read_icp_map_file(icp_map_file)
    if not icp_number in icp_map.keys():
        Logging.logger.error(f'No entry for ICP {icp_number}')
    remedy_list = [x.strip('-')
                   for x in icp_map[icp_number].remedy.split('\n')]
    return remedy_list
