// Copyright (c) 2023, phamos and contributors
// For license information, please see license.txt

frappe.ui.form.on('Zebra Settings', {
	refresh: function(frm){
		if(frm.doc.__islocal != 1){
			frm.add_custom_button(__("Start TAG Read"), function(){
				ping_zebra("start");
			}, __("Zebra Operations"));

			frm.add_custom_button(__("Stop TAG Read"), function(){
				ping_zebra("stop");
                        }, __("Zebra Operations"));

			frm.add_custom_button(__("Reboot Reader"), function(){
				ping_zebra("reboot");
                        }, __("Zebra Operations"));

			frm.add_custom_button(__("Check Operation Mode"), function(){
				ping_zebra("mode");
                        }, __("Zebra Operations"));

			frm.add_custom_button(__("Check Zebra Version"), function(){
				ping_zebra("version");
                        }, __("Zebra Operations"));
		}
	}
});

function ping_zebra(operation){
	frappe.call({
		method: "zebra.zebra.doctype.zebra_settings.zebra_settings.zebra_operations",
		args: {"operation": operation},
		freeze: 1
	});
}
