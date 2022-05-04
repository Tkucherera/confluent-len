import pyghmi.ipmi.command as cmd
import sys
import os
# alternatively, the following ipmi raw sequence:
# 0x3a 0xc4 0x3 0x0 0x21 0x1 0x9d 0x2f 0x76 0x32 0x2f 0x69 0x62 0x6d 0x63 0x2f 0x75 0x65 0x66 0x69 0x2f 0x66 0x6f 0x72 0x63 0x65 0x2d 0x69 0x6e 0x76 0x65 0x6e 0x74 0x6f 0x72 0x79 0x11 0x1

c = cmd.Command(sys.argv[1], os.environ['XCCUSER'], os.environ['XCCPASS'], verifycallback=lambda x: True)
c.oem_init()
c._oem.immhandler.set_property('/v2/ibmc/uefi/force-inventory', 1)