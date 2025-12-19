# Uygulamanın başlatıcısı ve Arayüz (Qt) kodları

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit, QPushButton, QFileDialog, QLabel
import os
# Backend sınıfımızı içeri alıyoruz
from backend.rag_manager import RAGManager



class ChatApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF Asistanı")
        self.setGeometry(100, 100, 800, 600)
        self.init_ui()

        # --- Backend Hazırlığı ---
        # Veritabanı yolunu belirliyoruz
        current_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(current_dir, "..", "chroma_db")

        self.manager = RAGManager(persist_directory=db_path)

    def init_ui(self):
            # 1. Ana Taşıyıcıyı Hazırla
            self.central_widget = QWidget() # DÜZELTME: Parantez () eklendi!
            self.setCentralWidget(self.central_widget)
            
            self.layout = QVBoxLayout()
            self.central_widget.setLayout(self.layout)

            # 2. Üst Panel (Yatay)
            top_layout = QHBoxLayout()
            
            self.lbl_status = QLabel("PDF Yüklü Değil") # Yazım hatası düzeltildi (stasu -> status)
            self.btn_load = QPushButton("PDF Yükle")
            self.btn_load.clicked.connect(self.upload_pdf)
            
            # DÜZELTME: addWidget içine neyi ekleyeceğimizi yazdık
            top_layout.addWidget(self.lbl_status)
            top_layout.addWidget(self.btn_load)
            
            # Üst paneli ana yapıya ekle
            self.layout.addLayout(top_layout)

            # 3. Sohbet Alanı (Orta)
            self.chat_area = QTextEdit()
            self.chat_area.setReadOnly(True)
            self.layout.addWidget(self.chat_area)

            # 4. Alt Panel (Giriş Kısmı)
            bottom_layout = QHBoxLayout()
            
            self.input_field = QLineEdit()
            self.input_field.setPlaceholderText("Sorunuzu buraya yazın...") # İpucu yazısı ekledik
            self.btn_send = QPushButton("Gönder")

            # Butona tıklanınca
            self.btn_send.clicked.connect(self.ask_gpt)
            
            # Enter tuşuna basılınca (Input kutusundayken)
            self.input_field.returnPressed.connect(self.ask_gpt)
            
            # DÜZELTME: Bunları eklemeyi unutmuştun
            bottom_layout.addWidget(self.input_field)
            bottom_layout.addWidget(self.btn_send)
            
            # Alt paneli ana yapıya bağla
            self.layout.addLayout(bottom_layout)

    def upload_pdf(self):
         file_path, _ = QFileDialog.getOpenFileName(
              self,
              "PDF Dosyasını Seç",
              "",
              "PDF Dosyaları (*.pdf)"
         )

         if file_path:
            self.lbl_status.setText("Yükleniyor... Lütfen bekleyin.")
            QApplication.processEvents()

            basari = self.manager.load_and_index(file_path)

            if basari:
                self.lbl_status.setText(f"Yüklendi: {os.path.basename(file_path)}")
                self.chat_area.append(f"SYSTEM: {os.path.basename(file_path)} başarıyla yüklendi ve analiz edildi.\n")
            else:
                self.lbl_status.setText("Hata Oluştu!")

    def ask_gpt(self):
        # 1. Yazıyı al
        soru = self.input_field.text().strip()
        
        # Boşsa işlem yapma
        if not soru:
            return
            
        # 2. Ekrana kullanıcının sorusunu yaz
        self.chat_area.append(f"\n<b>SEN:</b> {soru}")
        self.input_field.clear() # Kutuyu temizle
        
        # Arayüzün donduğunu sanmasınlar diye küçük bir hile:
        self.lbl_status.setText("Asistan düşünüyor...")
        QApplication.processEvents() # Ekranı güncelle
        
        # 3. Backend'e sor (Cevap gelene kadar arayüz hafif donabilir, normaldir)
        try:
            cevap = self.manager.ask_question(soru)
            
            # 4. Cevabı ekrana yaz
            self.chat_area.append(f"<b>ASİSTAN:</b> {cevap}")
            self.chat_area.append("-" * 30) # Ayırıcı çizgi
            self.lbl_status.setText("Hazır")
            
        except Exception as e:
            self.chat_area.append(f"<font color='red'>Hata: {str(e)}</font>")
            self.lbl_status.setText("Hata oluştu")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window =ChatApp()
    window.show()
    sys.exit(app.exec())

