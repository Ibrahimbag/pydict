import sys
import json
import pyttsx3
import sqlite3
import webbrowser
from functools import partial
from PySide6.QtCore import Slot, QRegularExpression, Qt
from PySide6.QtGui import QIcon, QRegularExpressionValidator
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QLineEdit,
    QLabel,
    QPushButton,
    QScrollArea,
    QHBoxLayout,
    QErrorMessage,
    QComboBox,
    QCompleter
)

ONLINE_DICTIONARIES = {
    "Search online": "",
    "Britannica": "https://www.britannica.com/dictionary/",
    "Cambridge": "https://dictionary.cambridge.org/dictionary/english/",
    "Collins": "https://www.collinsdictionary.com/dictionary/english/",
    "Dictionary.com": "https://www.dictionary.com/browse/",
    "Longman": "https://www.ldoceonline.com/dictionary/",
    "Merriam-Webster": "https://www.merriam-webster.com/dictionary/",
    "Oxford": "https://www.oed.com/search/dictionary/?scope=Entries&q=",
    "Oxford Learners": "https://www.oxfordlearnersdictionaries.com/definition/english/",
    "Wiktionary": "https://en.wiktionary.org/wiki/",
}


class Bookmarks_Db:
    def __init__(self):
        self.conn = sqlite3.connect("bookmarks.db")

        self.sql_statements = {
            "create_table": """CREATE TABLE IF NOT EXISTS word_list (
                word TEXT UNIQUE NOT NULL
            );""",
            "select_words": "SELECT word FROM word_list",
            "insert_word": "INSERT INTO word_list(word) VALUES(?)",
            "delete_word": "DELETE FROM word_list WHERE word == ?",
        }

    def select_words(self):
        cursor = self.conn.cursor()
        cursor.execute(self.sql_statements["select_words"])
        return cursor.fetchall()

    def create_db(self):
        cursor = self.conn.cursor()
        cursor.execute(self.sql_statements["create_table"])
        self.conn.commit()

    def insert_db(self, word):
        cursor = self.conn.cursor()
        try:
            cursor.execute(self.sql_statements["insert_word"], (word,))
            self.conn.commit()
        except sqlite3.IntegrityError:
            return False
        return True

    def delete_db(self, word):
        cursor = self.conn.cursor()
        cursor.execute(self.sql_statements["delete_word"], (word,))
        self.conn.commit()

    def close_db(self):
        self.conn.close()


class Parse_Dictionary:
    def __init__(self):
        try:
            with open("words.json", "r") as file:
                self.data = json.load(file)
        except Exception as e:
            print("Error loading words.json:", e)
            sys.exit(1)

        self.words = [word.lower() for word in self.data.keys()]

    def get_meanings(self, word):
        word = word.upper()

        output = []
        if self.data[word]["MEANINGS"]:
            for meaning in self.data[word]["MEANINGS"]:
                output.append("<br>")

                part_of_speech = meaning[0]
                definition = meaning[1]
                related_words = meaning[2]
                examples = meaning[3]

                if part_of_speech:
                    output.append(part_of_speech)
                    output.append("<br><br>")
                if definition:
                    output.append(definition)
                    output.append("<br><br>")

                output.append("Related words:<br>")
                for related_word in related_words:
                    output.append(related_word)
                    output.append(", ")
                output.pop()
                if related_words:
                    output.append("<br><br>")

                output.append("Examples:<br>")
                for example in examples:
                    output.append(example)
                    output.append("<br><br>")
                output.pop()

                # Only add separator if not the last meaning
                if meaning != self.data[word]["MEANINGS"][-1]:
                    output.append("<br><hr>")
                else:
                    output.append("<br>")
        else:
            return "No meanings found"

        return "".join(output)

    def get_anytonyms(self, word):
        word = word.upper()

        output = []
        if self.data[word]["ANTONYMS"]:
            for antonym in self.data[word]["ANTONYMS"]:
                output.append(antonym)
                output.append(", ")
            output.pop()
        else:
            return "No antonyms found"

        return "".join(output)

    def get_synonyms(self, word):
        word = word.upper()

        output = []
        if self.data[word]["SYNONYMS"]:
            for synonym in self.data[word]["SYNONYMS"]:
                output.append(synonym)
                output.append(", ")
            output.pop()
        else:
            return "No synonyms found"

        return "".join(output)


class Widget(QWidget, Parse_Dictionary, Bookmarks_Db):
    def __init__(self):
        QWidget.__init__(self)
        Parse_Dictionary.__init__(self)
        Bookmarks_Db.__init__(self)

        completer = QCompleter(self.words)
        completer.setCaseSensitivity(Qt.CaseInsensitive)

        self.search_box = QLineEdit()
        self.search_box.setCompleter(completer)
        validator = QRegularExpressionValidator(QRegularExpression(r"[a-zA-Z0-9-\.']+"))
        self.search_box.setValidator(validator)
        self.search_box.setPlaceholderText("Type to search...")
        self.search_box.textChanged.connect(self.search_box_changed)

        bookmarks_button = QPushButton("Bookmarks")
        bookmarks_button.clicked.connect(self.bookmarks_button_clicked)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        content_widget = QWidget()
        layout1 = QHBoxLayout(content_widget)
        layout1.setContentsMargins(0, 0, 0, 0)
        content_widget2 = QWidget()
        layout2 = QVBoxLayout(content_widget2)
        layout2.setContentsMargins(0, 0, 0, 0)

        layout1.addWidget(self.search_box)
        layout1.addWidget(bookmarks_button)
        layout2.addWidget(self.scroll_area)

        layout = QVBoxLayout(self)
        layout.addWidget(content_widget)
        layout.addWidget(content_widget2)

    @Slot()
    def search_box_changed(self, word):
        self.word = word

        try:
            meanings = self.get_meanings(word)
            anytonyms = self.get_anytonyms(word)
            synonyms = self.get_synonyms(word)
        except KeyError:
            pass

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)

        word_label = QLabel(f"<h1>{word.capitalize()}</h1>")
        content_layout.addWidget(word_label)

        button_layout = QHBoxLayout()

        tts_button = QPushButton("")
        tts_button.clicked.connect(self.tts_button_click)
        tts_button.setFixedSize(24, 24)
        tts_icon = QIcon("assets/volume-icon.png")
        tts_button.setIcon(tts_icon)
        tts_button.setToolTip("Read this word")
        button_layout.addWidget(tts_button)

        bookmark_button = QPushButton("")
        bookmark_button.clicked.connect(self.add_bookmark_button_click)
        bookmark_button.setFixedSize(24, 24)
        bookmark_icon = QIcon("assets/bookmark.png")
        bookmark_button.setIcon(bookmark_icon)
        bookmark_button.setToolTip("Bookmark this word")
        button_layout.addWidget(bookmark_button)

        self.combo_box = QComboBox()
        self.combo_box.addItems(ONLINE_DICTIONARIES.keys())
        model = self.combo_box.model()
        item = model.item(0)
        item.setEnabled(False)
        self.combo_box.currentIndexChanged.connect(self.combo_box_changed)
        button_layout.addWidget(self.combo_box)

        content_layout.addLayout(button_layout)

        try:
            meanings_label = QLabel(f"<b>Meanings:</b><br>{meanings}")
            meanings_label.setWordWrap(True)
            content_layout.addWidget(meanings_label)

            anytonyms_label = QLabel(f"<b>Antonyms:</b><br>{anytonyms}")
            anytonyms_label.setWordWrap(True)
            content_layout.addWidget(anytonyms_label)

            synonyms_label = QLabel(f"<b>Synonyms:</b><br>{synonyms}")
            synonyms_label.setWordWrap(True)
            content_layout.addWidget(synonyms_label)
        except UnboundLocalError:
            pass

        self.scroll_area.setWidget(content_widget)

    @Slot()
    def bookmarks_button_clicked(self):
        words = self.select_words()
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        self.search_box.setText("")
        for word in words:
            word = word[0].capitalize()
            button = QPushButton(word)
            button.clicked.connect(partial(self.search_box_changed, word))
            content_layout.addWidget(button)
        self.scroll_area.setWidget(content_widget)

    @Slot()
    def tts_button_click(self):
        try:
            pyttsx3.speak(self.word)
        except:
            pass

    @Slot()
    def add_bookmark_button_click(self):
        try:
            self.create_db()
            word = self.word.capitalize()
            success = self.insert_db(word)
            if not success:
                self.delete_db(word)
        except sqlite3.Error as e:
            print(e)
            # NOTE: This only works with Python version 3.11 and above
            QErrorMessage(self).showMessage(
                e.sqlite_errorcode + " " + e.sqlite_errorname
            )

    @Slot()
    def combo_box_changed(self, index):
        webbrowser.open(
            f"{ONLINE_DICTIONARIES[self.combo_box.itemText(index)]}{self.word.lower()}"
        )


def main():
    app = QApplication([])

    widget = Widget()
    widget.setWindowTitle("PyDict")
    widget.resize(500, 600)
    widget.show()

    ret = app.exec()
    widget.close_db()
    sys.exit(ret)


if __name__ == "__main__":
    main()
