from kivy.config import Config

Config.set('graphics', 'resizable', 0)

import datetime
import threading
from kivy.clock import mainthread
import sqlite3
from bs4 import BeautifulSoup
from urllib.error import HTTPError, URLError
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.app import MDApp
from kivymd.uix.pickers import MDDatePicker
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCardSwipe
from kivymd.uix.datatables import MDDataTable
from kivy.metrics import dp
from kivy.properties import StringProperty
from io import BytesIO
import win32clipboard as clip
from PIL import Image


class AdminLoginDialog(MDBoxLayout):
    pass


class UserRegisterDialog(MDBoxLayout):
    pass


class HalfboardCalculateDialog(MDBoxLayout):
    pass


class HalfboardCalculateDialog2(MDBoxLayout):
    pass


class NewMessageDialog(MDBoxLayout):
    pass


class NewDraftDialog(MDBoxLayout):
    pass


class ConfirmDraftDeleteDialog(MDBoxLayout):
    pass


class MessageCard(MDCardSwipe):
    text = StringProperty()


class DraftCard(MDCardSwipe):
    text = StringProperty()


class LoginScreen(Screen):
    pass


class SearchScreen(Screen):
    pass


class DraftsScreen(Screen):
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
    period_ = None
    adults = None
    children = None
    child1 = None
    child2 = None
    child3 = None
    promo = None

    active_user = None
    quotation_number = None

    dialog = None
    new_user = None

    adults_menu = None
    children_menu = None
    child1_menu = None
    child2_menu = None
    child3_menu = None

    can_search = True
    available = []
    messages = []
    new_message = ""
    new_message_instance = None
    delete_draft_instance = None

    con = sqlite3.connect("quotation.db")
    cur = con.cursor()
    cur.execute("""CREATE TABLE if not exists users_info (
                                                        user_number TEXT,
                                                        user_password TEXT,
                                                        user_name TEXT)""")
    cur.execute("""CREATE TABLE if not exists history_info (
                                                        quotation_date TEXT,
                                                        quotation_user TEXT,
                                                        quotation_number TEXT)""")
    cur.execute("""CREATE TABLE if not exists drafts (draft TEXT)""")
    con.commit()

    history_check = cur.execute("SELECT quotation_user FROM history_info WHERE quotation_user='ADMINISTRADOR'")

    if history_check.fetchone() is None:
        current_time = datetime.datetime.now()
        now = f"{current_time.day}/{current_time.month}/{current_time.year}  {current_time.hour}:{current_time.minute}:{current_time.second}"
        cur.execute("""INSERT INTO history_info (quotation_date, quotation_user, quotation_number)
                                        VALUES (?, 'ADMINISTRADOR', '0000000000000')""", [now])
        con.commit()

    drafts_check = cur.execute(
        "SELECT draft FROM drafts WHERE draft='Aceitamos pagamentos em até 4x sem juros no cartão, ou podemos fazer um desconto de 10% em pagamento à vista, sendo o pagamento 30% em depósito bancário e o restante em espécie no check-in.'")

    if drafts_check.fetchone() is None:
        cur.execute(
            """INSERT INTO drafts VALUES ('Aceitamos pagamentos em até 4x sem juros no cartão, ou podemos fazer um desconto de 10% em pagamento à vista, sendo o pagamento 30% em depósito bancário e o restante em espécie no check-in.')""")
        con.commit()
        cur.execute(
            """INSERT INTO drafts VALUES ('Estamos na Rua Travessa da Pedra nº 2, em Monte Verde (Camanducaia-MG), à 900m da avenida principal.')""")
        con.commit()

    admin_check = cur.execute("SELECT user_name FROM users_info WHERE user_name='ADMINISTRADOR'")

    if admin_check.fetchone() is None:
        cur.execute("""INSERT INTO users_info (user_number, user_password, user_name)
                                        VALUES ('0', '91166863', 'ADMINISTRADOR')""")
        con.commit()

    pull_users = cur.execute("SELECT * FROM users_info")
    pull_users = pull_users.fetchall()

    pull_history = cur.execute("SELECT * FROM history_info")
    pull_history = pull_history.fetchall()

    pull_drafts = cur.execute("SELECT * FROM drafts")
    pull_drafts = pull_drafts.fetchall()

    con.close()

    users_info = {}
    history_info = []
    drafts = []

    for user in pull_users:
        users_info[user[0]] = {"password": user[1], "name": user[2]}

    for quotation in pull_history:
        history_info.append(quotation)

    for draft in pull_drafts:
        drafts.append(draft[0])

    def call_login(self):
        if self.can_search:
            if self.root.current == "history":
                self.root.get_screen("history").ids.history_alert.color = self.theme_cls.primary_color
                self.root.get_screen("history").ids.history_alert.text = "Carregando..."
            else:
                self.root.get_screen("search").ids.search_alert.color = self.theme_cls.primary_color
                self.root.get_screen("search").ids.search_alert.text = "Carregando..."

            self.root.get_screen("login").ids.login_alert.text = ""

            self.root.transition.direction = "left" if self.root.current == "history" else "right"
            self.root.transition.duration = .05
            self.root.current = "login"

            self.root.get_screen("search").ids.period_button.text = "[b]Período[/b]"
            self.set_adults("Adultos")
            self.set_children("Crianças:")
            self.root.get_screen("search").ids.promo_field.text = ""
            self.root.get_screen("search").ids.promo_field.hint_text = "Promoção (opcional)"

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

        if self.root.current == "send" and self.dialog is not None and self.dialog.content_cls.ids.new_message_field.text != "" and self.dialog.content_cls.ids.new_message_field.text.isspace() != True:
            self.dialog.content_cls.ids.new_message_alert.color = self.theme_cls.primary_color
            self.dialog.content_cls.ids.new_message_alert.text = ""
            self.new_message = self.dialog.content_cls.ids.new_message_field.text
            self.add_message(self.new_message_instance)
        elif self.dialog is not None and self.root.current == "send":
            self.dialog.content_cls.ids.new_message_alert.color = 1, 0, 0, 1
            self.dialog.content_cls.ids.new_message_alert.text = "Mensagem Inválida!"
        elif self.root.current == "drafts" and self.dialog is not None and self.dialog.content_cls.ids.new_draft_field.text != "" and self.dialog.content_cls.ids.new_draft_field.text.isspace() != True:
            self.add_draft()

        elif self.dialog is not None and self.root.current == "drafts":
            self.dialog.content_cls.ids.new_draft_alert.color = 1, 0, 0, 1
            self.dialog.content_cls.ids.new_draft_alert.text = "Texto Inválido!"
        else:
            self.root.get_screen("send").ids.send_alert.text = ""
            self.root.get_screen("drafts").ids.drafts_alert.text = ""

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
        if self.can_search:
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
            if self.root.current == "send":
                if self.dialog is None:
                    self.root.get_screen("send").ids.send_alert.text = ""
                else:
                    try:
                        self.dialog.content_cls.ids.new_message_alert.text = ""
                    except:
                        pass
            if self.root.current == "drafts":
                if self.dialog is None:
                    self.root.get_screen("drafts").ids.send_alert.text = ""
                else:
                    try:
                        self.dialog.content_cls.ids.new_draft_alert.text = ""
                    except:
                        pass
            if self.root.current == "history":
                self.root.get_screen("history").ids.history_alert.text = ""

    def login(self):

        if self.root.current == "history":
            self.root.get_screen("history").ids.history_layout.clear_widgets()

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

            self.root.get_screen("login").ids.login_alert.color = self.theme_cls.primary_color
            self.root.get_screen("login").ids.login_alert.text = "Usuário Cadastrado!"

            self.dialog_dismiss("Close")

    def call_search(self):
        if self.root.current == "login":
            self.root.get_screen("login").ids.login_alert.color = self.theme_cls.primary_color
            self.root.get_screen("login").ids.login_alert.text = "Carregando..."

        self.root.get_screen("result").ids.result_layout.clear_widgets()

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
        if self.root.current == "drafts":
            self.root.transition.direction = "up"
            self.root.get_screen("drafts").ids.drafts_layout.clear_widgets()

        self.root.transition.duration = .05
        self.root.current = "search"

    def show_date_picker(self):

        date_dialog = MDDatePicker(elevation=50, shadow_color=self.theme_cls.accent_color,
                                   overlay_color=(0, 0, 0, 0), _scale_x=.82, _scale_y=1, text_button_color="black",
                                   title="PERÍODO:", title_input="PERÍODO:",
                                   mode="range", min_year=2022, max_year=2024,
                                   )
        date_dialog.bind(on_save=self.get_date, on_cancel=self.cancel_date)
        date_dialog.open()

    def get_date(self, instance, value, date_range):
        try:
            self.period = date_range
            self.root.get_screen("search").ids.period_button.text = \
                f"[b]{self.period[0].strftime('%d/%m')} à {self.period[-1].strftime('%d/%m')}[/b]"
        except:
            self.root.get_screen("search").ids.period_button.text = "[b]Período[/b]"

    def cancel_date(self, instance, value):
        pass

    def set_adults(self, item):
        self.root.get_screen("search").ids.adults_menu.text = f"[b]{item}[/b]"
        if item == "Adultos":
            self.root.get_screen("search").ids.adults_menu.text_color = self.theme_cls.accent_color
        else:
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

    def pre_gather_info(self):
        if self.can_search:
            if self.root.get_screen("search").ids.period_button.text == "[b]Período[/b]":
                self.root.get_screen("search").ids.search_alert.color = 1, 0, 0, 1
                self.root.get_screen("search").ids.search_alert.text = "Defina o Período!"

            elif self.root.get_screen("search").ids.adults_menu.text == "[b]Adultos[/b]":
                self.root.get_screen("search").ids.search_alert.color = 1, 0, 0, 1
                self.root.get_screen("search").ids.search_alert.text = "Defina o Número de Adultos!"

            elif self.root.get_screen("search").ids.adults_menu.text == "[b]1 Adulto[/b]" and \
                    self.root.get_screen("search").ids.children_menu.text == "[b]Crianças:[/b]":
                self.root.get_screen("search").ids.search_alert.color = 1, 0, 0, 1
                self.root.get_screen(
                    "search").ids.search_alert.text = "Você definiu apenas 1 adulto.\nDefina também pelo menos 1 criança!"

            else:

                self.root.get_screen("search").ids.search_alert.color = self.theme_cls.primary_color
                self.root.get_screen("search").ids.search_alert.text = "Carregando..."

                self.can_search = False
                threading.Timer(1, self.gather_info).start()

    def gather_info(self):
        try:
            self.period_ = f"&checkin={self.period[0].strftime('%d/%m/%Y')}&checkout={self.period[-1].strftime('%d/%m/%Y')}"

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

            url = f"https://hbook.hsystem.com.br/booking?companyId=5cbe1acdab41d514844a5ac0{self.period_}{self.adults}{self.children}{self.child1}{self.child2}{self.child3}{self.promo}&utm_source=website&utm_medium=search-box&utm_campaign=website"

            options = Options()
            options.add_argument('--headless')
            browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
            browser.get(url)
            soup = BeautifulSoup(browser.page_source, "html.parser")
            rooms = soup.find_all("div", {"class": "room-item"})
            self.available = []
            for room in rooms:
                divs = room.find_all("div", {"class": None})
                _div = []
                for div in divs:
                    if div["style"]:
                        _div.append(div["style"])
                if _div[2][0:-1] == "display: none":
                    room_name = room.find("span", {"class": "room-name"}).text
                    room_breakfast = room.find_all("span", {"class": "item-value primary-color"})[0].text.replace(
                        "\xa0", " ")
                    try:
                        room_halfboard = room.find_all("span", {"class": "item-value primary-color"})[1].text.replace(
                            "\xa0", " ")
                    except:
                        room_halfboard = "INDISPONÍVEL PARA O PERÍODO"
                    self.available.append([room_name, room_breakfast, room_halfboard])
            if len(self.available) > 0:
                self.root.get_screen("search").ids.search_alert.color = self.theme_cls.primary_color
                self.root.get_screen("search").ids.search_alert.text = "Pronto!"
                if self.available[0][2] == "INDISPONÍVEL PARA O PERÍODO":
                    self.halfboard_calculate_dialog()
                else:
                    self.prepare_result()
            else:
                self.root.get_screen("search").ids.search_alert.color = 0, 0, 0, 1
                self.root.get_screen("search").ids.search_alert.text = "Nenhuma acomodação disponível."
            self.can_search = True
        except (HTTPError, URLError):
            self.root.get_screen("search").ids.search_alert.color = 1, 0, 0, 1
            self.root.get_screen("search").ids.search_alert.text = "Erro de conexão!"
            self.can_search = True

    @mainthread
    def halfboard_calculate_dialog(self):
        self.dialog = MDDialog(
            height=20,
            type="custom",
            auto_dismiss=False,
            title="Meia Pensão",
            content_cls=HalfboardCalculateDialog(),
            radius=[24, 0, 24, 0],
            buttons=[
                MDFlatButton(
                    text="NÃO",
                    theme_text_color="Custom",
                    text_color=self.theme_cls.primary_color,
                    on_release=self.halfboard_calculate_dialog2
                ),
                MDFlatButton(
                    text="SIM",
                    theme_text_color="Custom",
                    text_color=self.theme_cls.primary_color,
                    on_release=self.halfboard_calculate
                ),
            ],
        )
        self.dialog.open()

    @mainthread
    def halfboard_calculate_dialog2(self, *args):
        self.dialog_dismiss("Close")
        self.dialog = MDDialog(
            type="custom",
            auto_dismiss=False,
            title="Calcular Automaticamente",
            content_cls=HalfboardCalculateDialog2(),
            radius=[24, 0, 24, 0],
            buttons=[
                MDFlatButton(
                    text="NÃO",
                    theme_text_color="Custom",
                    text_color=self.theme_cls.primary_color,
                    on_release=self.halfboard_remove
                ),
                MDFlatButton(
                    text="SIM",
                    theme_text_color="Custom",
                    text_color=self.theme_cls.primary_color,
                    on_release=self.prepare_result
                ),
            ],
        )
        self.dialog.open()

    def halfboard_remove(self, *args):
        self.dialog_dismiss("Close")
        for room in self.available:
            del room[-1]
        self.root.get_screen("search").ids.search_alert.text = "Meia Pensão Removida"
        self.prepare_result()

    def halfboard_calculate(self, *args):
        self.dialog_dismiss("Close")
        n_person = float(self.adults[-1]) + float(self.children[-1]) if self.children != "" else float(self.adults[-1])
        n_days = (self.period[-1] - self.period[0]).days
        halfboard = 80.00 * (n_person * n_days)
        for room in self.available:
            old = ""
            for char in room[1]:
                if char.isnumeric() or char == ",": old += char
            old = old.replace(",", ".")
            new = float(old) + float(halfboard)
            room[2] = f"R$ {format(new, '.2f')}"
            room[2] = room[2].replace(".", ",")
            if len(room[2]) == 12:
                room[2] = room[2][:6] + "." + room[2][-6:]
            if len(room[2]) == 11:
                room[2] = room[2][:5] + "." + room[2][-6:]
            if len(room[2]) == 10:
                room[2] = room[2][:4] + "." + room[2][-6:]
        self.root.get_screen("search").ids.search_alert.text = "Meia Pensão Incluída"
        self.prepare_result()

    @mainthread
    def prepare_result(self, *args):
        if self.dialog is not None:
            self.dialog_dismiss("Close")

        self.root.get_screen("result").ids.result_layout.add_widget(MDLabel(text=""))
        self.root.get_screen("result").ids.result_layout.add_widget(MDLabel(text=""))

        for room in self.available:
            l = MDLabel(text=room[0])
            self.root.get_screen("result").ids.result_layout.add_widget(l)
            self.root.get_screen("result").ids.result_layout.add_widget(MDLabel(text=""))

            l = MDLabel(text="Pensão Simples:")
            self.root.get_screen("result").ids.result_layout.add_widget(l)
            l = MDLabel(text=room[1])
            self.root.get_screen("result").ids.result_layout.add_widget(l)

            if len(room) == 3:
                l = MDLabel(text="Meia Pensão:")
                self.root.get_screen("result").ids.result_layout.add_widget(l)
                l = MDLabel(text=room[2])
                self.root.get_screen("result").ids.result_layout.add_widget(l)

            self.root.get_screen("result").ids.result_layout.add_widget(MDLabel(text=""))
            self.root.get_screen("result").ids.result_layout.add_widget(MDLabel(text=""))

        self.call_result()

    def call_drafts(self):

        self.root.get_screen("drafts").ids.drafts_alert.text = ""

        if self.can_search:
            for draft in self.drafts:
                self.root.get_screen("drafts").ids.drafts_layout.add_widget(
                    DraftCard(text=draft)
                )

            self.root.transition.direction = "down"
            self.root.transition.duration = .05
            self.root.current = "drafts"

    def new_draft_dialog(self):
        self.dialog = MDDialog(
            type="custom",
            content_cls=NewDraftDialog(),
            radius=[24, 0, 24, 0],
            buttons=[
                MDFlatButton(
                    text="Cancelar",
                    theme_text_color="Custom",
                    text_color=self.theme_cls.primary_color,
                    on_release=self.dialog_dismiss
                ),
                MDFlatButton(
                    text="Adicionar",
                    theme_text_color="Custom",
                    text_color=self.theme_cls.primary_color,
                    on_release=self.on_input_validate
                ),
            ],
        )
        self.dialog.open()

    def add_draft(self):
        self.con = sqlite3.connect("quotation.db")
        self.cur = self.con.cursor()
        new_draft = [self.dialog.content_cls.ids.new_draft_field.text]
        self.cur.execute("""INSERT INTO drafts VALUES (?)""", new_draft)
        self.con.commit()

        pull_drafts = self.cur.execute("SELECT * FROM drafts")
        pull_drafts = pull_drafts.fetchall()
        self.con.close()

        self.drafts = []
        for draft in pull_drafts:
            self.drafts.append(draft[0])
        self.root.get_screen("drafts").ids.drafts_layout.clear_widgets()
        for draft in self.drafts:
            self.root.get_screen("drafts").ids.drafts_layout.add_widget(
                DraftCard(text=draft)
            )
        self.dialog_dismiss("whatever")

    def remove_draft_dialog(self, draft):
        self.delete_draft_instance = draft
        self.dialog = MDDialog(
            height=20,
            type="custom",
            auto_dismiss=False,
            title="Rascunho",
            content_cls=ConfirmDraftDeleteDialog(),
            radius=[24, 0, 24, 0],
            buttons=[
                MDFlatButton(
                    text="NÃO",
                    theme_text_color="Custom",
                    text_color=self.theme_cls.primary_color,
                    on_release=self.dialog_dismiss
                ),
                MDFlatButton(
                    text="SIM",
                    theme_text_color="Custom",
                    text_color=self.theme_cls.primary_color,
                    on_release=self.remove_draft
                ),
            ],
        )
        self.dialog.open()

    def remove_draft(self, *args):
        self.con = sqlite3.connect("quotation.db")
        self.cur = self.con.cursor()
        draft = [self.delete_draft_instance.text]
        self.cur.execute("""DELETE FROM drafts WHERE draft = ?""", draft)
        self.con.commit()

        pull_drafts = self.cur.execute("SELECT * FROM drafts")
        pull_drafts = pull_drafts.fetchall()
        self.con.close()

        self.drafts = []
        for draft in pull_drafts:
            self.drafts.append(draft[0])
        self.root.get_screen("drafts").ids.drafts_layout.clear_widgets()
        for draft in self.drafts:
            self.root.get_screen("drafts").ids.drafts_layout.add_widget(
                DraftCard(text=draft)
            )
        self.dialog_dismiss("whatever")

    def copy_draft(self, instance):

        try:
            clip.OpenClipboard()
            clip.EmptyClipboard()
            clip.SetClipboardText(instance.text, clip.CF_TEXT)
            clip.CloseClipboard()
            self.root.get_screen("drafts").ids.drafts_alert.color = self.theme_cls.primary_color
            self.root.get_screen("drafts").ids.drafts_alert.text = "Copiado!"
            print(instance.text)
        except:
            self.root.get_screen("drafts").ids.drafts_alert.color = 1, 0, 0, 1
            self.root.get_screen("drafts").ids.drafts_alert.text = "Clique novamente"

    def call_result(self):
        self.root.get_screen("send").ids.send_layout.clear_widgets()

        if self.root.current == "search":
            self.root.get_screen("search").ids.search_alert.color = self.theme_cls.primary_color
            self.root.get_screen("search").ids.search_alert.text = "Carregando..."
        else:
            self.root.get_screen("send").ids.send_alert.color = self.theme_cls.primary_color
            self.root.get_screen("send").ids.send_alert.text = "Carregando..."

        self.root.transition.direction = "left" if self.root.current == "search" else "right"
        self.root.transition.duration = .05
        self.root.current = "result"

    def prepare_messages(self):

        self.messages = [
            f"Para o período de {self.period[0].strftime('%d/%m')} à {self.period[-1].strftime('%d/%m')} temos disponíveis as seguintes acomodações:"]

        for room in self.available:
            self.messages.append(room)
            self.messages.append(f"[FOTOS {room[0]}]")

        for i, message in enumerate(self.messages):
            if len(message) == 2 or len(message) == 3:
                info = ""
                if len(message) == 2:
                    info = f"{message[0]}\nTarifa com café da manhã: {message[1]}"
                elif len(message) == 3:
                    info = f"{message[0]}\nTarifa com café da manhã: {message[1]}\nTarifa com meia pensão (café da manhã e jantar): {message[2]}"
                self.messages[i] = info

        self.messages.append(
            "Aceitamos pagamentos em até 4x sem juros no cartão, ou podemos fazer um desconto de 10% em pagamento à vista, sendo o pagamento 30% em depósito bancário e o restante em espécie no check-in.")

        for i, message in enumerate(self.messages):
            self.root.get_screen("send").ids.send_layout.add_widget(
                MessageCard(text=message)
            )
        self.call_send()

    def remove_message(self, instance):

        self.messages.remove(instance.text)
        self.root.get_screen("send").ids.send_layout.clear_widgets()

        for i, message in enumerate(self.messages):
            self.root.get_screen("send").ids.send_layout.add_widget(
                MessageCard(text=message)
            )

    def new_message_dialog(self, instance):
        self.new_message_instance = instance

        self.dialog = MDDialog(
            type="custom",
            content_cls=NewMessageDialog(),
            radius=[24, 0, 24, 0],
            buttons=[
                MDFlatButton(
                    text="Cancelar",
                    theme_text_color="Custom",
                    text_color=self.theme_cls.primary_color,
                    on_release=self.dialog_dismiss
                ),
                MDFlatButton(
                    text="Adicionar",
                    theme_text_color="Custom",
                    text_color=self.theme_cls.primary_color,
                    on_release=self.on_input_validate
                ),
            ],
        )
        self.dialog.open()

    def add_message(self, instance):

        m = 0
        while True:
            if instance.text == self.messages[m]:
                break
            else:
                m += 1

        self.messages = self.messages[:m + 1] + [self.new_message] + self.messages[m + 1:]

        self.root.get_screen("send").ids.send_layout.clear_widgets()

        for i, message in enumerate(self.messages):
            self.root.get_screen("send").ids.send_layout.add_widget(
                MessageCard(text=message)
            )
        self.dialog_dismiss("whatever")

    def call_send(self):
        self.root.get_screen("send").ids.send_alert.text = ""
        self.root.transition.direction = "left" if self.root.current == "result" else "right"
        self.root.transition.duration = .05
        self.root.current = "send"

    def send_messages(self):

        """
           def send_to_clipboard(clip_type, data):
               clip.OpenClipboard()
               clip.EmptyClipboard()
               clip.SetClipboardData(clip_type, data)
               clip.CloseClipboard()

           filepath = 'Ico2.png'
           image = Image.open(filepath)

           output = BytesIO()
           image.convert("RGB").save(output, "BMP")
           data = output.getvalue()[14:]
           output.close()

           send_to_clipboard(clip.CF_DIB, data)
           """

        self.root.get_screen("search").ids.period_button.text = "[b]Período[/b]"
        self.set_adults("Adultos")
        self.set_children("Crianças:")
        self.root.get_screen("search").ids.promo_field.text = ""
        self.root.get_screen("search").ids.promo_field.hint_text = "Promoção (opcional)"

        self.call_search()

    def call_history(self):

        history_table = MDDataTable(
            use_pagination=True,
            size_hint=(1, None),
            height=400,
            column_data=[
                ("Data", dp(20)),
                ("Usuário", dp(30)),
                ("Nº do Hóspede", dp(30))
            ],
            row_data=[quotation for quotation in self.history_info[::-1]],
            sorted_order="DSC",
            elevation=2,
        )
        self.root.get_screen("history").ids.history_layout.add_widget(history_table)

        self.root.get_screen("login").ids.login_alert.color = self.theme_cls.primary_color
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
