from tkinter import *
from scapy.all import *
import time
import threading

# Create GUI
window = Tk()
window.title("HV/DCDC ADC Parameters")
window.geometry("800x600")

# Create a frame for the FSI data
fsi_frame = Frame(window, bd=1, relief=SOLID)
fsi_frame.pack(side=LEFT, padx=10, pady=10)

# Create a label for the frame
fsi_label = Label(fsi_frame, text="FSI Data From HV/DCDC", font=("Arial", 14, "bold"))
fsi_label.pack(side=TOP)

# Create a Frame for the left side
left_frame = Frame(fsi_frame)
left_frame.pack(side=LEFT, padx=10, pady=10)

# Create a Frame for the right side
right_frame = Frame(fsi_frame)
right_frame.pack(side=LEFT, padx=10, pady=10)

# Create text boxes and labels in the left side
text_boxes_left = {
    "Current_LV_Phase1_u16": Entry(left_frame, width=20, state="readonly"),
    "Current_LV_Phase2_u16": Entry(left_frame, width=20, state="readonly"),
    "Current_LV_u16": Entry(left_frame, width=20, state="readonly"),
    "Voltage_LV_u16": Entry(left_frame, width=20, state="readonly"),
    "Voltage_VClamp_u16": Entry(left_frame, width=20, state="readonly"),
    "Voltage_HV_u16": Entry(left_frame, width=20, state="readonly"),
    "Current_HV_u16": Entry(left_frame, width=20, state="readonly")
}

labels_left = {}

for i, (key, text_box) in enumerate(text_boxes_left.items()):
    labels_left[key] = Label(left_frame, text=key + ": ", anchor=W)
    labels_left[key].grid(row=i, column=0, sticky=W)
    text_box.grid(row=i, column=1, sticky=W)
    text_box.insert(END, "No Data Available")

# Create raw data text boxes in the right side
raw_text_boxes_left = {
    key: Entry(right_frame, width=20, state="readonly") for key in text_boxes_left.keys()
}

scaling_factors = {
    "Current_LV_Phase1_u16": {"lower_limit": 0, "upper_limit": 0},
    "Current_LV_Phase2_u16": {"lower_limit": 0, "upper_limit": 0},
    "Current_LV_u16": {"lower_limit": -165, "upper_limit": 165, "resolution": 0.080586081, "offset": 2047.5},
    "Voltage_LV_u16": {"lower_limit": 0, "upper_limit": 26.871, "resolution": 0.006561905, "offset": 0},
    "Voltage_VClamp_u16": {"lower_limit": 0, "upper_limit": 93.748, "resolution": 0.022893284, "offset": 0},
    "Voltage_HV_u16": {"lower_limit": 0, "upper_limit": 996.3793, "resolution": 0.243316068, "offset": 0},
    "Current_HV_u16": {"lower_limit": -14.285714, "upper_limit": 14.285714, "resolution": 0.00697715, "offset": 2047.5}
}

# Adjust row heights to increase vertical space
for i in range(len(text_boxes_left)):
    right_frame.rowconfigure(i, minsize=30)

speed_label = Label(left_frame, text="Speed: ", anchor=CENTER)
speed_label.grid(row=len(text_boxes_left), columnspan=2, sticky=W+E)

packet_count = 0
start_time = 0
payload = b""  # Initialize payload variable

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

        for i, (key, text_box, raw_text_box) in enumerate(zip(text_boxes_left.keys(), text_boxes_left.values(), raw_text_boxes_left.values())):
            if key in scaling_factors and i < len(data):
                scaling_factor = scaling_factors[key]
                hex_value = int.from_bytes(data[i], byteorder="big", signed=False)
                scaled_value = ((hex_value - scaling_factor.get("offset", 0)) * scaling_factor.get("resolution", 1.0))

                text_box.config(state="normal")
                text_box.delete(0, END)
                text_box.insert(END, "{:.2f}".format(scaled_value))
                text_box.config(state="readonly")

                raw_text_box.config(state="normal")
                raw_text_box.delete(0, END)
                raw_text_box.insert(END, "0x{:04x}".format(hex_value))
                raw_text_box.config(state="readonly")
            else:
                text_box.config(state="normal")
                text_box.delete(0, END)
                text_box.insert(END, "No Data Available")
                text_box.config(state="readonly")

                raw_text_box.config(state="normal")
                raw_text_box.delete(0, END)
                raw_text_box.config(state="readonly")

        packet_count += 1

# Function to capture packets
def capture_packets(interface):
    sniff(iface=interface, prn=process_packet, filter="ether dst host 00:73:41:00:04:f8", store=0)

# Start capturing packets in a separate thread
interface = "Ethernet"  # Update with the correct interface name
capture_thread = threading.Thread(target=capture_packets, args=(interface,))
capture_thread.start()

# Start the GUI main loop
window.after(100, update_gui)  # Start the GUI update loop
window.after(1000, calculate_speed)  # Start the speed calculation loop
window.mainloop()
