# -*- coding: utf-8 -*-

import os
import sys
import os.path as op
from pyrevit import HOST_APP

def load_assemblies():
    directory = op.dirname(__file__)
    framework_path = os.path.join(directory, HOST_APP.version)
    sys.path.append(framework_path)