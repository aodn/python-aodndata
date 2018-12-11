from __future__ import absolute_import
from __future__ import unicode_literals
import os

def dest_path_deakin_bathymetry(filepath):
    path_list = ['Deakin_University', 'bathymetry']
    path_list.append(os.path.basename(filepath))
    return os.path.join(*path_list)
