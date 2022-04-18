# FFControlPanel

Serial Terminal Control Panel (mainly targetted for BLE on Robots)
Written by Rob Probin, 2022.
Licensed under the MIT license. 

# Goals

- Provide a BLE serial terminal interface, without resorting to kernel level serial drivers.
- Allow extra BLE profiles/characteristics to be added in parallel with serial interface
- Allow control not just be text based, but a tkInter clickable button interface for controlling, say, a robot.
- Allow Serial (RS232 or USB) and BT classic serial as well as BLE
- Provide a GUI terminal interface, not just a command line interface
- Allow the terminal to have a remote end analyser that can understand and interrogate the remote end and spot Errors.


# Commands

_to be added_

# Extending Functionality

_to be added_


# History - BLE

Dealing with Bluetooth Low Energy (BLE) is more tricky than Bluetooth Classic Serial Port Protocol (SSP) - also called RFCOMM, the later which was designed as a serial port replacement.

BLE is really a short of shared variable system between central and device - where changes in the device can be polled or notified, and acknowledgements are optional. The whole concept is to save RF transmissions by exposing the actual data that's changing, and it suits very well where the BLE chip is also the microcontroller/microprocessor controlling the device.

However, if the device is split into seperate microprocessors/microcontrollers, then this information has be passed chip to chip - this is generally done with some sort of serial link (e.g. UART, SPI, I2C, etc.) and hence a shared variable system (or local database) is not usually the system implemented - although is possible and it does happen. 

Secondly, lots of systems have a serial interface already defined, either for machine-to-machine communcation (often for previous serial or Wi-Fi use) or for human interaction.

In the case of this project there were two uses:

 * UKMARSBot - both for the mazerunner example and for ukmarsey have a human serial interface - usually over serial or Bluetooth SPP.
 * Forth usage on various platforms ukmarsbot_forth.

While you can use a kernel driver with a BLE serial driver per device, it appeared that a custom terminal would avoid potential system instability due to kernel drivers, and have a longer life with more flexibility to extend the interface to take account of BLE specific features (like extra profiles and characteristics beyond the basic serial interface).


#History - Inspiration from other Serial Terminals

Takes inspiration from e4thcom and ff-shell, but also several other serial programs.

e4thcom - a Forth based serial terminal, with extra facilities client side. 
 - https://wiki.forth-ev.de/doku.php/en:projects:e4thcom
 - https://mecrisp-stellaris-folkdoc.sourceforge.io/serial-terminals.html
 - https://hackaday.io/project/16097-eforth-for-cheap-stm8s-gadgets/log/188503-new-e4thcom-features-matched-by-codeloadpy

ff-shell provided with FlashForth for interacting with the Forth from a terminal.
 - https://github.com/oh2aun/flashforth/tree/master/shell

PicoCom - Simple terminal that's less hard core than minicom 
 - https://linux.die.net/man/8/picocom

CoolTerm - Create simple cross-platform GUI terminal for embedded work
 - https://freeware.the-meiers.org/

iTerm2 - Mac based easy launching of PicoCom and e4thcom that are both command line based.
 - https://iterm2.com/





