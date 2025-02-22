## Yasal uyarı

Herhangibir illegal kullanımda tüm sorumluluk kullanıcıya aittir.
Yerel ağa pentest (yük ve trafik testi) yapmak için yazılmıştır.
Nkill herhangibir IP spoofing özelliği içermemektedir(Wireshark gibi bir yazılım ile saldırı yapan kolayca tesbit edilebilir).
Ping Of Death saldırılarında kullanmayınız.


## Kurulum && Çalıştırma

***Önce python kurulumu yapılmalıdır***

<pre><code>
cd Nkill
pip install -r requirements.txt
cd src
sudo python gui.py  #veya
sudo python terminal.py
</code></pre>


Alias ataması yapılarak çalıştırılması önerilir.

## Bilgilendirme

Windows yönetici Mac, Linux ve Android(Termux) için Root yetkisi alınarak çalıştırılmalıdır.
Thread(İş parçacığı) sayısı saniyede yollanacak paket sayısını, Paket boyutu ise yollanan her paketin kaç Byte olacağını gösterir.
Hedef IP adresine ne girerseniz girin tüm yerel ağ etkilenecektir.

![resim](https://github.com/user-attachments/assets/2640948c-80a9-41ba-b66d-07ac7b82f554)

![resim](https://github.com/user-attachments/assets/867c9f30-e2d1-4bd1-8a7c-fe3ef93f1ab9)




