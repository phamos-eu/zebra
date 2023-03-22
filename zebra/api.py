import frappe
from frappe import _
import time
import json

@frappe.whitelist(allow_guest=True)
def callback(**kwargs):
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
        doc.save(ignore_permissions=True)

        equipment = frappe.db.exists("Equipment", {"rfid_number":  d['data']['idHex']})
        if not equipment:
            equ_doc = frappe.new_doc("Equipment")
            #equ_doc.serial_number =  d['data']['idHex']
            equ_doc.rfid_number =  d['data']['idHex']
            equ_doc.status = "Working"
            equ_doc.naming_series = "EQ"
            equ_doc.insert(ignore_permissions=True, ignore_mandatory=True)
