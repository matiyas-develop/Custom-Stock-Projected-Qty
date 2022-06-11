// Copyright (c) 2022, Matiyas Solution LLP and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Stock Availability Report"] = {
	"filters": [
		{
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company"
		},
		{
			"fieldname":"warehouse",
			"label": __("Warehouse"),
			"fieldtype": "Link",
			"options": "Warehouse",
			"get_query": () => {
				return {
					filters: {
						company: frappe.query_report.get_filter_value('company')
					}
				}
			}
		},
		{
			"fieldname":"s_item_code",
			"label": __("Item Code"),
			"fieldtype": "Data"
		},
		{
			"fieldname":"item_group",
			"label": __("Item Group"),
			"fieldtype": "Link",
			"hidden": 1,
			"options": "Item Group"
		},
		{
			"fieldname":"item_category",
			"label": __("Item Category"),
			"fieldtype": "Link",
			"options": "Item Category"
		},
		{
			"fieldname":"available_qty",
			"label": __("Available Qty >"),
			"fieldtype": "Data"
		},
		{
			"fieldname":"selling_rate",
			"label": __("Selling Rate <"),
			"fieldtype": "Data"
		},
		{
			"fieldname":"s_item_name",
			"label": __("Item Name"),
			"fieldtype": "Data"
		},
		{
			"fieldname":"brand",
			"label": __("Brand"),
			"fieldtype": "Link",
			"options": "Brand"
		},
		{
			"fieldname":"include_uom",
			"label": __("Include UOM"),
			"fieldtype": "Link",
			"hidden": 1,
			"options": "UOM"
		}
	]
};
