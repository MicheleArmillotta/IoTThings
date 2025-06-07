def configure_things_text_tags(text_widget):
    # Titolo della thing
    text_widget.tag_config("title", font=("Arial", 11, "bold"), foreground="#2a4d69")
    # Indirizzo (address)
    text_widget.tag_config("address", font=("Consolas", 10, "bold"), foreground="#4fc3f7")
    # Descrizione (description)
    text_widget.tag_config("description", font=("Consolas", 10, "italic"), foreground="#ffd166")
    # Entities
    text_widget.tag_config("entity", font=("Consolas", 10, "bold"), foreground="#90caf9")
    # Nessun servizio
    text_widget.tag_config("warn", foreground="#d9534f")
    #servizio
    text_widget.tag_config("service", font=("Consolas", 10, "bold"), foreground="#e43731")

    # Spaziatore
    text_widget.tag_config("spacer", spacing1=5)
    
    