import string
from pymongo import MongoClient
from deep_translator import GoogleTranslator
import pysrt
from kivy.core.window import Window
from kivy.properties import StringProperty, ColorProperty
from kivy.utils import rgba
from kivymd.app import MDApp
from kivymd.theming import ThemableBehavior
from kivymd.toast import toast
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.list import OneLineIconListItem, MDList
from kivymd.uix.card import MDCardSwipe
from kivymd.uix.behaviors import TouchBehavior
import os
import dns

res = dns.resolver.Resolver(configure=False)
res.nameservers = ["8.8.8.8"]
dns.resolver.default_resolver = res

client = MongoClient(os.environ.get("MONGODB_URI"))
db = client["learn-with-srt"]
my_collection = db["users"]

icons_item = {
    "folder": "My files",
    "star": "Starred",
    "history": "Recent",
    "upload": "Upload",
}

srt_word_list = set([])
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
                if temp_word not in known_words and not any(
                    map(str.isdigit, temp_word)
                ):
                    srt_word_list.add(temp_word)

    def read_known_words(self):
        global known_words
        with open("known_words.txt") as txt_file:
            temp_words = txt_file.readlines()

        temp_words = [word.lower().replace("\n", "") for word in temp_words]
        known_words.extend(temp_words)

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
    current_user = StringProperty()

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

    def login(self):
        email = self.root.ids.email.text
        password = self.root.ids.password.text
        is_login = False
        check = my_collection.find_one({"email": email})
        check2 = my_collection.find_one({"username": email})
        user = check if check is not None else check2
        if email == "" or password == "":
            toast("Please type your email and password")
        else:
            if user is not None:
                if user["password"] == password:
                    self.root.ids.screen_manager.current = "app"
                    self.current_user = user["username"]
                    global known_words
                    known_words.extend(user["words"])
                    is_login = True
                else:
                    toast("Email or password incorrect!")
            else:
                toast("Email or password incorrect!")
            if not is_login:
                toast("Email or password incorrect!")
        self.root.ids.email.text = ""
        self.root.ids.password.text = ""

    def register(self):
        name = self.root.ids.r_name.text
        username = self.root.ids.r_username.text
        email = self.root.ids.r_email.text
        password = self.root.ids.r_password.text
        check = my_collection.find_one({"username": username})
        check2 = my_collection.find_one({"email": email})

        if check is None and check2 is None:
            self.root.ids.screen_manager.current = "login"
            toast("Now, you can login the app")
            new_user = {
                "name": name,
                "username": username,
                "email": email,
                "password": password,
                "words": [],
            }
            my_collection.insert_one(new_user)
        else:
            if check is not None:
                toast("Username has already been taken")
                self.root.ids.r_username.text = ""
            else:
                toast("Email has already been taken")
                self.root.ids.r_email.text = ""

    def change_screen(self):
        self.root.ids.screen_manager.current = "register"

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
        for text in list(srt_word_list)[self.start_point : self.end_point]:
            self.root.ids.word_list.add_widget(
                SwipeToLearnWord(text=text, actual_word=text)
            )

    def on_swipe_complete(self, instance):
        self.root.ids.word_list.remove_widget(instance)
        global srt_word_list
        srt_word_list.remove(instance.actual_word)
        if instance.actual_word not in known_words:
            known_words.append(instance.actual_word)
        user = my_collection.find_one({"username": self.current_user})
        if instance.actual_word not in user["words"]:
            my_collection.update_one(
                {"username": self.current_user},
                {"$push": {"words": instance.actual_word}},
            )

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
