import tkinter as tk

def create_services_tab(master, context):
    frame = tk.Frame(master)
    text = tk.Text(frame, wrap="word")
    text.pack(fill=tk.BOTH, expand=True)

    def update():
        text.delete(1.0, tk.END)
        for thing in sorted(context.things.values(), key=lambda x: x.name):
            for service in sorted(thing.services, key=lambda s: s.name):
                text.insert(tk.END, f"Name: {service.name}\n")
                text.insert(tk.END, f"Thing: {service.thing_name}\n")
                text.insert(tk.END, f"API: {service.api}\n")
                text.insert(tk.END, f"Description: {service.description}\n\n")
        frame.after(1000, update)

    update()
    return frame
