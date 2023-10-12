# -*- coding: utf-8 -*-

import clr
clr.AddReference("dosymep.Revit.dll")
clr.AddReference("dosymep.Bim4Everyone.dll")

import dosymep
clr.ImportExtensions(dosymep.Revit)
clr.ImportExtensions(dosymep.Bim4Everyone)

from System import Guid
from System.Collections.Generic import *

from Autodesk.Revit.DB import *

from dosymep.Revit.Comparators import *
from dosymep.Bim4Everyone.Templates import ProjectParameters
from dosymep.Bim4Everyone.SharedParams import SharedParamsConfig
from dosymep.Bim4Everyone.ProjectParams import ProjectParamsConfig

from operator import itemgetter
from pyrevit import script
from pyrevit import revit
from pyrevit import forms


def get_table_columns():
    return ["SheetId", "SheetName"]


def get_row_section(output, element):
    return [output.linkify(element.Id), element.Name]


def get_table_data(output, sheets):
    return [get_row_section(output, sheets) for sheets in sheets]


def show_error_sheets(title, sheets):
    if sheets:
        output = script.get_output()
        output.set_title(title)
        output.center()

        table_columns = get_table_columns()
        table_data = get_table_data(output, sheets)
        show_table(output, title,
                   "Виды к которых совпадает атрибут \"Номер листа\".", table_columns, table_data)


def show_table(output, title, table_title, table_columns, table_data, exit_script=True):
    output.print_table(title=table_title, columns=table_columns, table_data=table_data)

    if exit_script:
        script.exit()


class DocumentRepository(object):
    def __init__(self, ui_application):
        self.UIApplication = ui_application

    @property
    def Application(self):
        return self.UIApplication.Application

    @property
    def Document(self):
        return self.ui_document.Document

    @property
    def ui_document(self):
        return self.UIApplication.ActiveUIDocument

    def get_view_sheets(self):
        return FilteredElementCollector(self.Document).OfClass(ViewSheet).ToElements()

    def get_selected_view_sheets(self):
        return filter(lambda x: isinstance(x, ViewSheet), self.ui_document.GetSelectedElements())


class ViewSheetModel(object):
    def __init__(self, index, view_sheet):
        self.__index = index
        self.__viewSheet = view_sheet

    @property
    def Id(self):
        return self.__viewSheet.Id

    @property
    def sheet_album(self):
        return ViewSheetModel.get_sheet_album(self.__viewSheet)

    @property
    def sheet_index(self):
        return self.__index

    @property
    def sheet_name(self):
        if self.sheet_album:
            return "{}-{}".format(self.sheet_album, self.__index)

        return str(self.__index)

    @property
    def original_sheet_index(self):
        return int(self.original_sheet_name.split("-").pop())

    @property
    def original_sheet_name(self):
        return self.__viewSheet.GetParamValueOrDefault(BuiltInParameter.SHEET_NUMBER)

    def update_name(self):
        self.__viewSheet.SetParamValue(SharedParamsConfig.Instance.StampSheetNumber, str(self.__index))
        self.__viewSheet.SetParamValue(BuiltInParameter.SHEET_NUMBER, self.sheet_name)

    def update_unique_name(self):
        self.__viewSheet.SetParamValue(BuiltInParameter.SHEET_NUMBER, str(Guid.NewGuid()))

    @staticmethod
    def get_sheet_album(view_sheet):
        complect_blueprints = view_sheet.GetParamValueOrDefault(SharedParamsConfig.Instance.AlbumBlueprints)
        return complect_blueprints if complect_blueprints else ""


class OrderViewSheetModel(object):
    def __init__(self, document_repository, start_index=1):
        self.ViewSheets = []
        self.StartIndex = start_index
        self.DocumentRepository = document_repository

    def order_view_sheets(self):
        project_parameters = ProjectParameters.Create(self.DocumentRepository.Application)
        project_parameters.SetupRevitParams(self.DocumentRepository.Document,
                                            SharedParamsConfig.Instance.AlbumBlueprints,
                                            SharedParamsConfig.Instance.StampSheetNumber)

        with revit.TransactionGroup("BIM: Перенумерация листов") as transaction:
            # переименовываем листы на случайные имена
            # чтобы случайно не пересеклись новые имена со старыми
            self.update_unique_names()
            self.update_names()

    def check_uniques_names(self):
        sheet_ids = [sheet.Id for sheet in self.ViewSheets]
        sheets = filter(lambda x: x.Id not in sheet_ids, self.get_view_sheets())

        sheet_names = [sheet.sheet_name for sheet in self.ViewSheets]
        error_sheets = filter(lambda x: x.SheetNumber in sheet_names, sheets)

        show_error_sheets("Ошибка", error_sheets)

    def update_names(self):
        with revit.Transaction("BIM: Нумерация"):
            for view_sheet in self.ViewSheets:
                view_sheet.update_name()

    def update_unique_names(self):
        with revit.Transaction("BIM: Нумерация"):
            for view_sheet in self.ViewSheets:
                view_sheet.update_unique_name()

    def get_view_sheets(self):
        return self.DocumentRepository.get_view_sheets()

    def get_selected_view_sheet(self):
        selections = self.DocumentRepository.get_selected_view_sheets()
        selections = [view for view in selections if view.ViewType == ViewType.DrawingSheet]
        return OrderViewSheetModel.check_sheets(selections)

    def load_view_sheets(self):
        selected_view_sheet = self.get_selected_view_sheet()[0]

        view_album = ViewSheetModel.get_sheet_album(selected_view_sheet)
        self.set_view_sheets([sheet for sheet in self.get_view_sheets() if ViewSheetModel.get_sheet_album(sheet) == view_album])

    def load_selected_view_sheets(self):
        self.set_view_sheets(self.get_selected_view_sheet())

    def set_view_sheets(self, sheets):
        sheets = sorted(sheets, cmp=ViewSheetComparer().Compare)
        self.ViewSheets = [ViewSheetModel(index + self.StartIndex, view_sheet) for index, view_sheet in enumerate(sheets)]

    @staticmethod
    def check_sheets(selections):
        if not selections:
            forms.alert("Не были выбраны листы.", exitscript=True)

        sheet_numbers = set([ViewSheetModel.get_sheet_album(s) for s in selections])
        if len(sheet_numbers) > 1:
            forms.alert("У выделенных листов указано несколько альбомов.", exitscript=True)

        return selections


# Проверка на соответствие выбранному альбому
def album_filter(x, album):
    if x.GetParamValueOrDefault(SharedParamsConfig.Instance.AlbumBlueprints) == album:
        return 1
    else:
        return 0


# Получение числа из строки
def clear_string(msg):
    number = ""
    for i in range(len(msg)):
        if msg[i].isdigit():
            number += msg[i]
    return number


# Получаем число для сравнения из строки вида "str-num.num"
def get_number(splitted):
    return float(splitted.pop())


def check_sheets(selections):
    if not selections:
        forms.alert("Не были выбраны листы.", exitscript=True)

    sheet_numbers = set([ViewSheetModel.get_sheet_album(s) for s in selections])
    if len(sheet_numbers) > 1:
        forms.alert("У выделенных листов указано несколько альбомов.", exitscript=True)


def renumber(step, direction, count, transaction_name):
    doc = __revit__.ActiveUIDocument.Document
    selection = list(__revit__.ActiveUIDocument.GetSelectedElements())
    selection = [view for view in selection if view.ViewType == ViewType.DrawingSheet]

    # проверка выделенных элементов
    check_sheets(selection)

    # настройка атрибутов
    project_parameters = ProjectParameters.Create(__revit__.Application)
    project_parameters.SetupRevitParams(doc, SharedParamsConfig.Instance.AlbumBlueprints,
                                        SharedParamsConfig.Instance.StampSheetNumber)

    # список из листов участвующих в перестановке
    sheets_current_album_list = []

    # список, на основе которого будет сортировка
    sorting_list = []

    # список, на основе которого будет происходить перенумерование листов
    sheets_compose_album_list = []

    # пара значений, будет хранить в себе номер крайнего листа среди рабочих
    prop = [get_number(selection[0].GetParamValueOrDefault(BuiltInParameter.SHEET_NUMBER).split("-")), ""]

    # название альбома
    album = selection[0].GetParamValueOrDefault(SharedParamsConfig.Instance.AlbumBlueprints)

    # все листы проекта
    sheets_base_list = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Sheets).ToElements()

    # составляем список из троек значений, [пригодный для сортировки номер, сам лист, номер листа в строковой форме]
    for sheet in sheets_base_list:
        if album_filter(sheet, album):
            number_string = sheet.GetParamValueOrDefault(BuiltInParameter.SHEET_NUMBER)
            number_list = get_number(number_string.split("-"))
            sorting_list.append([number_list, sheet, number_string])

    # сортируем список
    sheets_current_album_list = sorted(sorting_list, cmp=ViewSheetComparer().Compare, key=lambda x: x[1])

    # если перемещаем вниз, то нужно перевернуть список
    if direction < 0:
        sheets_current_album_list = sheets_current_album_list[::-1]

    # находим опорное значение из выбранных листов, при уменьшении номера ищем большее, иначе - меньшее
    for sheet in selection:
        number_string = sheet.GetParamValueOrDefault(BuiltInParameter.SHEET_NUMBER)
        number_int = get_number(number_string.split("-"))
        if direction * prop[0] < direction * number_int:
            prop[0] = number_int
            prop[1] = number_string

    # идем с конца списка, удаляя все листы стоящие после наших выбранных
    for sheet in sheets_current_album_list[::-1]:
        if direction * prop[0] < direction * sheet[0]:
            sheets_current_album_list.pop()
        else:
            break

    # удаляем листы стоящие перед выбранными плюс step листов
    while len(sheets_current_album_list) > count + step:
        sheets_current_album_list.pop(0)

    # теперь размер списка постоянный, запишем его длину
    n = len(sheets_current_album_list)

    # кладем листы в нужном порядке первым значением из пары, второе значение это номера с неизменным порядком
    for i in range(n - count, n):
        element = [sheets_current_album_list[i - (n - count)][0], sheets_current_album_list[i][1], sheets_current_album_list[i - (n - count)][2]]
        sheets_compose_album_list.append(element)
    for i in range(n - count):
        element = [sheets_current_album_list[i + count][0], sheets_current_album_list[i][1], sheets_current_album_list[i + count][2]]
        sheets_compose_album_list.append(element)

    with revit.Transaction("BIM: " + transaction_name):
        for idx, sheet in enumerate(sheets_compose_album_list):
            sheet[1].SetParamValue(BuiltInParameter.SHEET_NUMBER, str(idx) + "+Temp")
        for sheet in sheets_compose_album_list:
            sheet[1].SetParamValue(BuiltInParameter.SHEET_NUMBER, sheet[2])
            sheet[1].SetParamValue(SharedParamsConfig.Instance.StampSheetNumber, str(int(sheet[0])))
