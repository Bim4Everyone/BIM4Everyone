# -*- coding: utf-8 -*-


class Environment:
    # std
    import sys
    import traceback
    import unicodedata
    import os
    # clr
    import clr
    clr.AddReference('System')
    clr.AddReference('System.IO')
    clr.AddReference('PresentationCore')
    clr.AddReference("PresentationFramework")
    clr.AddReference("System.Windows")
    clr.AddReference("System.Xaml")
    clr.AddReference("WindowsBase")

    from System.Windows import MessageBox
    #
    @classmethod
    def Exit(cls):
        cls.sys.exit("Exit current environment!")

    @classmethod
    def GetLastError(cls):
        info = cls.sys.exc_info()
        infos = ''.join(cls.traceback.format_exception(info[0], info[1], info[2]))
        return infos

    @classmethod
    def GetString(cls, array, delim):
        if not isinstance(array, list): return ""
        if array is None: return ""
        if delim is None: delim = ""
        strn = ""
        i = 1
        l = len(array)
        strn += array[0]
        while i < l:
            elemt = array[i]
            if elemt is None: elemt = ""
            if type(elemt) is not str: elemt = str(elemt)
            if strn is not "": strn += delim
            strn += elemt
            i += 1
        return strn

    @classmethod
    def Message(cls, msg):
        if not msg is None and type(msg) == str:
            cls.MessageBox.Show(msg)
        else:
            cls.MessageBox.Show("Empty argument or non string error message!")

    @classmethod
    def SafeCall(cls, code, tail, show):
        back = None
        flag = 0
        info = "empty"
        if not code is None:
            try:
                back = code(tail)
                flag = 1
            except:
                exc_t, exc_v, exc_i = sys.exc_info()
                info = ''.join(cls.traceback.format_exception(exc_t, exc_v, exc_i))
                if show: cls.Message(info)
        return [flag, back, info]


from Autodesk.Revit.DB import ElementId, FilteredElementCollector, BuiltInCategory, BuiltInParameter, Transaction, \
    TransactionGroup, View
from Autodesk.Revit.DB import ViewDuplicateOption


class property_names:
    view_purpose = "Назначение вида"
    view_name = "Имя вида"
    view_template = "Шаблон вида"
    view_local_group1 = "_Группа Видов"
    view_local_group2 = "Вид.НазначениеВида"
    view_local_stage1 = "_Раздел Проекта"
    view_local_stage2 = "Вид.СтадияПроекта"


class DataWorker:
    def __init__(self, **kwargs):
        self.doc = __revit__.ActiveUIDocument.Document
        self.uidoc = __revit__.ActiveUIDocument
        self.selection = [self.doc.GetElement(elId) for elId in __revit__.ActiveUIDocument.Selection.GetElementIds()]
        self.dupopt = ViewDuplicateOption
        self._setup(**kwargs)

    def _setup(self, **kwargs):
        pass

    def CheckParameter(self, param):
        if param is None:
            # alert("Номер листа отсутствует")
            sys.exit()
        checker = []
        for item in self.selection:
            p = item.LookupParameter(param)
            if p is None:
                continue
            checker.append(p.AsString())

        res = all((checker[0] == n) for n in checker)

        return res

    def GetElement(self, id):
        return self.doc.GetElement(id)

    def GetBase(self):
        pass

    def GetByParameter(self, param):
        pass

    def CheckType(self):
        pass

    @staticmethod
    def GetParameter(item, param):
        if item is None or param is None:
            return None
        res = item.LookupParameter(param)
        if res:
            return res.AsString()
        else:
            return None

    @staticmethod
    def SetParameter(item, param, volume):
        if item is None or param is None or volume is None:
            return False
        return item.LookupParameter(param).Set(volume)

    def Transaction(self, fun, *args):
        def wrapped(*args):
            tg = TransactionGroup(self.doc, "Update")
            tg.Start()
            t = Transaction(self.doc, "Update Parmeters")
            t.Start()

            fun(*args)

            t.Commit()

            tg.Assimilate()

        return wrapped(*args)


class ViewWorker(DataWorker):
    def _setup(self, **kwargs):
        pass

    def CheckType(self):
        return all(isinstance(n, View) for n in self.selection)

    def GetBase(self):
        self.base = FilteredElementCollector(self.doc).OfCategory(BuiltInCategory.OST_Views).ToElements()

    def GetPurposeList(self):
        if not hasattr(self, 'base'):
            self.GetBase()
        purpose = []
        for view in self.base:
            if view is None: continue
            param = self.GetParameter(view, property_names.view_purpose)
            if param is not None and param not in purpose: purpose.append(param)
            param = self.GetParameter(view, property_names.view_local_group2)
            if param is not None and param not in purpose: purpose.append(param)
            param = self.GetParameter(view, property_names.view_local_group1)
            if param is not None and param not in purpose: purpose.append(param)
        # Environment.Message(Environment.GetString(purpose, "\r\n"))
        return purpose

    def GetByUser(self, user):
        if not hasattr(self, 'base'):
            self.GetBase()

        UserView = []
        for view in self.base:

            if self.GetParameter(view, property_names.view_purpose) == user:
                if self.GetParameter(view, property_names.view_name):
                    UserView.append(view)

        self.purpose = user
        self.user = UserView

    def SetAfterCopy(self, view, name, res):
        newname = res["prefix"] + "_" + name + "_" + res["suffix"]
        try:
            view.LookupParameter(property_names.view_name).Set(newname)
            view.LookupParameter(property_names.view_purpose).Set(res["purpose"])
        except:
            info = Environment.GetLastError()
        # Environment.Message(info)
        try:
            param = view.LookupParameter(property_names.view_local_group2)
            if param is not None: param.Set(res["purpose"])
        except:
            info = Environment.GetLastError()
        # Environment.Message(info)
        try:
            param = view.LookupParameter(property_names.view_local_group1)
            if param is not None: param.Set(res["purpose"])
        except:
            info = Environment.GetLastError()
        # Environment.Message(info)
        Environment.Message("Готово!")

    @staticmethod
    def ResetTemplate(view):
        par = view.LookupParameter(property_names.view_template)
        if par:
            a = ElementId(-1)
            par.Set(a)

    @staticmethod
    def SplitPrefix(view):
        namePar = view.LookupParameter(property_names.view_name)
        if namePar:
            name = namePar.AsString()
            index = name.find("_")
            prefix = name[:index]
            purpose = name[index + 1:]
            return [prefix, purpose]
