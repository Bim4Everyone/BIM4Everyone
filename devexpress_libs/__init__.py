# -*- coding: utf-8 -*-

import os
import sys
import os.path as op


def load_assemblies():
    directory = op.dirname(__file__)
    framework_path = os.path.join(directory, "libs")
    sys.path.append(framework_path)
