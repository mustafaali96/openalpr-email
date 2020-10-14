import MySQLdb 
 
def db_insert(plate,uid,camera_id,date_time,plate_crop,car_crop,loc):
    #print(im_path)
    try: 
        print("Connecting to database using MySQLdb") 
        db_connection = MySQLdb.connect(host='localhost', db='parking', user='root', passwd= '') 
        #print("Succesfully Connected to database using MySQLdb!") 
        cur = db_connection.cursor()
        
        sql = "INSERT INTO data (`plate`,`date_time`,`uid`,`camera_id`,`number_plate`,`car_crop`,`loc`) VALUES ('%s','%s','%s','%s','%s','%s','%s')" %(plate,date_time,uid,camera_id,plate_crop,car_crop,loc)
        #print(sql)
        
        cur.execute(sql)
        db_connection.commit()
        
        cur.close()
        
        db_connection.close()
        print("Data Inserted into Database\n")           
    except:
        print("Error: Database Connection Failed")
        
def db_get_loc(cam_id):
    try:
        db_connection = MySQLdb.connect(host='localhost', db='parking', user='root', passwd= '') 

        #print("Succesfully Connected to database using MySQLdb!") 
        cur = db_connection.cursor()
        sql = "SELECT location FROM `camera_loc` WHERE camera_id = %s "

        cur.execute(sql,(cam_id,))
        myresult = cur.fetchall()

        for x in myresult:
            loc = x[0]
            print("Location is: ", loc)
            return loc
    except:
        print("No location Found for Camera ID: ",cam_id)
    