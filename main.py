import streamlit as st
import time
import threading
from udp import UDP
import struct
import binascii
import socket
from threading import Thread
import requests
import math

st.set_page_config(page_title = 'SIYI Gimbal Control',page_icon="SIYI.jpg", layout="wide", menu_items={
        'Get Help': 'https://www.linkedin.com/in/maazjamshaid/',
        'Report a bug': "https://www.linkedin.com/in/maazjamshaid/"
    })
st.title("SIYI Gimbal Control")

st.sidebar.image("SIYI.jpg")
st.sidebar.header('Instructions')
st.sidebar.info('Enter the Gimbal IP and Port')
st.sidebar.info('Reset Gimbal using the **GIMBAL RESET** button')
st.sidebar.info('Select the working mode of Gimbal')
st.sidebar.info('Move the Gimbal using Pan and Tilt sliders')
st.sidebar.info('Request Gimbal Camera Codec Specs')
st.sidebar.info('Send Codec Specs to Gimbal Camera')
st.sidebar.info('Control Zoom using Buttons and Slider (Click checkbox to activate **ZOOM CONTROL**)')

def send_udp_data(ip, port, data):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(data, (ip, int(port)))

def send_udp_data_ack(ip, port, data):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(5)  # Set a timeout to avoid indefinite waiting
    sock.sendto(data, (ip, int(port)))
    
    try:
        # Receiving response from the gimbal
        response, addr = sock.recvfrom(1024)  # 1024 is the buffer size
        st.code(f"ACK received from {addr}: {binascii.hexlify(response)}")
    except socket.timeout:
        st.error("No ACK received (timeout).")
    except Exception as e:
        st.error(f"No ACK received (timeout).")
    finally:
        sock.close()
    return response

def calculate_crc16_xmodem(data):
    crc = 0x0000

    for byte in data:
        crc ^= (byte << 8)
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc <<= 1

    crc &= 0xFFFF
    return crc.to_bytes(2, byteorder='little')

def extract_values(self, reply):
        """
        Extracts attitude status values from the received UDP reply.

        Parameters:
        - reply (bytes): The received UDP reply containing attitude status data.

        Returns:
        - tuple: A tuple containing yaw, pitch, roll, yaw velocity, pitch velocity, and roll velocity.

        """
        try:
            yaw = struct.unpack('<h', reply[8:10])[0] / 10.0
            pitch = struct.unpack('<h', reply[10:12])[0] / 10.0
            roll = struct.unpack('<h', reply[12:14])[0] / 10.0
            yaw_velocity = struct.unpack('<h', reply[14:16])[0] / 10.0
            pitch_velocity = struct.unpack('<h', reply[16:18])[0] / 10.0
            roll_velocity = struct.unpack('<h', reply[18:20])[0] / 10.0
            

            return yaw, pitch, roll, yaw_velocity, pitch_velocity, roll_velocity
        except:
            pass

st.info("GIMBAL IP AND PORT")

gimbal_ip = st.text_input('Enter Gimbal IP:', value="27.27.3.54")
gimbal_port = st.number_input('Enter Gimbal Port:', min_value=0, max_value=65535, value=37260)

st.markdown("---")

st.info("Test Command Interface")

test_cmd = st.text_input("Enter Test Command")
test_cmd = str(test_cmd)
if st.button("Send Test Command"):
    send_udp_data_ack(gimbal_ip, gimbal_port, bytes.fromhex(test_cmd))
st.markdown("---")


st.error("RESET OPTIONS", icon = "💀" )
col1, col2, col3 = st.columns(3)

with col1:
    if st.button('GIMBAL RESET', help="Allows for the controlled reboot of gimbal. Resets the gimbal's pan and tilt to default (0 degrees)"):
        st.session_state.pan_slider = 0
        st.session_state.tilt_slider = 0
        send_udp_data(gimbal_ip, gimbal_port, bytes.fromhex("556601020000008000011a8a"))
        st.error("GIMBAL RESETTING!!!")

with col2:
    if st.button('CAMERA RESET', help = "Allows for the controlled reboot of camera"):
        send_udp_data(gimbal_ip, gimbal_port, bytes.fromhex("556601020000008001000aa9"))
        st.error("CAMERA RESETTING!!!")

with col2:
    drnAlt = st.number_input("Enter Drone Altitude: ", max_value = 2000, min_value = 0, value = 1000)
    if st.button('ZOOM FIX'):
        zoom_level = (1/260) * (abs(drnAlt) + 5)
        zoom_level = math.ceil(zoom_level)
        st.code(f"Zoom Level: {zoom_level}X")
        zoom_hex = bytes.fromhex(f"556601020010000f0{zoom_level}00")
        zoom_crc = calculate_crc16_xmodem_2(zoom_hex)
        ZOOM = zoom_hex + zoom_crc
        send_udp_data(gimbal_ip, gimbal_port, ZOOM)
        st.error("ZOOM FIX!!!")

st.markdown("---")

st.info("CAMERA MODES")

col1, col2, col3 = st.columns(3)
with col1:     
    if st.button('FOLLOW MODE', help = "The gimbal follows the aircraft's yaw rotation, maintaining a stable shot."):
        send_udp_data(gimbal_ip, gimbal_port, bytes.fromhex("556601010000000c04b08e"))
        
with col2:     
    if st.button('LOCK MODE', help = "The gimbal remains fixed and does not follow aircraft rotation until reaching its limit."):
        send_udp_data(gimbal_ip, gimbal_port, bytes.fromhex("556601010000000c0357fe"))

with col3:
    if st.button('FPV MODE', help = "The gimbal rotates with the aircraft, providing a first-person view while stabilizing the image."):
        send_udp_data(gimbal_ip, gimbal_port, bytes.fromhex("556601010000000c05919e"))
        st.error("Only tilt function works in FPV Mode")

st.markdown("---")

st.info("GIMBAL SLIDER CONTROL")
if st.checkbox("ENABLE/DISABLE", key = 1):
    if 'pan_slider' not in st.session_state:
        st.session_state.pan_slider = 0
    if 'tilt_slider' not in st.session_state:
        st.session_state.tilt_slider = -30

    col1, col2, col3, col4 = st.columns(4)

    with col1:   
        st.session_state.pan_slider = st.slider('Gimbal Pan', min_value=-160, max_value=160, value=st.session_state.pan_slider)
        pan_slider = st.session_state.pan_slider * 10

    with col2:   
        st.session_state.tilt_slider = st.slider('Gimbal Tilt', min_value=-90, max_value=45, value=st.session_state.tilt_slider)
        tilt_slider = st.session_state.tilt_slider * 10

    with col4:
        if st.button('CENTRE GIMBAL'):
            st.session_state.pan_slider,st.session_state.tilt_slider = 0, 0
            # send_udp_data(gimbal_ip, gimbal_port, bytes.fromhex("556601010000000801d112"))

    pan_slider = int(pan_slider)
    tilt_slider = int(tilt_slider)
    pan_slider_bytes = pan_slider.to_bytes(2, byteorder='little', signed=True)
    tilt_slider_bytes = tilt_slider.to_bytes(2, byteorder='little', signed=True)
    original_hex = bytes.fromhex("556601040000000E")
    modified_hex = original_hex + pan_slider_bytes + tilt_slider_bytes 
    crc_result = calculate_crc16_xmodem(modified_hex)
    final_hex = modified_hex + crc_result
    send_udp_data(gimbal_ip, gimbal_port, final_hex)        
    time.sleep(0.001)

st.markdown("---")

st.info("ENABLE/DISABLE GIMBAL MANUAL CONTROL")
if st.checkbox("ENABLE/DISABLE", key = 2):
    st.info("MANUAL GIMBAL CONTROL")

    if 'pan_slider' not in st.session_state:
        st.session_state.pan_slider = 0
    if 'tilt_slider' not in st.session_state:
        st.session_state.tilt_slider = 0

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("PAN RIGHT"):
            st.session_state.pan_slider = st.session_state.pan_slider + 5
        if st.button("TILT UP"):
            st.session_state.tilt_slider = st.session_state.tilt_slider + 5
    with col2:
        if st.button("PAN LEFT"):
            st.session_state.pan_slider = st.session_state.pan_slider - 5
        if st.button("TILT DOWN"):
            st.session_state.tilt_slider = st.session_state.tilt_slider - 5
    with col3:
        st.info(f"PAN: {st.session_state.pan_slider}°")
        st.info(f"TILT: {st.session_state.tilt_slider}°")

st.markdown("---")

st.info("REQUESTING GIMBAL CAMERA CODEC SPECS")
codec_options = ["Recording stream", "Main stream", "Sub stream"]
selected_option = st.selectbox("Request for:", codec_options, help = "Substream only available in case of ZT6 and ZR30")

if selected_option == "Recording stream":
    req_codec_bit = "00"
elif selected_option == "Main stream":
    req_codec_bit = "01"
elif selected_option == "Sub stream":
    req_codec_bit = "02"

request_codec_cmd = bytes.fromhex(f"5566010100000020{req_codec_bit}")

# st.write(type(request_codec_cmd))
request_codec_cmd = request_codec_cmd + calculate_crc16_xmodem(request_codec_cmd)
# st.write("Command Generated: ", request_codec_cmd)

if st.button("Request"):
    response = send_udp_data_ack(gimbal_ip, gimbal_port, request_codec_cmd)

    cmd = binascii.hexlify(response)
    resolution_l_hex = cmd[20:24] 
    resolution_h_hex = cmd[24:28] 
    stream_type = cmd[16:18]  
    video_enc_type_hex = cmd[18:20]  
    bitrate_hex = cmd[28:32] 
    frame_rate = cmd[32:34]

    def reverse_and_convert(hex_str):
        reversed_hex = hex_str[2:4] + hex_str[0:2]  
        decimal_value = int(reversed_hex, 16)  
        return decimal_value

    resolution_l = reverse_and_convert(resolution_l_hex)  
    resolution_h = reverse_and_convert(resolution_h_hex)  

    if stream_type == b"00":
        stream_type_desc = "Recording Stream"  
    elif stream_type == b"01":
        stream_type_desc = "Main Stream" 
    elif stream_type == b"02":
        stream_type_desc = "Sub Stream"  


    video_enc_type = video_enc_type_hex
    if video_enc_type == b"01":
        video_enc_type_desc = "H264"
    elif video_enc_type == b"02":
        video_enc_type_desc = "H265"


    bitrate = reverse_and_convert(bitrate_hex)  
    bitrate_mbps = bitrate / 1000 

    frame_rate = int(frame_rate, 16)

    st.write(f"Resolution (Width): {resolution_l} pixels")  
    st.write(f"Resolution (Height): {resolution_h} pixels") 
    st.write(f"Stream Type: {stream_type_desc}")
    st.write(f"Bitrate: {bitrate_mbps} Mbps")  
    st.write(f"Video Encoding Type: {video_enc_type_desc}")
    st.write(f"Video Frame Rate: {frame_rate}")
    
st.markdown("---")

st.info("SEND CODEC SPECS")
#BITRATE 
bitrate = st.number_input("Enter Bitrate (Mbps)", min_value = 2, max_value = 4, value = 4)
bitrate = int(f"{bitrate}000")
hex_bitrate = format(bitrate, '04x') 
byte1, byte2 = hex_bitrate[:2], hex_bitrate[2:] 
reversed_bytes = byte2 + byte1
###

#ENCODING
enc_options = ["H264", "H265"]
encoding_format = st.selectbox("Select Encoding Format:", enc_options)

if encoding_format == "H264":
    enc_bits = "01"
elif encoding_format == "H265":
    enc_bits = "02"
###

#RESOLUTION
res_options = ["UHD", "HD"]
resolution = st.selectbox("Select Resolution:", res_options)

if resolution == "UHD":
    res_bits = "80073804"
elif resolution == "HD":
    res_bits = "0005D002"
###

#STREAM 
stream_options = ["Recording stream", "Main stream", "Sub stream"]
stream = st.selectbox("Select Stream:", stream_options)

if stream == "Recording stream":
    stream_bits = "00"
elif stream == "Main stream":
    stream_bits = "01"
elif stream == "Sub stream":
    stream_bits = "02"
###

codec_command = bytes.fromhex(f"5566010900000021{stream_bits}{enc_bits}{res_bits}{reversed_bytes}00")
crc_codec = calculate_crc16_xmodem(codec_command)
codec_command = codec_command + crc_codec

st.write("Command Generated: ", binascii.hexlify(codec_command))

if st.button("Send"):
    send_udp_data(gimbal_ip, gimbal_port, codec_command)

st.markdown("---")
st.info("ZOOM CONTROL")
if st.checkbox("ENABLE/DISABLE", key = 3):
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("ZOOM IN"):
            send_udp_data(gimbal_ip, gimbal_port, bytes.fromhex("5566010100000005018d64"))
            time.sleep(0.5)
            send_udp_data(gimbal_ip, gimbal_port, bytes.fromhex("556601010000000500AC74"))
    with col2:
        if st.button("STOP"):
            send_udp_data(gimbal_ip, gimbal_port, bytes.fromhex("556601010000000500AC74"))
    with col3:
        if st.button("ZOOM OUT"):
            send_udp_data(gimbal_ip, gimbal_port, bytes.fromhex("5566010100000005FF5c6a"))
            time.sleep(0.5)
            send_udp_data(gimbal_ip, gimbal_port, bytes.fromhex("556601010000000500AC74"))

    st.info("ZOOM CONTROL SLIDER")
    if st.checkbox("ZOOM SLIDER"):
        st.error("Zoom Slider Mode is ON")
        zoom_value = st.slider('Zoom Value', min_value=1.0, max_value=6.0, step=0.1, value=1.0, format="%.1f")
        integer = int(zoom_value)
        decimal = int((zoom_value - integer) * 10)
        zoom_command = bytes.fromhex(f"556601020010000f0{integer}0{decimal}")
        crc_zoom = calculate_crc16_xmodem(zoom_command)
        zoom_command = zoom_command + crc_zoom
        send_udp_data(gimbal_ip, gimbal_port,zoom_command)
