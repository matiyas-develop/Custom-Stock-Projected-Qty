// Copyright (c) 2022, Matiyas Solution LLP and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Custom Stock Projected Qty"] = {
	"filters": [
		{
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company")
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
			"fieldname":"item_code",
			"label": __("Item"),
			"fieldtype": "Link",
			"options": "Item",
			"get_query": function() {
				return {
					query: "erpnext.controllers.queries.item_query"
				}
			}
		},
		{
			"fieldname":"item_group",
			"label": __("Item Group"),
			"fieldtype": "Link",
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
			"fieldname":"standard_rate",
			"label": __("Standard Rate <"),
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
			"options": "UOM"
		}
	]
};
