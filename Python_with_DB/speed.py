from tkinter import *
from scapy.all import *
import time

# Create GUI
window = Tk()
window.title("Packet Sniffer")
window.geometry("400x100")

# Create label for speed
speed_label = Label(window, text="Speed: ", anchor=CENTER)
speed_label.pack()

packet_count = 0
start_time = time.time()
payload_size = 0

# Function to calculate and update the speed label
def calculate_speed():
    global packet_count, start_time
    elapsed_time = time.time() - start_time
    receiving_speed = (packet_count * payload_size * 8) / (elapsed_time * 1000000)
    speed_label.config(text="Speed: {:.2f} Mbps".format(receiving_speed))
    packet_count = 0
    start_time = time.time()
    window.after(1000, calculate_speed)  # Schedule the next speed calculation

# Function to process each packet
def process_packet(packet):
    global packet_count, payload_size
    if packet.haslayer(Ether) and packet.haslayer(Raw):
        payload = packet.getlayer(Raw).load
        payload_size = len(payload)
        packet_count += 1

# Function to capture packets
def capture_packets(interface):
    sniff(iface=interface, prn=process_packet, filter="ether dst host F8:E4:3B:73:58:19", store=0)

# Start capturing packets in a separate thread
interface = "Ethernet 3"  # Update with the correct interface name
capture_thread = threading.Thread(target=capture_packets, args=(interface,))
capture_thread.start()

# Start the GUI main loop
window.after(1000, calculate_speed)  # Start the speed calculation loop
window.mainloop()
