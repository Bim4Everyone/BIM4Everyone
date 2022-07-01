# -*- coding: utf-8 -*-

import os
import sys
import shutil
import os.path as op

from pyrevit import HOST_APP


def copy_files(source_dir, target_dir):
    for file_name in os.listdir(source_dir):
        source = op.join(source_dir, file_name)
        target = op.join(target_dir, file_name)
        if os.path.isfile(source):
            shutil.copy(source, target)


def load_assemblies():
    temp_path = os.path.join(os.getenv('TEMP'), "Bim4Everyone", "dosymep")
    if not op.exists(temp_path):
        app_libs = op.join(op.dirname(__file__), "libs")

        version_libs = op.join(app_libs, HOST_APP.version)
        shutil.copytree(version_libs, temp_path)
        copy_files(app_libs, temp_path)

    sys.path.append(temp_path)


