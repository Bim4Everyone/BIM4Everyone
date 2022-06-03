# -*- coding: utf-8 -*-

import clr
import traceback

from dosymep_libs.simple_services import *

def log_plugin(plugin_name):
    def plugin_decorator(func):
        def wrapper(*args, **kwargs):
            plugin_logger_service = get_logger_service().ForPluginContext(plugin_name)
            plugin_logger_service.Information("Запуск команды расширения.")
            try:
                func(plugin_logger_service, *args, **kwargs)
                plugin_logger_service.Information("Выход из команды расширения.")
            except SystemExit:
                plugin_logger_service.Information("Выход из команды расширения.")
                raise
            except System.OperationCanceledException:
                plugin_logger_service.Information("Отмена выполнения команды расширения.")
                raise
            except Autodesk.Revit.Exceptions.OperationCanceledException:
                plugin_logger_service.Information("Отмена выполнения команды расширения.")
                raise
            except Exception as ex:
                plugin_logger_service.Warning("IronPython Traceback.\r\n" + traceback.format_exc().strip())
                raise

        return wrapper

    return plugin_decorator