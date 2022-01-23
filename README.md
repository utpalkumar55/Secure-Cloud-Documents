# Secure Cloud Documents
This project demonstrates a way to secure personal files in the cloud server using user-end encryption and authentication methods. The project flow is given below.
1. At first, the project will ask for a user password.
2. After the password is provided, the project will create encryption key and HMAC key by using PBKDF2 (Password-Based Key Derivation Function 2).
3. Then, the project will ask to select one of the two commands which are "Encrypt" and "Decrypt".
4. When "Encrypt" command is selected...
     * The project will ask for the file name which will be encrypted, hashed, and uploaded to google drive. This project only works for text file for now.
     * When the file name is given, the file will be encrypted using AES256 encryption algorithm with counter (CTR) mode. The encrypted content will be saved in 'encrypted.txt'          file.
     * Then the hash value (checksum) of the content of 'encrypted.txt' file will be calculated using SHA256 hashing algorithm and the hash value will be added at the end of the          file.
     * Then the file will be uploaded to google drive.
5. When "Decrypt" command is selected...
     * The project will ask for the file name which will be downloaded and decrypted.
     * After providing the file name, the file will be downloaded and saved as downloaded.txt.
     * Then the hash value (checksum) of the file will be extracted and the other content of the file will be stored in checksum_excluded.txt file.
     * After that, the hash value (checksum) will be calculated again from the content of checksum_excluded.txt file using SHA256 hashing algorithm.
     * Next, the newly calculated checksum value will be compared with the checksum value that was extracted from the downloaded.txt file.
     * If the checksums donot match then it can be concluded that there was unauthorized modification, an error message will pop up, and the project will be terminated.
     * If the checksums match then, it can be concluded that there was no unauthorized modification on the file and the file will go to the decryption phase.
     * In the decryption phase, the file will be decrypted using AES256 decryption algorithm with the same key and the decrypted content will be saved in decrypted.txt file.

N.B.: Please have a look on the readme.txt file for dependencies, necessary resources, and the instructions to compile and run this project.
