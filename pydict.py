import sys
import json
from PySide6 import QtCore, QtWidgets


class Parse_Dictionary:
    def __init__(self):
        try:
            with open("words.json", "r") as file:
                self.data = json.load(file)
        except Exception as e:
            print("Error loading words.json:", e)
            sys.exit(1)

    def get_meanings(self, word):
        word = word.upper()

        output = []
        if self.data[word]["MEANINGS"]:
            for meaning in self.data[word]["MEANINGS"]:
                output.append("<br>")

                part_of_speech = meaning[0]
                explanation = meaning[1]
                related_words = meaning[2]
                examples = meaning[3]

                output.append(part_of_speech)
                output.append("<br>")
                output.append(explanation)
                output.append("<br>")

                for related_word in related_words:
                    output.append(related_word)
                    output.append(", ")
                output.pop()
                output.append("<br>")

                for example in examples:
                    output.append(example)
                    output.append(", ")
                output.pop()

                # Only add separator if not the last meaning
                if meaning != self.data[word]["MEANINGS"][-1]:
                    output.append("<br><hr>")
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
        else:
            return "No antonyms found"

        return "".join(output)

    def get_synonym(self, word):
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


class Widget(QtWidgets.QWidget, Parse_Dictionary):
    def __init__(self):
        super().__init__()

        self.parser = self

        self.search_box = QtWidgets.QLineEdit()
        self.search_box.setPlaceholderText("Type to search...")
        self.search_box.textChanged.connect(self.search_box_changed)

        content_widget = QtWidgets.QWidget()
        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setWidget(content_widget)
        self.scroll_area.setWidgetResizable(True)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.search_box)
        self.layout.addWidget(self.scroll_area)

    @QtCore.Slot()
    def search_box_changed(self, word):
        try:
            meanings = self.parser.get_meanings(word)
            anytonyms = self.parser.get_anytonyms(word)
            synonyms = self.parser.get_synonym(word)
        except KeyError:
            pass

        content_widget = QtWidgets.QWidget()
        content_layout = QtWidgets.QVBoxLayout(content_widget)

        word_label = QtWidgets.QLabel(f"<h1>{word.capitalize()}</h1>")
        content_layout.addWidget(word_label)

        try:
            meanings_label = QtWidgets.QLabel(f"<b>Meanings:</b><br>{meanings}")
            meanings_label.setWordWrap(True)
            content_layout.addWidget(meanings_label)

            anytonyms_label = QtWidgets.QLabel(f"<b>Antonyms:</b><br>{anytonyms}")
            anytonyms_label.setWordWrap(True)
            content_layout.addWidget(anytonyms_label)

            synonyms_label = QtWidgets.QLabel(f"<b>Synonyms:</b><br>{synonyms}")
            synonyms_label.setWordWrap(True)
            content_layout.addWidget(synonyms_label)
        except UnboundLocalError:
            pass

        self.scroll_area.setWidget(content_widget)


def main():
    app = QtWidgets.QApplication([])

    widget = Widget()
    widget.setStyleSheet("background-color: #F4F6F8;")
    widget.setWindowTitle("PyDict")
    widget.resize(500, 600)
    widget.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
