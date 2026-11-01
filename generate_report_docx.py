import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn, nsdecls

def create_report():
    doc = docx.Document()

    # Set page margins (1 inch around)
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    # Palette
    COLOR_PRIMARY = RGBColor(24, 43, 73)      # Deep Navy
    COLOR_SECONDARY = RGBColor(37, 99, 235)   # Tech Blue
    COLOR_TEXT = RGBColor(30, 41, 59)         # Slate text
    COLOR_MUTED = RGBColor(100, 116, 139)     # Gray text

    # Helper: Set cell shading
    def set_cell_shading(cell, color_hex):
        shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>')
        cell._tc.get_or_add_tcPr().append(shading)

    # Helper: Set table borders
    def style_table(table, header_bg="1E3A8A", alt_bg="F1F5F9"):
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        for i, row in enumerate(table.rows):
            for cell in row.cells:
                tcPr = cell._tc.get_or_add_tcPr()
                # cell padding (margins)
                tcMar = OxmlElement('w:tcMar')
                topMar = OxmlElement('w:top')
                topMar.set(qn('w:w'), '120')
                topMar.set(qn('w:type'), 'dxa')
                bottomMar = OxmlElement('w:bottom')
                bottomMar.set(qn('w:w'), '120')
                bottomMar.set(qn('w:type'), 'dxa')
                leftMar = OxmlElement('w:left')
                leftMar.set(qn('w:w'), '160')
                leftMar.set(qn('w:type'), 'dxa')
                rightMar = OxmlElement('w:right')
                rightMar.set(qn('w:w'), '160')
                rightMar.set(qn('w:type'), 'dxa')
                tcMar.append(topMar)
                tcMar.append(bottomMar)
                tcMar.append(leftMar)
                tcMar.append(rightMar)
                tcPr.append(tcMar)

                if i == 0:
                    set_cell_shading(cell, header_bg)
                    for paragraph in cell.paragraphs:
                        for run in paragraph.runs:
                            run.font.bold = True
                            run.font.color.rgb = RGBColor(255, 255, 255)
                            run.font.size = Pt(10)
                else:
                    if i % 2 == 1:
                        set_cell_shading(cell, alt_bg)
                    else:
                        set_cell_shading(cell, "FFFFFF")
                    for paragraph in cell.paragraphs:
                        for run in paragraph.runs:
                            run.font.size = Pt(9.5)
                            run.font.color.rgb = COLOR_TEXT

    # Helper: Add Section Header
    def add_section_header(title):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(16)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(title)
        run.font.bold = True
        run.font.size = Pt(13)
        run.font.color.rgb = COLOR_PRIMARY
        return p

    # Helper: Add Subsection Header
    def add_sub_header(title):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(title)
        run.font.bold = True
        run.font.size = Pt(11)
        run.font.color.rgb = COLOR_SECONDARY
        return p

    # Helper: Add Body Paragraph
    def add_body_p(text, bold_prefix=None):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.line_spacing = 1.15
        if bold_prefix:
            r_pre = p.add_run(bold_prefix)
            r_pre.font.bold = True
            r_pre.font.size = Pt(10.5)
            r_pre.font.color.rgb = COLOR_PRIMARY
        run = p.add_run(text)
        run.font.size = Pt(10.5)
        run.font.color.rgb = COLOR_TEXT
        return p

    # Helper: Add Bullet
    def add_bullet(text, bold_prefix=None):
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.15
        if bold_prefix:
            r_pre = p.add_run(bold_prefix)
            r_pre.font.bold = True
            r_pre.font.size = Pt(10)
            r_pre.font.color.rgb = COLOR_PRIMARY
        run = p.add_run(text)
        run.font.size = Pt(10)
        run.font.color.rgb = COLOR_TEXT
        return p

    # Helper: Add Callout Box (Table 1x1)
    def add_callout_box(title, text_lines, border_color="2563EB", bg_color="F8FAFC"):
        tbl = doc.add_table(rows=1, cols=1)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell = tbl.cell(0, 0)
        set_cell_shading(cell, bg_color)
        
        # Style borders: thick left border, none for others
        tcPr = cell._tc.get_or_add_tcPr()
        borders = parse_xml(f'''
            <w:tcBorders {nsdecls("w")}>
                <w:top w:val="none"/>
                <w:left w:val="single" w:sz="24" w:space="0" w:color="{border_color}"/>
                <w:bottom w:val="none"/>
                <w:right w:val="none"/>
            </w:tcBorders>
        ''')
        tcPr.append(borders)
        
        # cell margins
        tcMar = parse_xml(f'''
            <w:tcMar {nsdecls("w")}>
                <w:top w:w="160" w:type="dxa"/>
                <w:bottom w:w="160" w:type="dxa"/>
                <w:left w:w="240" w:type="dxa"/>
                <w:right w:w="240" w:type="dxa"/>
            </w:tcMar>
        ''')
        tcPr.append(tcMar)

        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(4)
        r_title = p.add_run(title + "\n")
        r_title.font.bold = True
        r_title.font.size = Pt(10.5)
        r_title.font.color.rgb = COLOR_PRIMARY

        for line in text_lines:
            p2 = cell.add_paragraph()
            p2.paragraph_format.space_before = Pt(1)
            p2.paragraph_format.space_after = Pt(2)
            r_line = p2.add_run(line)
            r_line.font.size = Pt(9.5)
            r_line.font.color.rgb = COLOR_TEXT
            
        doc.add_paragraph().paragraph_format.space_after = Pt(4)

    # Helper: Placeholder Image Frame
    def add_image_placeholder(title, instruction="[ Insert Screenshot / Hardware Photo Here ]", height_lines=4):
        tbl = doc.add_table(rows=1, cols=1)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell = tbl.cell(0, 0)
        set_cell_shading(cell, "F8FAFC")
        
        tcPr = cell._tc.get_or_add_tcPr()
        borders = parse_xml(f'''
            <w:tcBorders {nsdecls("w")}>
                <w:top w:val="dashed" w:sz="12" w:space="0" w:color="94A3B8"/>
                <w:left w:val="dashed" w:sz="12" w:space="0" w:color="94A3B8"/>
                <w:bottom w:val="dashed" w:sz="12" w:space="0" w:color="94A3B8"/>
                <w:right w:val="dashed" w:sz="12" w:space="0" w:color="94A3B8"/>
            </w:tcBorders>
        ''')
        tcPr.append(borders)
        
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(18)
        p.paragraph_format.space_after = Pt(4)
        r1 = p.add_run(title + "\n")
        r1.font.bold = True
        r1.font.size = Pt(10.5)
        r1.font.color.rgb = COLOR_PRIMARY
        
        r2 = p.add_run(instruction)
        r2.font.italic = True
        r2.font.size = Pt(9.5)
        r2.font.color.rgb = COLOR_MUTED
        
        for _ in range(height_lines):
            p_extra = cell.add_paragraph()
            p_extra.paragraph_format.space_before = Pt(8)
            p_extra.paragraph_format.space_after = Pt(8)
            
        p_last = cell.add_paragraph()
        p_last.paragraph_format.space_after = Pt(12)
        doc.add_paragraph().paragraph_format.space_after = Pt(4)

    # ==================== DOCUMENT CONTENT ====================

    # Title
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(10)
    p_title.paragraph_format.space_after = Pt(18)
    r_title = p_title.add_run("SMART STREET LIGHT MONITORING AND AUTOMATION SYSTEM")
    r_title.font.bold = True
    r_title.font.size = Pt(16)
    r_title.font.color.rgb = COLOR_PRIMARY

    # Subtitle / Metadata
    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_before = Pt(0)
    p_sub.paragraph_format.space_after = Pt(20)
    r_sub = p_sub.add_run("An IoT-Based Edge Sensing, Containerized Backend, and Real-Time Dashboard Prototype\n")
    r_sub.font.bold = True
    r_sub.font.size = Pt(11)
    r_sub.font.color.rgb = COLOR_SECONDARY
    r_meta = p_sub.add_run("Platform: ESP32 DevKit V1 | Node.js / Express | PostgreSQL | Docker | Render Cloud")
    r_meta.font.italic = True
    r_meta.font.size = Pt(9.5)
    r_meta.font.color.rgb = COLOR_MUTED

    # 1. INTRODUCTION
    add_section_header("1. INTRODUCTION")
    add_body_p(
        "Street lighting is a fundamental municipal infrastructure service that provides illumination for public roads, "
        "pedestrian pathways, and urban commercial centers, ensuring safety and visual convenience after dusk. However, "
        "conventional street lighting infrastructures suffer from significant energy wastage, high operating costs, and reliance "
        "on manual labor or rigid mechanical timers. Such legacy systems are incapable of adapting to actual ambient lighting "
        "conditions (such as heavy overcast, rain, or seasonal variations) and frequently remain illuminated during bright daytime hours."
    )
    add_body_p(
        "To address this issue, this project proposes an IoT-based Smart Street Light Monitoring and Automation System that "
        "autonomously measures ambient light levels, controls street lighting in real time, and transmits operational telemetry "
        "to a containerized cloud backend and database for centralized monitoring. The system integrates an ESP32 microcontroller "
        "with a Light Dependent Resistor (LDR) optical sensor module and high-luminosity LED actuator. The telemetry data is "
        "packaged into structured JSON format and transmitted over Wi-Fi via secure HTTPS to a containerized Node.js/Express "
        "backend running in the cloud on Render, persisted in a managed PostgreSQL database, and visualized through a real-time web dashboard."
    )
    add_body_p(
        "This solution offers an energy-efficient, robust, and scalable framework to automate municipal street lighting while "
        "providing administrators with real-time visibility, automated historical logging, and reduced operational overhead."
    )

    # 2. AIM OF THE PROJECT
    add_section_header("2. AIM OF THE PROJECT")
    add_body_p(
        "The main aim of this project is to design and implement an IoT-enabled smart street light automation and monitoring system "
        "that continuously detects ambient light intensity, autonomously switches the street light LED ON during darkness and OFF "
        "during daylight, transmits real-time telemetry to a containerized cloud backend, and enables municipal supervisors to "
        "monitor system status and historical trends remotely via a web dashboard."
    )

    # 3. OBJECTIVES
    add_section_header("3. OBJECTIVES")
    add_bullet("To measure ambient light levels in real time using a Light Dependent Resistor (LDR) sensor module with LM393 comparator.")
    add_bullet("To autonomously control the street light LED locally at the edge with near-zero latency, ensuring failsafe operation independent of internet connectivity.")
    add_bullet("To process sensor data and actuator states through an ESP32 microcontroller and transmit secure JSON telemetry over Wi-Fi via HTTPS.")
    add_bullet("To deploy a containerized Node.js/Express backend service using Docker and Render cloud infrastructure.")
    add_bullet("To persist all time-stamped sensor readings and lighting states in a scalable PostgreSQL relational database.")
    add_bullet("To develop an interactive, real-time web dashboard featuring dynamic status cards, Chart.js time-series graphs, and telemetry history tables.")
    add_bullet("To provide a cost-effective, low-power, and compact IoT hardware prototype suitable for municipal and commercial deployments.")

    # 4. EXISTING SYSTEM
    add_section_header("4. EXISTING SYSTEM")
    add_body_p(
        "The existing street light control mechanisms in most conventional municipalities are manual or analog, relying on manual "
        "switchboards toggled by physical maintenance crews or fixed astronomical timer relays."
    )
    add_body_p("Disadvantages:")
    add_bullet("Manual operation is labor-intensive, time-consuming, and prone to human error and neglect.")
    add_bullet("Astronomical or mechanical timer switches cannot adapt to sudden daylight changes caused by rain, clouds, or eclipses.")
    add_bullet("Significant electrical power wastage occurs when lights remain switched ON during daylight hours.")
    add_bullet("No real-time fault notifications, centralized telemetry, or remote observability.")
    add_bullet("Lack of historical telemetry records and data analytics for municipal energy audits and predictive maintenance.")

    # 5. PROPOSED SYSTEM
    add_section_header("5. PROPOSED SYSTEM")
    add_body_p(
        "The proposed system introduces an IoT-based smart street light device and cloud infrastructure capable of measuring "
        "ambient illumination accurately, switching light actuators automatically, and transmitting operational telemetry to a cloud server in real time."
    )
    add_body_p(
        "The ESP32 microcontroller samples the digital output of an LDR sensor module. When ambient light drops below a preset "
        "threshold (indicating dusk or darkness), the ESP32 energizes the street light LED actuator immediately. When daylight returns, "
        "the LED is de-energized. Simultaneously, the ESP32 transmits telemetry packets containing the device ID, LDR output (0/1), "
        "ambient status ('Dark'/'Bright'), and LED status ('ON'/'OFF') to a containerized Node.js cloud server via HTTPS."
    )
    add_body_p(
        "This design eliminates manual operational dependency, ensures instantaneous local switching, saves significant energy, "
        "and provides a live, interactive web dashboard accessible from any internet-connected device."
    )

    # 6. SYSTEM ARCHITECTURE
    add_section_header("6. SYSTEM ARCHITECTURE")
    add_body_p("The system architecture comprises two primary functional layers — the Device Layer (Edge) and the Cloud/Backend Layer.")
    
    add_sub_header("6.1 Hardware Components")
    add_bullet("ESP32 DevKit V1: 32-bit dual-core microcontroller with integrated 2.4 GHz Wi-Fi (802.11 b/g/n) for edge computation and secure HTTPS communication.")
    add_bullet("LDR Optical Sensor Module: Photoresistor circuit integrated with an LM393 comparator providing sensitivity adjustment and digital threshold output (DO).")
    add_bullet("Street Light LED Actuator: High-luminosity 5mm white LED simulating the street lamp fixture, driven via GPIO 2 with a 220Ω current-limiting resistor.")
    add_bullet("Prototyping Breadboard: Sturdy base board providing secure physical mounting and circuit wiring for components.")
    add_bullet("Jumper Wires: High-grade Dupont jumper wires (Male-to-Male, Male-to-Female) for breadboard pin interconnects.")
    add_bullet("Power Supply (5V): Standard 5V 1A Micro-USB adapter powering the ESP32 and peripheral sensors.")

    add_sub_header("6.2 Software Components")
    add_bullet("Arduino IDE 2.x: Integrated development environment used to program, configure, compile, and flash firmware to the ESP32 microcontroller.")
    add_bullet("Node.js & Express (Backend): RESTful web service handling telemetry ingestion (`/api/readings`), health checks, and summary statistics.")
    add_bullet("PostgreSQL Database: Production-ready relational database storing time-stamped telemetry with composite indexes (`(device_id, received_at)`).")
    add_bullet("Dashboard Interface: Modern web frontend built with HTML5, CSS3 Grid, and Chart.js for real-time data plotting and telemetry inspection.")
    add_bullet("Docker & Docker Compose: Containerization engine packaging the Node.js application (`node:22-alpine`) and local PostgreSQL database.")
    add_bullet("Render Cloud Platform: Cloud PaaS used for hosting the web service and managed cloud PostgreSQL instance via Render Blueprint (`render.yaml`).")

    # 7. WORKING PRINCIPLE
    add_section_header("7. WORKING PRINCIPLE")
    add_body_p("The operational workflow follows seven coordinated steps across edge sensing, local control, and cloud telemetry:")
    add_bullet("Step 1 (Initialization): Upon power-on, the ESP32 initializes GPIO pin modes (GPIO 2 as OUTPUT, GPIO 27 as INPUT), connects to the local Wi-Fi network, and initiates an immediate diagnostic sensor scan.")
    add_bullet("Step 2 (Data Acquisition): The LDR sensor module continuously monitors ambient illumination. The onboard LM393 comparator compares the analog resistance against a calibrated potentiometer threshold and outputs a clean digital logic level.")
    add_bullet("Step 3 (Immediate Local Control): The ESP32 evaluates the digital logic signal. If darkness is detected (`DO == HIGH`), the LED is activated immediately (`GPIO 2 = HIGH`); if bright daylight is detected, the LED is turned OFF. This occurs in <5ms without network dependency.")
    add_bullet("Step 4 (Event & Periodic Telemetry): When a change in lighting state is detected or when the 5-second periodic timer expires, a cloud telemetry dispatch is triggered.")
    add_bullet("Step 5 (Secure Cloud Transmission): The ESP32 formats a JSON payload: `{\"device_id\":\"esp32_street_01\", \"sensor\":1, \"ambient\":\"Dark\", \"led\":\"ON\"}` and dispatches it over Wi-Fi via `HTTPS POST` to the Render cloud backend using TLS encryption.")
    add_bullet("Step 6 (Data Persistence): The Node.js Express backend validates the payload structure and inserts a new record into the PostgreSQL `sensor_readings` table with an automatic UTC timestamp.")
    add_bullet("Step 7 (Live Dashboard Monitoring): The web dashboard polls the backend REST APIs every 3 seconds, dynamically updating the status cards, Chart.js time-series line chart, doughnut state distribution, and the database log table.")

    # 8. CONNECTION DETAILS
    add_section_header("8. CONNECTION DETAILS")
    add_body_p("The hardware interconnection pin mapping between the ESP32 microcontroller and the peripheral components is summarized below:")

    # Table
    table = doc.add_table(rows=6, cols=5)
    headers = ["Component", "Peripheral Pin", "Pin Type", "ESP32 Pin", "Operating Voltage"]
    for col_idx, h_text in enumerate(headers):
        table.cell(0, col_idx).paragraphs[0].text = h_text

    connections = [
        ["LDR Sensor Module", "VCC", "Power Supply", "3.3V (3V3)", "3.3V DC"],
        ["LDR Sensor Module", "GND", "Ground", "GND", "0V"],
        ["LDR Sensor Module", "DO (Digital Out)", "Digital Input", "GPIO 27", "3.3V Logic"],
        ["Street Light LED", "Anode (+)", "Digital Output", "GPIO 2 (via 220Ω)", "3.3V Logic"],
        ["Street Light LED", "Cathode (-)", "Ground", "GND", "0V"]
    ]

    for row_idx, row_data in enumerate(connections):
        for col_idx, cell_value in enumerate(row_data):
            table.cell(row_idx + 1, col_idx).paragraphs[0].text = cell_value

    style_table(table)
    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # 9. CLOUD & CONTAINER HOSTING
    add_section_header("9. CLOUD & CONTAINER HOSTING")
    add_body_p(
        "The backend application is containerized and hosted in the cloud to ensure high reliability, continuous uptime, "
        "and remote accessibility from anywhere in the world."
    )
    add_bullet("Render Cloud Web Service: The Express backend is deployed as a managed Node.js web service on Render.com with automated build (`npm install`) and start (`npm start`) procedures.")
    add_bullet("Render Managed PostgreSQL: A dedicated cloud PostgreSQL database instance (`streetlight-postgres`) is provisioned on Render. The connection URI is dynamically injected via the `DATABASE_URL` environment variable.")
    add_bullet("Blueprint Automation (`render.yaml`): Infrastructure as Code (IaC) configuration declares both the database and web service simultaneously, guaranteeing automated zero-configuration deployments.")
    add_bullet("Docker Setup (`Dockerfile`): Multi-stage container build utilizing `node:22-alpine` produces an ultra-compact (<80 MB) container image, ensuring rapid build cycles and minimal memory footprint.")
    add_bullet("Docker Compose (`docker-compose.yml`): Provides local orchestration for offline testing, coordinating a local PostgreSQL 16 container and Node.js container with integrated health checks (`pg_isready`).")
    add_bullet("Data Management & Auto-Migration: The backend automatically creates the `sensor_readings` table and composite index `(device_id, received_at)` upon startup, eliminating manual SQL script executions.")

    # 10. RESULTS
    add_section_header("10. RESULTS")
    add_body_p("The implemented smart street light system was rigorously tested, successfully demonstrating the following results:")
    add_bullet("Autonomous Edge Switching: The LDR sensor accurately detects transitions between dark and bright environments. The street light LED turns ON immediately upon sensing darkness and turns OFF under bright light.")
    add_bullet("Reliable HTTPS Telemetry: The ESP32 successfully connects to Wi-Fi and dispatches JSON telemetry packets, consistently receiving `HTTP 201 Created` responses from the cloud server.")
    add_bullet("Fault-Tolerant Local Operation: When network connectivity was deliberately interrupted, local light actuation continued without hesitation or system lockup.")
    add_bullet("Persistent Cloud Storage: PostgreSQL database records every event with millisecond precision, accurately logging device IDs, sensor DO states, ambient conditions, and LED status.")
    add_bullet("Real-Time Visualization: The web dashboard updates dynamically every 3 seconds, updating metric cards, rendering time-series graphs, and logging historical telemetry records.")
    add_bullet("Universal Accessibility: The dashboard is fully responsive and verified accessible across desktop browsers, laptops, tablets, and smartphones.")

    # 11. ADVANTAGES
    add_section_header("11. ADVANTAGES")
    add_bullet("Substantial Energy Conservation: Prevents unnecessary street light operation during daylight hours, reducing municipal electricity bills by an estimated 35%–50%.")
    add_bullet("Autonomous Failsafe Operation: Core switching functions occur locally at the microcontroller level, ensuring street lights operate even during internet outages.")
    add_bullet("Zero Human Dependency: Eliminates the necessity for manual patrol crews to toggle switches across city sectors.")
    add_bullet("Real-Time Centralized Visibility: Municipal supervisors can verify the operational status of all street lighting assets in real time via an intuitive dashboard.")
    add_bullet("Predictive Maintenance & Auditing: Historical telemetry records stored in PostgreSQL enable energy auditing, burn-time calculation, and proactive maintenance planning.")
    add_bullet("Low Cost & High Scalability: Built using standard off-the-shelf ESP32 boards and containerized cloud services that scale seamlessly to hundreds of lighting nodes.")

    # 12. APPLICATIONS
    add_section_header("12. APPLICATIONS")
    add_bullet("Smart City Municipal Roads: Automated lighting for highways, main roads, urban streets, and pedestrian zones.")
    add_bullet("Educational & Corporate Campuses: Energy-efficient pathway and quad illumination across university and corporate facilities.")
    add_bullet("Gated Residential Communities: Automated security and street illumination for apartment complexes and residential neighborhoods.")
    add_bullet("Industrial Yards & Warehouses: Perimeter security lighting and loading bay illumination automated based on ambient daylight.")
    add_bullet("Public Parks & Parking Facilities: Smart illumination for parking garages, outdoor lots, and municipal park promenades.")

    # 13. FUTURE ENHANCEMENTS
    add_section_header("13. FUTURE ENHANCEMENTS")
    add_bullet("PIR Motion Sensor Integration: Incorporating Passive Infrared (PIR) sensors to dim lights to 20% power during late-night hours and boost to 100% when pedestrian or vehicular movement is detected.")
    add_bullet("Analog Illuminance & PWM Dimming: Interfacing the LDR analog output (AO) to an ESP32 ADC pin to implement multi-step PWM dimming proportional to twilight intensity.")
    add_bullet("Current Sensor & Fault Detection: Adding an ACS712 current sensor to detect lamp burn-out or open circuits, dispatching immediate fault alerts to maintenance technicians.")
    add_bullet("Solar PV & Battery Storage: Coupling the system with a solar panel, LiFePO4 battery, and charge controller for completely green, self-sustaining off-grid operation.")
    add_bullet("Push & SMS Notifications: Integrating Webhooks or Telegram Bot APIs to send instant threshold alerts and fault summaries to municipal administrators' mobile devices.")

    # 14. CONCLUSION
    add_section_header("14. CONCLUSION")
    add_body_p(
        "The Smart Street Light Monitoring and Automation System demonstrates a complete, reliable, and production-ready IoT prototype "
        "that resolves the shortcomings of conventional municipal lighting. By combining autonomous edge sensing on an ESP32 with "
        "a containerized cloud backend, PostgreSQL relational storage, and a real-time web dashboard, the project fulfills all objectives "
        "of modern IoT system design."
    )
    add_body_p(
        "The system dramatically minimizes electrical energy consumption, eradicates human operational delay, enhances road safety, "
        "and provides a cost-effective, scalable foundation for future municipal smart city automation initiatives."
    )

    # 15. PROJECT DESIGN
    add_section_header("15. PROJECT DESIGN")
    add_body_p("The end-to-end data flow of the smart street light system is organized into four sequential stages:")
    add_callout_box(
        "End-to-End Data Flow Pipeline",
        [
            "1. LDR Sensor Module → ESP32: Samples ambient illumination; comparator digitizes threshold; ESP32 actuates LED locally in <5ms.",
            "2. ESP32 → Cloud (Render Backend): Packages telemetry into JSON and dispatches via HTTPS POST over Wi-Fi on state transitions and 5s heartbeat.",
            "3. Cloud Backend → PostgreSQL Database: Express API validates schema and executes parameterized INSERT into the 'sensor_readings' table.",
            "4. Cloud Backend → Web Dashboard: Client browser polls REST endpoints every 3 seconds to update metric cards, Chart.js trends, and history logs."
        ],
        border_color="2563EB",
        bg_color="EFF6FF"
    )

    # 16. HARDWARE COMPONENTS
    add_section_header("16. HARDWARE COMPONENTS")
    add_body_p("The prototype hardware setup combines modular IoT edge computing and optical sensing components:")
    add_bullet("ESP32-WROOM-32: Dual-core Xtensa 32-bit LX6 microprocessor running at 240 MHz with 520 KB SRAM, 4 MB Flash, and integrated 802.11 b/g/n Wi-Fi transceiver.")
    add_bullet("LDR Module (Light Dependent Resistor): Features a cadmium sulfide (CdS) photoresistor whose resistance decreases in light, integrated with an LM393 comparator and onboard trimmer potentiometer.")
    add_bullet("Actuator Unit: 5mm diffused white LED paired with a 220Ω metal-film resistor to safeguard GPIO 2 against overcurrent while delivering clear visual indication.")
    add_bullet("Wiring Harness: Solderless breadboard and color-coded Dupont jumpers providing low-impedance electrical connections.")
    
    add_image_placeholder("Hardware Components & Circuit Assembly", "[ Insert photo of ESP32, LDR Sensor, and LED Breadboard Circuit ]", height_lines=5)

    # 17. BLOCK DIAGRAM
    add_section_header("17. BLOCK DIAGRAM")
    add_body_p("The architectural block diagram illustrates the modular layer-by-layer organization of the system:")
    
    add_callout_box(
        "System Block Diagram Hierarchy",
        [
            "┌────────────────────────────────────────────────────────────────────────┐",
            "│ 1. PHYSICAL SENSING & ACTUATION LAYER                                  │",
            "│   [ LDR Sensor Module (GPIO 27) ] ───► [ Street Light LED (GPIO 2) ]   │",
            "└───────────────────────────────────┬────────────────────────────────────┘",
            "                                    ▼",
            "┌────────────────────────────────────────────────────────────────────────┐",
            "│ 2. PROCESSING & WIRELESS CONNECTIVITY (ESP32 DevKit V1)               │",
            "│   - Ambient Logic Evaluation (Dark / Bright)                           │",
            "│   - Autonomous Actuator Control Loop (<5ms)                            │",
            "│   - JSON Telemetry Serialization & HTTPS Client Transport               │",
            "└───────────────────────────────────┬────────────────────────────────────┘",
            "                                    ▼ (Wi-Fi / HTTPS POST)",
            "┌────────────────────────────────────────────────────────────────────────┐",
            "│ 3. CONTAINERIZED CLOUD BACKEND & DATABASE LAYER (Render / Docker)      │",
            "│   - Node.js / Express REST API Engine (Port 3000)                      │",
            "│   - Schema Validation & PostgreSQL Connection Pool (pg.Pool)           │",
            "│   - Managed PostgreSQL Database ('sensor_readings' Table)              │",
            "└───────────────────────────────────┬────────────────────────────────────┘",
            "                                    ▼ (HTTP GET / REST APIs)",
            "┌────────────────────────────────────────────────────────────────────────┐",
            "│ 4. USER INTERFACE & REAL-TIME VISUALIZATION LAYER                      │",
            "│   - Web Dashboard (Responsive HTML5 / CSS3 Grid)                       │",
            "│   - Ambient & LED Status Cards with Dynamic Visual Cue                 │",
            "│   - Chart.js Time-Series History & LED State Distribution Doughnut     │",
            "│   - Live Database Telemetry Log Table (Auto-polled every 3s)           │",
            "└────────────────────────────────────────────────────────────────────────┘"
        ],
        border_color="0F766E",
        bg_color="F0FDFA"
    )
    add_image_placeholder("Visual Block Diagram", "[ Insert Formal Block Diagram Graphic if available ]", height_lines=3)

    # 18. FINAL PRODUCT AND PRESENTATION
    add_section_header("18. FINAL PRODUCT AND PRESENTATION")
    add_body_p(
        "The finalized physical prototype was assembled and evaluated under simulated real-world conditions. "
        "During evaluation, covering the LDR sensor simulated nighttime ambient darkness, triggering instant LED illumination "
        "and sending telemetry to the cloud backend. When exposed to ambient room light or a flashlight, the LED turned OFF "
        "immediately and transmitted updated status to the cloud."
    )
    add_bullet("Physical Prototype Assembly: Breadboard circuit incorporating the ESP32, LDR sensor module, and LED fixture powered via 5V USB.")
    add_bullet("Serial Monitor Output: Demonstrates Wi-Fi connection establishment, local IP assignment, JSON telemetry construction, and `HTTP 201 Created` server responses.")
    add_bullet("Live Cloud Service: Confirmed active deployment on Render with green status indicators across both web service and PostgreSQL database.")
    
    add_image_placeholder("Physical Prototype Setup & Demonstration Photos", "[ Insert Photo of Your Assembled Breadboard Prototype & Serial Monitor Output ]", height_lines=6)

    # 19. DASHBOARD
    add_section_header("19. DASHBOARD")
    add_body_p(
        "The real-time web dashboard acts as the primary monitoring console for municipal supervisors, accessible from any modern web browser. "
        "It provides live operational metrics, historical trend analytics, and raw database records:"
    )
    add_bullet("Status Header: Features dynamic connection pill indicator (showing '● Backend + PostgreSQL connected' in green when operational).")
    add_bullet("Ambient Condition Card: Displays current ambient classification ('Dark' or 'Bright') derived from the latest reading.")
    add_bullet("Street Light LED Card: Highlights the current actuator state ('ON' in yellow accent, 'OFF' in neutral accent).")
    add_bullet("LDR Digital Output Card: Displays the discrete digital sensor value (1 for Dark, 0 for Bright).")
    add_bullet("Total Records Card: Live count of all telemetry readings accumulated in the PostgreSQL database.")
    add_bullet("Time-Series Line Chart: Chart.js visualization showing temporal LDR digital output variations across historical records.")
    add_bullet("LED State Distribution Chart: Chart.js doughnut chart depicting the proportional distribution between LED ON and OFF states.")
    add_bullet("Database Telemetry Log: Dynamic table presenting the 10 most recent readings with timestamps, device IDs, LDR states, ambient levels, and LED statuses.")

    add_image_placeholder("Web Dashboard Interface Screenshot", "[ Insert Screenshot of Live Web Dashboard with Active Telemetry & Charts ]", height_lines=6)

    # Save Document
    filename = "SMART_STREET_LIGHT_PROJECT_REPORT.docx"
    doc.save(filename)
    print(f"Document successfully created and saved as: {filename}")

if __name__ == "__main__":
    create_report()
