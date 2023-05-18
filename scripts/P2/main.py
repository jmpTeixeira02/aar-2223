GROUP_NUMBER = "4"

import getpass
import SerialSetup
import OSPFConfig

password = getpass.getpass()


try:
    OSPFConfig.init(GROUP_NUMBER, password)
except:
    SerialSetup.init(GROUP_NUMBER)
    OSPFConfig.init(GROUP_NUMBER, password)