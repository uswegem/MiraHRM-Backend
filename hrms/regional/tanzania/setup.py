# Copyright (c) 2026, MiraHRM Contributors
# License: GNU General Public License v3. See license.txt
#
# Regional module for Tanzania. Auto-discovered by hrms.overrides.company.run_regional_setup()
# / make_salary_components() the moment a Company's Country field is set to "Tanzania" - see
# hrms/overrides/company.py:make_company_fixtures. No hooks.py wiring is required.
#
# IMPORTANT: statutory rates below (PAYE, NSSF, WCF, SDL, NHIF) change via the annual Finance Act
# and TRA/NSSF/WCF/SDL/NHIF notices. Verify current rates before relying on this in production -
# see docs/TANZANIA_CUSTOMIZATION.md in the repo root for sources and the review checklist.

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

from hrms.setup import delete_custom_fields

# Monthly PAYE bands (TZS), Tanzania Mainland, per Finance Act 2023 - verify before use.
MONTHLY_PAYE_BANDS = [
	(0, 270_000, 0),
	(270_000, 520_000, 8),
	(520_000, 760_000, 20),
	(760_000, 1_000_000, 25),
	(1_000_000, None, 30),
]

NSSF_EMPLOYEE_RATE = 10  # % of gross pay
NSSF_EMPLOYER_RATE = 10  # % of gross pay
WCF_RATE = 0.6  # % of gross emoluments, employer only (private sector default)
SDL_RATE = 3.5  # % of gross emoluments, employer only (employers with >= 4 employees)
NHIF_EMPLOYEE_RATE = 3  # % of gross pay
NHIF_EMPLOYER_RATE = 3  # % of gross pay


def setup():
	make_custom_fields()
	create_default_income_tax_slab()


def uninstall():
	delete_custom_fields(get_custom_fields())


def make_custom_fields(update=True):
	create_custom_fields(get_custom_fields(), update=update)


def get_custom_fields():
	return {
		"Employee": [
			{
				"fieldname": "tanzania_statutory_section",
				"label": "Tanzania Statutory Details",
				"fieldtype": "Section Break",
				"insert_after": "payroll_cost_center",
				"collapsible": 1,
				"depends_on": "eval:doc.__islocal || doc.tin_number || doc.nssf_number",
			},
			{
				"fieldname": "tin_number",
				"label": "TIN Number",
				"fieldtype": "Data",
				"insert_after": "tanzania_statutory_section",
				"description": "Tanzania Revenue Authority Taxpayer Identification Number",
				"translatable": 0,
			},
			{
				"fieldname": "social_security_scheme",
				"label": "Social Security Scheme",
				"fieldtype": "Select",
				"options": "\nNSSF\nPSSSF",
				"insert_after": "tin_number",
				"description": "NSSF for private sector, PSSSF for public service employees",
			},
			{
				"fieldname": "tz_statutory_col_break",
				"fieldtype": "Column Break",
				"insert_after": "social_security_scheme",
			},
			{
				"fieldname": "social_security_number",
				"label": "Social Security Number",
				"fieldtype": "Data",
				"insert_after": "tz_statutory_col_break",
				"description": "NSSF or PSSSF membership number, matching Social Security Scheme above",
				"translatable": 0,
			},
			{
				"fieldname": "nhif_number",
				"label": "NHIF Number",
				"fieldtype": "Data",
				"insert_after": "social_security_number",
				"translatable": 0,
			},
		],
		"Company": [
			{
				"fieldname": "tanzania_statutory_section",
				"label": "Tanzania Statutory Details",
				"fieldtype": "Section Break",
				"insert_after": "default_payroll_payable_account",
				"collapsible": 1,
			},
			{
				"fieldname": "tin_number",
				"label": "TIN Number",
				"fieldtype": "Data",
				"insert_after": "tanzania_statutory_section",
				"translatable": 0,
			},
			{
				"fieldname": "sdl_applicable",
				"label": "SDL Applicable (>= 4 employees)",
				"fieldtype": "Check",
				"insert_after": "tin_number",
				"default": "1",
			},
			{
				"fieldname": "tz_company_col_break",
				"fieldtype": "Column Break",
				"insert_after": "sdl_applicable",
			},
			{
				"fieldname": "wcf_number",
				"label": "WCF Employer Number",
				"fieldtype": "Data",
				"insert_after": "tz_company_col_break",
				"translatable": 0,
			},
			{
				"fieldname": "nssf_employer_number",
				"label": "NSSF/PSSSF Employer Number",
				"fieldtype": "Data",
				"insert_after": "wcf_number",
				"translatable": 0,
			},
		],
	}


def create_default_income_tax_slab():
	"""Create a submitted default PAYE Income Tax Slab for Tanzania (TZS, annualised bands).

	Frappe HR's Income Tax Slab works on *annual* taxable earnings, so the well-known monthly
	PAYE bands are multiplied by 12 here. Re-run/adjust manually if the Finance Act changes them.
	"""
	slab_name = "Tanzania PAYE Slab"

	if frappe.db.exists("Income Tax Slab", slab_name):
		return

	slabs = []
	for from_monthly, to_monthly, percent in MONTHLY_PAYE_BANDS:
		row = {
			"from_amount": from_monthly * 12,
			"percent_deduction": percent,
		}
		if to_monthly is not None:
			row["to_amount"] = to_monthly * 12
		slabs.append(row)

	slab = frappe.new_doc("Income Tax Slab")
	slab.update(
		{
			"name": slab_name,
			"title": slab_name,
			"effective_from": frappe.utils.nowdate(),
			"currency": "TZS",
			"allow_tax_exemption": 0,
			"slabs": slabs,
		}
	)
	slab.insert(ignore_permissions=True, ignore_mandatory=True)
	try:
		slab.submit()
	except Exception:
		frappe.log_error(title="Could not auto-submit Tanzania PAYE Slab")
