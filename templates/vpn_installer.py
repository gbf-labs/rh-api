# -*- coding: utf-8 -*-
# pylint: disable=no-self-use, line-too-long, too-few-public-methods
"""Message Template"""
from datetime import date
COPYRIGHT_YEAR = str(date.today().year)

class VPNInstallTemp():
    """Class for Message"""

    def vpn_mgs_temp(self, msg, note, win_url, mac_url):
        """Message Temporary"""
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
                        <td style="padding:30px 30px 0px 30px">
                            <p style="font-family:arial,sans-serif;color:#474747;font-weight:normal;font-size:14px;margin:0;padding:0 0 0 0;text-align:left;line-height:1.5"><br>""" + msg + """</p>
                        </td>
                        </tr>
                        <tr>
                        <td style="padding:0px 30px 0px 30px">
                        	<p style="font-family:arial,sans-serif;color:#474747;font-weight:normal;font-size:14px;margin:0;padding:0 0 0 0;text-align:left;line-height:1.5"><br>Windows OS: Click <a href=\"""" + win_url + """\">here</a> to download.</p>
                        	<p style="font-family:arial,sans-serif;color:#474747;font-weight:normal;font-size:14px;margin:0;padding:0 0 0 0;text-align:left;line-height:1.5"><br>Mac OS: Click <a href=\"""" + mac_url + """\">here</a> to download.</p>
                        </td>
                        </tr>
                        <tr>
                        <td style="padding:0px 30px 30px 30px">
                            <p style="font-family:arial,sans-serif;color:#474747;font-weight:normal;font-size:14px;margin:0;padding:0 0 0 0;text-align:left;line-height:1.5"><br>""" + note + """</p>
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
