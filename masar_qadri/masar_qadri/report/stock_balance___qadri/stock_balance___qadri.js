// Copyright (c) 2025, KCSC and contributors
// For license information, please see license.txt

frappe.query_reports["Stock Balance - Qadri"] = {
	"filters": [
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			width: "80",
			options: "Company",
			default: frappe.defaults.get_default("company"),
		},
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			width: "80",
			reqd: 1,
			default: frappe.datetime.get_today(),
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			width: "80",
			reqd: 1,
			default: frappe.datetime.get_today(),
		},
		{
			fieldname: "item_group",
			label: __("Item Group"),
			fieldtype: "Link",
			width: "80",
			options: "Item Group",
		},
		{
			fieldname: "barcode",
			label: __("Barcode"),
			fieldtype: "Data",
			width: "80",
		},
		{
			fieldname: "item_name",
			label: __("Item Name"),
			fieldtype: "Data",
			width: "80",
		},
		{
			fieldname: "warehouse",
			label: __("Warehouse"),
			fieldtype: "Link",
			width: "80",
			options: "Warehouse",
			get_query: () => {
				let company = frappe.query_report.get_filter_value("company");

				return {
					filters: {
						...(company && { company }),
					},
				};
			},
		},
		{
			fieldname: "article",
			label: __("Article"),
			fieldtype: "Data",
			width: "80",
		},
		{
			fieldname: "color",
			label: __("Color"),
			fieldtype: "Data",
			width: "80",
		},
		{
			fieldname: "show_variant_attributes",
			label: __("Show Variant Attributes"),
			fieldtype: "Check",
			default: 1,
		},
		{
			fieldname: "show_stock_ageing_data",
			label: __("Show Stock Ageing Data"),
			fieldtype: "Check",
			hidden: 1,
		},
		{
			fieldname: "ignore_closing_balance",
			label: __("Ignore Closing Balance"),
			fieldtype: "Check",
			hidden: 1,
			default: 0,
		},
		{
			fieldname: "include_zero_stock_items",
			label: __("Include Zero Stock Items"),
			fieldtype: "Check",
			default: 0,
			hidden: 1,
		},

	]
};