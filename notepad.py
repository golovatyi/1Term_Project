import ctypes
import configparser
import os
import sys

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5.QtPrintSupport import QPrintPreviewDialog
from PyQt5.QtPrintSupport import QPrinter


CONFIG_FILE_PATH = "notepad.ini"

ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("notepad")
QtCore.QTextCodec.setCodecForLocale(QtCore.QTextCodec.codecForName("utf-8"))


class Notepad(QtWidgets.QMainWindow):

    def __init__(self):
        self.judgeConfig()
        self.cur_file = ''
        self.default_dir = ''
        self.clipboard = QtWidgets.QApplication.clipboard()
        self.last_search = ''
        self.font_family = 'Consolas'
        self.font_size = '16'
        self.font_bold = 'False'
        self.font_italic = 'False'
        self.font_strikeOut = 'False'
        self.font_underline = 'False'
        self.config = configparser.ConfigParser()
        self.config.read(CONFIG_FILE_PATH, 'utf-8')
        super(QtWidgets.QMainWindow, self).__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Без названия - Блокнот')
        self.setWindowIcon(QtGui.QIcon('resource/notepad.png'))
        self.statusBar().showMessage('Ready')
        self.createEditText()
        self.createActions()
        self.createMenubar()
        self.createToolbar()
        self.readSettings()
        self.cutAction.setEnabled(False)
        self.copyAction.setEnabled(False)
        self.undoAction.setEnabled(False)
        self.redoAction.setEnabled(False)
        self.text.copyAvailable.connect(self.cutAction.setEnabled)
        self.text.copyAvailable.connect(self.copyAction.setEnabled)
        self.text.undoAvailable.connect(self.undoAction.setEnabled)
        self.text.redoAvailable.connect(self.redoAction.setEnabled)
        self.text.textChanged.connect(self.findEnable)

    def findEnable(self):

        if self.text.toPlainText():
            self.findAction.setEnabled(True)
        else:
            self.findAction.setEnabled(False)
            self.findNextAction.setEnabled(False)

    def createEditText(self):
        self.text = QtWidgets.QPlainTextEdit()
        self.text.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.text.customContextMenuRequested.connect(self.showContextMenu)
        self.setCentralWidget(self.text)

    def showContextMenu(self):
        menu = QtWidgets.QMenu(self)
        menu.addAction(self.undoAction)
        menu.addAction(self.redoAction)
        menu.addSeparator()
        menu.addAction(self.cutAction)
        menu.addAction(self.copyAction)
        menu.addAction(self.pasteAction)
        menu.addSeparator()
        menu.addAction(self.selectAllAction)
        menu.exec_(QtGui.QCursor.pos())


    def judgeConfig(self):

        if not os.path.exists(CONFIG_FILE_PATH):
            f = open(CONFIG_FILE_PATH, 'w', encoding='utf-8')
            f.close()

    def readSettings(self):
        # регулировка размера окна
        width = self.getConfig('Display', 'width', 800)
        height = self.getConfig('Display', 'height ', 600)
        px = self.getConfig('Display', 'x', 0)
        py = self.getConfig('Display', 'y', 0)
        self.move(int(px), int(py))
        self.resize(int(width), (height))

        self.default_dir = self.getConfig('Setting', 'dir', '')

        self.font_family = self.getConfig('Font', 'family', 'Consolas')
        self.font_size = self.getConfig('Font', 'size', '10')
        self.font_bold = self.getConfig('Font', 'bold', '0')
        self.font_italic = self.getConfig('Font', 'italic', '0')
        self.font_strikeOut = self.getConfig('Font', 'strikeOut', '0')
        self.font_underline = self.getConfig('Font', 'underline', '0')
        font = QtGui.QFont(self.font_family, int(self.font_size))
        font.setBold(int(self.font_bold))
        font.setItalic(int(self.font_italic))
        font.setStrikeOut(int(self.font_strikeOut))
        font.setUnderline(int(self.font_underline))
        self.text.setFont(font)

    def writeSetting(self):

        self.writeConfig('Display', 'width', str(self.size().width()))
        self.writeConfig('Display', 'height', str(self.size().height()))
        self.writeConfig('Display', 'x', str(self.pos().x()))
        self.writeConfig('Display', 'y', str(self.pos().y()))

        self.writeConfig('Setting', 'dir', self.default_dir)

        self.writeConfig('Font', 'family', self.text.font().family())
        self.writeConfig('Font', 'size', str(self.text.font().pointSize()))
        self.writeConfig('Font', 'bold', int(self.text.font().bold()))
        self.writeConfig('Font', 'italic', int(self.text.font().italic()))
        self.writeConfig('Font', 'strikeOut', int(
            self.text.font().strikeOut()))
        self.writeConfig('Font', 'underline', int(
            self.text.font().underline()))


        self.config.write(open(CONFIG_FILE_PATH, 'w', encoding='utf-8'))

    def createMenubar(self):
        fileMenu = QtWidgets.QMenu('ФАЙЛ', self)
        fileMenu.addAction(self.newAction)
        fileMenu.addAction(self.openAction)
        fileMenu.addAction(self.saveAction)
        fileMenu.addAction(self.saveAsAction)
        fileMenu.addSeparator()
        fileMenu.addAction(self.printAction)
        fileMenu.addAction(self.printReviewAction)
        fileMenu.addSeparator()
        fileMenu.addAction(self.quitAction)
        editMenu = QtWidgets.QMenu('РЕДАКТИРОВАТЬ', self)
        editMenu.addAction(self.undoAction)
        editMenu.addAction(self.redoAction)
        editMenu.addSeparator()
        editMenu.addAction(self.cutAction)
        editMenu.addAction(self.copyAction)
        editMenu.addAction(self.pasteAction)
        editMenu.addSeparator()


        self.findAction.setEnabled(False)
        self.findNextAction.setEnabled(False)

        editMenu.addAction(self.findAction)
        editMenu.addAction(self.findNextAction)
        editMenu.addAction(self.replaceAction)

        styleMenu = QtWidgets.QMenu('ФОРМАТ', self)
        styleMenu.addAction(self.lineWrapAction)
        styleMenu.addAction(self.fontAction)
        helpMenu = QtWidgets.QMenu('ПОМОЩЬ', self)
        helpMenu.addAction(self.aboutAction)

        self.menuBar().addMenu(fileMenu)
        self.menuBar().addMenu(editMenu)
        self.menuBar().addMenu(styleMenu)
        self.menuBar().addMenu(helpMenu)

    def createToolbar(self):
        toolbar = self.addToolBar('показать меню')
        toolbar.addAction(self.newAction)
        toolbar.addAction(self.openAction)
        toolbar.addAction(self.saveAction)
        toolbar.addSeparator()
        toolbar.addAction(self.cutAction)
        toolbar.addAction(self.copyAction)
        toolbar.addAction(self.pasteAction)

    def createActions(self):
        self.undoAction = QtWidgets.QAction(QtGui.QIcon(
            'resource/undo.png'), "ОТМЕНИТЬ", self, shortcut=QtGui.QKeySequence.Undo, statusTip="ОТМЕНИТЬ ПОСЛЕДНЕЕ ДЕЙСТВИЕ", triggered=self.text.undo)
        self.redoAction = QtWidgets.QAction(QtGui.QIcon(
            'resource/redo.png'), 'ВЕРНУТЬ', self, shortcut=QtGui.QKeySequence.Redo, statusTip='ВЕРНУТЬ ОТМЕНЕННОЕ ДЕЙСТВИЕ', triggered=self.text.redo)
        self.cutAction = QtWidgets.QAction(QtGui.QIcon(
            'resource/cut.png'), "ВЫРЕЗАТЬ", self, shortcut=QtGui.QKeySequence.Cut, statusTip="ВЫРЕЗАТЬ", triggered=self.text.cut)
        self.copyAction = QtWidgets.QAction(QtGui.QIcon(
            'resource/copy.png'), "КОПИРОВАТЬ", self, shortcut=QtGui.QKeySequence.Copy, statusTip="КОПИРОВАТЬ В БУФЕР ОБМЕНА", triggered=self.text.copy)
        self.pasteAction = QtWidgets.QAction(QtGui.QIcon(
            'resource/paste.png'), "ВСТАВИТЬ", self, shortcut=QtGui.QKeySequence.Paste, statusTip="ВСТАВИТЬ ИЗ БУФЕРА ОБМЕНА", triggered=self.text.paste)
        self.selectAllAction = QtWidgets.QAction(QtGui.QIcon(
            'resource/SelectAll.png'), "ВЫБРАТЬ ВСЁ", self, shortcut=QtGui.QKeySequence.SelectAll, statusTip="ВЫБРАТЬ ВСЁ", triggered=self.text.selectAll)
        self.newAction = QtWidgets.QAction(QtGui.QIcon(
            'resource/new.png'), 'НОВЫЙ', self, shortcut=QtGui.QKeySequence.New, statusTip='НОВЫЙ ФАЙЛ', triggered=self.newFile)
        self.openAction = QtWidgets.QAction(QtGui.QIcon(
            'resource/open.png'), 'ОТКРЫТЬ', self, shortcut=QtGui.QKeySequence.Open, statusTip='ОТКРЫТЬ ФАЙЛ', triggered=self.openFile)
        self.saveAction = QtWidgets.QAction(QtGui.QIcon(
            'resource/save.png'), 'СОХРАНИТЬ', self, shortcut=QtGui.QKeySequence.Save, statusTip='СОХРАНИТЬ ФАЙЛ', triggered=self.saveFile)
        self.saveAsAction = QtWidgets.QAction(QtGui.QIcon(
            'resource/save.png'), 'СОХРАНИТЬ КАК', self, shortcut=QtGui.QKeySequence.SaveAs, statusTip='СОХРАНИТЬ ФАЙЛ', triggered=self.saveAsFile)
        self.quitAction = QtWidgets.QAction(QtGui.QIcon(
            'resource/exit.png'), 'ВЫХОД', self, shortcut="Ctrl+Q", statusTip='ЗАКРЫТЬ ПРОГРАММУ', triggered=self.close)
        self.lineWrapAction = QtWidgets.QAction(QtGui.QIcon(
            'resource/check.png'), 'ПРОВЕРИТЬ', self, triggered=self.setLineWrap)
        self.fontAction = QtWidgets.QAction(QtGui.QIcon(
            'resource/font.png'), 'ШРИФТ', self, statusTip='ИЗМЕНЕНИЕ ШРИФТА', triggered=self.setFont)
        self.aboutAction = QtWidgets.QAction(QtGui.QIcon(
            'resource/about.png'), 'О ПРОГРАММЕ', self, statusTip='О ПРОГРАММЕ', triggered=self.about)
        self.findAction = QtWidgets.QAction(QtGui.QIcon(
            'resource/find.png'), 'НАЙТИ', self, statusTip='НАЙТИ', shortcut='Ctrl+F', triggered=self.findText)
        self.findNextAction = QtWidgets.QAction(QtGui.QIcon(
            'resource/find.png'), 'НАЙТИ ДАЛЕЕ', self, statusTip='НАЙТИ ДАЛЕЕ', shortcut='F3', triggered=self.searchText)
        self.replaceAction = QtWidgets.QAction(QtGui.QIcon(
            'resource/replace.png'), 'ЗАМЕНИТЬ', self, statusTip='ЗАМЕНИТЬ', shortcut='Ctrl+H', triggered=self.replace)
        self.printAction = QtWidgets.QAction(QtGui.QIcon(
            'resource/print.png'), 'ПЕЧАТЬ', self, statusTip='ПЕЧАТЬ', shortcut='Ctrl+P', triggered=self.printDocument)
        self.printReviewAction = QtWidgets.QAction(QtGui.QIcon(
            'resource/print.png'), 'ПРЕДВАРИТЕЛЬНЫЙ ПРОСМОТР', self, statusTip='ПРЕДВАРИТЕЛЬНЫЙ ПРОСМОТР', triggered=self.printReview)



    def closeEvent(self, event):
        if self.maybeSave():

            self.writeSetting()
            event.accept()
        else:
            event.ignore()

    def newFile(self):
        if self.maybeSave():
            self.text.clear()

    def openFile(self):
        if self.maybeSave():
            filename, _ = QtWidgets.QFileDialog.getOpenFileName(
                self, '', self.default_dir, 'Текст (*.txt);;Все файлы(*.*)')
            file = QtCore.QFile(filename)
            if not file.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text):
                return
            inf = QtCore.QTextStream(file)
            self.text.setPlainText(inf.readAll())
            self.setCurrentFile(filename)

    def saveFile(self):
        if not self.cur_file:
            return self.saveAsFile()
        writer = QtGui.QTextDocumentWriter(self.cur_file)
        success = writer.write(self.text.document())
        self.setCurrentFile(self.cur_file)
        if success:
            self.statusBar().showMessage('Сохранено', 1000)
        return success

    def saveAsFile(self):
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, '', self.default_dir + 'Без названия', 'текст (*.txt);;Все файлы(*.*)')

        if not filename:
            return False
        self.setCurrentFile(filename)
        return self.saveFile()

    def getConfig(self, section, key, default):

        try:
            return self.config[section][key]
        except:
            return default

    def findText(self):
        self.find_dialog = QtWidgets.QDialog(self)
        self.find_dialog.setWindowTitle('Найти')
        search_label = QtWidgets.QLabel('Найти：')
        self.search_text = QtWidgets.QLineEdit(self.last_search)
        search_label.setBuddy(self.search_text)
        self.search_btn = QtWidgets.QPushButton('Найти далее')
        self.search_btn.setDefault(True)

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(search_label)
        layout.addWidget(self.search_text)
        layout.addWidget(self.search_btn)

        self.search_btn.clicked.connect(self.searchText)
        self.find_dialog.setLayout(layout)
        self.find_dialog.show()

    def searchText(self):
        cursor = self.text.textCursor()
        start = cursor.anchor()
        text = self.search_text.text()
        self.last_search = text

        if self.last_search:
            self.findNextAction.setEnabled(True)
        text_len = len(text)
        context = self.text.toPlainText()

        index = context.find(text, start)
        if -1 == index:
            QtWidgets.QMessageBox.information(
                self.find_dialog, 'Блокнот', 'Не найдено\"%s\"' % text)
        else:
            start = index
            cursor = self.text.textCursor()
            cursor.clearSelection()
            cursor.movePosition(QtGui.QTextCursor.Start,
                                QtGui.QTextCursor.MoveAnchor)

            cursor.movePosition(QtGui.QTextCursor.Right,
                                QtGui.QTextCursor.MoveAnchor, start + text_len)

            cursor.movePosition(QtGui.QTextCursor.Left,
                                QtGui.QTextCursor.KeepAnchor, text_len)
            cursor.selectedText()
            self.text.setTextCursor(cursor)



    def replaceText(self):
        cursor = self.text.textCursor()
        start = cursor.anchor()
        text = self.search_text.text()
        text_len = len(text)
        context = self.text.toPlainText()
        index = context.find(text, start)
        sender = self.sender()

        if sender is self.replace_button:
            if text == cursor.selectedText():
                position = cursor.anchor()
                cursor.removeSelectedText()
                replace_text = self.replace_text.text()
                cursor.insertText(replace_text)

                self.replaceText()
                return
        if -1 == index:
            QtWidgets.QMessageBox.information(
                self.replace_dialog, 'Блокнот', 'Не найдено\"%s\"' % text)
        else:
            start = index
            cursor = self.text.textCursor()
            cursor.clearSelection()
            cursor.movePosition(QtGui.QTextCursor.Start,
                                QtGui.QTextCursor.MoveAnchor)
            cursor.movePosition(QtGui.QTextCursor.Right,
                                QtGui.QTextCursor.MoveAnchor, start + text_len)
            cursor.movePosition(QtGui.QTextCursor.Left,
                                QtGui.QTextCursor.KeepAnchor, text_len)
            cursor.selectedText()
            self.text.setTextCursor(cursor)

    def replaceAll(self):
        context = self.text.toPlainText()
        search_word = self.search_text.text()
        replace_word = self.replace_text.text()
        new_context = context.replace(search_word, replace_word)
        doc = self.text.document()
        curs = QtGui.QTextCursor(doc)

        curs.select(QtGui.QTextCursor.Document)

        curs.insertText(new_context)

    def printDocument(self):

        document = self.text.document()
        printer = QPrinter()
        dlg = QPrintPreviewDialog(printer, self)
        if dlg.exec_() != QtWidgets.QDialog.Accepted:
            return
        document.print_(printer)
        self.statusBar().showMessage("Печать успешна", 2000)

    def printReview(self):
        printer = QPrinter(QPrinter.HighResolution)
        review = QPrintPreviewDialog(printer, self)
        review.setWindowFlags(QtCore.Qt.Window)
        review.paintRequested.connect(self.print)
        review.exec_()

    def print(self, printer):
        self.text.print_(printer)

    def replace(self):
        self.replace_dialog = QtWidgets.QDialog(self)
        self.replace_dialog.setWindowTitle('Заменить')
        search_label = QtWidgets.QLabel('Поиск текста：')
        self.search_text = QtWidgets.QLineEdit()
        search_label.setBuddy(self.search_text)
        replace_label = QtWidgets.QLabel('Заменить на：')

        self.replace_text = QtWidgets.QLineEdit()
        replace_label.setBuddy(self.replace_text)
        self.find_button = QtWidgets.QPushButton('Найти далее')
        self.replace_button = QtWidgets.QPushButton('Заменить')
        self.replace_all_button = QtWidgets.QPushButton('Заменить всё')

        self.replace_button.setEnabled(False)
        self.replace_all_button.setEnabled(False)

        self.find_button.clicked.connect(self.replaceText)
        self.replace_button.clicked.connect(self.replaceText)
        self.replace_all_button.clicked.connect(self.replaceAll)
        self.search_text.textChanged.connect(self.replaceEnable)

        layout = QtWidgets.QGridLayout()
        layout.addWidget(search_label, 0, 0)
        layout.addWidget(self.search_text, 0, 1)
        layout.addWidget(self.find_button, 0, 2)
        layout.addWidget(replace_label, 1, 0)
        layout.addWidget(self.replace_text, 1, 1)
        layout.addWidget(self.replace_button, 1, 2)
        layout.addWidget(self.replace_all_button, 2, 2)
        self.replace_dialog.setLayout(layout)
        self.replace_dialog.show()

    def replaceEnable(self):
        if not self.search_text.text():
            self.replace_button.setEnabled(False)
            self.replace_all_button.setEnabled(False)
        else:
            self.replace_button.setEnabled(True)
            self.replace_all_button.setEnabled(True)

    def maybeSave(self):

        if self.text.document().isModified():
            alert = QtWidgets.QMessageBox(self)
            alert.setWindowTitle('Блокнот')
            alert.setText('Сохранить изменения %s ？' % self.cur_file)
            saveButton = alert.addButton(
                'Да', QtWidgets.QMessageBox.ActionRole)
            unSaveButton = alert.addButton(
                'Нет', QtWidgets.QMessageBox.ActionRole)
            cancelButton = alert.addButton(
                'Отмена', QtWidgets.QMessageBox.ActionRole)
            alert.exec_()

            ret = alert.clickedButton()
            if ret == saveButton:
                return self.saveFile()
            elif ret == unSaveButton:
                return True
            elif ret == cancelButton:
                return False
        return True

    def about(self):
        QtWidgets.QMessageBox.about(
            self, 'О программе', r'<h2>КП по ОП</h2><p> <b>Выполнил студент</b> <br> <b>Группы P3175</b> <br>Головатый А.Д. <br>при использовании PYQT5 и Python3.4</p>')

    def setLineWrap(self):
        if not self.text.lineWrapMode():
            self.text.setLineWrapMode(QtWidgets.QPlainTextEdit.WidgetWidth)
            self.lineWrapAction.setIcon(QtGui.QIcon('resource/check.png'))
        else:
            self.text.setLineWrapMode(QtWidgets.QPlainTextEdit.NoWrap)
            self.lineWrapAction.setIcon(QtGui.QIcon(''))

    def setFont(self):

        font, ok = QtWidgets.QFontDialog.getFont(self.text.font(), self, 'Выбор шрифта')
        if ok:
            self.text.setFont(QtGui.QFont(font))

    def setCurrentFile(self, filename):
        self.cur_file = filename
        path, _ = os.path.split(filename)
        self.default_dir = path + '/'
        if not filename:
            self.setWindowTitle('Без названия - Блокнот')
        else:
            self.setWindowTitle('%s - Блокнот' % filename)
        self.text.document().setModified(False)

    def writeConfig(self, section, key, value):

        if not self.config.has_section(section):
            self.config.add_section(section)

        self.config.set(section, key, str(value))


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    if len(sys.argv) > 1:
        locale = sys.argv[1]
    else:
        locale = QtCore.QLocale.system().name()

    notepad = Notepad()
    notepad.show()
    app.exec_()

  
