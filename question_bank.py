import sys
import json
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                           QPushButton, QLineEdit, QTextEdit, QListWidget, QLabel,
                           QMessageBox, QInputDialog, QFileDialog, QComboBox, QGroupBox,
                           QRadioButton, QButtonGroup)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch
from reportlab.lib import colors

class QuestionBankApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.questions = {}
        self.current_category = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Soru Bankası Uygulaması')
        self.setWindowIcon(QIcon('icon.png'))
        self.setGeometry(100, 100, 900, 650)

        # Ana widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Sol panel - Kategoriler ve sorular
        left_panel = QGroupBox("Kategoriler ve Sorular")
        left_panel.setStyleSheet("QGroupBox { font-weight: bold; }")
        left_layout = QVBoxLayout(left_panel)

        # Kategori işlemleri
        category_layout = QHBoxLayout()
        self.category_combo = QComboBox()
        self.category_combo.setStyleSheet("QComboBox { padding: 5px; }")
        self.category_combo.currentTextChanged.connect(self.load_questions)
        
        add_category_btn = QPushButton('+')
        add_category_btn.setToolTip('Yeni kategori ekle')
        add_category_btn.setFixedWidth(30)
        add_category_btn.clicked.connect(self.add_category)
        
        remove_category_btn = QPushButton('-')
        remove_category_btn.setToolTip('Kategoriyi sil')
        remove_category_btn.setFixedWidth(30)
        remove_category_btn.clicked.connect(self.remove_category)
        
        category_layout.addWidget(self.category_combo, 5)
        category_layout.addWidget(add_category_btn, 1)
        category_layout.addWidget(remove_category_btn, 1)

        # Soru listesi
        self.question_list = QListWidget()
        self.question_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #ccc;
                padding: 5px;
                background-color: #f9f9f9;
            }
            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid #eee;
            }
            QListWidget::item:hover {
                background-color: #e0e0e0;
            }
            QListWidget::item:selected {
                background-color: #4CAF50;
                color: white;
            }
        """)
        self.question_list.itemClicked.connect(self.show_question)

        left_layout.addLayout(category_layout)
        left_layout.addWidget(QLabel("Sorular:"))
        left_layout.addWidget(self.question_list)

        # Sağ panel - Soru detayları
        right_panel = QGroupBox("Soru Detayları")
        right_panel.setStyleSheet("QGroupBox { font-weight: bold; }")
        right_layout = QVBoxLayout(right_panel)

        # Soru tipi seçimi
        self.question_type = QComboBox()
        self.question_type.addItems(["Klasik", "Çoktan Seçmeli"])
        self.question_type.currentIndexChanged.connect(self.change_question_type)

        # Soru başlığı ve içeriği
        self.question_title = QLineEdit(placeholderText="Soru Başlığı (Örnek: Matematik - Türev 1)")
        self.question_title.setStyleSheet("QLineEdit { padding: 8px; }")
        
        self.question_content = QTextEdit(placeholderText="Soru İçeriği (Soruyu detaylı yazın)")
        self.question_content.setStyleSheet("QTextEdit { padding: 8px; }")

        # Cevap alanı (dinamik)
        self.answer_widget = QWidget()
        self.answer_layout = QVBoxLayout(self.answer_widget)
        self.setup_classic_answer()

        # Butonlar
        btn_layout = QHBoxLayout()
        save_btn = QPushButton('Kaydet')
        save_btn.setStyleSheet("QPushButton { background-color: darkgreen; color: white; padding: 8px; }")
        save_btn.clicked.connect(self.save_question)
        
        delete_btn = QPushButton('Sil')
        delete_btn.setStyleSheet("QPushButton { background-color: darkred; color: white; padding: 8px; }")
        delete_btn.clicked.connect(self.delete_question)
        
        clear_btn = QPushButton('Temizle')
        clear_btn.setStyleSheet("QPushButton { background-color: blue; color: white; padding: 8px; }")
        clear_btn.clicked.connect(self.clear_fields)
        
        pdf_btn = QPushButton('PDF Oluştur')
        pdf_btn.setStyleSheet("QPushButton { background-color: deeppink; color: white; padding: 8px; }")
        pdf_btn.clicked.connect(self.export_to_pdf)

        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(delete_btn)
        btn_layout.addWidget(clear_btn)
        btn_layout.addWidget(pdf_btn)

        right_layout.addWidget(QLabel("Soru Tipi:"))
        right_layout.addWidget(self.question_type)
        right_layout.addWidget(QLabel("Soru Başlığı:"))
        right_layout.addWidget(self.question_title)
        right_layout.addWidget(QLabel("Soru İçeriği:"))
        right_layout.addWidget(self.question_content)
        right_layout.addWidget(QLabel("Cevap:"))
        right_layout.addWidget(self.answer_widget)
        right_layout.addLayout(btn_layout)

        # Ana layout
        main_layout.addWidget(left_panel, 1)
        main_layout.addWidget(right_panel, 2)

        # Menü çubuğu
        menubar = self.menuBar()
        menubar.setStyleSheet("""
            QMenuBar {
                background-color: #f0f0f0;
                padding: 5px;
            }
            QMenuBar::item {
                padding: 5px 10px;
                background: transparent;
            }
            QMenuBar::item:selected {
                background: #ddd;
            }
        """)
        
        file_menu = menubar.addMenu('Dosya')
        file_menu.addAction('Kaydet', self.save_to_file)
        file_menu.addAction('Yükle', self.load_from_file)
        file_menu.addAction('PDF Oluştur', self.export_to_pdf)

    def add_category(self):
        name, ok = QInputDialog.getText(self, "Yeni Kategori", "Kategori adı:")
        if ok and name:
            if name not in self.questions:
                self.questions[name] = []
                self.category_combo.addItem(name)
                self.category_combo.setCurrentText(name)
                QMessageBox.information(self, 'Başarılı', f'"{name}" kategorisi eklendi!')

    def remove_category(self):
        if not self.current_category:
            return
            
        reply = QMessageBox.question(
            self, 'Onay', 
            f'"{self.current_category}" kategorisini ve tüm sorularını silmek istediğinize emin misiniz?',
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            del self.questions[self.current_category]
            self.category_combo.removeItem(self.category_combo.currentIndex())
            self.question_list.clear()
            self.clear_fields()

    def load_questions(self, category):
        self.current_category = category
        self.question_list.clear()
        if category in self.questions:
            for q in self.questions[category]:
                self.question_list.addItem(q['title'])

    def change_question_type(self, index):
        if index == 0:  
            self.setup_classic_answer()
        else:  
            self.setup_multiple_choice()

    def setup_classic_answer(self):
        self.clear_layout(self.answer_layout)
        self.answer_text = QTextEdit(placeholderText="Cevap metnini yazın...")
        self.answer_text.setStyleSheet("QTextEdit { padding: 8px; }")
        self.answer_layout.addWidget(self.answer_text)

    def setup_multiple_choice(self):
        self.clear_layout(self.answer_layout)
        
        self.option_a = QLineEdit(placeholderText="A seçeneği")
        self.option_b = QLineEdit(placeholderText="B seçeneği")
        self.option_c = QLineEdit(placeholderText="C seçeneği")
        self.option_d = QLineEdit(placeholderText="D seçeneği")
        
        self.correct_option = QButtonGroup()
        rb_a = QRadioButton("A")
        rb_b = QRadioButton("B")
        rb_c = QRadioButton("C")
        rb_d = QRadioButton("D")
        
        self.correct_option.addButton(rb_a, 1)
        self.correct_option.addButton(rb_b, 2)
        self.correct_option.addButton(rb_c, 3)
        self.correct_option.addButton(rb_d, 4)
        
        
        options_layout = QVBoxLayout()
        options_layout.addWidget(QLabel("Seçenekler:"))
        
        for widget in [self.option_a, self.option_b, self.option_c, self.option_d]:
            widget.setStyleSheet("QLineEdit { padding: 5px; }")
            options_layout.addWidget(widget)
        
        options_layout.addWidget(QLabel("Doğru Cevap:"))
        
        rb_layout = QHBoxLayout()
        for rb in [rb_a, rb_b, rb_c, rb_d]:
            rb_layout.addWidget(rb)
        
        options_layout.addLayout(rb_layout)
        self.answer_layout.addLayout(options_layout)

    def clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def show_question(self, item):
        title = item.text()
        for q in self.questions[self.current_category]:
            if q['title'] == title:
                self.question_title.setText(q['title'])
                self.question_content.setPlainText(q['content'])
                self.question_type.setCurrentText(q['type'])
                
                if q['type'] == "Klasik":
                    self.answer_text.setPlainText(q['answer'])
                else:
                    options = q['answer']['options']
                    self.option_a.setText(options[0])
                    self.option_b.setText(options[1])
                    self.option_c.setText(options[2])
                    self.option_d.setText(options[3])
                    self.correct_option.button(q['answer']['correct']+1).setChecked(True)
                break

    def save_question(self):
        if not self.current_category:
            QMessageBox.warning(self, "Uyarı", "Önce bir kategori seçin!")
            return
            
        title = self.question_title.text()
        content = self.question_content.toPlainText()
        q_type = self.question_type.currentText()
        
        if not title or not content:
            QMessageBox.warning(self, "Uyarı", "Başlık ve içerik boş olamaz!")
            return
        
        if q_type == "Klasik":
            answer = self.answer_text.toPlainText()
            if not answer:
                QMessageBox.warning(self, "Uyarı", "Cevap boş olamaz!")
                return
            answer_data = answer
        else:
            options = [
                self.option_a.text(),
                self.option_b.text(),
                self.option_c.text(),
                self.option_d.text()
            ]
            if any(not opt for opt in options):
                QMessageBox.warning(self, "Uyarı", "Tüm seçenekleri doldurun!")
                return
            if not self.correct_option.checkedButton():
                QMessageBox.warning(self, "Uyarı", "Doğru cevabı seçin!")
                return
            answer_data = {
                'options': options,
                'correct': self.correct_option.checkedId()-1  # 0-3 arası
            }
        
       
        question = {
            'title': title,
            'content': content,
            'type': q_type,
            'answer': answer_data
        }
        
       
        updated = False
        for i, q in enumerate(self.questions[self.current_category]):
            if q['title'] == title:
                self.questions[self.current_category][i] = question
                updated = True
                break
        
        if not updated:
            self.questions[self.current_category].append(question)
            self.question_list.addItem(title)
        
        QMessageBox.information(self, "Başarılı", "Soru kaydedildi!")

    def delete_question(self):
        if not self.question_list.currentItem():
            QMessageBox.warning(self, "Uyarı", "Silinecek soru seçin!")
            return
            
        title = self.question_list.currentItem().text()
        reply = QMessageBox.question(
            self, "Onay", f"'{title}' silinsin mi?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            for i, q in enumerate(self.questions[self.current_category]):
                if q['title'] == title:
                    del self.questions[self.current_category][i]
                    break
            self.question_list.takeItem(self.question_list.currentRow())
            self.clear_fields()

    def clear_fields(self):
        self.question_title.clear()
        self.question_content.clear()
        if self.question_type.currentText() == "Klasik":
            self.answer_text.clear()
        else:
            self.option_a.clear()
            self.option_b.clear()
            self.option_c.clear()
            self.option_d.clear()
            self.correct_option.setExclusive(False)
            for btn in self.correct_option.buttons():
                btn.setChecked(False)
            self.correct_option.setExclusive(True)

    def save_to_file(self):
        if not self.questions:
            QMessageBox.warning(self, "Uyarı", "Kaydedilecek soru bulunamadı!")
            return
            
        filename, _ = QFileDialog.getSaveFileName(
            self, "Kaydet", "", "JSON Dosyaları (*.json)"
        )
        if filename:
            if not filename.endswith('.json'):
                filename += '.json'
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(self.questions, f, ensure_ascii=False, indent=4)
                QMessageBox.information(self, "Başarılı", "Dosya başarıyla kaydedildi!")
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Dosya kaydedilirken hata oluştu: {str(e)}")

    def load_from_file(self):
        filename, _ = QFileDialog.getOpenFileName(
            self, "Yükle", "", "JSON Dosyaları (*.json)"
        )
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    self.questions = json.load(f)
                    self.category_combo.clear()
                    self.category_combo.addItems(self.questions.keys())
                    if self.questions:
                        self.category_combo.setCurrentIndex(0)
                    QMessageBox.information(self, "Başarılı", "Dosya başarıyla yüklendi!")
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Dosya yüklenirken hata oluştu: {str(e)}")

    def export_to_pdf(self):
        if not self.questions:
            QMessageBox.warning(self, "Uyarı", "PDF oluşturmak için soru bulunamadı!")
            return

        filename, _ = QFileDialog.getSaveFileName(
            self, "PDF Olarak Kaydet", "", "PDF Dosyaları (*.pdf)"
        )
        
        if not filename:
            return
            
        if not filename.endswith('.pdf'):
            filename += '.pdf'

        try:
            doc = SimpleDocTemplate(filename, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []
            
            title_style = styles["Heading1"]
            title_style.textColor = colors.blue
            title_style.alignment = 1  
            
            category_style = styles["Heading2"]
            category_style.textColor = colors.darkgreen
            
            # Soru stili
            question_style = styles["Normal"]
            question_style.fontSize = 12
            
            # Cevap stili
            answer_style = styles["Normal"]
            answer_style.textColor = colors.darkred
            
            # Başlık ekle
            story.append(Paragraph("SORU BANKASI", title_style))
            story.append(Spacer(1, 0.5 * inch))
            
            # Kategorileri ve soruları ekle
            for category, questions in self.questions.items():
                if not questions:
                    continue
                    
                story.append(Paragraph(category.upper(), category_style))
                story.append(Spacer(1, 0.2 * inch))
                
                for i, question in enumerate(questions, 1):
                    # Soru başlığı
                    story.append(Paragraph(f"{i}. {question['title']}", question_style))
                    
                    # Soru içeriği
                    story.append(Paragraph(f"<b>Soru:</b> {question['content']}", question_style))
                    
                    # Cevap
                    if question['type'] == "Klasik":
                        story.append(Paragraph(f"<b>Cevap:</b> {question['answer']}", answer_style))
                    else:
                        options = "\n".join(
                            [f"{chr(65+j)}. {opt}" 
                             for j, opt in enumerate(question['answer']['options'])]
                        )
                        correct = chr(65 + question['answer']['correct'])
                        story.append(Paragraph(f"<b>Seçenekler:</b>\n{options}", question_style))
                        story.append(Paragraph(f"<b>Doğru Cevap:</b> {correct}", answer_style))
                    
                    story.append(Spacer(1, 0.3 * inch))
            
            doc.build(story)
            QMessageBox.information(self, "Başarılı", f"PDF başarıyla oluşturuldu:\n{filename}")
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"PDF oluşturulurken hata:\n{str(e)}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = QuestionBankApp()
    window.show()
    sys.exit(app.exec_())