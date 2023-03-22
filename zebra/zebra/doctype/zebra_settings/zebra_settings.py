# Copyright (c) 2023, phamos and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
import requests
from requests.auth import HTTPDigestAuth
from urllib3.exceptions import InsecureRequestWarning
import time

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

class ZebraSettings(Document):
    pass

def get_setting():
    return frappe.get_single("Zebra Settings")

def get_token():
    doc = get_setting()
    url = f'{doc.zebra_url}/cloud/localRestLogin'
    headers = {"Content-Type": "text/plain", "Authorization": "Basic YWRtaW46U3RhcnQxMjMh"}
    res = requests.get(url, \
            auth=HTTPDigestAuth(f'{doc.username}', f'doc.get_password("password")'), \
            headers=headers, verify=False)
    return res

@frappe.whitelist()
def start_tag_read():
    doc = get_setting()
    response = get_token()
    if response.status_code == 200:
        token = response.json()['message']
        url = f'{doc.zebra_url}/cloud/start'
        headers = {"Accept": "application/json", "Authorization": f"Bearer {token}"}
        response = requests.put(url, headers=headers, verify=False)
        print(response.status_code)
        if response.status_code == 200:
            time.sleep(10)
            frappe.msgprint("We are now started reading Zebra Tags...")
        else:
            frappe.msgprint("Something went wrong please try again later!")
    else:
        frappe.msgprint("Something went wrong please try again later!")

@frappe.whitelist()
def zebra_operations(operation):
    doc = get_setting()
    response = get_token()
    if response.status_code == 200:
        token = response.json()['message']
        url = f'{doc.zebra_url}/cloud/{operation}'
        headers = {"Accept": "application/json", "Authorization": f"Bearer {token}"}

        if operation in ['start', 'stop', 'reboot']:
            response = requests.put(url, headers=headers, verify=False)
        else:
            response = requests.get(url, headers=headers, verify=False)

        if response.status_code == 200:
            if operation in ['start', 'stop', 'reboot']:
                time.sleep(10)
                frappe.msgprint(f"Zebra TAG reader {operation}!")
            else:
                frappe.msgprint(f'{response.text}')
        else:
            frappe.msgprint("Something went wrong please try again later!")
    else:
        frappe.msgprint("Something went wrong please try again later!")


