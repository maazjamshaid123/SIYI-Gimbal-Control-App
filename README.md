# SIYI-Gimbal-Control-App
![Maaz Jamshaid](app.jpg)
## Overview
The SIYI Gimbal Control application allows users to control a SIYI gimbal remotely via a web interface. This app facilitates the management of gimbal functions such as pan and tilt adjustments, mode selections, and camera codec requests.

## Prerequisites
**Network Configuration**: Ensure that your gimbal camera is connected to the same network as your computer running this application. This is crucial for successful communication between the application and the gimbal.
**Install Dependencies**: Make sure you have the required Python packages installed. You can do this by running:
```
pip install streamlit requests
```

## Getting Started
1. **Launch the Application:**
- Open your terminal.
- Navigate to the directory containing your application script.
- Run the application using the command:

```
streamlit run main.py
```
2. **Access the Web Interface:**
- Once the application is running, open a web browser and go to the URL provided in the terminal (typically `http://localhost:8501`).

## Using the Application
1. **Gimbal Configuration**
- Enter Gimbal IP and Port:
  - In the input fields, enter the IP address and port number of your gimbal camera. The default values are typically `27.27.3.54` for IP and `37260` for port.

2. **Gimbal Control**
- **Reset Options:**
  - Use the **GIMBAL RESET** button to reset the gimbal's pan and tilt to their default positions (0 degrees).
  - Use the **CAMERA RESET** button to reboot the camera.

- **Camera Modes:**
  - Choose between **FOLLOW MODE**, **LOCK MODE**, and **FPV MODE** to set the gimbal's operational behavior.

- **Gimbal Slider Control:**
  - Adjust the pan and tilt angles using the sliders provided. Enable or disable the sliders using the checkbox.
  - Click the CENTRE GIMBAL button to reset both pan and tilt to 0 degrees.
 
3. **Zoom Control**
- **Zoom Control:**
  - Activate the zoom control feature using the checkbox. You can control the zoom using buttons and a slider.

4. **Codec Requests**
- **Requesting Gimbal Camera Codec Specs:**
  - Select the desired codec from the dropdown (Recording stream, Main stream, or Sub stream) and click Request to obtain codec specifications.

5. **Sending Test Commands**
- **Test Command Interface:**
  - Enter a hex command in the provided input box and click Send Test Command to send it to the gimbal.

## Troubleshooting
- If you experience any issues, ensure that the gimbal IP and port are correctly configured and that both the gimbal and your computer are connected to the same network.
- Check for any error messages displayed in the application for further insights.

## Support
For further assistance, please contact the developer:
[Maaz Jamshaid](https://www.linkedin.com/in/maazjamshaid/?lipi=urn%3Ali%3Apage%3Ad_flagship3_feed%3B1h1SO1tYRpmlRJlv%2Bgi4eg%3D%3D)

## License
This project is licensed under the MIT License.
