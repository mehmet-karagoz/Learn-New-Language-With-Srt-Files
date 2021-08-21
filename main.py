import string
from deep_translator import GoogleTranslator
import pysrt
from kivy.core.window import Window
from kivy.properties import StringProperty, ColorProperty
from kivy.utils import rgba
from kivymd.app import MDApp
from kivymd.theming import ThemableBehavior
from kivymd.toast import toast
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.list import OneLineIconListItem, MDList, OneLineListItem

icons_item = {
    "folder": "My files",
    "star": "Starred",
    "history": "Recent",
    "upload": "Upload",
}

word_list = []


class Processes:

    def read_srt_file(self, path):
        subtitles = pysrt.open(path)
        for sub in subtitles:
            line = sub.text.replace("\n", " ")
            words = line.split(" ")
            for word in words:
                word_list.append(
                    word.translate(str.maketrans('', '', string.punctuation)))

    def translate_word(self, word):
        translated_word = GoogleTranslator(source="auto",
                                           target="tr").translate(word)
        return translated_word


class ItemDrawer(OneLineIconListItem):
    icon = StringProperty()
    text_color = ColorProperty()
    theme_text_color = StringProperty()

    def on_release(self):
        toast("Coming Soon")


class DrawerList(ThemableBehavior, MDList):
    pass


class Word(OneLineListItem):
    actual_word = StringProperty()
    translated_word = StringProperty()

    def on_release(self):
        if self.translated_word == "":
            self.translated_word = Processes().translate_word(self.actual_word)
        if self.text == self.actual_word:
            self.text = self.translated_word
        else:
            self.text = self.actual_word


class SrtApp(MDApp):
    background_color = rgba("#2b2b31")
    start_point = 0
    end_point = 5

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(on_keyboard=self.events)
        self.manager_open = False
        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager,
            select_path=self.select_path,
        )

    def file_manager_open(self):
        self.file_manager.show('/')  # output manager to the screen
        self.manager_open = True

    def select_path(self, path):
        self.exit_manager()
        # TODO: file open
        Processes().read_srt_file(path)
        self.update_word_list()

    def exit_manager(self, *args):
        self.manager_open = False
        self.file_manager.close()

    def events(self, instance, keyboard, keycode, text, modifiers):
        '''Called when buttons are pressed on the mobile device.'''

        if keyboard in (1001, 27):
            if self.manager_open:
                self.file_manager.back()
        return True

    def on_start(self):
        # add options to the list
        for icon_name in icons_item.keys():
            self.root.ids.md_list.add_widget(
                ItemDrawer(icon=icon_name, text=icons_item[icon_name],
                           theme_text_color="Custom",
                           text_color=rgba("#f4f4f4"))
            )

        self.update_word_list()

    def update_word_list(self):
        self.root.ids.word_list.clear_widgets()
        for text in word_list[self.start_point:self.end_point]:
            self.root.ids.word_list.add_widget(
                Word(text=text, actual_word=text)
            )

    @staticmethod
    def btn_learn_words():
        toast("Coming Soon")

    def btn_previous_page(self):
        if self.start_point <= 5:
            self.start_point = 0
            if len(word_list) >= 5:
                self.end_point = self.start_point + 5
            else:
                self.end_point = len(word_list)
        else:
            self.start_point -= 5
            if len(word_list) >= 5:
                self.end_point = self.start_point + 5
            else:
                self.end_point = len(word_list)

        self.update_word_list()

    def btn_next_page(self):
        if self.end_point >= len(word_list):
            self.end_point = len(word_list)
            if len(word_list) >= 5:
                self.start_point = self.end_point - 5
            else:
                self.start_point = 0
        else:
            self.end_point += 5
            if len(word_list) >= 5:
                self.start_point = self.end_point - 5
            else:
                self.start_point = 0
        self.update_word_list()

    def btn_yes(self):
        toast("Coming Soon")

    def btn_no(self):
        toast("Coming Soon")


if __name__ == '__main__':
    SrtApp().run()
