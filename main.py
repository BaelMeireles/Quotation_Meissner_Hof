from kivy.config import Config

Config.set('graphics', 'resizable', 0)

import datetime
from kivy.lang import Builder
from kivy.core.window import Window
# from kivy.metrics import dp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.app import MDApp
from kivymd.uix.pickers import MDDatePicker
from kivymd.uix.menu import MDDropdownMenu


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
    adults_menu = None
    children_menu = None
    child1_menu = None
    child2_menu = None
    child3_menu = None

    def call_login(self):
        self.root.get_screen("login").ids.login_alert.text = ""
        self.root.transition.direction = "left" if self.root.current == "history" else "right"
        self.root.transition.duration = .05
        self.root.current = "login"

    def register(self):
        pass
        # self.root.get_screen("login").ids.login_alert.text = "Worked!"

    def call_search(self):
        self.root.get_screen("login").ids.login_alert.color = 0, 1, 0, 1
        self.root.get_screen("login").ids.login_alert.text = "Carregando..."

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

    def call_result(self):
        self.root.transition.direction = "left" if self.root.current == "search" else "right"
        self.root.transition.duration = .05
        self.root.current = "result"

    def call_send(self):
        self.root.transition.direction = "left" if self.root.current == "result" else "right"
        self.root.transition.duration = .05
        self.root.current = "send"

    def call_history(self):
        self.root.transition.direction = "right" if self.root.current == "login" else "left"
        self.root.transition.duration = .05
        self.root.current = "history"

    def build(self):
        Window.size = (270, 600)
        # self.title = "Cotações"
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Green"
        self.theme_cls.accent_palette = "Gray"
        return Builder.load_file("main.kv")


QuotationApp().run()
