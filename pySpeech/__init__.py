# -*- coding: utf-8 -*-
import clr
clr.AddReference("System.Windows.Forms")
from System.Windows.Forms import MessageBox


def alert(msg):
	MessageBox.Show(msg)
def AlbumFilter(x, album):
	if x is None: return 0
	if album is None: return 0
	parameter = x.LookupParameter("Альбом")
	if parameter is None: return 0
	
	if parameter.AsString()==album:
		return 1
	else:
		return 0
#Получение числа из строки
def ClearString(msg): 
	number=""
	for i in range(len(msg)):
		if msg[i].isdigit():
			number+=msg[i]
	return number
#Получаем число для сравнения из строки вида "str-num.num"
def GetNumber(list):
	first = ClearString(list[0])
	first = float(first)
	if len(list)>1:
		first+=1-0.5/float(list[1]) if list[1]>0 else 0.6
	return first
	
def FormNum(album, start, count):
	res = []
	for i in range(count):
		num = album+"-"+str(start+i)
		res.append(num)
	return res