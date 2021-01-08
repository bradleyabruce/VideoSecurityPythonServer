import socket
import sys
import uuid
import time
from requests import get
from DL import DBConn
from Enums import ServerStatus
from Enums.eTransactionType import eTransactionType
from Objects.Exceptions import NetworkAddressNotAvailableException, MacAddressNotAvailableException
from Objects.Query import Query
from Objects.Server import Server


sql_select = "SELECT s.ServerID, s.Name, s.MacAddress, s.InternalAddress, s.ExternalAddress, s.PortNumber, s.ServerStatusID, s.DirectoryPath "
sql_from = " FROM tServers s "


def get_local_ip():
    try:
        os = sys.platform
        local_ip = "Unavailable"
        if os == "linux" or os == "win32":
            host_name = socket.gethostname()
            local_ip = socket.gethostbyname(host_name + ".local")

        else:
            # MacOS
            local_ip = socket.gethostbyname_ex(socket.gethostname())[-1][0]

        return local_ip
    except Exception:
        raise NetworkAddressNotAvailableException


def get_external_ip():
    try:
        external_ip = get('https://api.ipify.org').text
        return external_ip
    except Exception:
        raise NetworkAddressNotAvailableException


def get_current_mac_address():
    try:
        mac_address = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff)
                                for ele in range(0, 8 * 6, 8)][::-1])
        return mac_address
    except Exception:
        raise MacAddressNotAvailableException


def startup():
    try:
        print("Initializing Server...")

        mac_address = get_current_mac_address()
        server = get_server_from_mac_address(mac_address)

        # Update existing data and return
        if server is not None:
            update_startup_values_into_db(server)
        # Create new entry and return
        else:
            insert_default_values_into_db(mac_address)

        return get_server_from_mac_address(mac_address)

    except MacAddressNotAvailableException:
        print("Critical Error Occurred. Mac Address could not be identified.")
    except NetworkAddressNotAvailableException:
        print("Critical Error Occurred. Network Address could not be identified.")
    except Exception as err:
        update_server_status(server_id=None, status_id=ServerStatus.ServerStatus.Error.value)
        print(err)


def get_server_from_mac_address(mac_address):
    server = Server()

    query = Query()
    query.TransactionType = eTransactionType.MultiSelectQuery
    query.Sql = sql_select + sql_from + " WHERE s.MacAddress = ?"
    query.Args = [str(mac_address)]
    result = DBConn.single_query(query)
    if len(result) > 0:
        server.mapper(result)
        return server
    else:
        return None


def insert_default_values_into_db(mac_address):
    server = Server()
    server.Name = "Server"
    server.MacAddress = mac_address
    server.InternalAddress = get_local_ip()
    server.ExternalAddress = get_external_ip()
    server.PortNumber = 8089
    server.StatusID = ServerStatus.ServerStatus.StartingUp.value
    server.DirectoryPath = "/VideoSecurityServer"

    insert_query = Query()
    insert_query.TransactionType = eTransactionType.Insert
    insert_query.Sql = "INSERT INTO tServers (Name, MacAddress, InternalAddress, ExternalAddress, PortNumber, ServerStatusID, DirectoryPath) VALUES (?,?,?,?,?,?,?)"
    insert_query.Args = [str(server.Name), str(server.MacAddress), str(server.InternalAddress), str(server.ExternalAddress), str(server.PortNumber), str(server.StatusID), str(server.DirectoryPath)]
    server.ServerID = DBConn.single_query(insert_query)


def update_startup_values_into_db(server):
    server.InternalAddress = get_local_ip()
    server.ExternalAddress = get_external_ip()
    server.StatusID = ServerStatus.ServerStatus.StartingUp.value

    update_query = Query()
    update_query.TransactionType = eTransactionType.Update
    update_query.Sql = "UPDATE tServers SET InternalAddress = ?, ExternalAddress = ?, ServerStatusID = ? WHERE ServerID = ?"
    update_query.Args = [str(server.InternalAddress), str(server.ExternalAddress), str(server.StatusID), str(server.ServerID)]
    DBConn.single_query(update_query)


def update_server_status(server_id, status_id):
    # Server ID will not always be known. If it is not passed, look it up
    if server_id is None:
        mac_address = get_current_mac_address()
        server = get_server_from_mac_address(mac_address)
        server_id = server.ServerID

    update_query = Query()
    update_query.TransactionType = eTransactionType.Update
    update_query.Sql = "UPDATE tServers SET ServerStatusID = ? WHERE ServerID = ?"
    update_query.Args = [str(status_id), str(server_id)]
    DBConn.single_query(update_query)


def attempt_repair():
    update_server_status(server_id=None, status_id=ServerStatus.ServerStatus.Error.value)
    while 0 < 1:
        print("Awaiting repair...")
        time.sleep(5)


def standby(server):
    update_server_status(server.ServerID, status_id=ServerStatus.ServerStatus.WaitingForNewCamera.value)
    while 0 < 1:
        print("Waiting for Cameras")
        time.sleep(5)
