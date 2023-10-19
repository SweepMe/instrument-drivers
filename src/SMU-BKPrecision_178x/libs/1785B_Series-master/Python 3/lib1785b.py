def csum(command):  
    checksum = 0
    for i in range(25):     
        checksum = checksum + command[i]                    
    return (0xFF & checksum)                    
    
def command(command, serial):                          
    command[0] = 0xAA
    command[25] = csum(command)
    serial.write(command)                        
    resp = serial.read(26)
    if resp[2] == 0x12:
        if resp[3] == 0x80:
            """Success"""
            return
        elif resp[3] == 0x90:
            raise Exception('Checksum Error')
        elif resp[3] == 0xA0:
            raise Exception('Parameter Incorrect')
        elif resp[3] == 0xB0:
            raise Exception('Unrecognized Command')
        elif resp[3] == 0xC0:
            raise Exception('Invalid Command')
            
        print("Command Sent:\t\t",end=' ')
        printCmd(command)
            
        print("Reponse Received:\t",end=' ')    
        printCmd(resp)
    else:
        return resp
    
def printCmd(buff):
    x = " "        
    for y in range(len(buff)):
        x+=" "
        x+=hex(buff[y]).replace('0x','')   
    print(x)
    
def remoteMode(state, serial):
    """Remote Mode"""
    cmd = [0] * 26
    cmd[2] = 0x20
    if bool(state):
        cmd[3] = 1
    else:
        cmd[3] = 0
    command(cmd, serial)
    
def outputOn(state, serial):
    """Input On. state = True or False"""
    cmd = [0] * 26
    cmd[2] = 0x21
    if bool(state):
        cmd[3] = 1
    else:
        cmd[3] = 0
    command(cmd, serial)
    
def setMaxVoltage(voltage, serial):
    value = int(voltage * 1000)
    """Set Max Voltage"""
    cmd = [0] * 26
    cmd[2] = 0x22
    cmd[3] = value & 0xFF
    cmd[4] = (value >> 8) & 0xFF
    cmd[5] = (value >> 16) & 0xFF
    cmd[6] = (value >> 24) & 0xFF
    command(cmd, serial)
    
def volt(voltage, serial):
    """Set Voltage"""
    value = int(voltage * 1000)
    cmd = [0] * 26
    cmd[2] = 0x23
    cmd[3] = value & 0xFF
    cmd[4] = (value >> 8) & 0xFF
    cmd[5] = (value >> 16) & 0xFF
    cmd[6] = (value >> 24) & 0xFF
    command(cmd, serial)

def curr(current, serial):
    """Set max input current: %f & current"""
    value = int(current * 1000)
    cmd = [0] * 26
    cmd[2] = 0x24
    cmd[3] = value & 0xFF
    cmd[4] = (value >> 8) & 0xFF
    command(cmd, serial)

def setCommAddress(addr, serial):
    """Read the max setup input current."""
    cmd = [0] * 26
    cmd[2] = 0x25
    cmd[3] = addr & 0xFF
    resp = command(cmd, serial)
    
def readAll(serial):
    """Read Voltage and Current settings and readings"""
    """Returns dictionary of values"""
    cmd = [0] * 26
    cmd[2] = 0x26
    resp = command(cmd, serial)
    vals = {}
    vals['c'] = (resp[3]+(resp[4]<<8))/1000
    vals['v'] = (resp[5]+(resp[6]<<8)+(resp[7]<<16)+(resp[8]<<24))/1000
    vals['output'] = resp[9] & 0x01
    vals['overheat'] = resp[9] & 0x02
    mode = ''
    if (resp[9] & 0x0C)>>2 == 1:
        mode = 'CV'
    elif (resp[9] & 0x0C)>>2 == 2:
        mode = 'CC'
    else:
        mode = 'UNREG'
    vals['mode'] = mode
    vals['fanSpeed'] = (resp[9]>>4)&0x07
    vals['remoteCtl'] = (resp[9]&0x80)>>7
    vals['cset'] = (resp[10]+(resp[11]<<8))/1000
    vals['vmax'] = (resp[12]+(resp[13]<<8)+(resp[14]<<16)+(resp[15]<<24))/1000
    vals['vset'] = (resp[16]+(resp[17]<<8)+(resp[18]<<16)+(resp[19]<<24))/1000
    return vals
    
def readID(serial):
    """ID info - returns dict"""
    cmd = [0] * 26
    cmd[2] = 0x31
    resp = command(cmd, serial)
    vals = {}
    mod = ''
    for i in range(3,6,1):
        mod = mod + chr(resp[i])
    vals['model'] = mod
    vals['sw'] = resp[8]+(resp[9]<<8)
    sn = ''
    for i in range(10,19,1):
        sn = sn + chr(resp[i])
    vals['sn'] = sn
    return vals
    
def restoreFactoryCal(serial):
    """Restore factory calibration values"""
    cmd = [0] * 26
    cmd[2] = 0x32
    command(cmd, serial)

def enableLocalKey(state, serial):
    """Enable/Disable Local key (7) with bool value (True/False)"""
    cmd = [0] * 26
    cmd[2] = 0x37
    if bool(state):
        cmd[3] = 1
    else:
        cmd[3] = 0
    command(cmd, serial)
    
