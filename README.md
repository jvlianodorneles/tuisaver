# 🎨 TUIsaver

**TUIsaver** is a modern Terminal User Interface (TUI) application built with Python and Textual. It allows you to transform text into beautiful ASCII art instantly, with a focus on ease of use, aesthetic customization, and integration with terminal-based workflows.

![TUIsaver Preview](https://github.com/jvlianodorneles/tuisaver/blob/main/tuisaver.png)

## ✨ Features

- **Instant Preview:** See your ASCII art update in real-time as you type.
- **Multi-line Support:** Create complex designs with up to 3 lines of text.
- **Deep Customization:** 
    - Browse through all available FIGlet fonts.
    - Control Horizontal and Vertical kerning (Full, Fitted, Smushed).
    - **Smart Logic:** Controls are automatically disabled if the chosen font doesn't support kerning.
- **Theme Editor (`Ctrl+T`):** 
    - Full control over the app's color palette.
    - Paste custom themes directly from the clipboard.
    - Integrated link to [AI Colors](https://www.bairesdev.com/tools/ai-colors) for palette inspiration.
- **Workflow Integration:**
    - **Copy to Clipboard:** Instantly copy the result with `Ctrl+C`.
    - **Screensaver Sync:** Set your art as your system screensaver with one click (`Ctrl+S`).
- **Modern UI:** Built with a sleek sidebar layout, high-contrast focus states, and responsive design.

## 🚀 Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/tuisaver.git
   cd tuisaver
   ```

2. **Set up a virtual environment (recommended):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## 🎮 Usage

Launch the application by running:
```bash
python3 tuisaver.py
```

### Keyboard Shortcuts

| Shortcut | Action |
| :--- | :--- |
| `Ctrl + C` | Copy generated art to clipboard |
| `Ctrl + S` | Save art to screensaver path |
| `Ctrl + T` | Open the Theme Editor |
| `Esc` | Close Theme Editor / Cancel |
| `Tab` | Navigate between inputs and buttons |
| `Q` | Quit the application |

## 🎨 Theming

The **Theme Editor** supports a simple variable-based format. You can easily import palettes from tools like [AI Colors](https://www.bairesdev.com/tools/ai-colors) by pasting them into the editor.

Example format:
```css
--primary-100:#1F3A5F;
--accent-100:#3D5A80;
--bg-100:#0F1C2E;
...
```

## 🛠 Dependencies

TUIsaver is made possible thanks to these amazing libraries:
- [Textual](https://github.com/Textualize/textual) - The TUI framework.
- [Pyfiglet](https://github.com/patorjk/figlet.js) - The ASCII art engine.
- [Pyperclip](https://github.com/asweigart/pyperclip) - Clipboard management.
- [Rich](https://github.com/Textualize/rich) - Beautiful terminal formatting.

---
Built with ❤️ for the terminal.
