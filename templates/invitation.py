# -*- coding: utf-8 -*-
# pylint: disable=line-too-long, no-self-use, too-few-public-methods
"""Invitation Template"""
from datetime import date
COPYRIGHT_YEAR = str(date.today().year)

class Invitation():
    """Class for Invitation"""

    # # INITIALIZE
    # def __init__(self):
    #     """The Constructor Invitation class"""
    #     pass

    def invitation_temp(self, password, url):
        """Invite Temporary"""
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
                            <h1 style="font-family:arial,sans-serif;color:#222222;font-weight:bold;font-size:24px;margin:0;padding:0 0 20px 0;text-align:left">Invitation</h1>
                            <p style="font-family:arial,sans-serif;color:#474747;font-weight:normal;font-size:14px;margin:0;padding:0 0 0 0;text-align:left;line-height:1.5">By clicking on the URL, you will redirect to create account page.<br><a style="word-break:break-word" href="http://""" + str(url) + """/" target="_blank" data-saferedirecturl="https://""" + str(url) + """/">https://""" + str(url) + """/</a></p>
                            <p style="font-family:arial,sans-serif;color:#474747;font-weight:normal;font-size:14px;margin:0;padding:0 0 0 0;text-align:left;line-height:1.5"><br>Use the following code for your temporary password:</p>
                            <p style="background:#e1e1e1;padding:10px;border-radius:2px;font-weight:bold;color:#222222;font-size:18px">""" + password + """</p>
                            <p style="font-family:arial,sans-serif;color:#474747;font-weight:normal;font-size:14px;margin:0;padding:0 0 0 0;text-align:left;line-height:1.5">Your VPN credentials will be sent in a separate email, and this can take up to 30 minutes. Once you can log in, please go to your profile by clicking the email name on the top left sidebar menu and change your password and username for your security purposes.</p>
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
