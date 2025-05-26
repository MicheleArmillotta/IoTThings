import tkinter as tk

def create_relationships_tab(master, context):
    frame = tk.Frame(master)
    text = tk.Text(frame, wrap="word")
    text.pack(fill=tk.BOTH, expand=True)

    def update():
        text.delete(1.0, tk.END)
        for rel in context.get_relationships():
            text.insert(tk.END, f"Name: {rel.name}\n")
            text.insert(tk.END, f"Category: {rel.category}\n")
            text.insert(tk.END, f"Type: {rel.type}\n")
            text.insert(tk.END, f"Description: {rel.description}\n")
            text.insert(tk.END, f"Source: {rel.src}\n")
            text.insert(tk.END, f"Destination: {rel.dst}\n\n")
        frame.after(1000, update)

    update()
    return frame
