# -*- coding: utf-8 -*-

import clr
clr.AddReference('dosymep.Revit.dll')
clr.AddReference('dosymep.Bim4Everyone.dll')

clr.AddReference('dosymep.Xpf.Core.dll')
clr.AddReference('dosymep.SimpleServices.dll')

clr.AddReference('Serilog.dll')
clr.AddReference('Serilog.Sinks.File.dll')

from dosymep.SimpleServices import *
from dosymep.Bim4Everyone.SimpleServices import *


def get_logger_service():
    return ServicesProvider.GetPlatformService[ILoggerService]()


def get_notification_service():
    return ServicesProvider.GetPlatformService[INotificationService]()


def show_notification_service(title, body, footer=None, image_source=None):
    notification_service = get_notification_service()
    notification_service.CreateNotification(title, body, footer, image_source).ShowAsync()
