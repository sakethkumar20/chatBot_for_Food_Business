from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi import BackgroundTasks
import db_helper
import generic_helper

app = FastAPI()


def update_status_task():
    db_helper.update_order_status()


@app.on_event("startup")
async def startup_event():
    # db_helper.update_order_status()  # Update order_status initially on startup
    # Schedule the update_order_status function to run every 1 minute (adjust as needed)
    background_task = BackgroundTasks()
    background_task.add_task(update_status_task)
    await background_task()


@app.post("/")
async def handle_request(request: Request):
    payload = await request.json()
    intent = payload['queryResult']['intent']['displayName']
    parameters = payload['queryResult']['parameters']
    output_contexts = payload['queryResult']['outputContexts']
    intent_handler_dict = {
        'order.add - context: ongoing-order': add_to_order,
        'order.remove - context: ongoing-order': remove_from_order,
        'order.complete - context: ongoing-order': complete_order,
        'track.order - context: ongoing-tracking': track_order,
        'new.order': reset_inprogress_orders
        # 'check.number': take_phn_no
    }
    session_id = generic_helper.extract_session_id(output_contexts[0]['name'])
    return intent_handler_dict[intent](parameters, session_id)


'''def take_phn_no(parameters: dict, session_id: str):
    phn_no = str(int(parameters['number'][0]))
    if len(phn_no) != 10:
        fulfillment_text = 'Sorry! Could you please provide a valid mobile number.'
    else:
        generic_helper.mobile_no = phn_no
        if phn_no not in generic_helper.processing_mobile_no:
            fulfillment_text = f'Is this your mobile number {phn_no}? \tYes/No'
        else:
            fulfillment_text = f'Order with the mobile number: {phn_no} already exists.'
    return JSONResponse(content={
        'fulfillmentText': fulfillment_text
    })'''


def reset_inprogress_orders(parameters: dict, session_id: str):
    print('hiii')
    generic_helper.inprogress_orders.clear()


def remove_from_order(parameters: dict, session_id: str):
    if session_id not in generic_helper.inprogress_orders:
        fulfillment_text = "I'm having a trouble finding your order. Sorry! Can you place a new order please?"
    else:
        food_items = parameters["food-item"]
        quantities = parameters["number"]
        print(quantities)
        if len(food_items) != len(quantities):
            fulfillment_text = "Sorry I didn't understand. Can you please specify food items and quantities clearly?"
        else:
            flag = 0
            order = generic_helper.inprogress_orders[session_id]
            temp = dict(zip(food_items, quantities))
            for item, number in temp.items():
                if item in order and number <= order[item]:
                    order[item] -= number
                    if order[item] == 0:
                        del order[item]
                else:
                    flag = 1
                    fulfillment_text = "Sorry I didn't understand. Can you please specify food items and quantities clearly?"
                    break
            if flag == 0:
                order_str = generic_helper.get_str_from_food_dict(
                    generic_helper.inprogress_orders[session_id])
                fulfillment_text = f"So far you have: {order_str}. Do you need anything else?"
    return JSONResponse(content={
        'fulfillmentText': fulfillment_text
    })


def save_to_db(order: dict, session_id: str):
    next_order_id = db_helper.get_next_order_id()
    #phn_no = generic_helper.mobile_no
    for item, number in order.items():
        return_code = db_helper.insert_order_item(
            item,
            int(number),
            next_order_id
        )

        if return_code == -1:
            return -1

    db_helper.insert_order_tracking(
        next_order_id, 'Being Prepared')
    return next_order_id


def complete_order(parameters: dict, session_id: str):
    if session_id not in generic_helper.inprogress_orders:
        fulfillment_text = "I'm having a trouble finding your order. Sorry! Can you place a new order please?"
    else:
        order = generic_helper.inprogress_orders[session_id]
        order_id = save_to_db(order, session_id)
        if order_id == -1:
            fulfillment_text = "Sorry, I couldn't process your order due to a backend error. " \
                               "Please place a new order again"
        else:
            order_total = db_helper.get_order_total(order_id)
            # db_helper.update_order_status()
            fulfillment_text = f"Awesome. We have placed your order. " \
                f"Here is your order id # {order_id}. " \
                f"Total amount of your order is: {order_total}Rs. which you can pay at the time of delivery!"

        del generic_helper.inprogress_orders[session_id]
    return JSONResponse(content={'fulfillmentText': fulfillment_text})


def add_to_order(parameters: dict, session_id: str):
    food_items = parameters["food-item"]
    quantities = parameters["number"]

    if len(food_items) != len(quantities):
        fulfillment_text = "Sorry I didn't understand. Can you please specify food items and quantities clearly?"
    else:
        new_food_dict = dict(zip(food_items, quantities))

        if session_id in generic_helper.inprogress_orders:
            current_food_dict = generic_helper.inprogress_orders[session_id]
            current_food_dict.update(new_food_dict)
            generic_helper.inprogress_orders[session_id] = current_food_dict
        else:
            generic_helper.inprogress_orders[session_id] = new_food_dict

        order_str = generic_helper.get_str_from_food_dict(
            generic_helper.inprogress_orders[session_id])
        fulfillment_text = f"So far you have: {order_str}. Do you need anything else?"

    return JSONResponse(content={
        "fulfillmentText": fulfillment_text
    })


def track_order(parameters: dict, session_id: str):
    value = int(parameters['order_id'][0])
    order_id = int(value)
    order_status = db_helper.get_order_status_id(order_id)
    if order_status:
        fulfillment_text = f"The order status for the order id: {order_id} is {order_status}"
    else:
        fulfillment_text = f"No order found with order id: {order_id}. Make sure that you enter correct order id."
    return JSONResponse(content={
        "fulfillmentText": fulfillment_text
    })
