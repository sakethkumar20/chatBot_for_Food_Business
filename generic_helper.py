import re
inprogress_orders = {}

def get_str_from_food_dict(food_dict: dict):
    result = ""
    for item, number in food_dict.items():
        result += str(int(number))
        result = result+f" {item}, "
    result = result[:len(result)-2]
    return result


def extract_session_id(session_str: str):
    match = re.search(r"/sessions/(.*?)/contexts/", session_str)
    if match:
        extracted_string = match.group(1)
        return extracted_string

    return ""
