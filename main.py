from kivy.config import Config

Config.set('graphics', 'resizable', 0)

from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.uix.behaviors import CommonElevationBehavior

from kivymd.app import MDApp
from kivymd.uix.pickers import MDDatePicker


class LoginScreen(Screen):
    pass


class SearchScreen(Screen):
    pass


class SendScreen(Screen):
    pass


class HistoryScreen(Screen):
    pass


class WindowManager(ScreenManager):
    pass


class QuotationApp(MDApp):
    def build(self):
        Window.size = (270, 600)
        # self.title = "Cotações"
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Green"
        self.theme_cls.accent_palette = "Gray"
        return Builder.load_file("main.kv")

    def call_history(self):
        self.root.transition.direction = "right"
        self.root.current = "history"

    def call_login(self):
        self.root.transition.direction = "right" if self.root.current == "search" else "left"
        self.root.current = "login"

    def get_date(self, instance, value, date_range):
        pass

    def cancel_date(self, instance, value):
        pass

    def show_date_picker(self):
        date_dialog = MDDatePicker(mode="range")
        date_dialog.bind(on_save=self.get_date, on_cancel=self.cancel_date)
        date_dialog.open()


QuotationApp().run()
