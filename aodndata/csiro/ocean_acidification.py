from __future__ import absolute_import
from __future__ import unicode_literals
import os

def dest_path_oa(filepath):
    return os.path.join("CSIRO/Climatology/Ocean_Acidification/{filename}".format(filename=os.path.basename(filepath)))
