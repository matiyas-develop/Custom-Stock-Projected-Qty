# Copyright (c) 2022, Matiyas Solution LLP and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt, today

from erpnext.accounts.doctype.pos_invoice.pos_invoice import get_pos_reserved_qty
from erpnext.stock.utils import (
    is_reposting_item_valuation_in_progress,
    update_included_uom_in_report,
)


def execute(filters=None):
    is_reposting_item_valuation_in_progress()
    filters = frappe._dict(filters or {})
    include_uom = filters.get("include_uom")
    columns = get_columns()
    bin_list = get_bin_list(filters)
    item_map = get_item_map(filters.get("item_code"), include_uom, filters)

    warehouse_company = {}
    data = []
    conversion_factors = []
    for bin in bin_list:
        item = item_map.get(bin.item_code)

        if not item:
            # likely an item that has reached its end of life
            continue

        # item = item_map.setdefault(bin.item_code, get_item(bin.item_code))
        company = warehouse_company.setdefault(bin.warehouse,
                                               frappe.db.get_value("Warehouse", bin.warehouse, "company"))

        if filters.brand and filters.brand != item.brand:
            continue

        elif filters.item_group and filters.item_group != item.item_group:
            continue

        elif filters.item_category and filters.item_category != item.item_category:
            continue

        elif filters.company and filters.company != company:
            continue

        re_order_level = re_order_qty = 0

        for d in item.get("reorder_levels"):
            if d.warehouse == bin.warehouse:
                re_order_level = d.warehouse_reorder_level
                re_order_qty = d.warehouse_reorder_qty

        shortage_qty = 0
        if (re_order_level or re_order_qty) and re_order_level > bin.projected_qty:
            shortage_qty = re_order_level - flt(bin.projected_qty)

        reserved_qty_for_pos = get_pos_reserved_qty(
            bin.item_code, bin.warehouse)
        if reserved_qty_for_pos:
            bin.projected_qty -= reserved_qty_for_pos

        data.append([item.item_category, item.name, item.item_name, bin.location_name, bin.actual_qty, bin.reserved_qty, bin.ordered_qty, bin.projected_qty,
                     item.price_list_rate,  bin.valuation_rate, item.brand])

        if include_uom:
            conversion_factors.append(item.conversion_factor)

    update_included_uom_in_report(
        columns, data, include_uom, conversion_factors)
    return columns, data


def get_columns():
    return [

        {"label": _("Item Category"), "fieldname": "item_category", "fieldtype": "Link", "options": "Item Category", "width": 130},
        {"label": _("Item Code"), "fieldname": "item_code", "width": 140},
        {"label": _("Item Name"), "fieldname": "item_name", "width": 100},
        {"label": _("Branch"), "fieldname": "location_name", "fieldtype": "Link", "options": "Warehouse", "width": 140},
        {"label": _("Actual Qty"), "fieldname": "actual_qty",
         "fieldtype": "Float", "width": 100, "convertible": "qty"},
        {"label": _("Reserved Qty"), "fieldname": "reserved_qty",
         "fieldtype": "Float", "width": 100, "convertible": "qty"},
        {"label": _("Ordered Qty"), "fieldname": "ordered_qty",
         "fieldtype": "Float", "width": 100, "convertible": "qty"},
        {"label": _("Projected Qty"), "fieldname": "projected_qty",
         "fieldtype": "Float", "width": 100, "convertible": "qty"},
        {"label": _("Selling Price"), "fieldname": "price_list_rate",
         "fieldtype": "Link", "options": "Item Price", "width": 140},
        {"label": _("Valuation Rate"), "fieldname": "valuation_rate",
         "fieldtype": "Link", "options": "Bin", "width": 140},
        {"label": _("Brand"), "fieldname": "brand",
         "fieldtype": "Link", "options": "Brand", "width": 100}
        
    ]


def get_bin_list(filters):
    conditions = []

    if filters.item_code:
        conditions.append("item_code = '%s' " % filters.item_code)

    if filters.warehouse:
        warehouse_details = frappe.db.get_value(
            "Warehouse", filters.warehouse, ["lft", "rgt"], as_dict=1)

        if warehouse_details:
            conditions.append(" exists (select name from `tabWarehouse` wh \
				where wh.lft >= %s and wh.rgt <= %s and bin.warehouse = wh.name)" % (warehouse_details.lft,
                                                                         warehouse_details.rgt))

    actual_qty = filters.get("available_qty", 1)

    bin_list = frappe.db.sql("""select item_code, warehouse, actual_qty, planned_qty, indented_qty, projected_qty,
		ordered_qty, reserved_qty, reserved_qty_for_production, valuation_rate, reserved_qty_for_sub_contract, projected_qty, wh.location_name
		from tabBin bin 
        left join `tabWarehouse` wh on wh.name=bin.warehouse
        where actual_qty >= {actual_qty} and actual_qty > 0 {conditions} order by item_code, warehouse
		""".format(actual_qty=actual_qty, conditions=" and " + " and ".join(conditions) if conditions else ""), as_dict=1)

    return bin_list


def get_item_map(item_code, include_uom, filters):
    """Optimization: get only the item doc and re_order_levels table"""

    condition = ""
    if filters.get("s_item_code"):
        condition += 'and item.item_code like "%%{s_item_code}%%"'.format(
            s_item_code=filters.get("s_item_code"))

    conditions = ""
    if filters.get("selling_rate"):
        condition += 'and price_list_rate <= {selling_rate}'.format(
            selling_rate=filters.get("selling_rate"))
    if filters.get("s_item_name"):
        conditions += 'and item.item_name like "%%{s_item_name}%%"'.format(
            s_item_name=filters.get("s_item_name"))

    cf_field = cf_join = ""
    if include_uom:
        cf_field = ", ucd.conversion_factor"
        cf_join = "left join `tabUOM Conversion Detail` ucd on ucd.parent=item.name and ucd.uom=%(include_uom)s"

    items = frappe.db.sql("""
		select item.name, item.item_name, item.description, item.item_group,item.item_category, item.brand, item.stock_uom{cf_field},pr.price_list_rate
		from `tabItem` item
        left join `tabItem Price` pr on pr.item_code=item.item_code and pr.selling = 1 and pr.price_list = "Standard Selling"
		{cf_join}
		where item.is_stock_item = 1
		and item.disabled=0
		{condition}
		{conditions}
		and (item.end_of_life > %(today)s or item.end_of_life is null or item.end_of_life='0000-00-00')
		and exists (select name from `tabBin` bin where bin.item_code=item.name)"""
                          .format(cf_field=cf_field, cf_join=cf_join, conditions=conditions, condition=condition),
                          {"today": today(), "include_uom": include_uom}, as_dict=True)

    condition = ""
    if item_code:
        condition = 'where parent={0}'.format(
            frappe.db.escape(item_code, percent=False))

    reorder_levels = frappe._dict()
    for ir in frappe.db.sql("""select * from `tabItem Reorder` {condition}""".format(condition=condition), as_dict=1):
        if ir.parent not in reorder_levels:
            reorder_levels[ir.parent] = []

        reorder_levels[ir.parent].append(ir)

    item_map = frappe._dict()
    for item in items:
        item["reorder_levels"] = reorder_levels.get(item.name) or []
        item_map[item.name] = item

    return item_map