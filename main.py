import os
import paramiko
from paramiko.ssh_exception import AuthenticationException, SSHException
from dotenv import load_dotenv
from contextlib import contextmanager
import logging

load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(filename='myapp.log', level=logging.INFO)

HOST = os.getenv("HOST")
PORT = int(os.getenv("PORT"))
USER = os.getenv("USER")
PASSWORD = os.getenv("PASSWORD")

virtual = "./second_map"
local = "second_map_example/"


@contextmanager
def sftp_connect(host: str, port: int, user: str, password: str):
    """connection to sftp server"""
    client = None
    sftp = None
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(
            hostname=host,
            port=port,
            username=user,
            password=password,
            timeout=15,
            look_for_keys=False,
        )
        sftp = client.open_sftp()
        yield sftp
    except AuthenticationException:
        logger.error('SFTP auth failed')
        raise
    except SSHException:
        logger.error('SSH error')
        raise
    except Exception as e:
        logger.error('Unexpected SFTP error')
        raise
    finally:
        if sftp is not None:
            try:
                sftp.close()
            except Exception as e:
                logger.error('sftp.close() error')

        if client is not None:
            try:
                client.close()
            except Exception as e:
                logger.error('client.close() error')


def copy_directory(sftp_connection, directory_name: str):
    """recursive deleting for directories"""
    try:
        os.chdir(directory_name)
    except IOError:
        logger.error("problem with deleting files, smth with local path")

    try:
        sftp_connection.mkdir(directory_name)
    except Exception as e:
        logger.error("problem with making new virtual directory")

    try:
        sftp_connection.chdir(directory_name)
    except IOError:
        logger.error("problem with deleting files, smth with virtual path")

    for element in os.listdir():
        if os.path.isdir(element):
            copy_directory(sftp_connection, element)
        else:
            try:
                sftp_connection.put(element, element)
            except Exception as e:
                logger.error(f"problem with putting files {element}")

    os.chdir("..")
    sftp_connection.chdir("..")


def copy_files(sftp_connection, local_map_path: str, virtual_map_path: str):
    """copying files to server"""
    try:
        sftp_connection.chdir(virtual_map_path)
    except IOError:
        logger.error("problem with copying files, smth with virtual path")

    try:
        os.chdir(local_map_path)
    except IOError:
        logger.error("problem with copying files, smth with local path")

    for name in os.listdir():
        if os.path.isdir(name):
            try:
                copy_directory(sftp_connection, name)
            except Exception as e:
                logger.error(f"problem with coping directory {name}")
        else:
            try:
                sftp_connection.put(name, name)
            except Exception as e:
                logger.error(f"problem with putting files {name}")

    sftp_connection.chdir("..")


def delete_files(sftp_connection, virtual_map_path: str):
    """deleting files from server"""
    try:
        sftp_connection.chdir(virtual_map_path)
    except IOError:
        logger.error("problem with deleting files, smth with path")

    for name in sftp_connection.listdir():
        try:
            sftp_connection.remove(name)
        except Exception as e:
            logger.error(f"problem with deleting file {name}")

    sftp_connection.chdir("..")

with sftp_connect(HOST, PORT, USER, PASSWORD) as sftp:
    delete_files(sftp, virtual)
    copy_files(sftp, local, virtual)
