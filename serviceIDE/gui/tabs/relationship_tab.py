import tkinter as tk
from tkinter import ttk

def make_scrollable_text(parent):
    text_frame = tk.Frame(parent, bg="#f9f9f9")
    text_widget = tk.Text(text_frame, wrap="word", bg="white", fg="black", font=("Consolas", 14), relief=tk.FLAT)
    scrollbar = ttk.Scrollbar(text_frame, command=text_widget.yview)
    text_widget.config(yscrollcommand=scrollbar.set)

    text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    return text_frame, text_widget


def create_relationships_tab(master, context):
    frame = tk.Frame(master, bg="#f0f0f0")
    text_frame, text = make_scrollable_text(frame)
    text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def update():
        text.delete(1.0, tk.END)
        relationships = context.get_relationships()
        for rel in relationships:
            text.insert(tk.END, f"🔗 {rel.name}\n", "title")
            text.insert(tk.END, f"Category: {rel.category}\n")
            text.insert(tk.END, f"Type: {rel.type}\n")
            text.insert(tk.END, f"Description: {rel.description}\n")
            text.insert(tk.END, f"Source: {rel.src}\n")
            text.insert(tk.END, f"Destination: {rel.dst}\n")
            text.insert(tk.END, "-" * 70 + "\n", "separator")
        if not relationships:
            text.insert(tk.END, "⚠️ No relationships found.\n", "warn")
        frame.after(1000, update)

    text.tag_config("title", font=("Arial", 14, "bold"), foreground="#334d5c")
    text.tag_config("warn", foreground="#d9534f")
    text.tag_config("separator", foreground="#cccccc")

    update()
    return frame

