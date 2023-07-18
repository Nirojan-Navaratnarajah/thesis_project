from tkinter import *
from scapy.all import *
import time
import threading
import os
import sqlite3
from tkinter import messagebox

# Database file path
db_file = 'scaling_factors.db'

# Scaling Factors
scaling_factors = {
    "Current_LV_Phase1_u16": {"lower_limit": 0, "upper_limit": 0,"resolution": 0, "offset": 0},
    "Current_LV_Phase2_u16": {"lower_limit": 0, "upper_limit": 0, "resolution": 0, "offset": 0},
    "Current_LV_u16": {"lower_limit": -165, "upper_limit": 165, "resolution": 0.080586081, "offset": 2047.5},
    "Voltage_LV_u16": {"lower_limit": 0, "upper_limit": 26.871, "resolution": 0.006561905, "offset": 0},
    "Voltage_VClamp_u16": {"lower_limit": 0, "upper_limit": 93.748, "resolution": 0.022893284, "offset": 0},
    "Voltage_HV_u16": {"lower_limit": 0, "upper_limit": 996.3793, "resolution": 0.243316068, "offset": 0},
    "Current_HV_u16": {"lower_limit": -14.285714, "upper_limit": 14.285714, "resolution": 0.00697715, "offset": 2047.5}
}

# Check if database file exists
if not os.path.isfile(db_file):
    # Create and populate the database
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    c.execute('''CREATE TABLE scaling_factors
                 (parameter TEXT, lower_limit REAL, upper_limit REAL, resolution REAL, offset REAL)''')
    for parameter, values in scaling_factors.items():
        c.execute('''INSERT INTO scaling_factors VALUES (?, ?, ?, ?, ?)''',
                  (parameter, values['lower_limit'], values['upper_limit'], values['resolution'], values['offset']))
    conn.commit()
else:
    # Retrieve the scaling factors from the database
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    c.execute('''SELECT * FROM scaling_factors''')
    rows = c.fetchall()
    for row in rows:
        parameter, lower_limit, upper_limit, resolution, offset = row
        scaling_factors[parameter] = {'lower_limit': lower_limit, 'upper_limit': upper_limit, 'resolution': resolution, 'offset': offset}


def update_scaling_factors():
    # Create a new window
    update_window = Toplevel(window)

    # Create labels and entry widgets for each scaling factor
    entry_widgets = {}
    for i, parameter in enumerate(scaling_factors.keys()):
        Label(update_window, text=parameter).grid(row=i, column=0)
        entry_widgets[parameter] = {}
        for j, key in enumerate(['lower_limit', 'upper_limit', 'resolution', 'offset']):
            entry_widgets[parameter][key] = Entry(update_window)
            entry_widgets[parameter][key].grid(row=i, column=j+1)
            entry_widgets[parameter][key].insert(0, str(scaling_factors[parameter][key]))

    # Function to submit the changes
    def submit_changes():
        try:
            # Update the scaling_factors dictionary and the database
            for parameter, entries in entry_widgets.items():
                new_values = {key: float(entry.get()) for key, entry in entries.items()}
                scaling_factors[parameter] = new_values
                c.execute('''UPDATE scaling_factors SET lower_limit = ?, upper_limit = ?, resolution = ?, offset = ? WHERE parameter = ?''',
                          (new_values['lower_limit'], new_values['upper_limit'], new_values['resolution'], new_values['offset'], parameter))
            conn.commit()

            # Close the update window
            update_window.destroy()
        except ValueError:
            # Show an error message if the user input is not valid
            messagebox.showerror("Error", "Invalid input. Please enter numeric values.")

    # Create a submit button
    Button(update_window, text="Submit", command=submit_changes).grid(row=len(scaling_factors), column=0, columnspan=2)


# Create GUI
window = Tk()
window.title("HV/DCDC ADC Parameters")
window.geometry("600x450")

# Create a container for the left side widgets
left_container = Frame(window)
left_container.pack(side=LEFT)

# Create a frame for the FSI data
fsi_frame = Frame(left_container, bd=1, relief=SOLID)
fsi_frame.pack(padx=10, pady=10)

# Create a label for the frame
fsi_label = Label(fsi_frame, text="FSI Data From HV/DCDC", font=("Arial", 14, "bold"))
fsi_label.pack(side=TOP)

# Create a Frame for the left side
left_frame = Frame(fsi_frame)
left_frame.pack(side=LEFT, padx=10, pady=10)

# Create labels and text boxes in the left side
labels_left = {
    "Current_LV_Phase1_u16": Label(left_frame, text="Current_LV_Phase1_u16: ", anchor=W),
    "Current_LV_Phase2_u16": Label(left_frame, text="Current_LV_Phase2_u16: ", anchor=W),
    "Current_LV_u16": Label(left_frame, text="Current_LV_u16: ", anchor=W),
    "Voltage_LV_u16": Label(left_frame, text="Voltage_LV_u16: ", anchor=W),
    "Voltage_VClamp_u16": Label(left_frame, text="Voltage_VClamp_u16: ", anchor=W),
    "Voltage_HV_u16": Label(left_frame, text="Voltage_HV_u16: ", anchor=W),
    "Current_HV_u16": Label(left_frame, text="Current_HV_u16: ", anchor=W)
}

text_boxes_left = {}

for i, (key, label) in enumerate(labels_left.items()):
    label.grid(row=i, column=0, sticky=W, padx=5, pady=5)
    text_box = Entry(left_frame, width=20)
    text_box.grid(row=i, column=1, sticky=W, padx=5, pady=5)
    text_boxes_left[key] = text_box

speed_label = Label(left_frame, text="Speed: ", anchor=CENTER)
speed_label.grid(row=len(labels_left), columnspan=2, padx=5, pady=10)

packet_count = 0
start_time = 0
payload = b""  # Initialize payload variable

# Create a frame for the Update Scaling Factors button
button_frame = Frame(left_container)
button_frame.pack(padx=10, pady=10)

# Create a button to trigger updating the scaling factors
update_button = Button(button_frame, text="Update Scaling Factors", command=update_scaling_factors)
update_button.pack(pady=10)

# Create a Frame for the right side
right_frame = Frame(window)
right_frame.pack(side=RIGHT, padx=10, pady=10)

# Create a frame for the Ethernet Frame Sender
ethernet_frame_sender_frame = Frame(right_frame, bd=1, relief=SOLID)

# Use a label to set a minimum height for the frame
empty_label = Label(ethernet_frame_sender_frame, height=6)
empty_label.pack()

ethernet_frame_sender_frame.pack(padx=10, pady=10)

# Create a label for the Ethernet Frame Sender
ethernet_frame_sender_label = Label(ethernet_frame_sender_frame, text="Ethernet Frame Sender", font=("Arial", 14, "bold"))
ethernet_frame_sender_label.pack(side=TOP)

# Create labels and text boxes for data entry
data_labels = []
data_entries = []

for i in range(1, 5):
    data_label = Label(ethernet_frame_sender_frame, text="Data_{}".format(i))
    data_label.pack(anchor=W)
    data_labels.append(data_label)

    data_entry = Entry(ethernet_frame_sender_frame, width=30)
    data_entry.pack(pady=5)
    data_entries.append(data_entry)

# Create a function to send a single Ethernet frame
def send_single_frame():
    dst_mac = "04:03:02:01:06:05"  # Destination MAC address
    src_mac = "F8:E4:3B:73:58:19"  #"00:73:41:00:04:f8"  # Source MAC address
    ethertype = 0xffff  # EtherType (0xffff)

    payload = b""
    for i in range(4):
        data = data_entries[i].get().encode()[:4]  # Get the data from the entry widget and limit it to 32 bytes
        payload += data if data else b"\x00" * 32  # Use zero value if no data is entered

    packet = Ether(dst=dst_mac, src=src_mac, type=ethertype) / Raw(load=payload)

    # Try to send the packet multiple times
    max_attempts = 2
    for attempt in range(max_attempts):
        try:
            sendp(packet, iface="Gateway")  # Replace "Ethernet" with your network interface
            break  # If sending the packet was successful, break out of the loop
        except Exception as e:
            if attempt == max_attempts - 1:  # If this was the last attempt, raise the exception
                raise
            else:
                time.sleep(0.5)  # Otherwise, wait for a while before retrying


# Create a button to trigger sending a single frame
send_button = Button(ethernet_frame_sender_frame, text="Send Frame", command=send_single_frame)
send_button.pack(pady=10)

# Function to update the GUI
def update_gui():
    global packet_count, start_time
    window.update()
    window.after(100, update_gui)  # Schedule the next GUI update

# Function to calculate speed and update speed label
def calculate_speed():
    global packet_count, start_time
    elapsed_time = time.time() - start_time
    if elapsed_time > 0:
        receiving_speed = (packet_count * len(payload) * 8) / (elapsed_time * 1000000)
        speed_label.config(text="Speed: {:.2f} Mbps".format(receiving_speed))
        packet_count = 0
        start_time = time.time()
    window.after(1000, calculate_speed)  # Schedule the next speed calculation

# Function to process each packet
def process_packet(packet):
    global packet_count, payload
    if packet.haslayer(Ether) and packet.haslayer(Raw):
        payload = packet.getlayer(Raw).load
        data = [payload[i:i + 2][::-1] for i in range(0, len(payload), 2)]  # Note byte order switching

        for i, (key, text_box) in enumerate(text_boxes_left.items()):
            if key in scaling_factors and i < len(data):
                scaling_factor = scaling_factors[key]
                hex_value = int.from_bytes(data[i], byteorder="big", signed=False)
                scaled_value = ((hex_value - scaling_factor.get("offset", 0)) * scaling_factor.get("resolution", 1.0))

                text_box.delete(0, END)
                text_box.insert(END, "{:.2f}".format(scaled_value))
            else:
                text_box.delete(0, END)

        packet_count += 1

# Function to capture packets
def capture_packets(interface):
    sniff(iface=interface, prn=process_packet, filter="ether dst host F8:E4:3B:73:58:19", store=0)  #08:97:98:DD:EF:61", store=0)  # 00:73:41:00:04:f8", store=0)

# Start capturing packets in a separate thread
interface = "Gateway"  # Update with the correct interface name
capture_thread = threading.Thread(target=capture_packets, args=(interface,))
capture_thread.start()

# Start the GUI main loop
window.after(100, update_gui)  # Start the GUI update loop
window.after(1000, calculate_speed)  # Start the speed calculation loop
window.mainloop()
