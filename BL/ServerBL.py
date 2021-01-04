import socket
import sys
import uuid
import time
from requests import get
from DL import DBConn
from Enums import ServerStatus
from Enums.eTransactionType import eTransactionType
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
        return "Unavailable"


def get_external_ip():
    try:
        external_ip = get('https://api.ipify.org').text
        return external_ip
    except Exception:
        return "Unavailable"


def get_current_mac_address():
    try:
        mac_address = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff)
                                for ele in range(0, 8 * 6, 8)][::-1])
        return mac_address
    except Exception:
        return "Unavailable"


def startup():
    try:
        print("Initializing Server...")

        mac_address = get_current_mac_address()
        server = query_startup_values_from_db(mac_address)

        # Update existing data and return
        if server is not None:
            if update_startup_values_into_db(server):
                server = query_startup_values_from_db(mac_address)
                return server
            else:
                return None
        # Create new entry and return
        else:
            if insert_default_values_into_db(mac_address):
                server = query_startup_values_from_db(mac_address)
                return server
            else:
                return None

    except Exception as err:
        update_server_status(server_id=None, status_id=ServerStatus.ServerStatus.Error.value)
        print(err)


def query_startup_values_from_db(mac_address):
    try:
        server = Server()
        if mac_address == "Unavailable":
            return None
        else:
            query = Query()
            query.TransactionType = eTransactionType.Query
            query.Sql = sql_select + sql_from + " WHERE s.MacAddress = ?"
            query.Args = [str(mac_address)]
            result = DBConn.single_query(query)
            if len(result) > 0:
                server.mapper(result)
                return server
            else:
                return None
    except Exception as err:
        print(err)
        update_server_status(server_id=None, status_id=ServerStatus.ServerStatus.Error.value)
        return None


def insert_default_values_into_db(mac_address):
    try:
        # Insert into tCamera
        server = Server()
        server.Name = "Server"
        server.MacAddress = mac_address
        server.InternalAddress = get_local_ip()
        server.ExternalAddress = get_external_ip()
        server.PortNumber = 8089
        server.StatusID = ServerStatus.ServerStatus.StartingUp.value
        server.DirectoryPath = "/VideoSecurityServer"

        server_insert = Query()
        server_insert.TransactionType = eTransactionType.Insert
        server_insert.Sql = "INSERT INTO tServers (Name, MacAddress, InternalAddress, ExternalAddress, PortNumber, ServerStatusID, DirectoryPath) VALUES (?,?,?,?,?,?,?)"
        server_insert.Args = [str(server.Name), str(server.MacAddress), str(server.InternalAddress), str(server.ExternalAddress), str(server.PortNumber), str(server.StatusID), str(server.DirectoryPath)]
        server.ServerID = DBConn.single_query(server_insert)
        return True

    except Exception as err:
        print(err)
        # Do not attempt to update server status since since most likely doesnt exist in db
        return False


def update_startup_values_into_db(server):
    try:
        server.InternalAddress = get_local_ip()
        server.ExternalAddress = get_external_ip()
        server.StatusID = ServerStatus.ServerStatus.StartingUp.value

        update_query = Query()
        update_query.TransactionType = eTransactionType.Update
        update_query.Sql = "UPDATE tServers SET InternalAddress = ?, ExternalAddress = ?, ServerStatusID = ? WHERE ServerID = ?"
        update_query.Args = [str(server.InternalAddress), str(server.ExternalAddress), str(server.StatusID), str(server.ServerID)]
        updated_rows = DBConn.single_query(update_query)
        return True
    except Exception as err:
        print(err)
        update_server_status(server.ServerID, ServerStatus.ServerStatus.Error.value)
        return False


def update_server_status(server_id, status_id):
    try:
        # Server ID will not always be known. If it is not passed, look it up
        if server_id is None:
            mac_address = get_current_mac_address()
            server = query_startup_values_from_db(mac_address)
            server_id = server.ServerID

        update_query = Query()
        update_query.TransactionType = eTransactionType.Update
        update_query.Sql = "UPDATE tServers SET ServerStatusID = ? WHERE ServerID = ?"
        update_query.Args = [str(status_id), str(server_id)]
        updated_rows = DBConn.single_query(update_query)
        return True
    except Exception as err:
        print(err)
        return False


def attempt_repair():
    while 0 < 1:
        print("Awaiting repair...")
        time.sleep(5)
