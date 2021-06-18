# -*- coding: utf-8 -*-
import os.path as op

import clr
clr.AddReference("System.Windows.Forms")
# clr.AddReference("System")
# clr.AddReference("System.Drawing")
# from System.Drawing import Colors
# from System.Windows.Media.Brush import SolidColorBrush
from System.Windows.Forms import FolderBrowserDialog, DialogResult
from pyrevit import forms
from pyrevit.forms import SelectFromList, TemplateUserInputWindow

class TemplateWindow(TemplateUserInputWindow):

	def __init__(self, context, title, width, height, **kwargs):
		forms.WPFWindow.__init__(self, op.join(op.dirname(__file__), self.xaml_source))
		self.Title = title
		self.Width = width
		self.Height = height

		self._context = context
		self.response = None
		self.PreviewKeyDown += self.handle_input_key

		self._setup(**kwargs)	
	
class CopyFromView(TemplateWindow):
	xaml_source = 'CopyViews.xaml'
	
	def _setup(self, **kwargs):
		self.hide_element(self.clrsuffix_b)
		self.hide_element(self.clrprefix_b)
		self.clear_suffix(None, None)
		self.clear_prefix(None, None)
		self.prefix.Focus()
		
		for i in kwargs['list']:
			if i is None:
				continue
			if type(i) == str:
				self.purpose.AddText(i)

		button_name = kwargs.get('button_name', None)
		if button_name:
			self.select_b.Content = button_name
		
		self.checkDetail.IsChecked = True
		


	def button_select(self, sender, args):
		if self.suffix.Text:
			suffix = self.suffix.Text
		else:
			suffix = ""
		if self.prefix.Text:
			prefix = self.prefix.Text
		else:
			prefix = ""
		if self.purpose.Text:
			purpose = self.purpose.Text
		else:
			purpose = ""

		detail = self.checkDetail.IsChecked
		self.response = {"suffix": suffix,
						"prefix": prefix,
						"purpose": purpose,
						"detail": detail}
		self.Close()

	def suffix_txt_changed(self, sender, args):
		"""Handle text change in search box."""
		if self.suffix.Text == '':
			self.hide_element(self.clrsuffix_b)
		else:
			self.show_element(self.clrsuffix_b)
	
	def prefix_txt_changed(self, sender, args):
		"""Handle text change in search box."""
		if self.prefix.Text == '':
			self.hide_element(self.clrprefix_b)
		else:
			self.show_element(self.clrprefix_b)

	def clear_suffix(self, sender, args):
		"""Clear search box."""
		self.suffix.Text = ''
		self.suffix.Clear()
		self.suffix.Focus
		
	def clear_prefix(self, sender, args):
		"""Clear search box."""
		self.prefix.Text = ''
		self.prefix.Clear()
		self.prefix.Focus

class InputFormNumber(TemplateWindow):

    xaml_source = 'InputNumber.xaml'

    def _setup(self, **kwargs):
		self.hide_element(self.clrsearch_b)
		self.clear_search(None, None)
		self.search_tb.Focus()
		
		button_name = kwargs.get('button_name', None)
		if button_name:
			self.select_b.Content = button_name
		
		head = kwargs.get('head', None)
		if head:
			self.head.Text = head
		

    def button_select(self, sender, args):
        """Handle select button click."""
        if self.search_tb.Text:
			self.response = self.search_tb.Text
			self.Close()

    def search_txt_changed(self, sender, args):
        """Handle text change in search box."""
        if self.search_tb.Text == '':
            self.hide_element(self.clrsearch_b)
        else:
            self.show_element(self.clrsearch_b)


    def clear_search(self, sender, args):
        """Clear search box."""
        self.search_tb.Text = ' '
        self.search_tb.Clear()
        self.search_tb.Focus()

class InputFormText(TemplateWindow):

    xaml_source = 'InputText.xaml'

    def _setup(self, **kwargs):
		self.hide_element(self.clrsearch_b)
		self.clear_search(None, None)
		self.search_tb.Focus()
		
		button_name = kwargs.get('button_name', None)
		if button_name:
			self.select_b.Content = button_name
		
		head = kwargs.get('head', None)
		if head:
			self.head.Text = head
		

    def button_select(self, sender, args):
        """Handle select button click."""
        if self.search_tb.Text:
            self.response = self.search_tb.Text
        else:
            self.response = None
        self.Close()

    def search_txt_changed(self, sender, args):
        """Handle text change in search box."""
        if self.search_tb.Text == '':
            self.hide_element(self.clrsearch_b)
        else:
            self.show_element(self.clrsearch_b)


    def clear_search(self, sender, args):
        """Clear search box."""
        self.search_tb.Text = ' '
        self.search_tb.Clear()
        self.search_tb.Focus()

class CopyUserView(TemplateWindow):

	xaml_source = 'CopyUser.xaml'
	
	def _setup(self, **kwargs):
		self.hide_element(self.clrpurpose_b)
		self.hide_element(self.clrprefix_b)
		self.clear_purpose(None, None)
		self.clear_prefix(None, None)
		self.purpose.Focus()
		

		button_name = kwargs.get('button_name', None)
		if button_name:
			self.select_b.Content = button_name
		


	def button_select(self, sender, args):
		if self.prefix.Text:
			prefix = self.prefix.Text
		else:
			return
		if self.purpose.Text:
			purpose = self.purpose.Text
		else:
			return
		self.response = {"prefix": prefix,
						"purpose": purpose,
						"suffix": ''}
		self.Close()

	def purpose_txt_changed(self, sender, args):
		"""Handle text change in search box."""
		if self.purpose.Text == '':
			self.hide_element(self.clrpurpose_b)
		else:
			self.show_element(self.clrpurpose_b)
	
	def prefix_txt_changed(self, sender, args):
		"""Handle text change in search box."""
		if self.prefix.Text == '':
			self.hide_element(self.clrprefix_b)
		else:
			self.show_element(self.clrprefix_b)

	def clear_purpose(self, sender, args):
		"""Clear search box."""
		self.purpose.Text = ''
		self.purpose.Clear()
		self.purpose.Focus
		
	def clear_prefix(self, sender, args):
		"""Clear search box."""
		self.prefix.Text = ''
		self.prefix.Clear()
		self.prefix.Focus


class ReserveProjectForm(TemplateWindow):
	xaml_source = 'ReserveProject.xaml'

	def _setup(self, **kwargs):
		self.hide_element(self.clrsearch_b)
		self.clear_search(None, None)
		self.search_tb.Focus()
		
		button_name = kwargs.get('button_name', None)
		if button_name:
			self.select_b.Content = button_name
		
		head = kwargs.get('head', None)
		if head:
			self.head.Text = head

		default_folder = kwargs.get('folder', None)
		if default_folder:
			self.hasFolder = True
			self.dir_name.Text = default_folder
		else:
			self.hasFolder = False
		
	def pick_folder(self, sender, args):
		"""Pick folder."""
		folderBrowserDialog = FolderBrowserDialog()
		folderBrowserDialog.Description = "Выберите папку для сохранения резервной копии."
		folderBrowserDialog.ShowNewFolderButton = True

		if folderBrowserDialog.ShowDialog() == DialogResult.OK:
			folderName = folderBrowserDialog.SelectedPath
			self.dir_name.Text = folderName
			self.hasFolder = True
			# self.dir_name.Foreground = Brush.SolidColorBrush(Colors.Black)

		

	def button_select(self, sender, args):
		"""Handle select button click."""
		if self.hasFolder:
			res = {}
			if self.search_tb.Text:
				res["suffix"] = self.search_tb.Text
			else:
				res["suffix"] = None

			res["folder"] = self.dir_name.Text
			self.response = res
			self.Close()
		# else:
			# self.dir_name.Foreground = Brush.SolidColorBrush(Colors.Red)

	def search_txt_changed(self, sender, args):
		"""Handle text change in search box."""
		if self.search_tb.Text == '':
			self.hide_element(self.clrsearch_b)
		else:
			self.show_element(self.clrsearch_b)


	def clear_search(self, sender, args):
		"""Clear search box."""
		self.search_tb.Text = ' '
		self.search_tb.Clear()
		self.search_tb.Focus()