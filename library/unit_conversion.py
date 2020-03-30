# encoding: utf-8
# pylint: disable=no-self-use, too-many-branches, too-many-public-methods
"""Unit Conversion"""
import math

class UnitConversion():
    """Class for UnitConversion"""

    # # INITIALIZE
    # def __init__(self):
    #     """The Constructor UnitConversion class"""
    #     pass

    def to_degrees(self, label, val):
        """Convert Map Value to Degrees"""

        label = label.upper()
        absolute = abs(float(val))
        degrees = math.floor(absolute)
        minutes_not_truncated = (absolute - degrees) * 60
        minutes = math.floor(minutes_not_truncated)
        seconds = math.floor((minutes_not_truncated - minutes) * 60)

        if label == "LATITUDE":
            cardinal = "S"
            if float(val) >= 0:
                cardinal = "N"

        elif label == "LONGITUDE":
            cardinal = "W"
            if float(val) >= 0:
                cardinal = "E"

        else:
            cardinal = ''

        return str(degrees) + "° " + str(minutes) + "' " + str(seconds) + "''" + str(cardinal)

    def convert_uptime(self, data, exempt):
        """Convert Uptime to Day/ Hours/ Minutes/ Seconds"""

        if exempt:
            unit_value = int(data)
        else:
            unit_value = int(data) / 1000

        day = unit_value // (24 * 3600)
        time = unit_value % (24 * 3600)
        hour = time // 3600
        time %= 3600
        minutes = time // 60
        time %= 60
        seconds = time
        result = "%d Days %d Hours %d Minutes %d Seconds" % (day, hour, minutes, seconds)
        return result

    def convert_megahertz_to_hertz(self, data):
        """Convert Mz to Hz """

        result = data * 1000000
        return "{} Hz".format(result)

    def convert_milliampere_to_ampere(self, data):
        """Convert Milliampere to Ampere"""

        result = data * 0.001
        return "{} A".format(result)

    def convert_kilowatts(self, data):
        """Convert to Kilowatts"""

        result = data * 1000
        return "{} kW".format(result)

    def convert_msto_mileperhour(self, data):
        """Convert Meters per second to Miles per hour"""

        result = data * 2.23694
        return "{} mile/hour".format(result)

    def convert_msto_knots(self, data):
        """Convert Meters per second to Knots"""
        if data == 'N':
            return data
        result = data * 1.94
        return "{} knots".format(result)

    # Add unit
    def convert_ampere(self, data):
        """Add Unit to Ampere"""

        return "{} A".format(data)

    def convert_candela(self, data):
        """Add Unit to Candela"""

        return "{} cd".format(data)

    def convert_coulomb(self, data):
        """Add Unit to Coulomb"""

        return "{} C".format(data)

    def convert_cubic_metre(self, data):
        """Add Unit to Cubic Meter"""

        return "{} m³".format(data)

    def convert_day(self, data):
        """Add Unit to Day"""

        return "{} d".format(data)

    def convert_decibel_milliwats(self, data):
        """Add Unit to Decibel-milliwatts"""

        return "{} dBm".format(data)

    def convert_decibel_millivolt(self, data):
        """Add Unit to Decibels relative to one millivolt"""

        return "{} dBmV".format(data)

    def convert_decibel_unit(self, data):
        """Add Unit to Decibels Unit"""

        return "{} dBu".format(data)

    def convert_decibel_volt(self, data):
        """Add Unit to Decibels to Volt"""

        return "{} dBV".format(data)

    def convert_decibel(self, data):
        """Add Unit to Decibel"""

        return "{} db".format(data)

    def convert_degree(self, data):
        """Add Unit to Degree"""

        return "{} °".format(data)

    def convert_degree_celsius(self, data):
        """Add Unit to Degree Celcius"""

        return "{} °C".format(data)

    def convert_degree_per_second(self, data):
        """Add Unit to Degree per second"""

        return "{} °/s".format(data)

    def convert_degree_persecondsquared(self, data):
        """Add Unit to Degree per second squared"""

        return "{} °/s²".format(data)

    def convert_farad(self, data):
        """Add Unit to Farad"""

        return "{} F".format(data)

    def convert_gram(self, data):
        """Add Unit to Gram"""

        return "{} g".format(data)

    def convert_henry(self, data):
        """Add Unit to Henry"""

        return "{} H".format(data)

    def convert_hertz(self, data):
        """Add Unit to Hertz"""

        return "{} Hz".format(data)

    def convert_hour(self, data):
        """Add Unit to Hour"""

        return "{} h".format(data)

    def convert_joule(self, data):
        """Add Unit to Joule"""

        return "{} J".format(data)

    def convert_kelvin(self, data):
        """Add Unit to Kelvin"""

        return "{} K".format(data)

    def convert_lat(self, data):
        """Add Unit to Latitude"""

        return "{} °".format(data)

    def convert_litre(self, data):
        """Add Unit to Liter"""

        return "{} l".format(data)

    def convert_lon(self, data):
        """Add Unit to Longitude"""

        return "{} °".format(data)

    def convert_metre(self, data):
        """Add Unit to Meter"""

        return "{} m".format(data)

    def convert_metre_per_second(self, data):
        """Add Unit to Meter per second"""

        return "{} m/s".format(data)

    def convert_metre_per_second_square(self, data):
        """Add Unit to Meter per second square"""

        return "{} m/s²".format(data)

    def convert_metric_ton(self, data):
        """Add Unit to Metric Ton"""

        return "{} t".format(data)

    def convert_minute_angle(self, data):
        """Add Unit to Minute Angle"""

        return "{} '".format(data)

    def convert_minute(self, data):
        """Add Unit to Minute"""

        return "{} min".format(data)

    def convert_mol(self, data):
        """Add Unit to Mole"""

        return "{} mole".format(data)

    def convert_newton(self, data):
        """Add Unit to Newton"""

        return "{} N".format(data)

    def convert_newton_metre(self, data):
        """Add Unit to Newton Meter"""

        return "{} Nm".format(data)

    def convert_ohm(self, data):
        """Add Unit to Ohm"""

        return "{} Ω".format(data)

    def convert_radian(self, data):
        """Add Unit to Radian"""

        return "{} rad".format(data)

    def convert_radian_per_second(self, data):
        """Add Unit to Radian per second"""

        return "{} rad/s".format(data)

    def convert_radian_persecondsquared(self, data):
        """Add Unit to Radian per second squared"""

        return "{} rad/s²".format(data)

    def convert_second(self, data):
        """Add Unit to Second"""

        return "{} s".format(data)

    def convert_siemens(self, data):
        """Add Unit to Siemens"""

        return "{} S".format(data)

    def convert_square_metre(self, data):
        """Add Unit to Square meter"""

        return "{} m²".format(data)

    def convert_tesla(self, data):
        """Add Unit to Tesla"""

        return "{} T".format(data)

    # def convert_uptime(self, data):
    #     return "{} s".format(data)

    def convert_volt(self, data):
        """Add Unit to Volt"""

        return "{} V".format(data)

    def convert_watt(self, data):
        """Add Unit to Watt"""

        return "{} W".format(data)

    def convert_weber(self, data):
        """Add Unit to Weber"""

        return "{} Wb".format(data)

    def convert_va(self, data):
        """Add Unit to Volt-Ampere"""

        return "{} VA".format(data)

    def convert_no_spaces(self, data):
        """Remove Spaces"""

        return data.replace(" ", "")

    def convert_khz_ghz(self, data):
        """Add Kilohertz to Gigahertz"""

        data = data / 1000000

        return "{} GHz".format(data)

    def convert_mhz_ghz(self, data):
        """Add Kilohertz to Gigahertz"""

        data = data / 1000

        return "{} GHz".format(data)

    def check_unit(self, unit_value, exempt=False):
        """Check Unit per option"""

        json_data = []

        for data in unit_value:

            convert_value = data['value']
            option = data['option'].upper()
            data['original_value'] = data['value']

            if option in ['APPLICATION_UPTIME', 'SYSTEMUPTIME', 'SYSUPTIME',
                          'TOTALUPTIME', 'UPTIME', 'TOTALPREVLOOPTIME',
                          'MAINLOOPTIME', 'TIMEDELTA', 'TIMEHMS']:
                data['value'] = self.convert_uptime(float(convert_value), exempt)

            elif option in ['MEGAHERTZ', 'FREQUENCY_MHZ']:
                data['value'] = self.convert_megahertz_to_hertz(float(convert_value))

            # elif option in ['PDUPOWER']:
            #     data['value'] = self.convert_kilowatts(float(convert_value))

            elif option in ['KNOTS']:
                data['value'] = self.convert_msto_knots(convert_value)

            elif option in ['INFEEDCAPACITY', 'INFEEDLOADHIGHTHRESH',
                            'INFEEDLOADVALUE']:
                data['value'] = self.convert_ampere(convert_value)

            elif option in ['ABSOLUTEAZ', 'AZ_LIMIT_1', 'AZ_LIMIT_2', 'AZ_LIMIT_3',
                            'AZ_LIMIT_4', 'AZ_LIMIT_5', 'AZ_LIMIT_6', 'AZEND', 'AZIMUTH',
                            'AZIMUTH_STEP_SIZE', 'AZIMUTH_TRIM', 'AZSTART', 'BOWOFFSET',
                            'BZ1AZEND', 'BZ1AZSTART', 'BZ1ELEND', 'BZ1ELSTART', 'BZ2AZEND',
                            'BZ2AZSTART', 'BZ2ELEND', 'BZ2ELSTART', 'BZ3AZEND', 'BZ3AZSTART',
                            'BZ3ELEND', 'BZ3ELSTART', 'BZ4AZEND', 'BZ4AZSTART', 'BZ4ELEND',
                            'BZ4ELSTART', 'BZ5AZEND', 'BZ5AZSTART', 'BZ5ELEND', 'BZ5ELSTART',
                            'BZ6AZEND', 'BZ6AZSTART', 'BZ6ELEND', 'BZ6ELSTART', 'BZ7AZEND',
                            'BZ7AZSTART', 'BZ7ELEND', 'BZ7ELSTART', 'BZ8AZEND', 'BZ8AZSTART',
                            'BZ8ELEND', 'BZ8ELSTART', 'ELEND', 'ELEVATION', 'ELEVATION_TRIM',
                            'ELEVATON_STEP_SIZE', 'ELSTART', 'HEADING', 'LOCAL_HDG', 'POL',
                            'RELATIVEAZ', 'RELATIVEPOL', 'SAT_LONGITUDE', 'SATELLITERXPOL',
                            'SATELLITESKEW', 'SATELLITETXPOL', 'SKEWOFFSET', 'TARGETAZIMUTH',
                            'TARGETELEVATION', 'TARGETPOL', 'EL_LIMIT_12', 'EL_LIMIT_34',
                            'EL_LIMIT_56']:
                data['value'] = self.convert_degree(convert_value)

            elif option in ['ACM_TEMP', 'BUCTEMPERATURE', 'HPA_TEMP', 'MAINBOARD_TEMP']:
                data['value'] = self.convert_degree_celsius(convert_value)

            elif option in ['HUNT_FREQUENCY', 'HUNTFREQUENCY', 'PDULINEFREQUENCY', 'RX_IFFREQ',
                            'RXIFFREQ', 'TRANSMITFREQUENCY', 'TXIFFREQ', 'BANDWIDTH']:
                data['value'] = self.convert_hertz(convert_value)

            elif option in ['LATITUDE', 'LONGITUDE']:
                data['value'] = self.to_degrees(option, convert_value)

            elif option in ['SEALEVELHEIGHT']:
                data['value'] = self.convert_metre(convert_value)

            elif option in ['MAINUPDATETIME',
                            'MGMT_DHCPLEASETIME', 'MINIMUMACUREBOOTTIME', 'MINIMUMMODEMREBOOTTIME',
                            'MINIMUMWAITBEFOREFIRSTREPAIR', 'TIME']:
                data['value'] = self.convert_second(convert_value)

            elif option in ['INFEEDVOLTAGE', 'PDUINLETVOLTAGE']:
                data['value'] = self.convert_volt(convert_value)

            elif option in ['DEVICEPOWERWATTS', 'INFEEDPOWER', 'PDUPOWER',
                            'PETHMAINPSECONSUMPTIONPOWER', 'PETHMAINPSEPOWER', 'SYSTEMTOTALPOWER']:
                data['value'] = self.convert_watt(convert_value)

            elif option in ['DEVICEPOWERVA', 'PDUVA']:
                data['value'] = self.convert_va(convert_value)

            elif option in ['PDUSERIALNUMBER', 'RULE', 'RX_LOCK', 'USER']:
                data['value'] = self.convert_no_spaces(convert_value)

            elif option in ['RX_POWER']:
                data['value'] = self.convert_decibel_milliwats(convert_value)

            elif option in ['RX_SNR']:
                data['value'] = self.convert_decibel(convert_value)

            elif option in ['TRACKINGFREQ']:

                data['value'] = self.convert_khz_ghz(int(convert_value.split(" ")[0]))

            elif option in ['LNBFREQ']:

                data['value'] = self.convert_mhz_ghz(int(convert_value.split("MHz")[0]))

            else:
                data['value'] = data['value']

            json_data.append(data)

        return json_data

# if (__name__ == "__main__"):
#     convert = UnitConversion()
#     print(convert.to_degrees('latitude', 51.12))
#     print(convert.to_degrees('longitude', 4.31))
#     print(convert.to_degrees('', 4.31))
