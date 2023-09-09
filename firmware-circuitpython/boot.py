import supervisor
import usb_hid
supervisor.set_usb_identification("@74th", "Sparrow-TV v1")
usb_hid.enable([usb_hid.Device.KEYBOARD, usb_hid.Device.MOUSE] 0)