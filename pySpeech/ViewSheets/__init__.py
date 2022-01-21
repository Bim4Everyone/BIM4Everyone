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

def alert(msg, exit_script=True):
    if msg:
        print msg

    if exit_script:
        script.exit()


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
        show_table(output, title, "Виды к которых совпадает атрибут \"Номер листа\".", table_columns, table_data)


def show_table(output, title, table_title, table_columns, table_data, exit_script=True):
    output.print_table(title=table_title, columns=table_columns, table_data=table_data)

    if exit_script:
        script.exit()


class DocumentRepository(object):
    def __init__(self, uiApplication):
        self.UIApplication = uiApplication

    @property
    def Application(self):
        return self.UIApplication.Application

    @property
    def Document(self):
        return self.UIDocument.Document

    @property
    def UIDocument(self):
        return self.UIApplication.ActiveUIDocument

    def GetViewSheets(self):
        return FilteredElementCollector(self.Document).OfClass(ViewSheet).ToElements()

    def GetSelectedViewSheets(self):
        return filter(lambda x: isinstance(x, ViewSheet), self.UIDocument.GetSelectedElements())


class ViewSheetModel(object):
    def __init__(self, index, viewSheet):
        self.__index = index
        self.__viewSheet = viewSheet

    @property
    def Id(self):
        return  self.__viewSheet.Id

    @property
    def SheetAlbum(self):
        return ViewSheetModel.GetSheetAlbum(self.__viewSheet)

    @property
    def SheetIndex(self):
        return self.__index

    # @property.setter
    # def SheetIndex(self, value):
    #     if isinstance(value, int):
    #         self.__index = value

    @property
    def SheetName(self):
        if self.SheetAlbum:
            return "{}-{}".format(self.SheetAlbum, self.__index)

        return str(self.__index)

    @property
    def OriginalSheetIndex(self):
        return int(self.OriginalSheetName.split("-").pop())

    @property
    def OriginalSheetName(self):
        return self.__viewSheet.GetParamValueOrDefault(BuiltInParameter.SHEET_NUMBER)

    def UpdateName(self):
        self.__viewSheet.SetParamValue(SharedParamsConfig.Instance.StampSheetNumber, str(self.__index))
        self.__viewSheet.SetParamValue(BuiltInParameter.SHEET_NUMBER, self.SheetName)

    def UpdateUniqueName(self):
        self.__viewSheet.SetParamValue(BuiltInParameter.SHEET_NUMBER, str(Guid.NewGuid()))

    @staticmethod
    def GetSheetAlbum(view_sheet):
        complect_blueprints = view_sheet.GetParamValueOrDefault(SharedParamsConfig.Instance.AlbumBlueprints)
        return complect_blueprints if complect_blueprints else ""


class OrderViewSheetModel(object):
    def __init__(self, documentRepository, start_index=1):
        self.DocumentRepository = documentRepository
        self.StartIndex = start_index

    def OrderViewSheets(self):
        project_parameters = ProjectParameters.Create(self.DocumentRepository.Application)
        project_parameters.SetupRevitParams(self.DocumentRepository.Document, SharedParamsConfig.Instance.AlbumBlueprints,
                                            SharedParamsConfig.Instance.StampSheetNumber)

        with TransactionGroup(self.DocumentRepository.Document) as transaction:
            transaction.Start("Перенумерация листов")

            # переименовываем листы на случайные имена
            # чтобы случайно не пересеклись новые имена со старыми
            self.UpdateUniqueNames()
            self.UpdateNames()

            transaction.Assimilate()

    def CheckUniquesNames(self):
        sheet_ids = [sheet.Id for sheet in self.ViewSheets]
        sheets = filter(lambda x: x.Id not in sheet_ids, self.GetViewSheets())

        sheet_names = [sheet.SheetName for sheet in self.ViewSheets]
        error_sheets = filter(lambda x: x.SheetNumber in sheet_names, sheets)

        show_error_sheets("Ошибка", error_sheets)

    def UpdateNames(self):
        with Transaction(self.DocumentRepository.Document) as transaction:
            transaction.Start("Нумерация")

            for view_sheet in self.ViewSheets:
                view_sheet.UpdateName()

            transaction.Commit()

    def UpdateUniqueNames(self):
        with Transaction(self.DocumentRepository.Document) as transaction:
            transaction.Start("Нумерация")

            for view_sheet in self.ViewSheets:
                view_sheet.UpdateUniqueName()

            transaction.Commit()

    def GetViewSheets(self):
        return self.DocumentRepository.GetViewSheets()

    def GetSelectedViewSheet(self):
        selections = self.DocumentRepository.GetSelectedViewSheets()
        return OrderViewSheetModel.CheckSheets(selections)

    def LoadViewSheets(self):
        selected_view_sheet = self.GetSelectedViewSheet()[0]

        view_album = ViewSheetModel.GetSheetAlbum(selected_view_sheet)
        self.SetViewSheets([sheet for sheet in self.GetViewSheets() if ViewSheetModel.GetSheetAlbum(sheet) == view_album])

    def LoadSelectedViewSheets(self):
        self.SetViewSheets(self.GetSelectedViewSheet())

    def SetViewSheets(self, sheets):
        sheets = sorted(sheets, cmp=ViewSheetComparer().Compare)
        self.ViewSheets = [ViewSheetModel(index + self.StartIndex, view_sheet) for index, view_sheet in enumerate(sheets)]

    @staticmethod
    def CheckSheets(selections):
        if not selections:
            alert("Не были выбраны элементы.")

        sheet_numbers = set([ViewSheetModel.GetSheetAlbum(s) for s in selections])
        if len(sheet_numbers) > 1:
            alert("У выделенных элементов указано несколько альбомов.")

        return selections



# Проверка на соответствие выбранному альбому
def AlbumFilter(x, album):
    if x.GetParamValueOrDefault(SharedParamsConfig.Instance.AlbumBlueprints) == album:
        return 1
    else:
        return 0


# Получение числа из строки
def ClearString(msg):
    number = ""
    for i in range(len(msg)):
        if msg[i].isdigit():
            number += msg[i]
    return number


# Получаем число для сравнения из строки вида "str-num.num"
def GetNumber(list):
    return float(list.pop())


def CheckSheets(selections):
    if not selections:
        alert("Не были выбраны элементы.")

    sheet_numbers = set([ViewSheetModel.GetSheetAlbum(s) for s in selections])
    if len(sheet_numbers) > 1:
        alert("У выделенных элементов указано несколько альбомов.")

    return selections


doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
selection = list(__revit__.ActiveUIDocument.GetSelectedElements())


def renumber(step, direction, count, transactionName):
    # проверка выделенных элементов
    CheckSheets(selection)

    # настройка атрибутов
    project_parameters = ProjectParameters.Create(__revit__.Application)
    project_parameters.SetupRevitParams(doc, SharedParamsConfig.Instance.AlbumBlueprints,
                                        SharedParamsConfig.Instance.StampSheetNumber)

    # список из листов учавствующих в перестановке
    SheetsCurrentAlbumList = []

    # список, на основе кторого будет сортировка
    SortingList = []

    # список, на основе которого будет происходить перенумерование листов
    SheetsComposeAlbumList = []

    # пара значений, будет хранить в себе номер крайнего листа среди рабочих
    prop = [GetNumber(selection[0].GetParamValueOrDefault(BuiltInParameter.SHEET_NUMBER).split("-")), ""]

    # название альбома
    album = selection[0].GetParamValueOrDefault(SharedParamsConfig.Instance.AlbumBlueprints)

    # все листы проекта
    SheetsBaseList = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Sheets).ToElements()

    # составляем список из троек значений, [пригодный для сортировки номер, сам лист, номер листа в строковой форме]
    for sheet in SheetsBaseList:
        if AlbumFilter(sheet, album):
            NumberString = sheet.GetParamValueOrDefault(BuiltInParameter.SHEET_NUMBER)
            NumberList = GetNumber(NumberString.split("-"))
            SortingList.append([NumberList, sheet, NumberString])

    # сортируем список
    SheetsCurrentAlbumList = sorted(SortingList, cmp=ViewSheetComparer().Compare, key=lambda x: x[1])

    # если перемещаем вниз, то нужно перевернуть список
    if direction < 0:
        SheetsCurrentAlbumList = SheetsCurrentAlbumList[::-1]

    # находим опорное значение из выбранных листов, при уменьшении номера ищем большее, иначе - меньшее
    for sheet in selection:
        NumberString = sheet.GetParamValueOrDefault(BuiltInParameter.SHEET_NUMBER)
        NumberInt = GetNumber(NumberString.split("-"))
        if direction * prop[0] < direction * NumberInt:
            prop[0] = NumberInt
            prop[1] = NumberString

    # идем с конца списка, удаляя все листы стоящие после наших выбранных
    for sheet in SheetsCurrentAlbumList[::-1]:
        if direction * prop[0] < direction * sheet[0]:
            SheetsCurrentAlbumList.pop()
        else:
            break

    # удаляем листы стоящие перед выбранными плюс step листов
    while len(SheetsCurrentAlbumList) > count + step:
        SheetsCurrentAlbumList.pop(0)

    # теперь размер списка постоянный, запишем его длину
    n = len(SheetsCurrentAlbumList)

    # кладем листы в нужном порядке первым значением из пары, второе значение это номера с неизменным порядком
    for i in range(n - count, n):
        element = [SheetsCurrentAlbumList[i - (n - count)][0], SheetsCurrentAlbumList[i][1], SheetsCurrentAlbumList[i - (n - count)][2]]
        SheetsComposeAlbumList.append(element)
    for i in range(n - count):
        element = [SheetsCurrentAlbumList[i + count][0], SheetsCurrentAlbumList[i][1], SheetsCurrentAlbumList[i + count][2]]
        SheetsComposeAlbumList.append(element)

    with Transaction(doc, transactionName) as transaction:
        transaction.Start()

        for idx, sheet in enumerate(SheetsComposeAlbumList):
            sheet[1].SetParamValue(BuiltInParameter.SHEET_NUMBER, str(idx) + "+Temp")
        for sheet in SheetsComposeAlbumList:
            sheet[1].SetParamValue(BuiltInParameter.SHEET_NUMBER, sheet[2])
            sheet[1].SetParamValue(SharedParamsConfig.Instance.StampSheetNumber, str(int(sheet[0])))

        transaction.Commit()