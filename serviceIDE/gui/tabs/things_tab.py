import tkinter as tk
from tkinter import ttk

def make_scrollable_text(parent):
    text_frame = tk.Frame(parent, bg="#f9f9f9")
    text_widget = tk.Text(text_frame, wrap="word", bg="white", fg="black", font=("Consolas", 10), relief=tk.FLAT)
    scrollbar = ttk.Scrollbar(text_frame, command=text_widget.yview)
    text_widget.config(yscrollcommand=scrollbar.set)

    text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    return text_frame, text_widget

def create_things_tab(master, context):
    frame = tk.Frame(master, bg="#f0f0f0")
    text_frame, text = make_scrollable_text(frame)
    text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def update():
        text.delete(1.0, tk.END)
        for thing in sorted(context.get_things(), key=lambda x: x.name):
            text.insert(tk.END, f"📦 Thing: {thing.name}\n", "title")
            text.insert(tk.END, f"Address: {thing.address}\n")
            text.insert(tk.END, f"Description: {thing.description}\n")
            text.insert(tk.END, "Entities:\n")
            for entity in sorted(thing.entities, key=lambda e: e.name):
                text.insert(tk.END, f" - {entity.name} ({len(entity.services)} services)\n", "entity")
                if not entity.services:
                    text.insert(tk.END, "    • No services found\n", "warn")
                else:
                    for service in sorted(entity.services, key=lambda s: s.name):
                        text.insert(tk.END, f"    • {service.name}\n")
            text.insert(tk.END, "\n", "spacer")
        frame.after(1000, update)

    text.tag_config("title", font=("Arial", 11, "bold"), foreground="#2a4d69")
    text.tag_config("entity", foreground="#4f81bd")
    text.tag_config("warn", foreground="#d9534f")
    text.tag_config("spacer", spacing1=5)

    update()
    return frame


