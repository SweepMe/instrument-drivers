# -*- coding: utf-8 -*-

import time
from comtypes.client import CreateObject
N778x = CreateObject("AgServerN778xLib.AgN778x")

try:
    N778x.Initialize('GPIB3::30::INSTR', True, True, 'Simulate = true')

    response = N778x.SCPIQuery('*IDN?')
    print('ID: ' + response)

    print('Close IVI session')
    N778x.Close()
    print('Script has finished')

except Exception as err:
    print('Exception: ' + str(err))

finally:
    # perform clean up operations
    print('complete')