from tkinter import *
from scapy.all import *
import time
import threading

# Create GUI
window = Tk()
window.title("HV/DCDC ADC Parameters")
window.geometry("800x600")

# Create labels
labels = {
    "Current_LV_Phase1_u16": Label(window, text="Current_LV_Phase1_u16: ", anchor=W),
    "Current_LV_Phase2_u16": Label(window, text="Current_LV_Phase2_u16: ", anchor=W),
    "Current_LV_u16": Label(window, text="Current_LV_u16: ", anchor=W),
    "Voltage_LV_u16": Label(window, text="Voltage_LV_u16: ", anchor=W),
    "Voltage_VClamp_u16": Label(window, text="Voltage_VClamp_u16: ", anchor=W),
    "Voltage_HV_u16": Label(window, text="Voltage_HV_u16: ", anchor=W),
    "Current_HV_u16": Label(window, text="Current_HV_u16: ", anchor=W)
}

# Create raw data labels
raw_labels = {
    key: Label(window, text="", anchor=W) for key in labels.keys()
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

# Grid labels and raw data labels
for i, (label, raw_label) in enumerate(zip(labels.values(), raw_labels.values())):
    label.grid(row=i, column=0, sticky=W)
    raw_label.grid(row=i, column=1, sticky=W)

speed_label = Label(window, text="Speed: ", anchor=CENTER)
speed_label.grid(row=8, column=0, sticky=W + E)

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

        for i, (key, label, raw_label) in enumerate(zip(labels.keys(), labels.values(), raw_labels.values())):
            if key in scaling_factors and i < len(data):
                scaling_factor = scaling_factors[key]
                hex_value = int.from_bytes(data[i], byteorder="big", signed=False)
                scaled_value = ((hex_value - scaling_factor.get("offset", 0)) * scaling_factor.get("resolution", 1.0))

                label.config(text="{}: {:.2f}".format(key, scaled_value))
                raw_label.config(text="Raw: 0x{:04x}".format(hex_value))
            else:
                label.config(text="{}: ".format(key))
                raw_label.config(text="")

        packet_count += 1

# Function to capture packets
def capture_packets(interface):
    sniff(iface=interface, prn=process_packet, filter="ether dst host 00:73:41:00:04:f8", store=0)

# Start capturing packets in a separate thread
interface = "Ethernet 2"  # Update with the correct interface name
capture_thread = threading.Thread(target=capture_packets, args=(interface,))
capture_thread.start()

# Start the GUI main loop
window.after(100, update_gui)  # Start the GUI update loop
window.after(1000, calculate_speed)  # Start the speed calculation loop
window.mainloop()
