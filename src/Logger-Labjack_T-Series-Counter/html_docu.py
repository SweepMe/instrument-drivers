url = (r"https://labjack.com/pages/support?doc=/software-driver"
       "/installer-downloads/ljm-software-installers-t4-t7-digit"
       "/#section-header-two-fhnxc")
ljm_hyperlink = f'<a href="{url}">LJM software</a>'
url2 = (r"https://labjack.com/pages/support?doc=/datasheets/t-series-datasheet/130-"
        "digital-io-t-series-datasheet/")
pin_names_hyperlink = f'<a href="{url2}">docu table 13</a>'
url3 = (r"https://labjack.com/pages/support?doc=/datasheets"
        "/t-series-datasheet/40-hardware-overview-t-series-datasheet/")
hardware_hyperlink = f'<a href="{url2}">pin functions</a>'
html_driver_descript = f"""
    <h3>Driver for the labjack T4/T7's counter functionality</h3>
    <p> The driver supports counting in non-stream mode </p>
    <p>Requirements:</p>
    <ul>
    <li>Please install the {ljm_hyperlink} (before first run)</li>
    </ul>
    <p>Features/Inputs:</p>
    <ul>
    <li>Counter pin names: pin names to read eg 'CIO0, CIO1'</li>
    <li>Count time (s): the count time in seconds<br></li>
    <li>Override clock: for some pins the counter function can conflict with the Labjack internal
     clock settings, if other EF DIO functions such as PWM have been used. Override will make sure
     the relevant clocks are set for counting but may affect other EF measurements.
    <li>Bus time correction (s): a correction to the measurement duration accounting for the 
    USB/ethernet 'stop' command transmission</li>
    <li>Pin name and functions can be found at {pin_names_hyperlink} and {hardware_hyperlink}</li>
    </ul>
    <p>&nbsp;</p>
    """