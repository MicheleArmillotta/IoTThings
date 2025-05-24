import tkinter as tk

def create_services_tab(master, context):
    frame = tk.Frame(master)
    text = tk.Text(frame, wrap="word")
    text.pack(fill=tk.BOTH, expand=True)

    def update():
        text.delete(1.0, tk.END)
        service_count = 0
        
        for thing in sorted(context.things.values(), key=lambda x: x.name):
            for entity in sorted(thing.entities, key=lambda e: e.name):
                for service in sorted(entity.services, key=lambda s: s.name):
                    service_count += 1
                    text.insert(tk.END, f"Service #{service_count}\n")
                    text.insert(tk.END, f"Name: {service.name}\n")
                    text.insert(tk.END, f"Thing: {service.thing_name}\n")
                    text.insert(tk.END, f"Entity: {entity.name} (ID: {service.entity_id})\n")
                    text.insert(tk.END, f"Type: {service.type}\n")
                    text.insert(tk.END, f"Category: {service.app_category}\n")
                    text.insert(tk.END, f"API: {service.api}\n")
                    text.insert(tk.END, f"Description: {service.description}\n")
                    if service.keywords:
                        text.insert(tk.END, f"Keywords: {service.keywords}\n")
                    text.insert(tk.END, f"Space ID: {service.space_id}\n")
                    text.insert(tk.END, "-" * 50 + "\n\n")
        
        if service_count == 0:
            text.insert(tk.END, "No services found.\n")
        else:
            text.insert(tk.END, f"Total services: {service_count}\n")
        
        # Programma il prossimo aggiornamento (FUORI dai loop)
        frame.after(1000, update)

    update()
    return frame