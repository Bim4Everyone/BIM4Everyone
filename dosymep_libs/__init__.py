# -*- coding: utf-8 -*-

import os
import sys
import shutil
import os.path as op
import pyrevit.coreutils.git as libgit
from pyrevit.versionmgr import updater
from pyrevit.loader import sessionmgr

from pyrevit import HOST_APP
from pyrevit.coreutils import envvars


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


def update_extension(extension_file):
    if not check_update_in_progress():
        set_autoupdate_in_progress(True)

        path = os.path.abspath(extension_file)
        repo_path = libgit.libgit.Repository.Discover(path)
        repo_info = libgit.get_repo(repo_path)
        updater.update_repo(repo_info)
        sessionmgr.load_session()

        set_autoupdate_in_progress(False)


def check_update_in_progress():
    return envvars.get_pyrevit_env_var(envvars.AUTOUPDATING_ENVVAR)


def set_autoupdate_in_progress(state):
    envvars.set_pyrevit_env_var(envvars.AUTOUPDATING_ENVVAR, state)
