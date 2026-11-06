
import os
import json
import qrcode

__version__ = "3.0.0"

from io import BytesIO
from datetime import datetime
from PIL import Image as PILImage

from kivy.app import App
from kivy.core.window import Window
from kivy.core.image import Image as CoreImage
from kivy.metrics import dp
from kivy.graphics import Color, RoundedRectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserIconView


# ==========================
# QR STUDIO 3.0 THEME
# ==========================

NAVY = (0.035, 0.055, 0.11, 1)
CARD = (0.075, 0.10, 0.18, 1)
BLUE = (0.15, 0.38, 0.95, 1)
PURPLE = (0.48, 0.25, 0.85, 1)
WHITE = (1, 1, 1, 1)
GREY = (0.65, 0.70, 0.80, 1)

Window.clearcolor = NAVY


# ==========================
# MAIN APPLICATION
# ==========================

class QRStudio(App):

    def build(self):

        self.qr_image = None
        self.logo_path = None
        self.history = []

        self.download_folder = os.path.join(self.user_data_dir, "QR_Codes")
        os.makedirs(self.download_folder, exist_ok=True)

        self.history_file = os.path.join(
            self.download_folder,
            "qr_studio_history.json"
        )

        self.qr_colors = {
            "Blue": ("#2563EB", "#FFFFFF"),
            "Purple": ("#7C3AED", "#FFFFFF"),
            "Black": ("#000000", "#FFFFFF"),
            "Teal": ("#008B8B", "#FFFFFF"),
            "Red": ("#C62828", "#FFFFFF"),
            "Green": ("#167D45", "#FFFFFF")
        }

        self.load_history()

        # Main scrolling interface
        scroll = ScrollView()

        root = BoxLayout(
            orientation="vertical",
            padding=dp(18),
            spacing=dp(13),
            size_hint_y=None
        )

        root.bind(
            minimum_height=root.setter("height")
        )

        scroll.add_widget(root)

               # CUSTOM BRAND HEADER

        header = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(75),
            spacing=dp(12)
        )

        logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "qr_studio_logo.jpg")

        if os.path.exists(logo_path):
            brand_logo = Image(
                source=logo_path,
                size_hint=(None, None),
                size=(dp(55), dp(55)),
                allow_stretch=True,
                keep_ratio=True
            )
            header.add_widget(brand_logo)
        else:
            self.add_label(
                header,
                "◆",
                30, PURPLE, 55
            )

        brand_name = Label(
            text="[b]QR STUDIO[/b]",
            markup=True,
            font_size="27sp",
            color=WHITE,
            halign="left",
            valign="middle"
        )

        header.add_widget(brand_name)
        root.add_widget(header)
 
        self.add_label(
            root,
            "CREATE. CUSTOMIZE. SHARE.",
            12, GREY, 30
        )

        self.add_label(
            root,
            "Create your QR code.",
            25, WHITE, 55
        )

        self.add_label(
            root,
            "Turn links, text and presentations into QR codes.",
            13, GREY, 45
        )

        # CONTENT CARD
        input_card = self.make_card(245)

        self.add_label(
            input_card,
            "YOUR CONTENT",
            14, (0.35, 0.60, 1, 1), 35
        )

        self.input_box = TextInput(
            hint_text="Enter a website link or text...",
            multiline=True,
            size_hint_y=None,
            height=dp(85),
            padding=dp(12),
            background_color=(0.04, 0.07, 0.14, 1),
            foreground_color=WHITE,
            hint_text_color=GREY,
            cursor_color=BLUE
        )

        input_card.add_widget(self.input_box)

        self.color_spinner = Spinner(
            text="Blue",
            values=tuple(self.qr_colors.keys()),
            size_hint_y=None,
            height=dp(45),
            background_normal="",
            background_color=PURPLE,
            color=WHITE
        )

        input_card.add_widget(self.color_spinner)

        root.add_widget(input_card)

        # LOGO SECTION
        logo_card = self.make_card(110)

        self.add_label(
            logo_card,
            "CUSTOM LOGO (OPTIONAL)",
            13, (0.75, 0.50, 1, 1), 35
        )

        logo_button = self.make_button(
            "CHOOSE LOGO IMAGE",
            PURPLE,
            WHITE
        )

        logo_button.bind(
            on_release=self.choose_logo
        )

        logo_card.add_widget(logo_button)

        self.logo_status = Label(
            text="No logo selected",
            color=GREY,
            font_size="11sp",
            size_hint_y=None,
            height=dp(25)
        )

        logo_card.add_widget(self.logo_status)

        root.add_widget(logo_card)

        # GENERATE BUTTON
        generate = self.make_button(
            "GENERATE QR CODE",
            BLUE,
            WHITE
        )

        generate.bind(
            on_release=self.generate_qr
        )

        root.add_widget(generate)

        # PREVIEW CARD
        preview_card = self.make_card(300)

        self.add_label(
            preview_card,
            "QR CODE PREVIEW",
            14, (0.75, 0.50, 1, 1), 35
        )

        self.preview = Image(
            size_hint=(1, 1),
            allow_stretch=True,
            keep_ratio=True
        )

        preview_card.add_widget(self.preview)

        root.add_widget(preview_card)

        # STATUS
        self.status = Label(
            text="Your QR code will appear here.",
            color=GREY,
            font_size="12sp",
            size_hint_y=None,
            height=dp(45)
        )

        root.add_widget(self.status)

        # SAVE BUTTON
        save = self.make_button(
            "SAVE QR CODE",
            PURPLE,
            WHITE
        )

        save.bind(
            on_release=self.save_qr
        )

        root.add_widget(save)

        # HISTORY BUTTON
        history_button = self.make_button(
            "VIEW QR HISTORY",
            CARD,
            WHITE
        )

        history_button.bind(
            on_release=self.show_history
        )

        root.add_widget(history_button)

        self.add_label(
            root,
            "QR STUDIO  |  PREMIUM EDITION"
             "\nCREATED BY JANE",
            10, GREY, 40
        )

        return scroll

    # ==========================
    # INTERFACE HELPERS
    # ==========================

    def add_label(
        self, parent, text, size,
        color, height, markup=False
    ):

        label = Label(
            text=text,
            markup=markup,
            font_size=f"{size}sp",
            color=color,
            size_hint_y=None,
            height=dp(height),
            halign="left",
            valign="middle"
        )

        label.bind(
            size=lambda obj, value:
            setattr(obj, "text_size", value)
        )

        parent.add_widget(label)

        return label

    def make_card(self, height):

        card = BoxLayout(
            orientation="vertical",
            padding=dp(14),
            spacing=dp(10),
            size_hint_y=None,
            height=dp(height)
        )

        with card.canvas.before:
            Color(*CARD)

            card.bg = RoundedRectangle(
                pos=card.pos,
                size=card.size,
                radius=[dp(18)]
            )

        card.bind(
            pos=lambda obj, value:
            setattr(card.bg, "pos", value),
            size=lambda obj, value:
            setattr(card.bg, "size", value)
        )

        return card

    def make_button(
        self, text, background, foreground
    ):

        return Button(
            text=text,
            size_hint_y=None,
            height=dp(52),
            background_normal="",
            background_color=background,
            color=foreground,
            font_size="14sp",
            bold=True
        )

    # ==========================
    # CHOOSE LOGO
    # ==========================

    def choose_logo(self, instance):

        chooser = FileChooserIconView(
            path=self.download_folder,
            filters=["*.png", "*.jpg", "*.jpeg"],
            dirselect=False
        )

        layout = BoxLayout(
            orientation="vertical",
            spacing=dp(8),
            padding=dp(8)
        )

        layout.add_widget(chooser)

        buttons = BoxLayout(
            size_hint_y=None,
            height=dp(48),
            spacing=dp(8)
        )

        select_button = Button(
            text="SELECT",
            background_normal="",
            background_color=BLUE
        )

        cancel_button = Button(
            text="CANCEL",
            background_normal="",
            background_color=PURPLE
        )

        buttons.add_widget(select_button)
        buttons.add_widget(cancel_button)

        layout.add_widget(buttons)

        popup = Popup(
            title="Choose your logo",
            content=layout,
            size_hint=(0.95, 0.85)
        )

        def select_logo(instance):

            if chooser.selection:
                self.logo_path = chooser.selection[0]

                self.logo_status.text = (
                    "Logo selected: " +
                    os.path.basename(self.logo_path)
                )

                popup.dismiss()

        select_button.bind(on_release=select_logo)
        cancel_button.bind(on_release=popup.dismiss)

        popup.open()

    # ==========================
    # GENERATE QR CODE
    # ==========================

    def generate_qr(self, instance):

        data = self.input_box.text.strip()

        if not data:
            self.status.text = "Please enter some content."
            return

        try:

            foreground, background = self.qr_colors[
                self.color_spinner.text
            ]

            qr = qrcode.QRCode(
                version=None,
                box_size=12,
                border=4,
                error_correction=qrcode.constants.ERROR_CORRECT_H
            )

            qr.add_data(data)
            qr.make(fit=True)

            image = qr.make_image(
                fill_color=foreground,
                back_color=background
            ).convert("RGB")

            # ADD OPTIONAL LOGO
            if self.logo_path:

                if os.path.exists(self.logo_path):

                    logo = PILImage.open(
                        self.logo_path
                    ).convert("RGBA")

                    max_size = image.width // 5

                    logo.thumbnail(
                        (max_size, max_size)
                    )

                    padding = max(
                        8, image.width // 40
                    )

                    logo_bg = PILImage.new(
                        "RGBA",
                        (
                            logo.width + padding * 2,
                            logo.height + padding * 2
                        ),
                        (255, 255, 255, 255)
                    )

                    logo_bg.alpha_composite(
                        logo,
                        (padding, padding)
                    )

                    position = (
                        (image.width - logo_bg.width) // 2,
                        (image.height - logo_bg.height) // 2
                    )

                    image.paste(
                        logo_bg.convert("RGB"),
                        position
                    )

                else:
                    self.logo_path = None
                    self.logo_status.text = "Logo file not found."

            self.qr_image = image

            # DISPLAY QR CODE
            buffer = BytesIO()

            image.save(buffer, format="PNG")
            buffer.seek(0)

            texture = CoreImage(
                buffer,
                ext="png"
            ).texture

            self.preview.texture = texture

            self.status.text = (
                "QR code generated successfully!"
            )

        except Exception as error:

            self.status.text = (
                "Generation error: " + str(error)
            )

    # ==========================
    # SAVE QR CODE
    # ==========================

    def save_qr(self, instance):

        if self.qr_image is None:

            self.status.text = "Generate a QR code first."
            return

        try:

            os.makedirs(
                self.download_folder,
                exist_ok=True
            )

            filename = (
                "QR_Studio_" +
                datetime.now().strftime("%Y%m%d_%H%M%S") +
                ".png"
            )

            filepath = os.path.join(
                self.download_folder,
                filename
            )

            self.qr_image.save(filepath)

            # SAVE HISTORY
            self.history.append({
                "name": filename,
                "path": filepath,
                "date": datetime.now().strftime(
                    "%Y-%m-%d %H:%M"
                ),
                "content": self.input_box.text.strip()
            })

            self.save_history()

            self.status.text = (
                "Saved successfully: " + filename
            )

        except Exception as error:

            self.status.text = (
                "Save error: " + str(error)
            )

    # ==========================
    # HISTORY SYSTEM
    # ==========================

    def load_history(self):

        try:

            if os.path.exists(self.history_file):

                with open(
                    self.history_file, "r"
                ) as file:

                    self.history = json.load(file)

        except Exception:
            self.history = []

    def save_history(self):

        try:

            with open(
                self.history_file, "w"
            ) as file:

                json.dump(
                    self.history,
                    file,
                    indent=4
                )

        except Exception:
            pass

    def show_history(self, instance):

        layout = BoxLayout(
            orientation="vertical",
            spacing=dp(8),
            padding=dp(10)
        )

        scroll = ScrollView()

        items = BoxLayout(
            orientation="vertical",
            spacing=dp(8),
            size_hint_y=None
        )

        items.bind(
            minimum_height=items.setter("height")
        )

        if not self.history:

            items.add_widget(
                Label(
                    text="No saved QR codes yet.",
                    size_hint_y=None,
                    height=dp(60)
                )
            )

        else:

            for record in reversed(self.history):

                text = (
                    record.get("name", "QR Code") +
                    "\n" +
                    record.get("date", "")
                )

                button = Button(
                    text=text,
                    size_hint_y=None,
                    height=dp(65),
                    background_normal="",
                    background_color=CARD
                )

                def load_record(
                    instance,
                    item=record
                ):

                    path = item.get("path", "")

                    if os.path.exists(path):

                        self.qr_image = PILImage.open(
                            path
                        ).convert("RGB")

                        buffer = BytesIO()

                        self.qr_image.save(
                            buffer,
                            format="PNG"
                        )

                        buffer.seek(0)

                        self.preview.texture = CoreImage(
                            buffer,
                            ext="png"
                        ).texture

                        self.status.text = (
                            "Previous QR code loaded."
                        )

                        popup.dismiss()

                button.bind(on_release=load_record)

                items.add_widget(button)

        scroll.add_widget(items)
        layout.add_widget(scroll)

        close = Button(
            text="CLOSE",
            size_hint_y=None,
            height=dp(45),
            background_normal="",
            background_color=PURPLE
        )

        layout.add_widget(close)

        popup = Popup(
            title="QR CODE HISTORY",
            content=layout,
            size_hint=(0.95, 0.8)
        )

        close.bind(on_release=popup.dismiss)

        popup.open()


# ==========================
# RUN APPLICATION
# ==========================

if __name__ == "__main__":

    QRStudio().run()
