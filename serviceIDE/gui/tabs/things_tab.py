import tkinter as tk

def create_things_tab(master, context):
    frame = tk.Frame(master)
    text = tk.Text(frame, wrap="word")
    text.pack(fill=tk.BOTH, expand=True)

    def update():
        text.delete(1.0, tk.END)
        for thing in sorted(context.things.values(), key=lambda x: x.name):
            text.insert(tk.END, f"Name: {thing.name}\n")
            text.insert(tk.END, f"Description: {thing.description}\n")
            text.insert(tk.END, "Services:\n")
            for service in sorted(thing.services, key=lambda s: s.name):
                text.insert(tk.END, f"  - {service.name}\n")
            text.insert(tk.END, "\n")
        frame.after(1000, update)

    update()
    return frame

