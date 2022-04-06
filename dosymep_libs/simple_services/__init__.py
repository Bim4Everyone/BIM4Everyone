# -*- coding: utf-8 -*-

import os.path

import clr
clr.AddReference('dosymep.Revit.dll')
clr.AddReference('dosymep.Bim4Everyone.dll')

clr.AddReference('dosymep.Xpf.Core.dll')
clr.AddReference('dosymep.SimpleServices.dll')

clr.AddReference('Serilog.dll')
clr.AddReference('Serilog.Sinks.File.dll')

from System import Uri
from System.Windows.Media.Imaging import BitmapImage

from pyrevit import script
from pyrevit import EXEC_PARAMS

from dosymep.SimpleServices import *
from dosymep.Bim4Everyone.SimpleServices import *


def get_logger_service():
    return ServicesProvider.GetPlatformService[ILoggerService]()


def get_notification_service():
    return ServicesProvider.GetPlatformService[INotificationService]()


def show_notification_service(title, body, footer=None, image_source=None):
    notification_service = get_notification_service()
    notification_service.CreateNotification(title, body, footer, image_source).ShowAsync()


def show_canceled_script_notification():
    show_script_notification("Выполнение скрипта отменено.")


def show_executed_script_notification():
    show_script_notification("Выполнение скрипта завершено успешно.")


def show_script_notification(body):
    image_path = EXEC_PARAMS.command_path + "\icon.png"

    image_source = None
    if os.path.isfile(image_path):
        image_source = BitmapImage(Uri(image_path))

    show_notification_service(script.get_button().ui_title, body, image_source=image_source)
