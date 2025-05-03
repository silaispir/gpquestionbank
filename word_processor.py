import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTextEdit, QAction, 
                           QFileDialog, QFontDialog, QColorDialog, QToolBar)
from PyQt5.QtGui import QIcon, QTextCharFormat, QFont
from PyQt5.QtCore import Qt

class WordProcessor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        # Ana metin alanı
        self.textEdit = QTextEdit()
        self.setCentralWidget(self.textEdit)
        
        # Menü çubuğu oluşturma
        menubar = self.menuBar()
        
        # Dosya menüsü
        fileMenu = menubar.addMenu('Dosya')
        
        # Yeni dosya aksiyonu
        newAction = QAction('Yeni', self)
        newAction.setShortcut('Ctrl+N')
        newAction.triggered.connect(self.newFile)
        fileMenu.addAction(newAction)
        
        # Aç aksiyonu
        openAction = QAction('Aç', self)
        openAction.setShortcut('Ctrl+O')
        openAction.triggered.connect(self.openFile)
        fileMenu.addAction(openAction)
        
        # Kaydet aksiyonu
        saveAction = QAction('Kaydet', self)
        saveAction.setShortcut('Ctrl+S')
        saveAction.triggered.connect(self.saveFile)
        fileMenu.addAction(saveAction)
        
        # Biçim menüsü
        formatMenu = menubar.addMenu('Biçim')
        
        # Yazı tipi aksiyonu
        fontAction = QAction('Yazı Tipi', self)
        fontAction.triggered.connect(self.setFont)
        formatMenu.addAction(fontAction)
        
        # Renk aksiyonu
        colorAction = QAction('Renk', self)
        colorAction.triggered.connect(self.setTextColor)
        formatMenu.addAction(colorAction)
        
        # Araç çubuğu
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        # Araç çubuğuna aksiyonları ekle
        toolbar.addAction(newAction)
        toolbar.addAction(openAction)
        toolbar.addAction(saveAction)
        toolbar.addAction(fontAction)
        toolbar.addAction(colorAction)
        
        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle('Basit Kelime İşlemci')
        self.show()
    
    def newFile(self):
        self.textEdit.clear()
    
    def openFile(self):
        filename, _ = QFileDialog.getOpenFileName(self, 'Dosya Aç', '', 
                                                'Text Files (*.txt);;All Files (*)')
        if filename:
            with open(filename, 'r', encoding='utf-8') as file:
                self.textEdit.setText(file.read())
    
    def saveFile(self):
        filename, _ = QFileDialog.getSaveFileName(self, 'Dosya Kaydet', '', 
                                                'Text Files (*.txt);;All Files (*)')
        if filename:
            with open(filename, 'w', encoding='utf-8') as file:
                file.write(self.textEdit.toPlainText())
    
    def setFont(self):
        font, ok = QFontDialog.getFont()
        if ok:
            self.textEdit.setFont(font)
    
    def setTextColor(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.textEdit.setTextColor(color)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = WordProcessor()
    sys.exit(app.exec_()) 