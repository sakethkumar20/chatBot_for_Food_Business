import generic_helper
import mysql.connector
from datetime import datetime, timedelta
import requests
global cnx

cnx = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Root",
    database="pandeyji_eatery"
)


def update_order_status():
    try:
        cursor = cnx.cursor()
        end_time = datetime.now()
        # Update order_status to 'Delivered' after 20 minutes and before 45 minutes
        query1 = "UPDATE order_tracking SET status = 'In transit' WHERE status = 'Being Prepared' AND TIMESTAMPDIFF(MINUTE, order_created_time, %s) >= %s AND (TIMESTAMPDIFF(MINUTE, order_created_time, %s) < %s)"
        cursor.execute(query1, (end_time, 20, end_time, 45))

        # Update order_status to 'Delivered' after 45 minutes
        query2 = "UPDATE order_tracking SET status = 'Delivered' WHERE status = 'In transit' AND TIMESTAMPDIFF(MINUTE, order_created_time, %s) >= %s"
        cursor.execute(query2, (end_time, 45))

        '''query = "select mobile_no from order_tracking where status='Delivered'"
        cursor.execute(query)
        result = cursor.fetchall()
        for i in range(len(result)):
            phn_no = result[i][0]
            print('Phone number: ', phn_no)
            if phn_no in generic_helper.processing_mobile_no:
                generic_helper.processing_mobile_no.remove(phn_no)
            generic_helper.delivered.append(phn_no)
            query = f"delete from orders where mobile_no={phn_no}"
            cursor.execute(query)
        query = "delete from order_tracking where status='Delivered'"
        cursor.execute(query)
        print('Delivered list: ', generic_helper.delivered)'''
        cnx.commit()

    except Exception as e:
        print("Error:", e)
    finally:
        cnx.commit()
        cursor.close()


def get_order_total(order_id):
    cursor = cnx.cursor()
    query = f'select sum(total_price) from orders where order_id={order_id}'
    cursor.execute(query)
    result = cursor.fetchone()[0]
    cursor.close()
    return result


def insert_order_tracking(order_id: int, status: str):
    cursor = cnx.cursor()
    query = 'insert into order_tracking values(%s,%s,%s)'
    cursor.execute(
        query, (order_id, status, datetime.now()))
    cnx.commit()
    cursor.close()


def insert_order_item(item, quantity, order_id):
    try:

        cursor = cnx.cursor()
        cursor.callproc('insert_order_item',
                        (item, quantity, order_id))
        cnx.commit()
        cursor.close()
        return 1

    except mysql.connector.Error as err:
        print(f"Error inserting order item: {err}")

        # Rollback changes if necessary
        cnx.rollback()

        return -1

    except Exception as e:
        print(f"An error occurred: {e}")
        # Rollback changes if necessary
        cnx.rollback()

        return -1


def get_next_order_id():
    cursor = cnx.cursor()
    query = 'select max(order_id) from order_tracking'
    cursor.execute(query)
    result = cursor.fetchone()[0]
    cursor.close()
    if result is None:
        return 1
    else:
        return result+1


def get_order_status_id(order_id):

    # create a cursor object
    cursor = cnx.cursor()

    # Executing the SQL query to fetch the order status
    query = f"SELECT status FROM order_tracking WHERE order_id = {order_id}"
    cursor.execute(query)

    # Fetching the result
    result = cursor.fetchone()

    # Closing the cursor
    cursor.close()

    # Returning the order status
    if result:
        return result[0]
    else:
        return None


'''def get_order_status_phn_no(phn_no: str):

    # create a cursor object
    cursor = cnx.cursor()

    # Executing the SQL query to fetch the order status
    query = f"SELECT status FROM order_tracking WHERE mobile_no = {phn_no}"
    cursor.execute(query)

    # Fetching the result
    result = cursor.fetchone()

    # Closing the cursor
    cursor.close()

    # Returning the order status
    if result:
        return result[0]
    else:
        return None'''
