##Making a measurement

Before making any measurements a user should start by wiring together the RFI scanner as in the diagram. One connection which is
not indicated is the 5v supply to the LNA. You can still make a measurement without the LNA inline but the gain calibration assumes that 
the their is LNA present will be inaccurate unless another calibration file is used. 


![schematics_rfi_scanner(1)](https://github.com/user-attachments/assets/843ec5f8-3f4c-4618-9ac8-7ecdee61c323)


In order to make a measurement there a two possible approaches, automatic or manual. 

#Automatic

The automatic measurement is launched using the setup script
