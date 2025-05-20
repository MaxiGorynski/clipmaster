import tkinter as tk
from tkinter import font as tkfont
import pyperclip
import threading
import time


class ClipboardManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Clipboard History")
        self.root.geometry("550x500")  # Made slightly wider and taller
        self.root.resizable(True, True)

        # Configure styles
        self.default_font = tkfont.Font(family="Helvetica", size=10)
        self.root.option_add("*Font", self.default_font)

        # History storage (max 10 items)
        self.clipboard_history = []
        self.max_history = 10
        self.current_clipboard = ""

        # Flag to ignore clipboard changes triggered by our app
        self.ignore_next_clipboard_change = False

        # Track expanded items
        self.expanded_items = set()

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
        # Main container frame
        main_frame = tk.Frame(self.root, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = tk.Label(main_frame, text="Clipboard Manager",
                               font=tkfont.Font(family="Helvetica", size=14, weight="bold"))
        title_label.pack(pady=(0, 10))

        # Current clipboard section
        current_section_label = tk.Label(main_frame, text="Currently Clipped Item",
                                         font=tkfont.Font(family="Helvetica", size=12, weight="bold"))
        current_section_label.pack(anchor="w", pady=(0, 5))

        # Current clipboard frame with border
        self.current_frame = tk.Frame(main_frame, bd=2, relief=tk.GROOVE)
        self.current_frame.pack(fill=tk.X, pady=(0, 15))

        # History section label
        history_section_label = tk.Label(main_frame, text="Clipboard History (Last 10 Items)",
                                         font=tkfont.Font(family="Helvetica", size=12, weight="bold"))
        history_section_label.pack(anchor="w", pady=(0, 5))

        # Instructions
        instructions = tk.Label(main_frame, text="Click on an item to copy it to clipboard")
        instructions.pack(pady=(0, 10))

        # Create a frame with scrollbar for history items
        history_container = tk.Frame(main_frame)
        history_container.pack(fill=tk.BOTH, expand=True)

        # Add scrollbar
        scrollbar = tk.Scrollbar(history_container)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Canvas for scrolling
        self.history_canvas = tk.Canvas(history_container)
        self.history_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Configure scrollbar
        scrollbar.config(command=self.history_canvas.yview)
        self.history_canvas.config(yscrollcommand=scrollbar.set)

        # Frame within canvas for history items
        self.history_frame = tk.Frame(self.history_canvas)
        self.history_canvas.create_window((0, 0), window=self.history_frame, anchor="nw", tags="self.history_frame")

        # Configure scrolling behavior
        self.history_frame.bind("<Configure>",
                                lambda e: self.history_canvas.configure(scrollregion=self.history_canvas.bbox("all")))

        # Buttons frame
        buttons_frame = tk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=(10, 0))

        # Clear button
        clear_button = tk.Button(buttons_frame, text="Clear History", command=self.clear_history)
        clear_button.pack(side=tk.RIGHT, padx=5)

        # Initial update of displays
        self.update_current_display()
        self.update_history_display()

    def monitor_clipboard(self):
        last_clipboard_content = pyperclip.paste()
        self.current_clipboard = last_clipboard_content

        while not self.stop_monitoring:
            try:
                # Get current clipboard content
                current_clipboard_content = pyperclip.paste()

                # Check if clipboard has changed
                if current_clipboard_content != last_clipboard_content:
                    # Update last known content
                    last_clipboard_content = current_clipboard_content
                    self.current_clipboard = current_clipboard_content

                    # Only add to history if not initiated by our app
                    if not self.ignore_next_clipboard_change:
                        # Add to history if not empty and not already in history
                        if current_clipboard_content and current_clipboard_content not in self.clipboard_history:
                            # Add to beginning of list (newest first)
                            self.clipboard_history.insert(0, current_clipboard_content)

                            # Trim history to max size
                            if len(self.clipboard_history) > self.max_history:
                                self.clipboard_history = self.clipboard_history[:self.max_history]

                            # Update the displays
                            self.root.after(100, self.update_history_display)
                    else:
                        # Reset the flag
                        self.ignore_next_clipboard_change = False

                    # Always update the current display
                    self.root.after(100, self.update_current_display)

                # Sleep for a short period before checking again
                time.sleep(0.5)

            except Exception as e:
                print(f"Error monitoring clipboard: {e}")
                time.sleep(1)

    def update_current_display(self):
        # Clear existing widgets in current frame
        for widget in self.current_frame.winfo_children():
            widget.destroy()

        if not self.current_clipboard:
            empty_label = tk.Label(self.current_frame, text="(Empty)", padx=10, pady=10)
            empty_label.pack(fill=tk.X)
            return

        # Create a display for the current clipboard content
        display_text = self.current_clipboard
        if len(display_text) > 100:
            display_text = display_text[:97] + "..."

        # Replace newlines for display
        display_text = display_text.replace('\n', '↵')

        # Create a label for the content
        content_label = tk.Label(self.current_frame, text=display_text, anchor="w", padx=10, pady=10, wraplength=500)
        content_label.pack(fill=tk.X)

    def update_history_display(self):
        # Clear existing widgets in history frame
        for widget in self.history_frame.winfo_children():
            widget.destroy()

        # Clear expanded items set when refreshing the display
        self.expanded_items = set()

        if not self.clipboard_history:
            empty_label = tk.Label(self.history_frame, text="(Clipboard history is empty)", padx=10, pady=10)
            empty_label.pack(pady=20)
            return

        # Add each clipboard item as a selectable button/label
        for i, content in enumerate(self.clipboard_history):
            # Create a frame for each item
            item_container = tk.Frame(self.history_frame)
            item_container.pack(fill=tk.X, padx=5, pady=5)

            # Main item frame with border
            item_frame = tk.Frame(item_container, bd=1, relief=tk.RIDGE)
            item_frame.pack(fill=tk.X)

            # Top row with summary and buttons
            top_row = tk.Frame(item_frame)
            top_row.pack(fill=tk.X)

            # Truncate long content for display
            display_text = content
            if len(display_text) > 50:
                display_text = display_text[:47] + "..."

            # Replace newlines for display
            display_text = display_text.replace('\n', '↵')

            # Add item number
            item_text = f"{i + 1}. {display_text}"

            # Create a label for the content in the top row
            content_label = tk.Label(top_row, text=item_text, anchor="w", padx=5, pady=5)
            content_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

            # Create an expand button
            expand_button = tk.Button(top_row, text="Expand", padx=5,
                                      command=lambda idx=i: self.toggle_expand_item(idx))
            expand_button.pack(side=tk.RIGHT, padx=5, pady=3)

            # Create a container for the expanded content (initially empty)
            expanded_container = tk.Frame(item_frame)
            expanded_container.pack(fill=tk.X, expand=True)

            # Store reference to the container in the item frame
            item_frame.expanded_container = expanded_container

            # Bind click event to copy back to main clipboard (only on the content label)
            content_label.bind("<Button-1>", lambda e, idx=i: self.restore_clipboard_item(idx))

            # Save references for later access
            item_frame.index = i
            item_frame.expand_button = expand_button

    def toggle_expand_item(self, index):
        # Find the item frame for this index
        for widget in self.history_frame.winfo_children():
            item_frame = widget.winfo_children()[0]  # Get the item_frame from the container

            if hasattr(item_frame, 'index') and item_frame.index == index:
                expanded_container = item_frame.expanded_container
                expand_button = item_frame.expand_button

                # Check if this item is already expanded
                if index in self.expanded_items:
                    # Collapse it - destroy all widgets in the expanded container
                    for widget in expanded_container.winfo_children():
                        widget.destroy()
                    self.expanded_items.remove(index)
                    expand_button.config(text="Expand")

                    # Make sure the container takes no space when collapsed
                    expanded_container.pack_forget()
                else:
                    # Expand it
                    self.expanded_items.add(index)
                    expand_button.config(text="Collapse")

                    # Ensure the container is packed
                    expanded_container.pack(fill=tk.X, expand=True)

                    # Get the full content
                    content = self.clipboard_history[index]

                    # Limit to 10 lines
                    lines = content.split('\n')
                    display_lines = lines[:10]
                    display_text = '\n'.join(display_lines)

                    if len(lines) > 10:
                        display_text += "\n(...more lines...)"

                    # Create a text widget to show the full content
                    text_widget = tk.Text(expanded_container, wrap=tk.WORD, height=min(10, len(display_lines) + 1),
                                          width=50, padx=5, pady=5)
                    text_widget.insert(tk.END, display_text)
                    text_widget.config(state=tk.DISABLED)  # Make it read-only
                    text_widget.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

                # Update the canvas scrollregion
                self.history_canvas.configure(scrollregion=self.history_canvas.bbox("all"))
                break

    def restore_clipboard_item(self, index):
        if 0 <= index < len(self.clipboard_history):
            # Get the content to restore
            content = self.clipboard_history[index]

            # Set the ignore flag before changing clipboard
            self.ignore_next_clipboard_change = True

            # Set it as the current clipboard content
            pyperclip.copy(content)
            self.current_clipboard = content

            # Update the display
            self.update_current_display()

            # Flash background of current item to indicate success
            self.flash_item()

    def flash_item(self):
        original_bg = self.current_frame.cget("background")

        # Change background to green
        self.current_frame.configure(background="#AAFFAA")

        # Schedule change back to original
        self.root.after(500, lambda: self.current_frame.configure(background=original_bg))

    def clear_history(self):
        self.clipboard_history = []
        self.expanded_items = set()
        self.update_history_display()

    def on_close(self):
        self.stop_monitoring = True
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = ClipboardManager(root)
    root.mainloop()