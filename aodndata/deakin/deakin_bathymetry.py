import os

def dest_path_deakin_bathymetry(filepath):
    path_list = ['Deakin_University', 'bathymetry']
    path_list.append(os.path.basename(filepath))
    return os.path.join(*path_list)
