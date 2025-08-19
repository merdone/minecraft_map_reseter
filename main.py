import os
import paramiko
from dotenv import load_dotenv

load_dotenv()

HOST = os.getenv("HOST")
PORT = int(os.getenv("PORT"))
USER = os.getenv("USER")
PASSWORD = os.getenv("PASSWORD")

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

client.connect(
    hostname=HOST,
    port=PORT,
    username=USER,
    password=PASSWORD,
    timeout=15,
    look_for_keys=False,
)

sftp = client.open_sftp()


virtual = "./second_map"
local = "second_map_example/"


def copy_directory(sftp_connection, directory_name):
    os.chdir(directory_name)

    sftp_connection.mkdir(directory_name)
    sftp_connection.chdir(directory_name)

    for element in os.listdir():
        if os.path.isdir(element):
            copy_directory(sftp_connection, element)
        else:
            sftp_connection.put(element, element)

    os.chdir("..")
    sftp_connection.chdir("..")


def copy_files(sftp_connection, local_map_path, virtual_map_path):
    sftp_connection.chdir(virtual_map_path)
    os.chdir(local_map_path)

    for name in os.listdir():
        if os.path.isdir(name):
            copy_directory(sftp_connection, name)
        else:
            sftp_connection.put(name, name)
    sftp_connection.chdir("..")


def delete_files(sftp_connection, virtual_map_path):
    sftp_connection.chdir(virtual_map_path)

    for name in sftp.listdir():
        sftp.remove(name)

    sftp_connection.chdir("..")


sftp.close()
client.close()
