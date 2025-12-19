# Uygulamanın başlatıcısı ve Arayüz (Qt) kodları
import os
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit, QPushButton, QFileDialog, QLabel
from PySide6.QtCore import QThread, Signal
from backend.rag_manager import RAGManager

class ChatWorker(QThread):
    # Sinyal Tüneli: İşçi işi bitince bu tünelden metin (str) gönderecek
    cevap_geldi = Signal(str)

    def __init__(self, manager, soru):
        super().__init__()
        self.manager = manager
        self.soru = soru

    def run(self):
        """
        Thread başlatılınca (start) burası çalışır.
        Burası Arayüzden bağımsızdır, donma yapmaz.
        """
        try:
            # Backend'deki o meşhur fonksiyonu burada çağırıyoruz
            cevap = self.manager.ask_question(self.soru)
            # Cevabı tünelden ana ekrana fırlatıyoruz
            self.cevap_geldi.emit(cevap)
        except Exception as e:
            self.cevap_geldi.emit(f"Hata oluştu: {str(e)}")

class LoaderWorker(QThread):
    # İş bitince sinyal gönderecek: (Başarılı mı?, Dosya Adı/Hata Mesajı)
    islem_bitti = Signal(bool, str)

    def __init__(self, manager, file_path):
        super().__init__()
        self.manager = manager
        self.file_path = file_path

    def run(self):
        try:
            # Ağır yükleme işlemini burada yapıyoruz
            basari = self.manager.load_and_index(self.file_path)
            if basari:
                self.islem_bitti.emit(True, self.file_path)
            else:
                self.islem_bitti.emit(False, "Bilinmeyen hata.")
        except Exception as e:
            self.islem_bitti.emit(False, str(e))

class ChatApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF Asistanı")
        self.setGeometry(100, 100, 800, 600)
        self.init_ui()

        # Modern Dark Tema (Koyu Mod)
        style_sheet = """
            QMainWindow {
                background-color: #2b2b2b;
            }
            QLabel {
                color: #dddddd;
                font-size: 14px;
                font-family: 'Segoe UI', sans-serif;
            }
            QTextEdit {
                background-color: #353535;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
            }
            QLineEdit {
                background-color: #353535;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 8px;
                padding: 8px;
                font-size: 14px;
            }
            QPushButton {
                background-color: #3d8ec9;
                color: white;
                border-radius: 6px;
                padding: 8px 15px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #2b6ca3;
            }
            QPushButton:pressed {
                background-color: #1e4d75;
            }
            /* Kırmızı 'Yeni Sohbet' butonu için özel stil */
            QPushButton#btn_reset {
                background-color: #e74c3c;
            }
            QPushButton#btn_reset:hover {
                background-color: #c0392b;
            }
        """
        self.setStyleSheet(style_sheet)

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
            
            self.btn_new_chat = QPushButton("Yeni Sohbet")
            self.btn_new_chat.setObjectName("btn_reset")
            self.btn_new_chat.setStyleSheet("background-color: #ff6b6b; color: white;") # İstersen kırmızı renk ver
            self.btn_new_chat.clicked.connect(self.reset_app) # Birazdan yazacağız
            top_layout.addWidget(self.btn_new_chat)

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
         # 1. Dosya Seç
        file_path, _ = QFileDialog.getOpenFileName(
            self, "PDF Seç", "", "PDF Dosyaları (*.pdf)"
        )
        
        if not file_path:
            return

        # 2. Arayüzü Hazırla (Donmasın diye kullanıcıya bilgi ver)
        self.lbl_status.setText("PDF Yükleniyor... (Arka planda)")
        self.btn_load.setEnabled(False) # Üst üste basılmasın
        
        # 3. Yükleme İşçisini Başlat
        self.loader_worker = LoaderWorker(self.manager, file_path)
        # İş bitince 'pdf_yuklendi_sonuc' fonksiyonuna git
        self.loader_worker.islem_bitti.connect(self.pdf_yuklendi_sonuc)
        self.loader_worker.start()

    def pdf_yuklendi_sonuc(self, basari, mesaj):
        """
        LoaderWorker işini bitirince burası çalışır.
        """
        self.btn_load.setEnabled(True) # Butonu tekrar aktif et
        
        if basari:
            dosya_adi = os.path.basename(mesaj)
            self.lbl_status.setText(f"Yüklendi: {dosya_adi}")
            self.chat_area.append(f"<font color='green'>SYSTEM: {dosya_adi} başarıyla işlendi.</font>")
            self.chat_area.append("-" * 30)
        else:
            self.lbl_status.setText("Hata oluştu!")
            self.chat_area.append(f"<font color='red'>Hata: {mesaj}</font>")

    def ask_gpt(self):
        soru = self.input_field.text().strip()
        if not soru:
            return

        # 1. Arayüzü Hazırla
        user_html = f"""
        <div style="width: 100%; text-align: left;">
            <div style="background-color: #444444; color: white; padding: 10px 15px; border-radius: 15px 0px 15px 15px; border: 1px solid #555555; display: inline-block; text-align: left; margin-right: 20px; max-width: 75%;">
                <small style="color: #cccccc; font-weight: bold; font-size: 10px;">SEN</small>
                <br>
                {soru}
            </div>
        </div>
        <br>
        """
        self.chat_area.append(user_html)
        self.input_field.clear()
        self.lbl_status.setText("Asistan düşünüyor... (Arayüz donmayacak!)")
        
        # Butonu pasif yapalım ki üst üste basılmasın
        self.btn_send.setEnabled(False) 
        self.input_field.setEnabled(False)

        # 2. İşçiyi Hazırla ve Başlat
        # self.worker değişkenine atıyoruz ki işlem bitmeden çöp toplayıcı (GC) silmesin
        self.worker = ChatWorker(self.manager, soru)
        
        # İşçi "cevap_geldi" sinyali atınca, bizim "cevap_isle" fonksiyonumuz çalışsın
        self.worker.cevap_geldi.connect(self.cevap_isle)
        
        # İşçiyi işe gönder
        self.worker.start()
    
    def reset_app(self):
        # 1. Backend'i sıfırla
        self.manager.reset_system()
        
        # 2. Ekranı temizle
        self.chat_area.clear()
        self.input_field.clear()
        
        # 3. Bilgilendirme yap
        self.lbl_status.setText("Sohbet sıfırlandı. Yeni bir PDF yükleyebilirsiniz.")
        self.chat_area.append("<font color='gray'><i>--- Yeni Sohbet Başlatıldı ---</i></font>")
        self.chat_area.append("Lütfen başlamak için yeni bir PDF yükleyin.\n")

    def cevap_isle(self, gelen_cevap):
        # Cevabı ekrana yaz
        formatli_cevap = gelen_cevap.replace("\n", "<br>")
        
        bot_html = f"""
        <div style="text-align: left;">
            <b>ASİSTAN:</b>
            <br>
            <div style="background-color: #444444; color: white; padding: 10px; border-radius: 10px; margin-top: 5px;">
                {formatli_cevap}
            </div>
        </div>
        <br>
        <hr style="border: 1px solid #555555;">
        """
        self.chat_area.append(bot_html)
        
        # ... fonksiyonun geri kalanı aynı ...
        self.lbl_status.setText("Hazır")
        self.btn_send.setEnabled(True)
        self.input_field.setEnabled(True)
        self.input_field.setFocus()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window =ChatApp()
    window.show()
    sys.exit(app.exec())

