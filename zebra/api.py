import frappe
from frappe import _
import time
import json

from frappe.exceptions import DoesNotExistError

MIN_SECONDS_FROM_LAST_LOG = 60

@frappe.whitelist(allow_guest=True)
def callback(**kwargs):
    """
    Endpoint for the RFID Reader to send data to.
    Gets the IP address from the frappe.request object 
    and find the corresponding reader's location.
    Creates RFID Logs and Equipment (if does not exist already).

    args: the RFID Reader sends data in this format:
        json = [
            {
                "data": {
                    "antenna": 1,
                    "idHex": "idHex",
                    "now": "now",
                    "peakRssi": "peakRssi",
                    "reads": "reads",
                    "eventNum": "eventNum",
                    "type": "type"
                },
                "type": "INVENTORY"
            }
        ]
    """
    ip_address = frappe.request.environ["REMOTE_ADDR"] #frappe.request.host.split(":")[0] #"152.63.45.95"
    (rfid_reader, location) = get_location(ip_address)

    data = kwargs.get("json")
    tag_data = json.loads(data or '[]')
    last_reading_by_tag = get_last_reading_by_tag(tag_data)
    print("TAG_DATA: ", tag_data)
    print("LAST_READING_BY_TAG: ", last_reading_by_tag)
    print("IP ADDRESS: ", ip_address)
    print("LOCATION: ", location)

    for tag in last_reading_by_tag.keys():
        can_create_new_log_var = can_create_new_log(tag, location)
        print("can_create_new_log: ", can_create_new_log_var)
        if can_create_new_log_var:
            create_rfid_log(last_reading_by_tag[tag], rfid_reader, location)


def create_rfid_log(reading, rfid_reader, location):
    if len(reading) == 0:
        return

    reading = reading[0]
    doc = frappe.new_doc("RFID Logs")
    doc.antenna = reading['data']['antenna']
    doc.id = reading['data']['idHex']
    print("CREATING LOG FOR TAG: ", doc.id)
    doc.datetime = frappe.utils.now()
    doc.rssi = reading['data']['peakRssi']
    doc.read = reading['data']['reads']
    doc.event_num = reading['data']['eventNum']
    doc.type = reading['type']
    doc.rfid_reader = rfid_reader
    doc.location = location
    doc.save(ignore_permissions=True)

    equipment = frappe.db.exists("Equipment", {"rfid_number":  reading['data']['idHex']})
    if not equipment:
        equ_doc = frappe.new_doc("Equipment")
        equ_doc.rfid_number =  reading['data']['idHex']
        equ_doc.status = "Working"
        equ_doc.naming_series = "EQ"
        equ_doc.insert(ignore_permissions=True, ignore_mandatory=True)


def get_location(ip_address):
    reader = frappe.db.get_list("RFID Reader", 
        filters = [["zebra_url", "like", "%{}%".format(ip_address)]], 
        fields = ["name", "location"])
    location = None
    rfid_reader = None
    if len(reader) > 0: # TODO: more than one RFID Reader with the same IP should not be allowed
        location = reader[0]["location"]
        rfid_reader = reader[0]["name"]
    return (rfid_reader, location)


def can_create_new_log(tag, location):
    try:
        last_doc = frappe.get_last_doc('RFID Logs', filters={"id": tag}, order_by="datetime desc")
        if last_doc.location != location: # only create log if location has changed
            return True
        # delta = frappe.utils.datetime.datetime.now() - last_doc.datetime
        # if delta.total_seconds() > MIN_SECONDS_FROM_LAST_LOG:
        #     return True
        return False
    except DoesNotExistError:
        return True


def get_last_reading_by_tag(data):
    unique_tags = list(set([d["data"]["idHex"] for d in data]))
    reading_by_tag = {}
    for tag in unique_tags:
        readings_for_tag = [d["data"]["eventNum"] for d in data if d["data"]["idHex"] == tag]
        max_event_num = max(readings_for_tag)
        last_reading = list(filter(lambda d: d["data"]["eventNum"] == max_event_num, data))
        reading_by_tag[tag] = last_reading
    
    return reading_by_tag


if __name__ == "__main__":
    data = {"json": """[
        {
            "data": {
                "antenna": 1,
                "eventNum": 1759,
                "format": "epc",
                "idHex": "112233445566778899001134",
                "peakRssi": -53,
                "reads": 387321
            },
            "timestamp": "2023-04-03T21:50:16.699+0200", 
            "type": "SIMPLE"
        },
        {
            "data": {
                "antenna": 1,
                "eventNum": 1761,
                "format": "epc",
                "idHex": "112233445566778899001134_2",
                "peakRssi": -53,
                "reads": 387321
            },
            "timestamp": "2023-04-03T21:50:17.699+0200", 
            "type": "SIMPLE"
        },
        {
            "data": {
                "antenna": 1,
                "eventNum": 1762,
                "format": "epc",
                "idHex": "112233445566778899001134",
                "peakRssi": -53,
                "reads": 387321
            },
            "timestamp": "2023-04-03T21:50:18.699+0200", 
            "type": "SIMPLE"
        },
        {
            "data": {
                "antenna": 1,
                "eventNum": 1763,
                "format": "epc",
                "idHex": "112233445566778899001134_2",
                "peakRssi": -53,
                "reads": 387321
            },
            "timestamp": "2023-04-03T21:50:19.699+0200", 
            "type": "SIMPLE"
        }
    ]"""}
    can_create_new_log("0001")