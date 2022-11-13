from kivy.config import Config

Config.set('graphics', 'resizable', 0)

import datetime
import sqlite3
import bs4 as BeautifulSoup
import requests
from kivy.lang import Builder
from kivy.core.window import Window
#from kivy.metrics import dp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.app import MDApp
from kivymd.uix.pickers import MDDatePicker
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog


class AdminLoginDialog(MDBoxLayout):
    pass


class UserRegisterDialog(MDBoxLayout):
    pass


class LoginScreen(Screen):
    pass


class SearchScreen(Screen):
    pass


class ResultScreen(Screen):
    pass


class SendScreen(Screen):
    pass


class HistoryScreen(Screen):
    pass


class WindowManager(ScreenManager):
    pass


class QuotationApp(MDApp):
    period = None
    adults = None
    children = None
    child1 = None
    child2 = None
    child3 = None
    promo = None
    url = None

    apaq = None
    apca = None
    apco = None
    apla = None
    apma = None
    chfa = None
    chhi = None
    chla = None
    chme = None

    active_user = None

    dialog = None
    new_user = None

    adults_menu = None
    children_menu = None
    child1_menu = None
    child2_menu = None
    child3_menu = None

    con = sqlite3.connect("quotation.db")
    cur = con.cursor()
    cur.execute("""CREATE TABLE if not exists users_info (
                                                        user_number TEXT,
                                                        user_password TEXT,
                                                        user_name TEXT)""")
    cur.execute("""CREATE TABLE if not exists history_info (
                                                        quotation_date TEXT,
                                                        quotation_user TEXT,
                                                        quotation_number TEXT,
                                                        quotation_values TEXT)""")
    con.commit()

    admin_check = cur.execute("SELECT user_name FROM users_info WHERE user_name='ADMINISTRADOR'")

    if admin_check.fetchone() is None:
        cur.execute("""INSERT INTO users_info (user_number, user_password, user_name)
                                        VALUES ('0', '91166863', 'ADMINISTRADOR')""")
        con.commit()

    pull_users = cur.execute("SELECT * FROM users_info")
    pull_users = pull_users.fetchall()

    con.close()

    users_info = {}

    for user in pull_users:
        users_info[user[0]] = {"password": user[1], "name": user[2]}

    def call_login(self):
        if self.root.current == "history":
            self.root.get_screen("history").ids.history_alert.color = 0, 1, 0, 1
            self.root.get_screen("history").ids.history_alert.text = "Carregando..."
        else:
            self.root.get_screen("search").ids.search_alert.color = 0, 1, 0, 1
            self.root.get_screen("search").ids.search_alert.text = "Carregando..."

        self.root.get_screen("login").ids.login_alert.text = ""

        self.root.transition.direction = "left" if self.root.current == "history" else "right"
        self.root.transition.duration = .05
        self.root.current = "login"

    def on_input_validate(self, wid):
        if self.root.current == "login":
            if wid == "user_number_field":
                self.root.get_screen("login").ids.user_password_field.focus = True
            elif wid == "user_password_field":
                self.login()
            elif wid == "admin_check_password":
                self.check_admin(wid)
            elif wid == "new_user_number_field":
                self.dialog.content_cls.ids.new_user_name_field.focus = True
            elif wid == "new_user_name_field":
                self.dialog.content_cls.ids.new_user_password_field.focus = True
            else:
                self.new_user_save(wid)

    def user_on_type(self):
        if self.root.current == "login":
            if self.root.get_screen("login").ids.user_number_field.text != "":
                if self.root.get_screen("login").ids.user_number_field.text in self.users_info:
                    self.root.get_screen("login").ids.user_name_field.text = \
                        self.users_info[self.root.get_screen("login").ids.user_number_field.text]["name"]
                else:
                    self.root.get_screen("login").ids.user_name_field.text = "Não encontrado"
            else:
                self.root.get_screen("login").ids.user_name_field.text = "Nome"

    def hide_alert(self):
        if self.root.current == "login":
            if self.dialog is None:
                self.root.get_screen("login").ids.login_alert.text = ""
            else:
                try:
                    self.dialog.content_cls.ids.dialog_admin_check_alert.text = ""
                except:
                    pass
                try:
                    self.dialog.content_cls.ids.dialog_new_user_alert.text = ""
                except:
                    pass
        if self.root.current == "search":
            self.root.get_screen("search").ids.search_alert.text = ""
        if self.root.current == "result":
            self.root.get_screen("result").ids.result_alert.text = ""
        if self.root.current == "send":
            self.root.get_screen("send").ids.send_alert.text = ""
        if self.root.current == "history":
            self.root.get_screen("history").ids.history_alert.text = ""

    def login(self):
        if self.root.get_screen("login").ids.user_number_field.text == "":

            self.root.get_screen("login").ids.login_alert.color = 1, 0, 0, 1
            self.root.get_screen("login").ids.login_alert.text = "Informe o usuário!"

        elif self.root.get_screen("login").ids.user_number_field.text not in self.users_info:

            self.root.get_screen("login").ids.login_alert.color = 1, 0, 0, 1
            self.root.get_screen("login").ids.login_alert.text = "Usuário Inválido!"

        elif self.users_info[self.root.get_screen("login").ids.user_number_field.text][
            "password"] != self.root.get_screen("login").ids.user_password_field.text:

            self.root.get_screen("login").ids.login_alert.color = 1, 0, 0, 1
            self.root.get_screen("login").ids.login_alert.text = "Senha Incorreta!"

        else:

            self.active_user = self.root.get_screen("login").ids.user_name_field.text
            self.root.get_screen("login").ids.user_number_field.text = ""
            self.root.get_screen("login").ids.user_password_field.text = ""
            self.call_search()

    def register(self):
        self.dialog = MDDialog(
            type="custom",
            content_cls=AdminLoginDialog(),
            radius=[24, 0, 24, 0],
            buttons=[
                MDFlatButton(
                    text="Cancelar",
                    theme_text_color="Custom",
                    text_color=self.theme_cls.primary_color,
                    on_release=self.dialog_dismiss
                ),
                MDFlatButton(
                    text="Entrar",
                    theme_text_color="Custom",
                    text_color=self.theme_cls.primary_color,
                    on_release=self.check_admin
                ),
            ],
        )
        self.dialog.open()

    def dialog_dismiss(self, obj):
        self.dialog.dismiss()
        self.dialog = None

    def check_admin(self, obj):
        if self.dialog.content_cls.ids.admin_check_password.text == self.users_info["0"]["password"]:
            self.dialog_dismiss("Close")
            self.dialog = MDDialog(
                type="custom",
                content_cls=UserRegisterDialog(),
                radius=[24, 0, 24, 0],
                buttons=[
                    MDFlatButton(
                        text="Cancelar",
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color,
                        on_release=self.dialog_dismiss
                    ),
                    MDFlatButton(
                        text="Entrar",
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color,
                        on_release=self.new_user_save
                    ),
                ],
            )
            self.dialog.open()

        else:
            self.dialog.content_cls.ids.dialog_admin_check_alert.color = 1, 0, 0, 1
            self.dialog.content_cls.ids.dialog_admin_check_alert.text = "Senha Incorreta!"

    def new_user_save(self, obj):
        names = [self.users_info[str(i)]["name"] for i in self.users_info]

        if self.dialog.content_cls.ids.new_user_number_field.text == "" or \
                self.dialog.content_cls.ids.new_user_name_field.text == "" or \
                self.dialog.content_cls.ids.new_user_password_field.text == "":

            self.dialog.content_cls.ids.dialog_new_user_alert.color = 1, 0, 0, 1
            self.dialog.content_cls.ids.dialog_new_user_alert.text = "Preencha todos os campos!"

        elif self.dialog.content_cls.ids.new_user_number_field.text in self.users_info:

            self.dialog.content_cls.ids.dialog_new_user_alert.color = 1, 0, 0, 1
            self.dialog.content_cls.ids.dialog_new_user_alert.text = "Número já Cadastrado!"

        elif self.dialog.content_cls.ids.new_user_name_field.text.upper() in names:

            self.dialog.content_cls.ids.dialog_new_user_alert.color = 1, 0, 0, 1
            self.dialog.content_cls.ids.dialog_new_user_alert.text = "Nome já Cadastrado!"

        elif not self.dialog.content_cls.ids.new_user_name_field.text.isalpha():

            self.dialog.content_cls.ids.dialog_new_user_alert.color = 1, 0, 0, 1
            self.dialog.content_cls.ids.dialog_new_user_alert.text = "Filho do Elon Musk?"

        else:

            self.con = sqlite3.connect("quotation.db")
            self.cur = self.con.cursor()
            self.new_user = (self.dialog.content_cls.ids.new_user_number_field.text,
                             self.dialog.content_cls.ids.new_user_password_field.text.upper(),
                             self.dialog.content_cls.ids.new_user_name_field.text.upper()
                             )
            self.cur.execute("""
                        INSERT INTO users_info (user_number, user_password, user_name)
                                        VALUES (?, ?, ?)
                            """, self.new_user)
            self.con.commit()

            pull_users = self.cur.execute("SELECT * FROM users_info")
            pull_users = pull_users.fetchall()
            self.con.close()

            self.users_info = {}

            for user in pull_users:
                self.users_info[user[0]] = {"password": user[1], "name": user[2]}

            self.root.get_screen("login").ids.login_alert.color = 0, 1, 0, 1
            self.root.get_screen("login").ids.login_alert.text = "Usuário Cadastrado!"

            self.dialog_dismiss("Close")

    def call_search(self):
        if self.root.current == "login":
            self.root.get_screen("login").ids.login_alert.color = 0, 1, 0, 1
            self.root.get_screen("login").ids.login_alert.text = "Carregando..."
        else:
            self.root.get_screen("result").ids.result_alert.color = 0, 1, 0, 1
            self.root.get_screen("result").ids.result_alert.text = "Carregando..."

        self.root.get_screen("search").ids.search_alert.text = ""

        self.adults_menu = MDDropdownMenu(
            caller=self.root.get_screen("search").ids.adults_menu,
            width_mult=2,
            max_height=200,
            radius=[24, 0, 24, 0],
            items=[
                {
                    "viewclass": "OneLineListItem",
                    "text": f"{i} Adultos" if i > 1 else "1 Adulto",
                    "on_release": lambda x=f"{i} Adultos" if i > 1 else "1 Adulto": self.set_adults(x)
                } for i in range(1, 5)],
            position="center"
        )
        self.adults_menu.bind()

        self.children_menu = MDDropdownMenu(
            caller=self.root.get_screen("search").ids.children_menu,
            width_mult=2,
            max_height=200,
            radius=[24, 0, 24, 0],
            items=[{"viewclass": "OneLineListItem", "text": "Nenhuma",
                    "on_release": lambda x="Crianças": self.set_children(x)},
                   {"viewclass": "OneLineListItem", "text": "1 Criança",
                    "on_release": lambda x="1 Criança": self.set_children(x)},
                   {"viewclass": "OneLineListItem", "text": "2 Crianças",
                    "on_release": lambda x="2 Crianças": self.set_children(x)},
                   {"viewclass": "OneLineListItem", "text": "3 Crianças",
                    "on_release": lambda x="3 Crianças": self.set_children(x)}
                   ],
            position="center"
        )
        self.children_menu.bind()

        self.child1_menu = MDDropdownMenu(
            caller=self.root.get_screen("search").ids.child1_menu,
            width_mult=2,
            max_height=400,
            radius=[24, 0, 24, 0],
            items=[
                {
                    "viewclass": "OneLineListItem",
                    "text": f"{i} Anos" if i > 0 else "Bebê",
                    "on_release": lambda x=f"{i} Anos" if i > 0 else "Bebê": self.set_child1(x)
                } for i in range(0, 18)],
            position="center"
        )
        self.child1_menu.bind()

        self.child2_menu = MDDropdownMenu(
            caller=self.root.get_screen("search").ids.child2_menu,
            width_mult=2,
            max_height=400,
            radius=[24, 0, 24, 0],
            items=[
                {
                    "viewclass": "OneLineListItem",
                    "text": f"{i} Anos" if i > 0 else "Bebê",
                    "on_release": lambda x=f"{i} Anos" if i > 0 else "Bebê": self.set_child2(x)
                } for i in range(0, 18)],
            position="center"
        )
        self.child2_menu.bind()

        self.child3_menu = MDDropdownMenu(
            caller=self.root.get_screen("search").ids.child3_menu,
            width_mult=2,
            max_height=400,
            radius=[24, 0, 24, 0],
            items=[
                {
                    "viewclass": "OneLineListItem",
                    "text": f"{i} Anos" if i > 0 else "Bebê",
                    "on_release": lambda x=f"{i} Anos" if i > 0 else "Bebê": self.set_child3(x)
                } for i in range(0, 18)],
            position="center"
        )
        self.child3_menu.bind()

        self.root.transition.direction = "left" if self.root.current == "login" else "right"
        self.root.transition.duration = .05
        self.root.current = "search"

    def show_date_picker(self):
        date_dialog = MDDatePicker(elevation=50, shadow_color=self.theme_cls.accent_color,
                                   overlay_color=(0, 0, 0, 0), _scale_x=.82, _scale_y=1, text_button_color="black",
                                   title="PERÍODO:", title_input="PERÍODO:",
                                   mode="range", min_year=2022, max_year=2024,
                                   min_date=datetime.date.today(),
                                   max_date=datetime.date(
                                       datetime.date.today().year,
                                       datetime.date.today().month,
                                       datetime.date.today().day + 1),
                                   )

        date_dialog.bind(on_save=self.get_date, on_cancel=self.cancel_date)
        date_dialog.open()

    def get_date(self, instance, value, date_range):
        self.period = date_range
        self.root.get_screen("search").ids.period_button.text = \
            f"[b]{self.period[0].strftime('%d/%m')} à {self.period[-1].strftime('%d/%m')}[/b]"

    def cancel_date(self, instance, value):
        pass

    def set_adults(self, item):
        self.root.get_screen("search").ids.adults_menu.text = f"[b]{item}[/b]"
        self.root.get_screen("search").ids.adults_menu.text_color = self.theme_cls.primary_color
        self.adults_menu.dismiss()

    def set_children(self, item):
        self.root.get_screen("search").ids.children_menu.text = f"[b]{item}:[/b]"
        self.root.get_screen("search").ids.children_menu.text_color = self.theme_cls.primary_color

        if item == "3 Crianças":

            self.root.get_screen("search").ids.child1_menu.disabled = False
            self.root.get_screen("search").ids.child1_menu.text = "[b]Bebê[/b]"
            self.root.get_screen("search").ids.child1_menu.text_color = self.theme_cls.primary_color
            self.root.get_screen("search").ids.child2_menu.disabled = False
            self.root.get_screen("search").ids.child2_menu.text = "[b]Bebê[/b]"
            self.root.get_screen("search").ids.child2_menu.text_color = self.theme_cls.primary_color
            self.root.get_screen("search").ids.child3_menu.disabled = False
            self.root.get_screen("search").ids.child3_menu.text = "[b]Bebê[/b]"
            self.root.get_screen("search").ids.child3_menu.text_color = self.theme_cls.primary_color

        elif item == "2 Crianças":

            self.root.get_screen("search").ids.child1_menu.disabled = False
            self.root.get_screen("search").ids.child1_menu.text = "[b]Bebê[/b]"
            self.root.get_screen("search").ids.child1_menu.text_color = self.theme_cls.primary_color
            self.root.get_screen("search").ids.child2_menu.disabled = False
            self.root.get_screen("search").ids.child2_menu.text = "[b]Bebê[/b]"
            self.root.get_screen("search").ids.child2_menu.text_color = self.theme_cls.primary_color
            self.root.get_screen("search").ids.child3_menu.disabled = True
            self.root.get_screen("search").ids.child3_menu.text = "[b]-[/b]"
            self.root.get_screen("search").ids.child3_menu.text_color = self.theme_cls.accent_color

        elif item == "1 Criança":

            self.root.get_screen("search").ids.child1_menu.disabled = False
            self.root.get_screen("search").ids.child1_menu.text = "[b]Bebê[/b]"
            self.root.get_screen("search").ids.child1_menu.text_color = self.theme_cls.primary_color
            self.root.get_screen("search").ids.child2_menu.disabled = True
            self.root.get_screen("search").ids.child2_menu.text = "[b]-[/b]"
            self.root.get_screen("search").ids.child2_menu.text_color = self.theme_cls.accent_color
            self.root.get_screen("search").ids.child3_menu.disabled = True
            self.root.get_screen("search").ids.child3_menu.text = "[b]-[/b]"
            self.root.get_screen("search").ids.child3_menu.text_color = self.theme_cls.accent_color

        else:

            self.root.get_screen("search").ids.child1_menu.disabled = True
            self.root.get_screen("search").ids.child1_menu.text = "[b]-[/b]"
            self.root.get_screen("search").ids.child1_menu.text_color = self.theme_cls.accent_color
            self.root.get_screen("search").ids.child2_menu.disabled = True
            self.root.get_screen("search").ids.child2_menu.text = "[b]-[/b]"
            self.root.get_screen("search").ids.child2_menu.text_color = self.theme_cls.accent_color
            self.root.get_screen("search").ids.child3_menu.disabled = True
            self.root.get_screen("search").ids.child3_menu.text = "[b]-[/b]"
            self.root.get_screen("search").ids.child3_menu.text_color = self.theme_cls.accent_color

            self.root.get_screen("search").ids.children_menu.text_color = self.theme_cls.accent_color

        self.children_menu.dismiss()

    def set_child1(self, item):
        self.root.get_screen("search").ids.child1_menu.text = f"[b]{item}[/b]"
        self.child1_menu.dismiss()

    def set_child2(self, item):
        self.root.get_screen("search").ids.child2_menu.text = f"[b]{item}[/b]"
        self.child2_menu.dismiss()

    def set_child3(self, item):
        self.root.get_screen("search").ids.child3_menu.text = f"[b]{item}[/b]"
        self.child3_menu.dismiss()

    def gather_info(self):

        if self.root.get_screen("search").ids.period_button.text == "[b]Período[/b]":
            self.root.get_screen("search").ids.search_alert.color = 1, 0, 0, 1
            self.root.get_screen("search").ids.search_alert.text = "Defina o Período!"

        elif self.root.get_screen("search").ids.adults_menu.text == "[b]Adultos[/b]":
            self.root.get_screen("search").ids.search_alert.color = 1, 0, 0, 1
            self.root.get_screen("search").ids.search_alert.text = "Defina o Número de Adultos!"

        else:

            self.root.get_screen("search").ids.search_alert.color = 0, 1, 0, 1
            self.root.get_screen("search").ids.search_alert.text = "Carregando..."

            self.period = f"&checkin={self.period[0].strftime('%d/%m/%Y')}&checkout={self.period[-1].strftime('%d/%m/%Y')}"

            self.adults = f"&adults={self.root.get_screen('search').ids.adults_menu.text[3]}"

            if self.root.get_screen("search").ids.children_menu.text != "[b]Crianças:[/b]":
                self.children = f"&children={self.root.get_screen('search').ids.children_menu.text[3]}"
            else:
                self.children = ""

            if self.root.get_screen("search").ids.child1_menu.text != "[b]-[/b]":
                age = ""
                for char in self.root.get_screen('search').ids.child1_menu.text:
                    if char.isdigit():
                        age += char
                self.child1 = f"&childrenage={age}" \
                    if self.root.get_screen("search").ids.child1_menu.text != "[b]Bebê[/b]" else "&childrenage=0"
            else:
                self.child1 = ""

            if self.root.get_screen("search").ids.child2_menu.text != "[b]-[/b]":
                age = ""
                for char in self.root.get_screen('search').ids.child1_menu.text:
                    if char.isdigit():
                        age += char
                self.child1 = f"&childrenage={age}" \
                    if self.root.get_screen("search").ids.child2_menu.text != "[b]Bebê[/b]" else "&childrenage=0"
            else:
                self.child2 = ""

            if self.root.get_screen("search").ids.child3_menu.text != "[b]-[/b]":
                age = ""
                for char in self.root.get_screen('search').ids.child1_menu.text:
                    if char.isdigit():
                        age += char
                self.child1 = f"&childrenage={age}" \
                    if self.root.get_screen("search").ids.child3_menu.text != "[b]Bebê[/b]" else "&childrenage=0"
            else:
                self.child3 = ""

            if self.root.get_screen("search").ids.promo_field.text != "":
                self.promo = f"&promocode={self.root.get_screen('search').ids.promo_field.text}"
            else:
                self.promo = ""

            self.url = f"https://hbook.hsystem.com.br/booking?companyId=5cbe1acdab41d514844a5ac0{self.period}{self.adults}{self.children}{self.child1}{self.child2}{self.child3}{self.promo}&utm_source=website&utm_medium=search-box&utm_campaign=website"

    def call_result(self):
        if self.root.current == "search":
            self.root.get_screen("search").ids.search_alert.color = 0, 1, 0, 1
            self.root.get_screen("search").ids.search_alert.text = "Carregando..."
        else:
            self.root.get_screen("send").ids.send_alert.color = 0, 1, 0, 1
            self.root.get_screen("send").ids.send_alert.text = "Carregando..."

        self.root.get_screen("result").ids.result_alert.text = ""
        self.root.transition.direction = "left" if self.root.current == "search" else "right"
        self.root.transition.duration = .05
        self.root.current = "result"

    def call_send(self):
        self.root.get_screen("result").ids.result_alert.color = 0, 1, 0, 1
        self.root.get_screen("result").ids.result_alert.text = "Carregando..."

        self.root.get_screen("send").ids.send_alert.text = ""
        self.root.transition.direction = "left" if self.root.current == "result" else "right"
        self.root.transition.duration = .05
        self.root.current = "send"

    def call_history(self):
        self.root.get_screen("login").ids.login_alert.color = 0, 1, 0, 1
        self.root.get_screen("login").ids.login_alert.text = "Carregando..."

        self.root.get_screen("history").ids.history_alert.text = ""
        self.root.transition.direction = "right" if self.root.current == "login" else "left"
        self.root.transition.duration = .05
        self.root.current = "history"

    def call_print(self):
        pass

    def build(self):
        Window.size = (270, 600)
        # self.title = "Cotações"
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Green"
        self.theme_cls.accent_palette = "Gray"
        return Builder.load_file("main.kv")


QuotationApp().run()
