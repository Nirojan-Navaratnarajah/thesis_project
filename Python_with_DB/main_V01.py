from tkinter import *
from scapy.all import *
import time
import threading
import os
import sqlite3
from tkinter import messagebox
import csv


packet_count = 0
start_time = time.time()
payload_size = 0



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

# Function to log the recieved data
logging_enabled = False

# Function to log the received data
def log_payload_data():
    global payload_data, logging_enabled
    if payload_data and logging_enabled:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")  # Get the current timestamp
        with open('FSI_data.csv', 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([timestamp] + payload_data)  # Add the timestamp to the payload data
            file.write('\n \n')  # Add an extra newline and a space
        payload_data = []  # Clear the payload data after logging
    else:
        pass  # Debugging message


def start_logging():
    global logging_enabled
    logging_enabled = True
    log_button.configure(state=DISABLED)
    stop_button.configure(state=NORMAL)


def stop_logging():
    global logging_enabled
    logging_enabled = False
    log_button.configure(state=NORMAL)
    stop_button.configure(state=DISABLED)
    log_payload_data() # call the function one last time to log any remaining data

# Create GUI
window = Tk()
window.title("HV/DCDC ADC Parameters")
window.geometry("600x600")

# Create a container for the left side widgets
main_frame = Frame(window)
main_frame.pack(padx=10, pady=10)

left_container = Frame(main_frame)
left_container.pack(side=LEFT)

# Create a frame for the FSI data
fsi_frame = Frame(left_container, bd=1, relief=SOLID)
fsi_frame.pack(padx=10, pady=(60,10))

# Create a label for the frame
fsi_label = Label(fsi_frame, text="FSI Data From HV/DCDC", font=("Arial", 14, "bold"))
fsi_label.pack(side=TOP,pady=(20))

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

# Define the speed label similar to other labels
speed_label = Label(left_frame, text="Speed: ", anchor=W)
speed_label.grid(row=len(labels_left), column=0, padx=5, pady=5)

# Define a read-only Entry widget for the speed
speed_entry = Entry(left_frame, state='readonly', width=20)
speed_entry.grid(row=len(labels_left), column=1, padx=5, pady=5)

packet_count = 0
start_time = 0
payload = b""  # Initialize payload variable

# Create a frame for the Update Scaling Factors button
button_frame = Frame(left_container)
button_frame.pack(padx=10, pady=10)

# Create a button to trigger updating the scaling factors
update_button = Button(button_frame, text="Update Scaling Factors", command=update_scaling_factors)
update_button.pack(pady=10)

# Define a read-only Entry widget for the speed
speed_entry = Entry(left_frame, state='readonly', width=20)
speed_entry.grid(row=len(labels_left), column=1, padx=5, pady=5)

# Create a button to log data
log_button = Button(left_frame, text=" Start Logging", command=start_logging)
log_button.grid(row=len(labels_left) + 1, column=0, padx=(1,1), pady=(30,25))

# Create a button to stop logging
stop_button = Button(left_frame, text="Stop Logging", command=stop_logging, state=DISABLED)
stop_button.grid(row=len(labels_left) + 1, column=1, padx=(1,1), pady=(30,25))

# Create a Frame for the right side
right_frame = Frame(main_frame)
right_frame.pack(side=RIGHT, padx=10, pady=10)

# Create a frame for the Ethernet Frame Sender
ethernet_frame_sender_frame = Frame(right_frame, bd=1, relief=SOLID)

# Use a label to set a minimum height for the frame
empty_label = Label(ethernet_frame_sender_frame, height=1)
empty_label.pack()

ethernet_frame_sender_frame.pack(anchor=N,padx=10, pady=20)

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
send_button.pack(pady=(70,15))

# Function to update the GUI
def update_gui():
    global packet_count, start_time

    window.update()
    window.after(100, update_gui)  # Schedule the next GUI update


# Function to calculate speed and update speed label
def calculate_speed():
    global packet_count, start_time, payload_size
    elapsed_time = time.time() - start_time

    if elapsed_time > 0:
        total_size = packet_count * payload_size  # Total size of payload data received
        receiving_speed = (total_size * 8) / (elapsed_time * 1000000)  # Calculate speed in Mbps
        speed_entry.config(state='normal')  # Temporarily set state to normal to modify text
        speed_entry.delete(0, END)
        speed_entry.insert(END, "{:.2f} Mbps".format(receiving_speed))
        speed_entry.config(state='readonly')  # Set the state back to readonly

        packet_count = 0  # Reset packet count
        start_time = time.time()  # Reset start time
    window.after(500, calculate_speed)  # Schedule the next speed calculation


# Function to process each packet
payload_data = [] #global variable to store payload data


def process_packet(packet):
    global packet_count, payload, payload_data, payload_size

    if packet.haslayer(Ether) and packet.haslayer(Raw):
        payload = packet.getlayer(Raw).load
        payload_size = len(payload)  # Update payload_size
        data = [payload[i:i + 2][::-1] for i in range(0, len(payload), 4)]  # Note byte order switching

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

        # Store payload data in global variable
        payload_data = data
        log_payload_data()



# Function to capture packets
def capture_packets(interface):
    sniff(iface=interface, prn=process_packet, filter="ether dst host F8:E4:3B:73:58:19", store=0)  #08:97:98:DD:EF:61", store=0)  # 00:73:41:00:04:f8", store=0)

# Start capturing packets in a separate thread
interface = "Gateway"  # Update with the correct interface name
capture_thread = threading.Thread(target=capture_packets, args=(interface,))
capture_thread.start()



# Start the GUI main loop
window.after(100, update_gui)  # Start the GUI update loop
#window.after(500, calculate_speed)  # Start the speed calculation loop
window.mainloop()
