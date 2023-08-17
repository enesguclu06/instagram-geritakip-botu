import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QTextEdit
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QFont

class InstagramThread(QThread):
    finished = pyqtSignal()
    result_ready = pyqtSignal(list)

    def __init__(self, username, password):   #Nesnedeki özellikleri başlatmaya ve kullanmaya yarar.
        super().__init__()
        self.username = username
        self.password = password

    def run(self):
        browser = webdriver.Chrome() # Browserimizi Chrome Olarak Seçiyoruz
        browser.get("https://www.instagram.com/")   #İnstagram adresine giriyor.
        time.sleep(1)
        username = browser.find_element(By.XPATH, "//*[@id='loginForm']/div/div[1]/div/label/input") #xpath sayesinde kullanıcı adı yolunu buluyor.
        username.send_keys(self.username)   #Girilen kullanıcı adının kullanıcı adını giriyoruz
        password = browser.find_element(By.XPATH, "//*[@id='loginForm']/div/div[2]/div/label/input")
        password.send_keys(self.password)
        browser.find_element(By.XPATH, "//*[@id='loginForm']/div/div[3]").click() #Giriş yap butonunu buluyor ve tıklıyor.
        time.sleep(10)  # Uygulamanın açılması için 7 saniye bekliyor


        browser.get("https://www.instagram.com/" + self.username + "/followers/") #Girdiği kullanıcı adıyla takipçiler sekmesine giriyor
        time.sleep(7)

        self.js_command(browser) # Takipçi listesinin hepsini alması için otamatik scroll özelliği yapıyor.

        followers = browser.find_elements(By.CLASS_NAME, "_aacl._aaco._aacw._aacx._aad7._aade")
        #Takipçiler sekmesindeki tüm takip edenlerin sınıfının bilgilerini alıyor.
        takipci_liste = []
        for follower in followers:   #Tüm takipçi sınıfındaki verilerin yazı halini listeye atıyor
            takipci_liste.append(follower.text)

        browser.get("https://www.instagram.com/" + self.username + "/following/") # Takip Ettiğin listesine gidiyor
        time.sleep(7)

        self.js_command(browser) # Takip listesinin hepsini alması için otamatik scroll özelliği yapıyor
        followings = browser.find_elements(By.CLASS_NAME, "_aacl._aaco._aacw._aacx._aad7._aade")
        #Takipçiler sekmesindeki tüm takip edenlerin sınıfının bilgilerini alıyor.
        takip_liste = []

        for following in followings:  #Tüm takip ettiğin sınıfındaki verilerin yazı halini listeye atıyor
            takip_liste.append(following.text)

        takipci_kume = set(takipci_liste) #eleme yapmak için ikisinide set ediyor.
        takip_kume = set(takip_liste)

        self.senin_takip_etmediğin = list(takipci_kume.difference(takip_kume)) #takipçi listesinde olan ama senin takip ettiklerinde  olmayan bilgileri yeni listeye atar.

        self.seni_takip_etmeyenler = list(takip_kume.difference(takipci_kume)) #takip ettiğin listesinde olan ama senin takipçilerinde olmayan bilgileri yeni listeye atar.

        browser.quit()

        self.result_ready.emit([self.senin_takip_etmediğin, self.seni_takip_etmeyenler])  #Bilgiler yüklendiğinde bu komutu çalıştırıyor ve sağlıklı bir şekilde yüklenmesini sağlıyor.
        self.finished.emit()

    def js_command(self, browser):    #Otamatik Scroll özelliği veren fonksiyon
        jscommand = """
        followers = document.querySelector("._aano")
        followers.scrollTo(0, followers.scrollHeight);
        var lenOfPage=followers.scrollHeight;
        return lenOfPage;
        """

        lenofPage = browser.execute_script(jscommand)
        match = False
        while not match:
            lastCount = lenofPage
            time.sleep(1.5)
            lenofPage = browser.execute_script(jscommand)
            if lastCount == lenofPage:
                match = True

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("İnstagram Takipçi Kontrol (Coded By Enes Güçlü)") #Uygulama açıldığında üst tarafta yazan yazı
        self.showMaximized()

        self.username_label = QLabel("Kullanıcı Adı:")  #kullanıcı adı ve şifrenin yazdığı bir label.
        self.username_input = QLineEdit()

        self.password_label = QLabel("Şifre:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)

        self.login_button = QPushButton("Giriş")     #Fonksiyon atayacağımız butonları tanımlıyoruz.
        self.login_button.clicked.connect(self.login)

        self.extra_button2 = QPushButton("Senin Geri Takip Etmediğin")
        self.extra_button2.clicked.connect(self.geritakipetmedigin)
        self.extra_button1 = QPushButton("Seni Geri Takip Etmeyenler")
        self.extra_button1.clicked.connect(self.senitakipetmeyenler)

        self.info_output = QTextEdit()   #Bilgilerin çıkacağı yazı alanı.
        self.info_output.setFont(QFont("Arial", 16))
        self.info_output.setReadOnly(True)

        layout = QVBoxLayout()  #Arayüz düzenlemesi
        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_button)
        layout.addWidget(self.extra_button1)
        layout.addWidget(self.extra_button2)
        layout.addWidget(self.info_output)

        self.thread = None

        self.setLayout(layout)
    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if username and password:  #username ve password girilmişse uygulamayı açıyor.
            self.thread = InstagramThread(username, password)
            self.thread.start()

    def geritakipetmedigin(self): #Geri takip etmediğin butonunun fonksiyonlarını ayarlar.
        self.info_output.clear() #Sonuç bölümünü temizler
        self.info_output.append("Senin Geri Takip Etmediğin Bu Kişiler:")
        self.info_output.append("\n".join(self.thread.senin_takip_etmediğin)) #Sonuç kısmına alt alta listeyi ekler.

    def senitakipetmeyenler(self):#Seni Geri takip etmeyenler  butonunun fonksiyonlarını ayarlar.
        self.info_output.clear()
        self.info_output.append("Seni Geri Takip Etmeyenler Bu Kişiler:")
        self.info_output.append("\n".join(self.thread.seni_takip_etmeyenler)) #Sonuç kısmına alt alta listeyi ekler.

if __name__ == "__main__": #Uygulamayı başlatma Fonksiyonları
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
