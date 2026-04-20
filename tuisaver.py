import pyfiglet
import pyperclip
import json
import os
import shutil
import webbrowser
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, TextArea, Static, Select, Label, Button
from textual.reactive import reactive
from textual.screen import ModalScreen
from textual.events import Click
from rich.text import Text

CONFIG_FILE = "config.json"
SCREENSAVER_PATH = "~/.config/omarchy/branding/screensaver.txt"

# Default Theme (Deep Blue)
DEFAULT_THEME = """--primary-100:#1F3A5F;
--primary-200:#4d648d;
--primary-300:#acc2ef;
--accent-100:#3D5A80;
--accent-200:#cee8ff;
--text-100:#FFFFFF;
--text-200:#e0e0e0;
--bg-100:#0F1C2E;
--bg-200:#1f2b3e;
--bg-300:#374357;"""

class ThemeModal(ModalScreen):
    """A modal for editing the application theme."""
    BINDINGS = [("escape", "cancel", "Cancel")]

    def action_cancel(self) -> None:
        self.dismiss(None)

    def compose(self) -> ComposeResult:
        with Vertical(id="modal-container"):
            yield Label("Theme Variables Editor:")
            yield TextArea(id="theme-input", classes="theme-editor")
            yield Static(
                "Find more palettes at: [bold blue underline]https://www.bairesdev.com/tools/ai-colors[/]", 
                id="theme-link", 
                classes="theme-hint"
            )
            with Horizontal(id="modal-buttons"):
                yield Button("Apply", id="apply-theme", variant="success")
                yield Button("Reset", id="reset-theme", variant="primary")
                yield Button("Paste", id="paste-theme", variant="warning")
                yield Button("Cancel", id="cancel-theme", variant="error")

    def on_mount(self) -> None:
        self.query_one("#theme-input", TextArea).text = self.app.custom_theme_str

    def on_click(self, event: Click) -> None:
        """Handle clicks on the link static widget."""
        if event.widget.id == "theme-link":
            webbrowser.open("https://www.bairesdev.com/tools/ai-colors")
            self.app.notify("Opening browser...")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "apply-theme":
            theme_text = self.query_one("#theme-input", TextArea).text
            self.dismiss(theme_text)
        elif event.button.id == "reset-theme":
            self.query_one("#theme-input", TextArea).text = DEFAULT_THEME
        elif event.button.id == "paste-theme":
            try:
                clipboard_content = pyperclip.paste()
                if clipboard_content:
                    self.query_one("#theme-input", TextArea).text = clipboard_content
                    self.app.notify("Clipboard content pasted!")
                else:
                    self.app.notify("Clipboard is empty!", severity="warning")
            except Exception as e:
                self.app.notify(f"Paste failed: {e}", severity="error")
        else:
            self.dismiss(None)

class AsciiArtApp(App):
    TITLE = "TUIsaver"
    SUB_TITLE = "Modern ASCII Art Studio"

    CSS = """
    #modal-container {
        width: 75;
        height: 34;
        background: $panel;
        border: thick $primary;
        padding: 1;
        align: center middle;
    }
    .theme-editor {
        height: 1fr;
        margin-bottom: 0;
    }
    .theme-hint {
        color: $text-muted;
        margin-bottom: 1;
        text-align: center;
    }
    .theme-hint:hover {
        color: $accent;
        text-style: bold;
    }
    #modal-buttons {
        height: auto;
        align: center middle;
    }
    #modal-buttons Button {
        margin: 0 1;
        min-width: 12;
    }
    
    Screen {
        background: #0F1C2E;
        color: #FFFFFF;
    }

    #sidebar {
        width: 50;
        height: 100%;
        background: #1f2b3e;
        border-right: heavy #1F3A5F;
        padding: 1 2;
    }

    #canvas-container {
        height: 1fr;
        padding: 1 2;
        background: #0F1C2E;
    }

    #ascii-frame {
        width: 100%;
        height: 100%;
        border: double #3D5A80;
        background: #0F1C2E;
        overflow: auto auto;
        padding: 1;
    }

    #ascii-output {
        width: auto;
        text-wrap: nowrap;
        color: #cee8ff;
    }

    .section-title {
        text-style: bold;
        color: #acc2ef;
        margin-bottom: 1;
        text-align: center;
    }

    Label {
        color: #e0e0e0;
        margin-top: 1;
        width: 100%;
        text-style: bold;
    }

    TextArea, Select {
        background: #374357;
        color: #FFFFFF;
        border: none;
        width: 100%;
    }

    TextArea { height: 5; }
    Select { height: 3; padding: 0 1; }

    TextArea:focus, Select:focus {
        background: #3D5A80;
        color: #FFFFFF;
    }

    Select:disabled {
        opacity: 0.3;
        background: #1f2b3e;
    }

    .btn-action {
        width: 100%;
        margin-top: 1;
        height: 3;
        text-style: bold;
        border: none;
    }

    #btn-copy { background: #1F3A5F; color: #FFFFFF; }
    #btn-save { background: #4d648d; color: #FFFFFF; }
    #btn-theme { background: #3D5A80; color: #FFFFFF; margin-top: 2; }

    .btn-action:focus {
        background: #acc2ef;
        color: #0F1C2E;
        text-style: bold italic;
    }

    #info-panel {
        margin-top: 1;
        padding: 1;
        background: #1f2b3e;
        color: #cee8ff;
        text-align: center;
        height: 5;
        content-align: center middle;
    }
    """

    BINDINGS = [
        ("ctrl+c", "copy_to_clipboard", "Copy"),
        ("ctrl+s", "save_screensaver", "Set Screensaver"),
        ("ctrl+t", "open_theme_editor", "Theme Editor"),
        ("q", "quit", "Quit"),
    ]

    text = reactive("TUI\nsaver")
    font = reactive("standard")
    h_layout = reactive("default")
    v_layout = reactive("default")
    custom_theme_str = reactive(DEFAULT_THEME)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.figlet_fonts = sorted(pyfiglet.FigletFont.getFonts())
        self.layout_options = [
            ("Default", "default"), ("Full", "full"),
            ("Fitted", "fitted"), ("Smushed", "smushed"),
        ]
        config = self.load_config()
        self.text = config.get("text", "TUI\nsaver")
        self.font = config.get("font", "standard")
        self.h_layout = config.get("h_layout", "default")
        self.v_layout = config.get("v_layout", "default")
        self.custom_theme_str = config.get("theme_str", DEFAULT_THEME)

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f: return json.load(f)
            except: return {}
        return {}

    def save_config(self):
        config = {
            "text": self.text, 
            "font": self.font, 
            "h_layout": self.h_layout, 
            "v_layout": self.v_layout,
            "theme_str": self.custom_theme_str
        }
        try:
            with open(CONFIG_FILE, "w") as f: json.dump(config, f)
        except: pass

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            with Vertical(id="sidebar"):
                yield Static("SETTINGS", classes="section-title")
                
                yield Label("Text (Max 3 lines)")
                yield TextArea(self.text, id="text-input", show_line_numbers=True, soft_wrap=False)
                
                yield Label("Font Style")
                yield Select([(f, f) for f in self.figlet_fonts], value=self.font, id="font-select", allow_blank=False)
                
                yield Label("Horizontal Kerning", id="label-h-kerning")
                yield Select(self.layout_options, value=self.h_layout, id="h-layout-select", allow_blank=False)
                
                yield Label("Vertical Kerning", id="label-v-kerning")
                yield Select(self.layout_options, value=self.v_layout, id="v-layout-select", allow_blank=False)

                yield Button("COPY (Ctrl+C)", id="btn-copy", classes="btn-action")
                yield Button("SET AS SCREENSAVER (Ctrl+S)", id="btn-save", classes="btn-action")
                yield Button("THEME EDITOR (Ctrl+T)", id="btn-theme", classes="btn-action")
                
                yield Static(id="info-panel")

            with Vertical(id="canvas-container"):
                with Container(id="ascii-frame"):
                    yield Static(id="ascii-output")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#text-input").focus()
        self.apply_theme_from_str(self.custom_theme_str)
        self.check_font_support()
        self.update_ascii()

    def action_open_theme_editor(self) -> None:
        self.push_screen(ThemeModal(), self.theme_modal_callback)

    def on_text_area_changed(self, event: TextArea.Changed) -> None:
        if event.text_area.id == "text-input":
            lines = event.text_area.text.split("\n")
            if len(lines) > 3:
                event.text_area.text = "\n".join(lines[:3])
                event.text_area.move_cursor((2, len(lines[2])))
                self.notify("Max 3 lines allowed", severity="warning")
            self.text = event.text_area.text
            self.update_ascii()
            self.save_config()

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.value is None or event.value == Select.BLANK: return
        if event.select.id == "font-select":
            self.font = str(event.value)
            self.check_font_support()
        elif event.select.id == "h-layout-select": self.h_layout = str(event.value)
        elif event.select.id == "v-layout-select": self.v_layout = str(event.value)
        self.update_ascii()
        self.save_config()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-copy": self.copy_result()
        elif event.button.id == "btn-save": self.save_to_screensaver()
        elif event.button.id == "btn-theme":
            self.action_open_theme_editor()

    def theme_modal_callback(self, theme_str: str | None) -> None:
        if theme_str is not None:
            self.custom_theme_str = theme_str
            self.apply_theme_from_str(theme_str)
            self.save_config()
            self.notify("Theme updated!")

    def parse_theme(self, theme_str: str) -> dict:
        colors = {}
        for line in theme_str.split('\n'):
            line = line.strip()
            if line.startswith('--') and ':' in line:
                try:
                    key, val = line.split(':', 1)
                    colors[key.strip()] = val.split(';')[0].strip()
                except: continue
        return colors

    def apply_theme_from_str(self, theme_str: str) -> None:
        colors = self.parse_theme(theme_str)
        if not colors: return
        
        try:
            bg1 = colors.get("--bg-100", "#0F1C2E")
            bg2 = colors.get("--bg-200", "#1f2b3e")
            bg3 = colors.get("--bg-300", "#374357")
            p1 = colors.get("--primary-100", "#1F3A5F")
            p2 = colors.get("--primary-200", "#4d648d")
            p3 = colors.get("--primary-300", "#acc2ef")
            a1 = colors.get("--accent-100", "#3D5A80")
            a2 = colors.get("--accent-200", "#cee8ff")
            t1 = colors.get("--text-100", "#FFFFFF")
            t2 = colors.get("--text-200", "#e0e0e0")

            self.styles.background = bg1
            self.styles.color = t1
            sidebar = self.query_one("#sidebar")
            sidebar.styles.background = bg2
            sidebar.styles.border_right = ("heavy", p1)
            frame = self.query_one("#ascii-frame")
            frame.styles.background = bg1
            frame.styles.border = ("double", a1)
            canvas = self.query_one("#canvas-container")
            canvas.styles.background = bg1
            for label in self.query("Label"): label.styles.color = t2
            for title in self.query(".section-title"): title.styles.color = p3
            for ctrl in self.query("TextArea, Select"):
                ctrl.styles.background = bg3
                ctrl.styles.color = t1
            self.query_one("#ascii-output").styles.color = a2
            self.query_one("#btn-copy").styles.background = p1
            self.query_one("#btn-save").styles.background = p2
            self.query_one("#btn-theme").styles.background = a1
            info = self.query_one("#info-panel")
            info.styles.background = bg2
            info.styles.color = a2
        except: pass

    def check_font_support(self):
        try:
            f = pyfiglet.Figlet(font=self.font)
            supports_kerning = f.Font.smushMode != 64
            h_select, v_select = self.query_one("#h-layout-select", Select), self.query_one("#v-layout-select", Select)
            h_label, v_label = self.query_one("#label-h-kerning", Label), self.query_one("#label-v-kerning", Label)
            h_select.disabled = v_select.disabled = not supports_kerning
            if not supports_kerning:
                h_label.update("Horizontal Kerning (N/A)"); v_label.update("Vertical Kerning (N/A)")
                self.h_layout = self.v_layout = "default"
            else:
                h_label.update("Horizontal Kerning"); v_label.update("Vertical Kerning")
        except: pass

    def update_ascii(self) -> None:
        try:
            f = pyfiglet.Figlet(font=self.font, width=2000)
            if self.h_layout == "full": f.Font.smushMode = -1
            elif self.h_layout == "fitted": f.Font.smushMode = 1
            elif self.h_layout == "smushed": f.Font.smushMode = 2
            result = f.renderText(self.text)
            self.query_one("#ascii-output", Static).update(Text(result, no_wrap=True))
            lines = result.splitlines()
            h, w = len(lines), max(len(line) for line in lines) if lines else 0
            self.query_one("#info-panel", Static).update(f"Canvas: {w}x{h}\nFont: {self.font}")
        except: pass

    def action_copy_to_clipboard(self) -> None: self.copy_result()
    def action_save_screensaver(self) -> None: self.save_to_screensaver()

    def copy_result(self) -> None:
        try:
            f = pyfiglet.Figlet(font=self.font, width=2000)
            if self.h_layout == "full": f.Font.smushMode = -1
            elif self.h_layout == "fitted": f.Font.smushMode = 1
            elif self.h_layout == "smushed": f.Font.smushMode = 2
            pyperclip.copy(f.renderText(self.text))
            self.notify("Art copied to clipboard!")
        except: self.notify("Copy failed", severity="error")

    def save_to_screensaver(self) -> None:
        try:
            f = pyfiglet.Figlet(font=self.font, width=2000)
            if self.h_layout == "full": f.Font.smushMode = -1
            elif self.h_layout == "fitted": f.Font.smushMode = 1
            elif self.h_layout == "smushed": f.Font.smushMode = 2
            content = f.renderText(self.text)
            path = os.path.expanduser(SCREENSAVER_PATH)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            if os.path.exists(path) and not os.path.exists(path + ".bak"):
                shutil.copy2(path, path + ".bak")
                os.chmod(path + ".bak", 0o444)
            with open(path, 'w', encoding='utf-8') as f: f.write(content)
            self.notify("Screensaver updated!")
        except: self.notify("Save failed", severity="error")

if __name__ == "__main__":
    AsciiArtApp().run()
