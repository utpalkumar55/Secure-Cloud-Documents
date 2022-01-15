from __future__ import print_function
import pickle
import os.path
import io
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from apiclient.http import MediaFileUpload
from apiclient.http import MediaIoBaseDownload

import hashlib
import hmac
import sys
import mimetypes

import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

from pbkdf2 import PBKDF2


# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive']

def main():
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('drive', 'v3', credentials=creds)

	###PBKDF2
    user_password = raw_input("Enter user password: ")
    salt = os.urandom(8)
    key = PBKDF2(user_password, salt).read(64)
    encryption_key = key[:32]
    hmac_key = key[-32:]
    #print ('\n\nDerived key through password-based derivation function 2: %s\n\n' % key.encode("hex"))
    print('Encryption key: %s' % encryption_key.encode('hex'))
    print('HMAC SHA256 key: %s\n\n' % hmac_key.encode('hex'))
	
	
    while 1:
        user_command = raw_input("Select one of the following commands: \nEncrypt\nDecrypt\nEnter anything else to stop.\n\n")
        if user_command == "Encrypt":
            
			###Reading in file name
            print ('This program only works for text (.txt extension) file')
            input_file_name = raw_input("Enter the file name: ")
    
	
	        ###AES256 encryption
            print ('\n\nEncrypted content will be stored in encrypted.txt file.\nEncryption starting...')
            encrypted_file_name = 'encrypted.txt';
            file_object = open(encrypted_file_name, 'wb')
            backend = default_backend()
            iv = os.urandom(16)
            aes256_encryptor = Cipher(algorithms.AES(encryption_key), modes.CTR(iv), backend=backend).encryptor()
            block_size=65536
            with open(input_file_name, 'rb') as f:
                for block in iter(lambda: f.read(block_size), b''):
                    encrypted_text = aes256_encryptor.update(block) + aes256_encryptor.finalize()
                    file_object.write(encrypted_text);
                file_object.close();
            print ('Encryption is done. Now you can have a look on encrypted.txt file.\n\n')
	
	
	        ###SHA256 calculation
            print ('\n\nMAC of encrypted.txt file will be calculated using SHA256 method and appended at the end of the file. SHA256 calculation is starting...')
            block_size=65536
            hmac_sha256 = hmac.new(hmac_key, '', hashlib.sha256)
            with open(encrypted_file_name, 'rb') as f:
                for block in iter(lambda: f.read(block_size), b''):
                    hmac_sha256.update(block)
                checksum = hmac_sha256.hexdigest()
			
			
            ###Writing checksum into the file
            file_object = open(encrypted_file_name, "a")
            file_object.write(checksum);
            file_object.close();
            print ('SHA256 checksum calculation is done. Checksum of the encrypted file: %s' % checksum)
            print ('Now you can have a look on encrypted.txt file again.\n\n')
	
	
	        ###File upload
            print ('\n\nFile is uploading to google drive...')
            file_metadata = {'name': encrypted_file_name}
            input_file_mime_type = mimetypes.MimeTypes().guess_type(encrypted_file_name)[0]
            media = MediaFileUpload(encrypted_file_name, mimetype=input_file_mime_type) 
            file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            file_id = file.get('id')
            print ('File upload is done.\n\n')
	
	
        elif user_command == "Decrypt":
            encrypted_file_name = raw_input("Enter the file name which you want to download and decrypt: ")
            q_parameter = "name=" + "'" + encrypted_file_name + "'"
			
			
            ###File search
            page_token = None
            while True:
                response = service.files().list(q=q_parameter, spaces='drive', fields='nextPageToken, files(id, name)', pageToken=page_token).execute()
                for file in response.get('files', []):
                    file_name = file.get('name')
                    file_id = file.get('id')
                    print ('Found file: %s (%s)' % (file.get('name'), file.get('id')))
                    break;
                break;
      
	  
            ###File download
            print ('\n\nDownloaded file will be named as downloaded.txt.\nFile is downloading...')
            downloaded_file_name = 'downloaded.txt'
            request = service.files().get_media(fileId=file_id)
            fh = io.FileIO(downloaded_file_name, 'wb')
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                print ("Download %d%%." % int(status.progress() * 100))
            print ('File download is done.\n\n')
	
	
	        ###Retrieving checksum from the file
            print ('\n\nChecksum will be erased from downloaded.txt and stored in checksum_excluded.txt file.')
            file_object = open(downloaded_file_name, 'rb')
            for line in file_object:
                file_checksum = line
            file_checksum = file_checksum[-64:]
	
	
	        ###Erasing checksum from the file
            print ('Checksum is being erased from downloaded.txt file...')
            checksum_excluded_filename = 'checksum_excluded.txt'
            with open(downloaded_file_name, 'rb') as file_object:
                lines = file_object.readlines()
            lines[-1] = lines[-1][0:-64]
            with open(checksum_excluded_filename, 'wb') as file_object:
                for line in lines:
                    file_object.write(line)
            print ('Now you can have a look on checksum_excluded.txt file.\n\n')
	
	
            ###SHA256 recalculation
            print ('\n\nMAC of checksum_excluded.txt file will be recalculated using SHA256 method and compared with the existing checksum of the file.\nSHA256 recalculation is starting...')
            block_size=65536
            hmac_sha256 = hmac.new(hmac_key, '', hashlib.sha256)
            with open(checksum_excluded_filename, 'rb') as f:
                for block in iter(lambda: f.read(block_size), b''):
                    hmac_sha256.update(block)
                recalculated_checksum = hmac_sha256.hexdigest()
            print ('SHA256 checksum recalculation is done. Now comparing both the checksums...')
            
			
			###Comparison of both the checksums
            if file_checksum == recalculated_checksum:
                print ('Both the checksums are same. That means MAC verification is perfect.\n\n')
            else:
                print ('ERROR!!! Invalid Ciphertext!')
                print ('Program is terminating...\n\n')
                break
			
			
	        ###AES256 decryption
            print ('\n\nchecksum_excluded.txt file will be decrypted and stored in decrypted.txt file. Decryption is starting...')
            decrypted_file_name = 'decrypted.txt';
            file_object = open(decrypted_file_name, 'wb')
            aes256_decryptor = Cipher(algorithms.AES(encryption_key), modes.CTR(iv), backend=backend).decryptor()
            block_size=65536
            with open(checksum_excluded_filename, 'rb') as f:
                for block in iter(lambda: f.read(block_size), b''):
                    decrypted_text = aes256_decryptor.update(block) + aes256_decryptor.finalize()
                    file_object.write(decrypted_text);
                file_object.close();
            print ('Decryption is done. Now you can have a look on decrypted.txt file.\n\n')

			
        else:
            print ('\n\nProgram is terminating...\n\n')
            break
	
	
	
			
	
	
	
	
	
    # Call the Drive v3 API
    """results = service.files().list(
        pageSize=10, fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])

    if not items:
        print('No files found.')
    else:
        print('Files:')
        for item in items:
            print(u'{0} ({1})'.format(item['name'], item['id']))"""

if __name__ == '__main__':
    main()