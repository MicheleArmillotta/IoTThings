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


def create_services_tab(master, context):
    frame = tk.Frame(master, bg="#f0f0f0")
    text_frame, text = make_scrollable_text(frame)
    text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def update():
        text.delete(1.0, tk.END)
        count = 0
        for thing in sorted(context.get_things(), key=lambda x: x.name):
            for entity in sorted(thing.entities, key=lambda e: e.name):
                for service in sorted(entity.services, key=lambda s: s.name):
                    count += 1
                    text.insert(tk.END, f"🔧 Service #{count}: {service.name}\n", "title")
                    text.insert(tk.END, f"Thing: {service.thing_name} | Entity: {entity.name} (ID: {service.entity_id})\n")
                    text.insert(tk.END, f"Type: {service.type} | Category: {service.app_category}\n")
                    inputs = ", ".join([f"{k}: {v}" for k, v in service.input_params.items()]) if service.input_params else "None"
                    output = f"{service.output_name}: {service.output_type}" if service.output_name and service.output_type else "None"
                    text.insert(tk.END, f"Endpoint: {service.endpoint} | Inputs: {inputs} | Output: {output}\n")                   
                    text.insert(tk.END, f"Description: {service.description}\n")
                    if service.keywords:
                        if isinstance(service.keywords, str):
                            keywords_str = service.keywords
                        else:
                            keywords_str = ', '.join(service.keywords)
                        text.insert(tk.END, f"Keywords: {keywords_str}\n")
                    text.insert(tk.END, f"Space ID: {service.space_id}\n")
                    text.insert(tk.END, "-" * 80 + "\n", "separator")
        if count == 0:
            text.insert(tk.END, "⚠️ No services found, Scanning for Things...\n", "warn")
        else:
            text.insert(tk.END, f"Total services: {count}\n", "info")
        frame.after(1000, update)

    text.tag_config("title", font=("Arial", 14, "bold"), foreground="#1c4966")
    text.tag_config("warn", foreground="#d9534f")
    text.tag_config("info", foreground="#5cb85c")
    text.tag_config("separator", foreground="#aaaaaa")

    update()
    return frame
