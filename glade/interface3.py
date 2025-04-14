#Покажет пароль от vnc только если запущена от рута

import subprocess
import threading
import gi
import os
import urllib.parse
import re
import fileinput
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

#Работает, но pip не поставлен на сп8
#from elevate import elevate

#def is_root():
#        return os.getuid() == 0

#elevate()
#print(is_root())

class UnameApp:
    def __init__(self):
    # Попробуем загрузить интерфейс из файла Glade
        builder = Gtk.Builder()
        builder.add_from_file("/opt/glade/interface.glade")
        builder.connect_signals(self)

        # Получение элементов интерфейса
        self.window = builder.get_object("MainWindow")

        self.btn_run = builder.get_object("btn_run")
        self.btn_run_3 = builder.get_object("btn_run_3")
        self.btn_run_env = builder.get_object("btn_run_env")
        self.lbl_output_env = builder.get_object("lbl_output_env")
        self.lbl_output = builder.get_object("lbl_output")
        self.delete_proxy_settings = builder.get_object("delete_proxy_settings")

        ## Элементы для смены пароля
        self.entry_input = builder.get_object("entry_input")
        self.save_button = builder.get_object("save_button")

        # Элементы для смены proxy
        self.pass_input = builder.get_object("pass_input")
        self.login_input = builder.get_object("login_input")
        self.no_proxy_input = builder.get_object("no_proxy_input")

        ## Элементы для смены переменных
 #       self.entry_input_env = builder.get_object("entry_input")
        self.save_button_env = builder.get_object("save_button_env")

        ## Элементы для смены прокси исключении
        self.save_button_env_no_proxy = builder.get_object("save_button_env_no_proxy")

        # Подключение обработчиков сигналов
        self.btn_run_3.connect("clicked", self.on_btn_run_3_clicked)
        self.btn_run.connect("clicked", self.on_btn_run_clicked)
        self.btn_run_env.connect("clicked", self.on_btn_run_env_clicked)
        self.delete_proxy_settings.connect("clicked", self.on_delete_proxy_settings_clicked)

        # Подключение обработчиков сигналов смены пароля
        self.save_button.connect("clicked", self.on_save_button_clicked)

        # Подключение обработчиков сигналов смены переменных
        self.save_button_env.connect("clicked", self.on_save_button_clicked_env)

        # Подключение обработчиков сигналов прокси исключении
        self.save_button_env_no_proxy.connect("clicked", self.on_save_button_env_no_proxy)

        #Вывод успешной смены пароля
        self.lbl_output_3 = builder.get_object("lbl_output_3")

        #Выdод об успешной смене env
 ##       self.lbl_output_env = builder.get_object("lbl_output_env")

        self.window.connect("destroy", Gtk.main_quit)
        self.window.show_all()

###Меняем пароль VNC

    def on_save_button_clicked(self, button):
        input_text = self.entry_input.get_text().strip()
        if input_text:
            change_vnc = "x11vnc -storepasswd {} /etc/x11vnc.pass".format(input_text)
            os.system(change_vnc)
            text_pw_change = "Пароль от VNC изменен!"
            self.lbl_output_3.set_text(text_pw_change)
        else:
            text_pw_change = "Пустой пароль!"
            self.lbl_output_3.set_text(text_pw_change)

###Показать пароль VNC

    def on_btn_run_clicked(self, button):
        result = subprocess.Popen(
                "x11vnc -showrfbauth /etc/x11vnc.pass | awk '/pass: / {print $3}'",
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

        output, error = result.communicate()
        decoded_output = output.decode().strip()
        self.entry_input.set_text(decoded_output)

###Меняем переменные

    def on_save_button_clicked_env(self, button):
        proxy_user = self.login_input.get_text().strip()
        proxy_pass = self.pass_input.get_text().strip()
        #Пароль и учетку нужно обрабатывать URL-encoded
        proxy_user=urllib.parse.quote(proxy_user)
        proxy_pass=urllib.parse.quote(proxy_pass)


        #Проверяем на пустую строку в учетке/пароле
        input_text = self.login_input.get_text().strip()
        input_text2 = self.pass_input.get_text().strip()
        # проверяем чтобы оба поля не были пусты
        if not input_text or not input_text2:
            text_pw_change = "Нет учетки/пароля!"
            self.lbl_output_3.set_text(text_pw_change)
            return

        #если пустой, то добавляем строчки, по которым будут меняться значения
        proxy_file = "/etc/environment"
        template = "ftp_proxy=\nhttp_proxy=\nhttps_proxy=\nno_proxy=\n"

        if not os.path.exists(proxy_file) or os.path.getsize(proxy_file) <= 1:
            with open(proxy_file, 'w') as f:
                f.write(template)
            print(proxy_file)

        # Формируем proxy
        ftp_proxy = f"ftp_proxy=http://{proxy_user}:{proxy_pass}@i.tatar.ru:8080"
        http_proxy = f"http_proxy=http://{proxy_user}:{proxy_pass}@i.tatar.ru:8080"
        https_proxy = f"https_proxy=http://{proxy_user}:{proxy_pass}@i.tatar.ru:8080"

        for line in fileinput.input('/etc/environment', inplace=True):
            new_proxy = re.sub(r'ftp_proxy=.*', f'{ftp_proxy}', line)
            new_proxy = re.sub(r'http_proxy=.*', f'{http_proxy}', new_proxy)
            new_proxy = re.sub(r'https_proxy=.*', f'{https_proxy}', new_proxy)
            print(new_proxy, end='')

        self.lbl_output_3.set_text("Прокси-настройки сохранены!")
        self.on_btn_run_env_clicked(button)

    # отдельная кнопка для исключении
    def on_save_button_env_no_proxy(self, button):
        no_user_proxy = self.no_proxy_input.get_text().strip()
        no_user_proxy = f"no_proxy={no_user_proxy}"

    #Проверяем на пустую строку в исключениях
        input_text = self.no_proxy_input.get_text().strip()
        if not input_text:
            text_pw_change = "Пустые исключения!"
            self.lbl_output_3.set_text(text_pw_change)
            return

        for line in fileinput.input('/etc/environment', inplace=True):
            new_no_proxy = re.sub(r'no_proxy=.*', f'{no_user_proxy}', line)
            print(new_no_proxy, end='')

        self.lbl_output_3.set_text("Прокси исключения сохранены!")
        self.on_btn_run_env_clicked(button)

###Показать текущие переменные
    def on_btn_run_env_clicked(self, button):
        result = subprocess.Popen(
                "cat /etc/environment",
                shell=True, 
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

        output, error = result.communicate()
        decoded_output = output.decode().strip()
        text_buffer = self.lbl_output_env.get_buffer()
        text_buffer.set_text(decoded_output)
        self.text_buffer_env = self.lbl_output_env.get_buffer()

###Очистить выведенные результаты

    def on_btn_run_3_clicked(self, button):
        print_lacuna = ''
        self.entry_input.set_text(print_lacuna)
        self.lbl_output_3.set_text(print_lacuna)
        self.pass_input.set_text(print_lacuna)
        self.login_input.set_text(print_lacuna)
        self.no_proxy_input.set_text(print_lacuna)
        self.text_buffer_env.set_text(print_lacuna)

###Удалить все настройки переменных (сохранив бекап)

    def on_delete_proxy_settings_clicked(self, button):
        subprocess.run(['cp', '/etc/environment', '/tmp/environment'])
        open('/etc/environment', 'w').close()
        self.lbl_output_3.set_text("Прокси настройки удалены!\n(бекап настроек лежит в /tmp/)")


if __name__ == "__main__":
    app = UnameApp()
    Gtk.main()
