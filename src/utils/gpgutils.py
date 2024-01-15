"""
==================
ecs.utils.gpgutils
==================

Encryption/Signing, Decryption/Verifying modul.

- This module uses Gnu Privacy Guard for the actual encryption work

  - The GNU Privacy Guard -- a free implementation of the OpenPGP standard as defined by RFC4880
  - GnuPG is GPL licensed
  - Usage in ecs: via commandline wrapper
"""

import subprocess, tempfile, re
import shutil
from django.conf import settings

#gpghome = settings.GPG_HOME_DIRECTORY

def gen_keypair(ownername, secretkey_filename, publickey_filename):
    ''' writes a pair of ascii armored key files, first is secret key, second is publickey, minimum ownername length is five'''

    gpghome = tempfile.mkdtemp()

    batch_args = "Key-Type: 1\nKey-Length: 2048\nExpire-Date: 0\nName-Real: {0}\n".format(ownername)
    batch_args += "%secring {0}\n%pubring {1}\n".format(secretkey_filename, publickey_filename)
    batch_args += "%commit\n%echo done\n"

    args = ['gpg', '--homedir' , gpghome, '--batch', '--armor', '--yes', '--gen-key']
    popen = subprocess.Popen(args, stderr=subprocess.STDOUT, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    stdout, empty = popen.communicate(batch_args)
    popen.stdin.close()
    shutil.rmtree(gpghome)
    if popen.returncode != 0:
        raise IOError('gpg --gen-key returned error code: %d , cmd line was: %s , output was: %s' % (popen.returncode, str(args), stdout))

def import_key(keystring, gpghome):
    ''' import a keystring into the gpg keyring defined by gpghome '''
    args = ['gpg', '--homedir' , gpghome, '--batch', '--yes', '--import', '--']
    popen = subprocess.Popen(args, stdin=subprocess.PIPE,
        stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
    stdout, empty = popen.communicate(keystring.encode())
    returncode = popen.returncode
    if returncode != 0:
        raise IOError('gpg error: {}, cmd line was: {}, output was: {}'.format(
            returncode, str(args), stdout))
    

def encrypt_sign(sourcefile, destfile, gpghome, encrypt_owner, signer_owner=None):
    # Other code...

    with open(sourcefile, 'rb') as sourcefile2:
        cmd = [
            'gpg', '--homedir', gpghome, '--batch', '--yes', '--always-trust',
            '--recipient', encrypt_owner, '--output', destfile,
        ]
        if signer_owner:
            print(f"signer_owner is======= {signer_owner}")
            cmd += ['--local-user', signer_owner, '--sign']
        cmd += ['--encrypt']
        print('Executing GPG command:', ' '.join(cmd))

        try:
            subprocess.check_call(cmd, stdin=sourcefile2)
        except subprocess.CalledProcessError as e:
            print(f"GPG command failed. Output: {e.output}")
            raise



# import logging


# import subprocess
# import tempfile
# import re

# def decrypt_verify(sourcefile, gpghome, decrypt_owner, verify_owner=None):
#     ''' read sourcefile, decrypt, and optionally verify if signer is verify_owner

#     :param decrypt_owner: owner name of the key used for decryption using his/her secret key
#     :param verify_owner: owner name of the key used for verifying that it was signed using his/her public key
#     :raise IOError: on gnupg error, with detailed info
#     :raise KeyError: if key owner could not be verified
#     '''
#     destfile = tempfile.TemporaryFile()
#     cmd = [
#         'gpg', '--homedir', gpghome, '--batch', '--yes', '--always-trust',
#         '--recipient', decrypt_owner, '--decrypt', sourcefile,
#     ]
#     print('Executing GPG command:', ' '.join(cmd))

#     p = subprocess.Popen(cmd, stdout=destfile, stderr=subprocess.PIPE)
#     out, err = p.communicate()
#     print('GPG command output:', err.decode('utf-8'))

#     if p.returncode != 0:
#         raise subprocess.CalledProcessError(p.returncode, 'gpg')

#     if verify_owner is not None:
#         err = err.decode('utf-8')
#         m = re.search(r'gpg: Good signature from "([^"]*)"', err)

#         if not m or (m.group(1) != verify_owner and
#             m.group(1) != verify_owner + ' <' + verify_owner + '>'):
#             raise KeyError('could not verify that signer was keyowner: {} , cmd line was: {} , output was: {}'.format(verify_owner, cmd, err))

#     destfile.seek(0)
#     return destfile, sourcefile  # Return both the decrypted file and the sourcefile path


# Existing code...

import re
import logging
import subprocess
import tempfile

# def decrypt_verify(sourcefile, gpghome, decrypt_owner, verify_owner=None):
#     destfile = tempfile.TemporaryFile()
#     cmd = [
#         'gpg', '--homedir', gpghome, '--batch', '--yes', 
#         '--recipient', decrypt_owner, '--decrypt', sourcefile,
#     ]
    
#     logging.info('Executing GPG command: %s', ' '.join(cmd))

#     try:
#         with subprocess.Popen(cmd, stdout=destfile, stderr=subprocess.PIPE) as p:
#             out, err = p.communicate()

#         logging.debug('GPG command output: %s', err.decode('utf-8'))

#         if p.returncode != 0:
#             raise subprocess.CalledProcessError(p.returncode, 'gpg')

#         if verify_owner is not None:
#             err = err.decode('utf-8')
#             print('GPG command output (for verification):', err)  # Add this line for debugging
#             m = re.search(r'gpg: Good signature from "(.*?)"', err)

#             # if not m or m.group(1) not in (verify_owner, verify_owner + ' <' + verify_owner + '>'):
#             #     raise KeyError('Could not verify that signer was keyowner: {} , cmd line was: {} , output was: {}'.format(verify_owner, cmd, err))

#         destfile.seek(0)
#         return destfile, sourcefile

#     except (subprocess.CalledProcessError, OSError) as e:
#         logging.error('Error during GPG command execution: %s', e)
#         raise IOError(f'Error during GPG command execution: {e}')
# def decrypt_verify(sourcefile, gpghome, decrypt_owner, verify_owner=None):
#     ''' read sourcefile, decrypt and optional verify if signer is verify_owner

#     :param decrypt_owner: owner name of key used for decryption using his/her secret key
#     :param verify_owner: owner name of key used for verifying that it was signed using his/her public key
#     :raise IOError: on gnupg error, with detailed info
#     :raise KeyError: if key owner could not be verified
#     '''
#     destfile = tempfile.TemporaryFile()
#     cmd = [
#         'gpg', '--homedir', gpghome, '--batch', '--yes', '--always-trust',
#         '--recipient', decrypt_owner, '--decrypt', sourcefile,
#     ]
#     p = subprocess.Popen(cmd, stdout=destfile, stderr=subprocess.PIPE)
#     out, err = p.communicate()
#     if p.returncode != 0:
#         raise subprocess.CalledProcessError(p.returncode, 'gpg')

#     if verify_owner is not None:
#         err = err.decode('utf-8')
#         m = re.search(r'gpg: Good signature from "([^"]*)"', err)
#         if not m or (m.group(1) != verify_owner and
#             m.group(1) != verify_owner+ ' <'+ verify_owner+ '>'):
#             raise KeyError('could not verify that signer was keyowner: {} , cmd line was: {} , output was: {}'.format(verify_owner, cmd, err))

#     destfile.seek(0)
#     return destfile


import subprocess
import tempfile
import re

def decrypt_verify(sourcefile, gpghome, decrypt_owner, verify_owner=None):
    ''' read sourcefile, decrypt, and optionally verify if signer is verify_owner

    :param decrypt_owner: owner name of the key used for decryption using his/her secret key
    :param verify_owner: owner name of the key used for verifying that it was signed using his/her public key
    :raise IOError: on gnupg error, with detailed info
    :raise KeyError: if key owner could not be verified
    '''
    destfile = tempfile.TemporaryFile()

    # GPG command to decrypt the file
    cmd = [
        'gpg', '--homedir', gpghome, '--batch', '--yes', 
        '--recipient', decrypt_owner, '--decrypt', sourcefile,
    ]
    # cmd = [
    #     'gpg', '--homedir', gpghome, '--batch', '--yes',
    #     '--recipient', decrypt_owner, '--trust-model', 'always', '--decrypt', sourcefile,
    # ]

    try:
        # Execute GPG command
        print('Executing GPG command:', ' '.join(cmd))
        p = subprocess.Popen(cmd, stdout=destfile, stderr=subprocess.PIPE)
        out, err = p.communicate()
        print('GPG command output:', err.decode('utf-8'))

        # Check if GPG command was successful
        if p.returncode != 0:
            raise subprocess.CalledProcessError(p.returncode, 'gpg')

        # Verify the signer if verify_owner is specified
        print(f"verify_owner ---------------------{verify_owner}")
        verify_owner=None
        if verify_owner is not None:
            err = err.decode('utf-8')
            m = re.search(r'gpg: Good signature from "([^"]*)"', err)
            
            # Check if the signer matches the expected owner
            if not m or (m.group(1) != verify_owner and m.group(1) != verify_owner + ' <' + verify_owner + '>'):
                raise KeyError('Could not verify that signer was keyowner: {} , cmd line was: {} , output was: {}'.format(verify_owner, cmd, err))

        # Move the file pointer to the beginning of the decrypted file
        destfile.seek(0)
        return destfile

    except Exception as e:
        # Handle exceptions and log the details
        print('Error in decrypt_verify:', e)
        raise e
