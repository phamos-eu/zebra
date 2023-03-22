# Copyright (c) 2023, phamos and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class RFIDLogs(Document):
	def after_insert(self):
		""" When record is inserted check for the equipment with the rfid no. and update the location field """
		equipment = frappe.get_doc('Equipment', {'rfid_number': self.id})
		if equipment.last_location != self.location:
			equipment.last_location = self.location
			equipment.save()
