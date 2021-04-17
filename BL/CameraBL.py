from BL import ServerBL
from DL import DBConn
from Enums.ServerStatus import ServerStatus
from Enums.eTransactionType import eTransactionType
from Objects.Camera import Camera
from Objects.Query import Query

sql_select = " SELECT c.CameraID, c.Name, c.MacAddress, c.InternalAddress, c.ExternalAddress, c.CameraStatusID, c.CameraStatusID "
sql_from = " FROM tCamera c "


def get_all_cameras_for_server(server):
    try:
        cameras_array = []

        camera_link_query = Query()
        camera_link_query.TransactionType = eTransactionType.Query
        camera_link_query.Sql ="SELECT cs.CameraID FROM tCameraServer cs WHERE cs.ServerID = %s"
        camera_link_query.Args = [str(server.ServerID)]

        camera_ids_array = DBConn.single_query(camera_link_query)
        if len(camera_ids_array) > 0:
            camera_ids_string = ""
            for camera_id in camera_ids_array:
                value = camera_id.get("CameraID")
                camera_ids_string += str(value) + ","

            camera_ids_string = camera_ids_string[:-1]
            camera_query = Query()
            camera_query.TransactionType = eTransactionType.MultiSelectQuery
            camera_query.Sql = sql_select + sql_from + " WHERE c.CameraID IN (?)"
            camera_query.Args = [str(camera_ids_string)]
            camera_dict_list = DBConn.single_query(camera_query)

            for camera_dict in camera_dict_list:
                camera_obj = Camera()
                camera_obj.mapper(camera_dict)
                cameras_array.append(camera_obj)

        return cameras_array

    except Exception as err:
        print(err)
        ServerBL.update_server_status(server.ServerID, ServerStatus.Error.value)
        return []
