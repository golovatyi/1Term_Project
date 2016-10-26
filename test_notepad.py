from notepad import Notepad


import ctypes
import os
import sys

import PyQt5
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5.QtPrintSupport import QPrinter


import unittest
from unittest.mock import MagicMock


CONFIG_FILE_PATH = 'notepad.ini'

ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("notepad")
QtCore.QTextCodec.setCodecForLocale(QtCore.QTextCodec.codecForName("utf-8"))


app = QtWidgets.QApplication(sys.argv)



class TestNotepad(unittest.TestCase):

    def setUp(self):
        self.widget = Notepad()


    def tearDown(self):
        self.widget.close()

    def test_defaults(self):
        self.widget.show()
        assert self.widget.windowTitle() == 'Без названия - Блокнот'
        self.widget.resize(500, 500)
        self.assertEqual(self.widget.size(), PyQt5.QtCore.QSize(500, 500) )
        self.widget.text.appendPlainText('')
        assert self.widget.findAction.isEnabled() is False
        assert self.widget.findNextAction.isEnabled() is False
        assert self.widget.undoAction.isEnabled() is False
        assert self.widget.redoAction.isEnabled() is False
        assert self.widget.cutAction.isEnabled() is False
        assert self.widget.copyAction.isEnabled() is False
        assert self.widget.pasteAction.isEnabled() is True
        assert self.widget.selectAllAction.isEnabled() is True
        self.widget.close()


    def test_find_enable(self):

        print('Нажмите да и сохрани файл как test.txt в директории проекта')
        self.widget.text.appendPlainText('abc')

        assert self.widget.findAction.isEnabled() is True
        assert self.widget.findNextAction.isEnabled() is False

    def test_correctRead(self):
        f = open('test.txt')
        a = f.read()
        assert a == 'abc'


    def test_showContextMenu_defaults(self):
        print('нажмите на произвольную точку меню, затем на панели задач')
        self.widget.showContextMenu()




    def test_judgeConfig(self):
        os.remove('notepad.ini')
        assert self.widget.judgeConfig() is None
        assert os.path.exists(CONFIG_FILE_PATH)

    def test_closeEvent(self):
        pass



    def test_newFile(self):
        #мокаем лишнии функции т показываем, что
        # в ф-и newfile нет багов
        self.widget.maybeSave = MagicMock(return_value=False)
        assert self.widget.newFile() is None
        self.widget.maybeSave = MagicMock(return_value=True)
        assert self.widget.newFile() is None

        self.text = self.widget.text
        writer = QtGui.QTextDocumentWriter(self.widget.cur_file)
        success = writer.write(self.text.document())
        self.widget.saveFile = MagicMock(return_value=success)
        self.widget.maybeSave = MagicMock(return_value=self.widget.saveFile())
        assert self.widget.newFile() is None
        assert self.text.isVisible() is False


    def test_openFile(self):
        print('открой файл test_openfile.txt')
        self.widget.maybeSave = MagicMock(return_value=False)
        assert self.widget.openFile() is None
        self.widget.maybeSave = MagicMock(return_value=True)
        assert self.widget.openFile() is None
        assert self.widget.cur_file == 'D:/Рабочий Стол/Курсач ОП - копия/test_openfile.txt'
        assert self.widget.windowTitle() == 'D:/Рабочий Стол/Курсач ОП - копия/test_openfile.txt - Блокнот'

    def test_saveFile(self):
        print('сохраните файл как test_saveFile.txt')
        assert self.widget.saveFile() is True
        assert self.widget.cur_file == 'D:/Рабочий Стол/Курсач ОП - копия/test_saveFile.txt'

    def test_unsaveAction(self):
        print('нажмите отмена')
        assert self.widget.saveFile() is False



    def test_findText(self):
        self.widget.findText()
        assert self.widget.find_dialog.windowTitle() == 'Найти'
        assert self.widget.search_btn.isDefault() is True
        assert 'PyQt5.QtWidgets.QHBoxLayout' in str(self.widget.find_dialog.layout())
        self.widget.search_btn.click()

    def test_searchText(self):
        self.widget.last_search = MagicMock(return_value=None)
        assert self.widget.findNextAction.isEnabled() is False

    def test_replaceText(self):
        self.widget.findText()
        self.widget.replace()

        self.widget.sender = MagicMock(return_value=self.widget.search_btn)
        self.widget.replaceText()
        assert self.widget.replaceText() is None

        self.find = MagicMock(return_value=-1)
        self.widget.replaceText()
        assert self.widget.replaceText() is None


        self.widget.sender = MagicMock(self.widget.find_button)
        self.widget.replaceText()



    def test_replaceAll(self):

        self.widget.findText()
        self.widget.replace()
        self.widget.replaceText()

        assert self.widget.replaceAll() is None


    def test_printDocument(self):
        print('закройте диалог')
        self.widget.printDocument()

    def test_printReview(self):
        print('закройте диалог')
        self.widget.printReview()

    def test_print(self):
        print('закройте диалог')
        self.widget.print(QPrinter(QPrinter.HighResolution))

    def test_replaceEnable(self):
        self.widget.replace()
        self.widget.search_text.text = MagicMock(return_value=None)
        assert self.widget.replace_button.isEnabled() is False
        assert self.widget.replace_all_button.isEnabled() is False


    def test_replaceEnable2(self):
        self.widget.replace()
        self.widget.search_text.text = MagicMock(return_value='abc')
        self.widget.replaceEnable()
        assert self.widget.replace_button.isEnabled() is True
        assert self.widget.replace_all_button.isEnabled() is True

    def test_maybeSave(self):
        assert self.widget.maybeSave() is True
        self.widget.text.appendPlainText('zte')
        print('нажмите нет')
        assert self.widget.maybeSave() is True
        print('нажмите отмена')
        assert self.widget.maybeSave() is False

    def test_setFont(self):
        print('нажмите ОК')
        self.widget.setFont()



if __name__ == '__main__':

    unittest.main()
