## Making a measurement

Before making any measurements a user should start by wiring together the RFI scanner as in the diagram. One connection which is
not indicated is the 5v supply to the LNA. You can still make a measurement without the LNA inline but the gain calibration assumes that the their is LNA present will be inaccurate unless another calibration file is used. 

![schematics_rfi_scanner(1)](https://github.com/user-attachments/assets/843ec5f8-3f4c-4618-9ac8-7ecdee61c323)
<img src="https://github.com/user-attachments/assets/843ec5f8-3f4c-4618-9ac8-7ecdee61c323" width="200">


To use the warning light you can use the following pins

![rpi_pinout](https://github.com/user-attachments/assets/a8d17f1a-0a7d-46e0-b22b-34ccc905051e)


In order to make a measurement there a two possible approaches, automatic or manual, both approaches assume that you are using a Raspberry Pi 4/5 with network access, at least for the duration of the installation.

## Automatic

The automatic approach will create a local systemctl process which will start up on power on. If it finds a connected TinySA it will start to request scans whithin the range specified in the config.json file. A new .csv will be generated for every power on labelled with the Raspberry Pi's time (this time is not necessarily real time unless the pi is connected to a network). 


### 1. Clone the Repository

```bash
git clone https://github.com/Slash-4/RFI_scanner.git
```

### 2. Navigate into the Project Directory

```bash
cd RFI_scanner
```

### 3. Make the Setup Script Executable

```bash
chmod +x setup.bash
```

### 4. Run the Setup Script

```bash
./setup.bash
```

The service is called rfi_scanner.service


### Start/Stop service (for this boot)

```bash
sudo sytemctl start rfi_scanner.service
sudo systemctl stop rfi_scanner.service
```
### Enable/Disable service

```bash
sudo systemctl enable rfi_scanner.service
sudo systemctl disable rfi_scanner.service
```

## Stdout log 
Live output log for debug

```bash
sudo journalctl -u rfi_scanner.service -f
```

## Manual 

The manual approach allows you to run the python script by hand to make singleton measurements. One small risk with this approach
is the .venv setup. Notably, the pyserial package can cause some trouble due to shadowing of the package by other tools. A way to make sure it isn't overshadowed is to pip uninstall serial pyserial 

### 1. Clone the Repository

```bash
git clone https://github.com/Slash-4/RFI_scanner.git
cd RFI_scanner
```

### 2. Create venv

```bash
python3 -m <venv_name> <venv_path>
source <venv_path>/bin/activate
```
### 3.Install dependencies

```bash
pip install --upgrade pip setuptools wheel
pip install .
pip uninstall -y serial python-serial pyserial
pip install pyserial
```
### 4. Run script 

```bash
cd src/rfi_scanner/
./pi_ctrl.py
```

The script will run continously until halted by ctrl+C 
