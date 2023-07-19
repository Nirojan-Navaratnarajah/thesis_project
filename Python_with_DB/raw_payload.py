from scapy.all import *


def process_packet(packet):
    if packet.haslayer(Ether) and packet.haslayer(Raw):
        payload = packet.getlayer(Raw).load
        data = [payload[i:i + 2][::-1] for i in range(0, len(payload), 4)]  # Note byte order switching

        for i, value in enumerate(data):
            print(f"Raw Payload Value {i+1}: {value.hex()}")


def capture_packets(interface):
    sniff(iface=interface, prn=process_packet, filter="ether dst host F8:E4:3B:73:58:19", store=0)


interface = "Ethernet 3"  # Replace with the correct interface name
capture_thread = threading.Thread(target=capture_packets, args=(interface,))
capture_thread.start()

# Wait for KeyboardInterrupt (Ctrl+C) to stop the program
try:
    while True:
        pass
except KeyboardInterrupt:
    pass
