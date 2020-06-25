import socket
import sys
import uuid
from requests import get

from DL import DBConn
from Enums import ServerStatus
from Objects.Server import Server


def get_local_ip():
    try:
        os = sys.platform
        local_ip = "Unavailable"
        if os == "linux":
            host_name = socket.gethostname()
            local_ip = socket.gethostbyname(host_name + ".local")

        elif os == "darwin":
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
        return "Unavailable"\


def startup():
    try:
        mac_address = get_current_mac_address()
        server = query_values_from_db(mac_address)

        # Update existing data and return
        if server is not None:
            if update_values_into_db(server):
                server = query_values_from_db(mac_address)
                return server
            else:
                return None

        # Create new entry and return
        else:
            if insert_default_values_into_db(mac_address):
                server = query_values_from_db(mac_address)
                return server
            else:
                return None

    except Exception as err:
        print(err)


def query_values_from_db(mac_address):
    server = Server()
    if mac_address != "Unavailable":
        # query = "SELECT s.ServerID FROM tServer s WHERE s.MacAddress = '" + mac_address + "';"

        query = "SELECT s.ServerID, s.Name, s.MacAddress, s.InternalIPAddress, s.ExternalIPAddress, s.ServerStatusID, s.IsDebug, sd.DirectoryPath" \
                " FROM tServer s" \
                " LEFT JOIN tServerDirectory sd ON s.ServerID = sd.ServerID" \
                " WHERE s.MacAddress = '" + mac_address + "';"

        result = DBConn.query_return(query)
        if len(result) > 0:
            server.mapper(result[0])
            return server
        else:
            return None


def insert_default_values_into_db(mac_address):
    try:
        internal_ip = get_local_ip()
        external_ip = get_external_ip()

        # Insert into tCamera
        server = Server()
        server.Name = "Server"
        server.MacAddress = mac_address
        server.InternalIPAddress = internal_ip
        server.ExternalIPAddress = external_ip
        server.StatusID = ServerStatus.ServerStatus.StartingUp.value
        server.IsDebug = 0
        server.ServerID = 0
        server.DirectoryPath = ""

        query = "INSERT INTO tServer" \
                " (Name, MacAddress, InternalIPAddress, ExternalIPAddress, ServerStatusID, IsDebug)" \
                " VALUES" \
                " ('" + server.Name + "' ,'" + server.MacAddress + "', '" + server.InternalIPAddress + "', '" + server.ExternalIPAddress + "', " + str(server.StatusID) + ", " + str(server.IsDebug) + ");"
        server.ServerID = DBConn.query_update(query, True)

        # Insert into tServerDirectory
        query = "INSERT INTO tServerDirectory" \
                " (ServerID, DirectoryPath)" \
                " VALUES" \
                " (" + str(server.ServerID) + ", 'Server/" + str(server.ServerID) + "/');"
        camera_directory_id = DBConn.query_update(query, True)
        return True

    except Exception as err:
        print(err)
        return False


def update_values_into_db(server):
    try:
        internal_ip = get_local_ip()
        external_ip = get_external_ip()
        status_id = ServerStatus.ServerStatus.StartingUp.value

        server.InternalIPAddress = internal_ip
        server.ExternalIPAddress = external_ip
        server.StatusID = status_id

        query = "UPDATE tServer" \
                " SET" \
                " InternalIPAddress = '" + server.InternalIPAddress +"', ExternalIPAddress = '" + server.ExternalIPAddress + "', ServerStatusID = " + str(server.StatusID) + \
                " WHERE ServerID = " + str(server.ServerID)
        updated_rows = DBConn.query_update(query, False)
        # Updated rows will only be greater than 0 if something actually changes
        # We have to assume that it works
        return True
    except Exception as err:
        print(err)
        return False