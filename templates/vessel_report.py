# -*- coding: utf-8 -*-
# pylint: disable=line-too-long, no-self-use, bare-except
"""Vessel Report Template"""
import math
from datetime import date
COPYRIGHT_YEAR = str(date.today().year)

class VesselReport():
    """Class for VesselReport"""

    # # INITIALIZE
    # def __init__(self):
    #     """The Constructor VesselReport class"""
    #     pass

    def vessel_report_temp(self, infos, last_date):
        """Vessel Report Temporary"""
        email_temp = """
            <div style="background:#fcfcfc;font-family:arial,sans-serif;color:#474747;padding:2%">
                <table style="width:100%;max-width:600px;border:1px solid #dbdbdb;border-radius:5px;background:#fff;padding:0px;margin:0 auto 0px auto" border="0" cellspacing="0" cellpadding="0">
                    <tbody>
                        <tr>
                            <td style="padding:5px 30px 5px 30px;background:rgba(248,94,0);color:#fff;font-size:16px;text-align:left;font-weight:bold;border-radius:3px 3px 0 0;text-decoration:none">&nbsp;</td>
                        </tr>
                        <tr>
                            <td style="padding:30px;border-bottom:1px solid #dbdbdb"><a style="text-decoration:none" title="RadioHolland" href="https://www.radioholland.com/" target="_blank" data-saferedirecturl="https://www.radioholland.com/"><img style="width:auto;max-width:100%;margin:0 auto;font-weight:bold;color:#222;font-size:38px;text-decoration:none" src="https://s3.eu-central-1.amazonaws.com/rh.fileserver/Logo/radioholland-logo.png" alt="RadioHolland" class="CToWUd"></a></td>
                        </tr>
                        <tr>
                        <td style="padding:30px 30px 30px 30px">
                            <h1 style="font-family:arial,sans-serif;color:#222222;font-weight:bold;font-size:24px;margin:0;padding:0 0 20px 0;text-align:left">Vessel Report</h1>
                            <p style="background:#e1e1e1;padding:10px;border-radius:2px;color:#222222;font-size:12px">
                            """
        email_temp += "<b>As of " + last_date + "</b><br>\n<br>\n"

        for info in infos:

            if info['label'] == "":

                email_temp += "<br>\n"

            else:

                try:

                    if info['label'] == "LATITUDE":
                        latitude = self.to_degrees(info['value'])

                        lat_cardinal = "S"
                        if float(info['value']) >= 0:
                            lat_cardinal = "N"

                        info['value'] = str(latitude) + " " + str(lat_cardinal)

                    elif info['label'] == "LONGITUDE":

                        longitude = self.to_degrees(info['value'])

                        long_cardinal = "W"
                        if float(info['value']) >= 0:
                            long_cardinal = "E"

                        info['value'] = str(longitude) + " " + str(long_cardinal)

                    elif info['label'] == "HEADING":

                        info['value'] = str(int(float(info['value']))) + "°"

                except:

                    info['value'] = ""


                email_temp += info['label'] + ": " + info['value'] + "<br>\n"

        email_temp += """</p>
                        </td>
                        </tr>
                    </tbody>
                </table>
                <table style="width:100%;max-width:600px;text-align:left;margin:20px auto 0 auto;font-family:arial,sans-serif;font-size:10px;color:#777777;line-height:1.3" border="0" cellspacing="0" cellpadding="0">
                    <tbody>
                        <tr>
                            <td style="width:100%;text-align:left;padding-bottom:10px">Copyright © <span class="il">RadioHolland</span> """+  COPYRIGHT_YEAR +"""</td>
                        </tr>
                    </tbody>
                </table>
                <div class="yj6qo">
                </div>
                <div class="adL">
                </div>
            </div>
        """
        return email_temp

    def to_degrees(self, coordinate):
        """To Degrees"""
        absolute = abs(float(coordinate))
        degrees = math.floor(absolute)
        minutes_not_truncated = (absolute - degrees) * 60
        minutes = math.floor(minutes_not_truncated)
        seconds = math.floor((minutes_not_truncated - minutes) * 60)

        return str(degrees) + "° " + str(minutes) + "' " + str(seconds) + "''"
