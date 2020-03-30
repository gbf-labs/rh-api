# pylint: disable=no-self-use, bare-except
"""MD5 Security"""
import base64
# import argparse
# import sys
# import textwrap
from Crypto.Cipher import AES

class MD5Security:
    """Class for MD5Security"""
    #------------------------------------------------------
    # AUTHOR : KRISFEN G. DUCAO
    # FUNCTION: encypt_cipher
    # DESCRIPTION : This will create cipher
    # DATE CREATED: 04/18/2018
    #------------------------------------------------------

    # # INITIALIZE
    # def __init__(self):
    #     """The Constructor for MD5Security class"""
    #     pass

    def encypt_cipher(self, secret_key):
        """Encrypt Cipher"""
        # CREATE CIPHER
        cipher = AES.new(secret_key, AES.MODE_ECB)

        return cipher

    #------------------------------------------------------
    # AUTHOR : KRISFEN G. DUCAO
    # FUNCTION: decrypt_cipher
    # DESCRIPTION : This will create cipher
    # DATE CREATED: 04/18/2018
    #------------------------------------------------------

    def decrypt_cipher(self, secret_key):
        """"Decrypt Cipher"""
        # CREATE CIPHER
        cipher = AES.new(secret_key)

        return cipher

    #------------------------------------------------------
    # AUTHOR : KRISFEN G. DUCAO
    # FUNCTION: encryption
    # DESCRIPTION : This will encrypt your string
    # DATE CREATED: 04/18/2018
    # NOTE : AES key must be either 16, 24, or 32 bytes long
    #        SET AT LEAST 16 CHARACTER FOR secret_key VALUE
    #------------------------------------------------------

    def encryption(self, private_info, secret_key='1080pFullHD20188', padding='{', block_size=16):
        """Encryption"""
        # INIT
        pad = lambda s: s + (block_size - len(s) % block_size) * padding
        encode_aes = lambda c, s: base64.b64encode(c.encrypt(pad(s)))

        # GET THE CIPHER
        cipher = self.encypt_cipher(secret_key)

        # ENCRYPT
        encoded = encode_aes(cipher, private_info)

        return encoded

    #------------------------------------------------------
    # AUTHOR : KRISFEN G. DUCAO
    # FUNCTION: decryption
    # DESCRIPTION : This will decrypt your string
    # DATE CREATED: 04/18/2018
    # NOTE : AES key must be either 16, 24, or 32 bytes long
    #        SET AT LEAST 16 CHARACTER FOR secret_key VALUE
    #------------------------------------------------------

    def decryption(self, private_info, secret_key='1080pFullHD20188', padding='{'):
        """Decryption"""
        try:
            # INIT
            decode_aes = lambda c, e: c.decrypt(base64.b64decode(e)).rstrip(padding)

            # GET THE CIPHER
            cipher = self.decrypt_cipher(secret_key)

            # DECRYPT
            decoded = decode_aes(cipher, private_info)

        except:

            # RETURN UNDECODE
            decoded = private_info

        return decoded

    #------------------------------------------------------
    # AUTHOR : KRISFEN G. DUCAO
    # FUNCTION: key_encryptor
    # DESCRIPTION : This will encrypt keys in json
    # DATE CREATED: 04/18/2018
    #------------------------------------------------------

    def key_encryptor(self, json_data, keys):
        """Key Encryptor"""
        # INIT
        final_data = {}

        # LOOP JSON DATA
        for key, value in json_data.iteritems():

            # FIND KEYS
            if key in keys:

                # ENCRYPT VALUE
                value = self.encryption(value)

            # SET VALUE
            final_data[key] = value

        return final_data

    #------------------------------------------------------
    # AUTHOR : KRISFEN G. DUCAO
    # FUNCTION: key_decryptor
    # DESCRIPTION : This will encrypt keys in json
    # DATE CREATED: 04/18/2018
    #------------------------------------------------------

    def key_decryptor(self, json_data, keys):
        """Key Decryptor"""
        # INIT
        final_data = []

        # LOOP JSON DATA
        for json_dict in json_data:

            new_json_data = {}
            for key, value in json_dict.iteritems():

                # FIND KEYS
                if key in keys:
                    # DECRYPT VALUE
                    value = self.decryption(value)

                # SET VALUE
                new_json_data[key] = value
            final_data.append(new_json_data)

        return final_data



# parser = argparse.ArgumentParser(prog='PROG', add_help=False,
#                                  formatter_class=argparse.RawDescriptionHelpFormatter,
#                                  description=textwrap.dedent('''\
#                                  Please do not mess up this text!
#                                  --------------------------------
#                                     I have indented it
#                                     exactly the way
#                                     I want it
#                                  '''))

# decryption = parser.add_argument_group('Decryption', 'Decrypt the hash')

# decryption.add_argument("-t",
#                         "--type",
#                         help="Type of command (encryption, decryption)",
#                         default="private_info")

# encryption = parser.add_argument_group('Encryption', 'Encrypt the private info')

# encryption.add_argument("-t",
#                         "--type",
#                         help="Type of command (encryption, decryption)",
#                         default="private_info")
# encryption.add_argument("-p",
#                         "--private_info",
#                         help="Private info to be encrypt",
#                         default="private_info")
# encryption.add_argument("-s",
#                         "--salt",
#                         help="Salt for encryption must be either 16, 24, or 32 character long",
#                         default="1080pFullHD20188")

# args = parser.parse_args()

if __name__ == '__main__':
    # if len(args.salt) not in [16, 24, 32]:
    #     parser.print_help()
    #     sys.exit(0)

    MD5Security()
