import os
import paramiko
import posixpath
from paramiko.ssh_exception import AuthenticationException, SSHException
from dotenv import load_dotenv
from contextlib import contextmanager
import logging
from pathlib import Path

load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(filename='myapp.log', level=logging.INFO)

HOST = os.getenv("HOST")
PORT = int(os.getenv("PORT"))
USER = os.getenv("USER")
PASSWORD = os.getenv("PASSWORD")

virtual = "second_map"
local = "second_map_example"


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


def copy_directory(sftp_connection, local_path: str, virtual_path):
    """recursive coping for directories"""
    try:
        sftp_connection.mkdir(virtual_path)
    except Exception as e:
        logger.error("problem with making new virtual directory")

    for element in os.listdir(local_path):
        if os.path.isdir(local_path / element):
            copy_directory(sftp_connection, local_path / element, posixpath.join(virtual_path, element))
        else:
            try:
                sftp_connection.put(str(local_path / element), posixpath.join(virtual_path, element))
            except Exception as e:
                logger.error(f"problem with putting files {element}")


def copy_files(sftp_connection, local_path: str, virtual_path: str):
    """copying files to server"""
    local_path = Path(local_path).resolve()
    virtual_path = posixpath.join(".", virtual_path)

    for name in os.listdir(local_path):
        if os.path.isdir(local_path / name):
            try:
                copy_directory(sftp_connection, local_path / name, posixpath.join(virtual_path, name))
            except Exception as e:
                logger.error(f"problem with coping directory {name}")
        else:
            try:
                sftp_connection.put(str(local_path / name), posixpath.join(virtual_path, name))
            except Exception as e:
                logger.error(f"problem with putting files {name}")


def delete_files(sftp_connection, virtual_map: str):
    """deleting files from server"""
    for name in sftp_connection.listdir(virtual_map):
        try:
            sftp_connection.remove(posixpath.join(virtual_map, name))
        except Exception as e:
            logger.error(f"problem with deleting file {name}")


with sftp_connect(HOST, PORT, USER, PASSWORD) as sftp:
    copy_files(sftp, local, virtual)
    copy_files(sftp, local, virtual)
