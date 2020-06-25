from DL import DBConn
from Objects.Camera import Camera

sql_select = " SELECT c.CameraID, c.Name, c.MacAddress, c.InternalIPAddress, c.ExternalIPAddress, c.Height, c.Width, cd.DirectoryPath, c.CameraStatusID "
sql_from = " FROM tCamera c "
sql_directory_join = " LEFT JOIN tCameraDirectory cd ON c.CameraID = cd.CameraID "

def get_all_cameras(server):
    cameras = []
    query = "SELECT cs.CameraID" \
            " FROM" \
            " tCameraServer cs" \
            " WHERE cs.ServerID = " + str(server.ServerID) + ";"

    camera_ids_dict = DBConn.query_return(query)
    camera_ids_string = ""
    for camera_id in camera_ids_dict:
        value = camera_id.get("CameraID")
        camera_ids_string += str(value) + ","

    if camera_ids_string == "":
        return None
    else:
        camera_ids_string = camera_ids_string[:-1]
        query = sql_select + \
                sql_from + \
                sql_directory_join + \
                " WHERE c.CameraID IN (" + camera_ids_string + ");"

        camera_dict_list = DBConn.query_return(query)
        for camera_dict in camera_dict_list:
            camera_obj = Camera()
            camera_obj.mapper(camera_dict)
            cameras.append(camera_obj)

        return cameras