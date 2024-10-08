#Покажет пароль от vnc только если запущена от рута

import subprocess
import threading
import gi
import os
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
        self.lbl_output = builder.get_object("lbl_output")
        ## Элементы для смены пароля
        self.entry_input = builder.get_object("entry_input")
        self.save_button = builder.get_object("save_button")

        # Подключение обработчиков сигналов
        self.btn_run_3.connect("clicked", self.on_btn_run_3_clicked)
        self.btn_run.connect("clicked", self.on_btn_run_clicked)
        
        # Подключение обработчиков сигналов смены пароля
        self.save_button.connect("clicked", self.on_save_button_clicked)

        #Вывод успешной смены пароля
        self.lbl_output_3 = builder.get_object("lbl_output_3")

        self.window.connect("destroy", Gtk.main_quit)
        self.window.show_all()

#####################################################################################
#Меняем пароль VNC

    def on_save_button_clicked(self, button):
        input_text = self.entry_input.get_text().strip()
        #проверяем на рут тут и дальше в тело вывод полученной инфы!
        if os.geteuid() != 0:
            text_pw_change = "You need to bee root!"
            self.lbl_output_3.set_text(text_pw_change)
        else:    
            if input_text:
                change_vnc = "x11vnc -storepasswd {} /root/.vnc/passwd".format(input_text)
                os.system(change_vnc)
                text_pw_change = "Пароль от VNC изменен!"
                self.lbl_output_3.set_text(text_pw_change)
            else:
                text_pw_change = "Пустой пароль!"
                self.lbl_output_3.set_text(text_pw_change)

#####################################################################################
#Очистить выведенные поля 

    def on_btn_run_3_clicked(self, button):
        print_lacuna = ''
        self.lbl_output.set_text(print_lacuna)          

#####################################################################################

    def on_btn_run_clicked(self, button):
        
        result = subprocess.Popen(
                "x11vnc -showrfbauth /root/.vnc/passwd | awk '/pass: / {print $3}'", 
                shell=True, 
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
        
        output, error = result.communicate()
        decoded_output = output.decode().strip()
        self.lbl_output.set_text(decoded_output)
             

#####################################################################################

if __name__ == "__main__":
    app = UnameApp()
    Gtk.main()
