## IoTThings ServiceIDE

**IoTThings ServiceIDE** is a graphical Integrated Development Environment (IDE) designed for building, managing, and executing Internet of Things (IoT) applications in *smart space* environments. The platform focuses on simplifying IoT application orchestration through automatic device discovery and visual composition.

### Key Features

- **Automatic Discovery**  
  Devices (*Things*), their internal components (*Entities*), and exposed *Services* are automatically discovered via UDP multicast messages and maintained in a centralized runtime context.

- **Structured IoT Model**  
  - **Things**: Networked IoT devices  
  - **Entities**: Sensors, actuators, or logical modules within a device  
  - **Services**: Executable functionalities with defined inputs, outputs, and metadata  

- **Visual Graphical Interface**  
  The IDE provides dedicated tabs for:
  - Exploring discovered Things and Entities  
  - Inspecting available Services  
  - Defining logical relationships between services  
  - Creating, managing, and executing IoT applications  

- **Service Relationships**  
  Applications are built by connecting services using logical execution relationships, including:
  - *Ordered execution*
  - *On-success execution*
  - *Conditional execution based on output values*

- **Graphical Application Editor**  
  Users can visually compose applications using drag-and-drop:
  - Place services on a canvas  
  - Define relationships between services  
  - Configure service parameters  
  - Save and reload applications as portable JSON-based `.iot` files  

- **Execution and Monitoring**  
  Applications can be executed directly from the IDE, with real-time logs displayed in a terminal-like interface. Execution can be interrupted at any time.

### Technical Highlights

- Modular and extensible architecture
- JSON-based persistence for portability
- UDP multicast networking for device discovery
- No enforced constraints on service relationships to avoid semantic mismatches with external platforms

### Conclusion

IoTThings ServiceIDE enables intuitive and flexible development of complex IoT workflows by combining automatic discovery, visual composition, and real-time execution feedback. It is particularly suited for dynamic and heterogeneous smart environments where rapid prototyping and orchestration are essential.

---

More detailed information, diagrams, and implementation notes are available in the full project report:  
[IoTThings ServiceIDE – Final Project Report](IoT_Project_report.pdf) :contentReference[oaicite:0]{index=0}
