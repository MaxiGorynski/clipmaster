import tkinter as tk
from tkinter import font as tkfont
import pyperclip
import threading
import time


class ClipboardManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Clipboard History")
        self.root.geometry("500x300")
        self.root.resizable(True, True)

        # Configure styles
        self.default_font = tkfont.Font(family="Helvetica", size=10)
        self.root.option_add("*Font", self.default_font)

        # History storage (max 5 items)
        self.clipboard_history = []
        self.max_history = 5

        # Create GUI elements
        self.create_widgets()

        # Start the clipboard monitoring thread
        self.stop_monitoring = False
        self.monitor_thread = threading.Thread(target=self.monitor_clipboard)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()

        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def create_widgets(self):
        # Create frame
        main_frame = tk.Frame(self.root, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = tk.Label(main_frame, text="Clipboard History",
                               font=tkfont.Font(family="Helvetica", size=14, weight="bold"))
        title_label.pack(pady=(0, 10))

        # Instructions
        instructions = tk.Label(main_frame, text="Click on an item to copy it back to clipboard")
        instructions.pack(pady=(0, 10))

        # Clipboard history items frame
        self.history_frame = tk.Frame(main_frame)
        self.history_frame.pack(fill=tk.BOTH, expand=True)

        # Clear button
        clear_button = tk.Button(main_frame, text="Clear History", command=self.clear_history)
        clear_button.pack(pady=(10, 0))

        # Initial update of history display
        self.update_history_display()

    def monitor_clipboard(self):
        last_clipboard_content = pyperclip.paste()

        while not self.stop_monitoring:
            try:
                # Get current clipboard content
                current_clipboard_content = pyperclip.paste()

                # Check if clipboard has changed
                if current_clipboard_content != last_clipboard_content:
                    # Update last known content
                    last_clipboard_content = current_clipboard_content

                    # Add to history if not empty and not already at the top
                    if current_clipboard_content and (not self.clipboard_history or
                                                      current_clipboard_content != self.clipboard_history[0]):
                        # Add to beginning of list
                        self.clipboard_history.insert(0, current_clipboard_content)

                        # Trim history to max size
                        if len(self.clipboard_history) > self.max_history:
                            self.clipboard_history = self.clipboard_history[:self.max_history]

                        # Update the display
                        self.root.after(100, self.update_history_display)

                # Sleep for a short period before checking again
                time.sleep(0.5)

            except Exception as e:
                print(f"Error monitoring clipboard: {e}")
                time.sleep(1)

    def update_history_display(self):
        # Clear existing widgets in history frame
        for widget in self.history_frame.winfo_children():
            widget.destroy()

        if not self.clipboard_history:
            empty_label = tk.Label(self.history_frame, text="(Clipboard history is empty)")
            empty_label.pack(pady=20)
            return

        # Add each clipboard item as a selectable button/label
        for i, content in enumerate(self.clipboard_history):
            # Create a frame for each item with a border
            item_frame = tk.Frame(self.history_frame, bd=1, relief=tk.RIDGE)
            item_frame.pack(fill=tk.X, padx=5, pady=5)

            # Truncate long content for display
            display_text = content
            if len(display_text) > 50:
                display_text = display_text[:47] + "..."

            # Replace newlines for display
            display_text = display_text.replace('\n', '↵')

            # Create a label for the content
            content_label = tk.Label(item_frame, text=display_text, anchor="w", padx=5, pady=5)
            content_label.pack(fill=tk.X)

            # Bind click event to copy back to main clipboard
            item_frame.bind("<Button-1>", lambda e, idx=i: self.restore_clipboard_item(idx))
            content_label.bind("<Button-1>", lambda e, idx=i: self.restore_clipboard_item(idx))

    def restore_clipboard_item(self, index):
        if 0 <= index < len(self.clipboard_history):
            # Get the content to restore
            content = self.clipboard_history[index]

            # If it's not already at the top, move it there
            if index > 0:
                self.clipboard_history.pop(index)
                self.clipboard_history.insert(0, content)

            # Set it as the current clipboard content
            pyperclip.copy(content)

            # Update the display
            self.update_history_display()

            # Flash background of first item to indicate success
            self.flash_item()

    def flash_item(self):
        if self.history_frame.winfo_children():
            first_item = self.history_frame.winfo_children()[0]
            original_bg = first_item.cget("background")

            # Change background to green
            first_item.configure(background="#AAFFAA")

            # Schedule change back to original
            self.root.after(500, lambda: first_item.configure(background=original_bg))

    def clear_history(self):
        self.clipboard_history = []
        self.update_history_display()

    def on_close(self):
        self.stop_monitoring = True
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = ClipboardManager(root)
    root.mainloop()