#!/usr/bin/env python3

#INCLUDE LIBRARIES
import socket

class UDP:
    def __init__(self, ip, port):
        """
        Initializes the UDP server.

        Parameters:
        - ip (str): The IP address to bind the server socket to.
        - port (int): The port number to bind the server socket to.
        
        """
        self.UDP_IP = ip
        self.UDP_PORT = port
        self.MAX_PACKET_SIZE = 60000

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        print("waiting for connection...")
        
        

    def binding(self):
        self.socket.bind((self.UDP_IP, self.UDP_PORT))
        print("Connected")

    def send_data(self, data):
        """
        Sends data through the UDP socket.

        Parameters:
        ----------
        - data (bytes): The data to be sent through the UDP socket.

        """
        self.socket.sendto(data, (self.UDP_IP, self.UDP_PORT))

    def receive_data(self, buffer_size):
        """
        Receives data from the UDP socket with a specified buffer size.

        Parameters:
        ----------
        - data (bytes): The data to be received through the UDP socket.

        """
        return self.socket.recvfrom(buffer_size)

    def close(self):
        """
        Closes the UDP socket.

        """
        self.socket.close()
   

