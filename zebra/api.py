import frappe
from frappe import _
import time
import json

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
    ip_address = frappe.request.host.split(":")[0] #"152.63.45.95"
    (rfid_reader, location) = get_location(ip_address)

    data = kwargs.get("json")
    tag_data = json.loads(data or '[]')
    for d in tag_data:
        doc = frappe.new_doc("RFID Logs")
        doc.antenna = d['data']['antenna']
        doc.id = d['data']['idHex']
        doc.datetime = frappe.utils.now()
        doc.rssi = d['data']['peakRssi']
        doc.read = d['data']['reads']
        doc.event_num = d['data']['eventNum']
        doc.type = d['type']
        doc.rfid_reader = rfid_reader
        doc.location = location
        doc.save(ignore_permissions=True)

        equipment = frappe.db.exists("Equipment", {"rfid_number":  d['data']['idHex']})
        if not equipment:
            equ_doc = frappe.new_doc("Equipment")
            #equ_doc.serial_number =  d['data']['idHex']
            equ_doc.rfid_number =  d['data']['idHex']
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