# Setup

MiraHRM Backend is a normal Frappe app on top of the Frappe Framework + ERPNext (HRMS depends on
ERPNext for `Company`, `Account`, etc.). It is run via `bench`, same as upstream `frappe/hrms`.

## Local development (bench)

```bash
# Prerequisites: Python 3.10+, Node 18+, MariaDB, Redis, yarn — see
# https://frappeframework.com/docs/user/en/installation for full prerequisites, or use the
# docker/ folder in this repo for a containerized setup.

pip install frappe-bench
bench init mirahrm-bench --frappe-branch version-15
cd mirahrm-bench

bench get-app erpnext --branch version-15
bench get-app hrms https://github.com/uswegem/MiraHRM-Backend.git --branch main

bench new-site mirahrm.local
bench --site mirahrm.local install-app erpnext
bench --site mirahrm.local install-app hrms

bench start
```

Then in the Setup Wizard (or Company doctype), set **Country = Tanzania** — this triggers the
Tanzania regional setup automatically (see `docs/TANZANIA_CUSTOMIZATION.md`).

## Docker

See `docker/` for a docker-compose setup mirroring the upstream `frappe/hrms` container config.

## Frontend

The employee-portal (PWA) and shift-roster frontends live in the companion repo,
[`uswegem/MiraHRM-Frontend`](https://github.com/uswegem/MiraHRM-Frontend). They are Vite/Vue apps
that build static assets consumed by this backend's Frappe website routes (`hrms/www/hrms.py`,
`hrms/www/roster.py`). To wire them up locally:

```bash
cd ../MiraHRM-Frontend/frontend && yarn install && yarn build
# copy/symlink the build output into this bench's app public assets, matching how
# frappe/hrms's own build pipeline does it (see MiraHRM-Frontend/README.md)
```

A from-scratch CI/deploy pipeline that builds the frontend repo and publishes assets into a backend
site is not set up yet — see the TODO list in `docs/TANZANIA_CUSTOMIZATION.md`.

## Running tests

```bash
bench --site mirahrm.local run-tests --app hrms
```
