import string
from deep_translator import GoogleTranslator
from kivy.event import ObjectWithUid
import pysrt
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.properties import StringProperty, ColorProperty, ObjectProperty
from kivy.utils import rgba
from kivymd.app import MDApp
from kivymd.theming import ThemableBehavior
from kivymd.toast import toast
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.list import OneLineIconListItem, MDList
from kivymd.uix.card import MDCardSwipe
from kivymd.uix.behaviors import TouchBehavior

icons_item = {
    "folder": "My files",
    "star": "Starred",
    "history": "Recent",
    "upload": "Upload",
}

srt_word_list = []
known_words = []


class Processes:
    def read_srt_file(self, path):
        self.read_known_words()
        subtitles = pysrt.open(path)
        for sub in subtitles:
            line = sub.text.replace("\n", " ")
            words = line.split(" ")
            for word in words:
                temp_word = word.translate(
                    str.maketrans("", "", string.punctuation)
                ).lower()
                if temp_word not in known_words:
                    srt_word_list.append(temp_word)

    def read_known_words(self):
        global known_words
        with open("known_words.txt") as txt_file:
            known_words = txt_file.readlines()

        known_words = [word.lower().replace("\n", "") for word in known_words]

    def translate_word(self, word):
        translated_word = GoogleTranslator(source="auto", target="tr").translate(word)
        return translated_word


class ItemDrawer(OneLineIconListItem):
    icon = StringProperty()
    text_color = ColorProperty()
    theme_text_color = StringProperty()

    def on_release(self):
        toast("Coming Soon")


class DrawerList(ThemableBehavior, MDList):
    pass


class SwipeToLearnWord(MDCardSwipe, TouchBehavior):
    text = StringProperty()
    actual_word = StringProperty()
    translated_word = StringProperty()

    def translate_pressed_text(self):
        if self.translated_word == "":
            self.translated_word = Processes().translate_word(self.actual_word)
        if self.text == self.actual_word:
            self.text = self.translated_word
        else:
            self.text = self.actual_word

    def on_long_touch(self, touch, *args):
        pass


class SrtApp(MDApp):
    background_color = rgba("#2b2b31")
    start_point = 0
    end_point = 5

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_theme = "dark"
        Window.bind(on_keyboard=self.events)
        self.manager_open = False
        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager,
            select_path=self.select_path,
        )

    def build(self):
        self.icon = "icon.png"

    def change_screen(self, screen, *args):
        print(f"Username: {self.root.ids.email.text}")
        print(f"Password: {self.root.ids.password.text}")
        self.root.ids.screen_manager.current = screen

    def file_manager_open(self):
        self.file_manager.show(self.user_data_dir)  # output manager to the screen
        self.manager_open = True

    def select_path(self, path):
        self.exit_manager()
        Processes().read_srt_file(path)
        self.update_word_list()

    def exit_manager(self, *args):
        self.manager_open = False
        self.file_manager.close()

    def events(self, instance, keyboard, keycode, text, modifiers):
        """Called when buttons are pressed on the mobile device."""

        if keyboard in (1001, 27):
            if self.manager_open:
                self.file_manager.back()
        return True

    def on_start(self):
        # add options to the list
        for icon_name in icons_item.keys():
            self.root.ids.md_list.add_widget(
                ItemDrawer(
                    icon=icon_name,
                    text=icons_item[icon_name],
                    theme_text_color="Custom",
                    text_color=rgba("#f4f4f4"),
                )
            )

        self.update_word_list()

    def update_word_list(self):
        self.root.ids.word_list.clear_widgets()
        for text in srt_word_list[self.start_point : self.end_point]:
            self.root.ids.word_list.add_widget(
                SwipeToLearnWord(text=text, actual_word=text)
            )

    def on_swipe_complete(self, instance):
        global srt_word_list
        srt_word_list.remove(instance.actual_word)
        self.root.ids.word_list.remove_widget(instance)

    @staticmethod
    def btn_learn_words():
        toast("Coming Soon")

    def btn_previous_page(self):
        if self.start_point <= 5:
            self.start_point = 0
            if len(srt_word_list) >= 5:
                self.end_point = self.start_point + 5
            else:
                self.end_point = len(srt_word_list)
        else:
            self.start_point -= 5
            if len(srt_word_list) >= 5:
                self.end_point = self.start_point + 5
            else:
                self.end_point = len(srt_word_list)

        self.update_word_list()

    def btn_next_page(self):
        if self.end_point >= len(srt_word_list):
            self.end_point = len(srt_word_list)
            if len(srt_word_list) >= 5:
                self.start_point = self.end_point - 5
            else:
                self.start_point = 0
        else:
            self.end_point += 5
            if len(srt_word_list) >= 5:
                self.start_point = self.end_point - 5
            else:
                self.start_point = 0
        self.update_word_list()

    def btn_yes(self):
        toast("Coming Soon")

    def btn_no(self):
        toast("Coming Soon")

    def switch_theme(self):
        if self.current_theme == "dark":
            toast("Coming Soon")
            self.current_theme = "light"
        else:
            toast("Coming Soon")
            self.current_theme = "dark"


if __name__ == "__main__":
    SrtApp().run()
