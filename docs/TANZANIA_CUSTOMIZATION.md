# Tanzania Customization

MiraHRM Backend is `frappe/hrms` (Frappe HR) forked at commit `450f6ca` with a `hrms/regional/tanzania/`
module added, following the exact same extension pattern the upstream project already uses for India
and the UAE (`hrms/regional/india`, `hrms/regional/united_arab_emirates`).

**How it activates:** nothing to wire up manually. The moment a Company's `Country` field is set to
`Tanzania`, `hrms/overrides/company.py::make_company_fixtures` auto-discovers and runs
`hrms.regional.tanzania.setup.setup()` and merges `hrms/regional/tanzania/data/salary_components.json`
into the default Salary Component list. This fires on `Company.on_update` when `country` changes,
which for a fresh site normally happens once, right after the Setup Wizard.

## What's implemented

| Requirement | Status | Where |
|---|---|---|
| Employee register (personal/employment/contract/salary) | ✅ Already core HRMS | `Employee`, `Employee Grade`, `Salary Structure Assignment` |
| TIN, NSSF/PSSSF number, NHIF number fields | ✅ Added | `hrms/regional/tanzania/setup.py::get_custom_fields` (Employee + Company) |
| PAYE (progressive monthly tax) | ✅ Default slab seeded | `Income Tax Slab` "Tanzania PAYE Slab", via `Income Tax` component (core) |
| NSSF (10% employee / 10% employer) | ✅ Salary components seeded | `data/salary_components.json` |
| PSSSF (public sector alternative to NSSF) | ✅ Seeded, disabled by default | same file — enable per company if needed |
| WCF (employer-only, statistical) | ✅ Seeded | same file |
| SDL (employer-only, statistical, 4+ employees) | ✅ Seeded | same file |
| NHIF (employee/employer) | ✅ Seeded, disabled by default | same file — Tanzania's NHIF participation varies by sector, enable if applicable |
| Payslip generation | ✅ Already core HRMS | `Salary Slip` |
| GL posting on payroll approval | ✅ Already core HRMS, needs account mapping | `Payroll Entry` → `Journal Entry`, via `Salary Component Account` (map each component to a GL account per company — not seeded here since it's Chart-of-Accounts specific) |
| Leave balances & requests | ✅ Already core HRMS | `Leave Application`, `Leave Allocation`, `Leave Type` |
| Staff loan deductions in payroll | ✅ Already core HRMS | `Loan` + `Loan Repayment`, auto-pulled into `Salary Slip` (see `hrms/setup.py::create_salary_slip_loan_fields`) |

## ⚠️ Verify the rates before going to production

Tax and statutory contribution rates change via the annual Finance Act and notices from TRA, NSSF,
WCF, the SDL authority, and NHIF. The defaults seeded by this fork (in
`hrms/regional/tanzania/setup.py` and `data/salary_components.json`) are:

- **PAYE** (Mainland, per Finance Act 2023 bands): 0% to 270,000 TZS/mo, 8% to 520,000, 20% to
  760,000, 25% to 1,000,000, 30% above — annualised into the `Income Tax Slab` record since Frappe
  computes PAYE on annual taxable earnings.
- **NSSF**: 10% employee + 10% employer of gross pay.
- **WCF**: 0.6% of gross emoluments, employer only (private-sector rate; public institutions differ).
- **SDL**: 3.5% of gross emoluments, employer only, for employers with 4+ employees.
- **NHIF**: 3% employee + 3% employer of gross pay (disabled by default — enable if applicable to
  your organization).

Before running real payroll, confirm each rate against the current Finance Act / TRA notice and
update the `Income Tax Slab` slabs or the relevant `Salary Component`'s `formula` field to match —
no code change needed, these are just data.

## What's still TODO

- **Chart of Accounts**: no Tanzania-specific CoA template is included. Map each statutory Salary
  Component (NSSF Employee/Employer, WCF, SDL, NHIF, Income Tax) to a payable GL account per company
  via `Salary Component Account`, so `Payroll Entry` posts correctly.
- **Mobile money payout** (M-Pesa, Tigo Pesa, Airtel Money) for salary disbursement — not started.
- **Swahili translation** of the UI — not started; Frappe's translation framework (`locale/`) supports
  it, just needs `sw` strings contributed.
- **NBC/CRDB/NMB bank file formats** for bulk salary payment exports — not started.
- **Zanzibar-specific** payroll/statutory differences (ZSSF instead of NSSF, different PAYE
  administration in some cases) — not modeled; only Mainland Tanzania rates are seeded.

## Verifying the install

```
bench --site <site> execute hrms.regional.tanzania.setup.setup
bench --site <site> console
>>> frappe.get_all("Income Tax Slab", filters={"currency": "TZS"})
>>> frappe.get_all("Salary Component", filters={"salary_component": ["like", "%NSSF%"]})
```
