import sys
import json
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QPushButton, QLineEdit, QTextEdit, 
                           QListWidget, QLabel, QMessageBox, QInputDialog,
                           QFileDialog, QComboBox)
from PyQt5.QtCore import Qt

class QuestionBank(QMainWindow):
    def __init__(self):
        super().__init__()
        self.questions = {}
        self.current_category = None
        self.initUI()
        
    def initUI(self):
        # Ana widget ve layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # Sol panel - Kategoriler ve sorular listesi
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Kategori işlemleri
        category_layout = QHBoxLayout()
        self.category_combo = QComboBox()
        self.category_combo.currentTextChanged.connect(self.category_changed)
        add_category_btn = QPushButton('Kategori Ekle')
        add_category_btn.clicked.connect(self.add_category)
        category_layout.addWidget(self.category_combo)
        category_layout.addWidget(add_category_btn)
        
        # Soru listesi
        self.question_list = QListWidget()
        self.question_list.itemClicked.connect(self.question_selected)
        
        left_layout.addLayout(category_layout)
        left_layout.addWidget(self.question_list)
        
        # Sağ panel - Soru detayları
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Soru başlığı
        self.question_title = QLineEdit()
        self.question_title.setPlaceholderText('Soru Başlığı')
        
        # Soru içeriği
        self.question_content = QTextEdit()
        self.question_content.setPlaceholderText('Soru İçeriği')
        
        # Cevap
        self.answer = QTextEdit()
        self.answer.setPlaceholderText('Cevap')
        
        # Butonlar
        button_layout = QHBoxLayout()
        save_btn = QPushButton('Kaydet')
        save_btn.clicked.connect(self.save_question)
        delete_btn = QPushButton('Sil')
        delete_btn.clicked.connect(self.delete_question)
        button_layout.addWidget(save_btn)
        button_layout.addWidget(delete_btn)
        
        right_layout.addWidget(self.question_title)
        right_layout.addWidget(self.question_content)
        right_layout.addWidget(self.answer)
        right_layout.addLayout(button_layout)
        
        # Ana layout'a panelleri ekle
        main_layout.addWidget(left_panel, 1)
        main_layout.addWidget(right_panel, 2)
        
        # Menü çubuğu
        menubar = self.menuBar()
        file_menu = menubar.addMenu('Dosya')
        
        save_action = file_menu.addAction('Kaydet')
        save_action.triggered.connect(self.save_to_file)
        
        load_action = file_menu.addAction('Yükle')
        load_action.triggered.connect(self.load_from_file)
        
        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle('Soru Bankası')
        self.show()
    
    def add_category(self):
        category, ok = QInputDialog.getText(self, 'Kategori Ekle', 'Kategori adı:')
        if ok and category:
            if category not in self.questions:
                self.questions[category] = []
                self.category_combo.addItem(category)
                self.category_combo.setCurrentText(category)
    
    def category_changed(self, category):
        self.current_category = category
        self.question_list.clear()
        if category in self.questions:
            for question in self.questions[category]:
                self.question_list.addItem(question['title'])
    
    def save_question(self):
        if not self.current_category:
            QMessageBox.warning(self, 'Uyarı', 'Lütfen önce bir kategori seçin!')
            return
            
        title = self.question_title.text()
        content = self.question_content.toPlainText()
        answer = self.answer.toPlainText()
        
        if not title or not content or not answer:
            QMessageBox.warning(self, 'Uyarı', 'Tüm alanları doldurun!')
            return
        
        question = {
            'title': title,
            'content': content,
            'answer': answer
        }
        
        # Eğer aynı başlıkta soru varsa güncelle, yoksa yeni ekle
        found = False
        for i, q in enumerate(self.questions[self.current_category]):
            if q['title'] == title:
                self.questions[self.current_category][i] = question
                found = True
                break
        
        if not found:
            self.questions[self.current_category].append(question)
            self.question_list.addItem(title)
        
        self.clear_fields()
    
    def delete_question(self):
        current_item = self.question_list.currentItem()
        if not current_item:
            return
            
        title = current_item.text()
        for i, question in enumerate(self.questions[self.current_category]):
            if question['title'] == title:
                del self.questions[self.current_category][i]
                break
        
        self.question_list.takeItem(self.question_list.row(current_item))
        self.clear_fields()
    
    def question_selected(self, item):
        title = item.text()
        for question in self.questions[self.current_category]:
            if question['title'] == title:
                self.question_title.setText(question['title'])
                self.question_content.setPlainText(question['content'])
                self.answer.setPlainText(question['answer'])
                break
    
    def clear_fields(self):
        self.question_title.clear()
        self.question_content.clear()
        self.answer.clear()
    
    def save_to_file(self):
        filename, _ = QFileDialog.getSaveFileName(self, 'Kaydet', '', 'JSON Files (*.json)')
        if filename:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.questions, f, ensure_ascii=False, indent=4)
    
    def load_from_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, 'Yükle', '', 'JSON Files (*.json)')
        if filename:
            with open(filename, 'r', encoding='utf-8') as f:
                self.questions = json.load(f)
                self.category_combo.clear()
                self.category_combo.addItems(self.questions.keys())
                if self.questions:
                    self.category_combo.setCurrentIndex(0)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = QuestionBank()
    sys.exit(app.exec_()) 