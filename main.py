from kivy.config import Config

Config.set('graphics', 'resizable', 0)

import datetime
from kivy.lang import Builder
from kivy.core.window import Window
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
    childs = None
    child1 = None
    child2 = None
    child3 = None

    def call_login(self):
        self.root.transition.direction = "right" if self.root.current == "search" else "left"
        self.root.current = "login"

    def register(self):
        pass
        # self.root.get_screen("login").ids.login_alert.text = "Worked!"

    def call_search(self):
        self.root.transition.direction = "right"
        self.root.current = "search"

    def call_result(self):
        self.root.transition.direction = "right"
        self.root.current = "result"

    def call_history(self):
        self.root.transition.direction = "right"
        self.root.transition.duration = .05
        self.root.current = "history"

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
        self.root.get_screen("search").ids.period_confirm_button.text = \
            f"{self.period[0].strftime('%d/%m')} à {self.period[-1].strftime('%d/%m')}"

    def cancel_date(self, instance, value):
        pass

    def build(self):
        Window.size = (270, 600)
        # self.title = "Cotações"
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Green"
        self.theme_cls.accent_palette = "Gray"
        return Builder.load_file("main.kv")


QuotationApp().run()
