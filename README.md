# RFI_scanner

This repository contains the firmware and software for the RFI scanner, an radio interference monitor for radio observatories.


#  Getting Started

Follow these steps to get the service running a Rapberry pi 4/5, this assumes that the Raspberry pi has an network access in order to download the required packages.
If the pi is connected over USB to a TinySA spectrum analyzer the script can be launched immediately if not it can still be lauched but it will fail quietly in the background until it is plugged


## 1. Clone the Repository

```bash
git clone https://github.com/Slash-4/RFI_scanner.git
```

## 2. Navigate into the Project Directory

```bash
cd RFI_scanner
```

## 3. Make the Setup Script Executable

```bash
chmod +x setup.bash
```

## 4. Run the Setup Script

```bash
./setup.bash
```

If the TinySA is plugged and everything is working properly, the green bar at the bottom of the TinySa should look dashed and continuously scroll across the bottom.
If the line is continuous there could be a fault. 





