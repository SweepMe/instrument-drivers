""" HTML docu string for labjack TTL"""

url = (r"https://labjack.com/pages/support?doc=/software-driver"
       "/installer-downloads/ljm-software-installers-t4-t7-digit"
       "/#section-header-two-fhnxc")
ljm_hyperlink = f'<a href="{url}">LJM software</a>'
url2 = (r"https://labjack.com/pages/support?doc=/datasheets/t-series-datasheet/130-"
        "digital-io-t-series-datasheet/")
pin_names_hyperlink = f'<a href="{url2}">docu tables 13.0</a>'
html_driver_descript = f"""
    <h3>Switch driver for the Labjack T4/T7's pin outputs</h3>
    <p>The driver supports setting selected DIO outputs to high or low V using. DIO pins can be read
     with the Logger_Labjack-T-Series-ADC module which covers both digital and analog read.
     Note that a pin set to output cannot act as input and may result conflicts with a
     Logger_Labjack-T-Series-ADC</p>
    <p>Requirements:</p>
    <ul>
    <li>Please install the {ljm_hyperlink} (before first run).</li>
    </ul>
    <p>Features/Inputs:</p>
    <ul>
    <li>Output pin names: pin names (DIOX or FIOX etc) to be set</li>
    <li>State (start): the initial state (set at start of branch)</li>
    <li>State (end): the final state (set at end of branch)
    <li>SweepMode: will change the output state based on sweep values. Allowed values are 1 (high) 
    & 0 (low) </li>
    <br></li>
    <li>Pin name and functions can be found at {pin_names_hyperlink}
    </ul>
    <p>&nbsp;</p>
    """