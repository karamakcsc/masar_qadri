// Copyright (c) 2025, KCSC and contributors
// For license information, please see license.txt

frappe.query_reports["X Report"] = {
	"filters": [
		{
			"fieldname": "user",
			"label": "User",
			"fieldtype": "Link",
			"options": "User",
			"default": frappe.session.user,
			"read_only": 1
		}
	]
};
