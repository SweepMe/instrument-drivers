""" HTML docu string for labjack ADC"""

# URLS
ljm_url = (r"https://labjack.com/pages/support?doc=/software-driver"
           "/installer-downloads/ljm-software-installers-t4-t7-digit"
           "/#section-header-two-fhnxc")
pins_dio_url = (r"https://labjack.com/pages/support?doc=/datasheets/t-series-datasheet/130-"
                "digital-io-t-series-datasheet/")
hardware_url = (r"https://labjack.com/pages/support?doc=/datasheets"
                "/t-series-datasheet/40-hardware-overview-t-series-datasheet/")
url_ef = (r"https://labjack.com/pages/support?doc=/datasheets"
          "/t-series-datasheet/141-ain-extended-features-t-series-datasheet/")
errors_url = (
    r"https://labjack.com/pages/support/software/?doc=/software-driver/ljm-users-guide/error-codes/"
)

# HTML hyper links
ljm_hyperlink = f'<a href="{url}">LJM software</a>'
pin_names_hyperlink = f'<a href="{pins_dio_url}">docu table 13</a>'
hardware_hyperlink = f'<a href="{hardware_url}">pin functions</a'
error_hyperlink = f'<a href="{errors_url}">error codes</a>'

# HTML Driver text
html_driver_descript = f"""
    <h3>Driver to read labjack T4/T7's AIN and DIO pin inputs</h3>
    <p>The driver supports basic DIO read, basic AIN read and AIN extended functions (EF).<br>
    Instrument connections are based on serial numbers (use find ports).<br>
    EF settings will apply to all pins in the read list. To measure 2 different EFs from the same
    labjack make a second logger instance in the sequencer with the same SN but different read names
    and functions./p>
    <p>Requirements:</p>
    <ul>
    <li>Please install the {ljm_hyperlink} (before first run)</li>
    </ul>
    <p>Features/Inputs:</p>
    <ul>
    <li>Analog read pin names: pin names to read eg 'AIN0, AIN2'</li>
    <li>Digitial read pin names: pin names to read eg 'DIO12, FIO2'<br></li>
    <li>Extended AIN mode: applies an EF mode to all selected AIN read pins.
     Config via Kippling or config string.</li>
    <li>EF config string: a string to be parsed to a dictionary with EF config options.
     See <a href="{url_ef}">AIN EF functions</a>
       examples are within quotes. Please do not copy the quotes.
       EXAMPLE 1: 'A: 100, B:3, C: , D:, E:, F:, G:'
       EXAMPLE 2: 'A: 100, B:4' </li>
    <li>Note invalid EF parameters (possibly including empty) will lead to errors during measure's
     readnames(). See  {error_hyperlink} <br></li>
    <li>T4 flex pins can also be set to analog in</li>
    <li>Pin name and functions can be found at {pin_names_hyperlink} and {hardware_hyperlink}
    </ul>
    <p>&nbsp;</p>
    """