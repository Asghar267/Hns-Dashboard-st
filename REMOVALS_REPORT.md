# Removal Report (Cleanup Log)

Date: 2026-03-28
Scope: Current codebase + UI export cleanup + QR Commission table removal

## Export Features Removed

### PDF Export (All Areas)
- PDF download buttons removed from export sections.
- `export_to_pdf` helper function removed.
- PDF removed from export formats list.

Files:
- components/ui_components.py
- dashboard_tabs/overview_tab.py
- modules/utils.py
- modules/config.py
- archive/hns_dashboard.py
- archive/hns_dashboard_imported.py
- archive/pre_mod.py
- archive/pre_orig.py

### CSV Export (All Areas)
- All CSV download buttons removed (UI export sections and specific tab downloads).
- CSV export option removed from export formats.
- Any leftover CSV helper usage in tabs removed.

Files (non-archive/current):
- components/ui_components.py
- dashboard_tabs/overview_tab.py
- dashboard_tabs/category_coverage_tab.py
- dashboard_tabs/chef_sales_tab.py
- dashboard_tabs/order_takers_tab.py
- dashboard_tabs/pivot_tables_tab.py
- dashboard_tabs/ramzan_deals_tab.py
- dashboard_tabs/trends_analytics_tab.py
- dashboard_tabs/ot_targets_tab.py
- dashboard_tabs/chef_targets_tab.py
- modules/config.py

Files (archive, for parity):
- archive/hns_dashboard.py
- archive/hns_dashboard_imported.py

Notes:
- Export UI now shows Excel-only.
- Any leftover CSV-only code paths were removed or neutralized.

## QR Commission Tab: Table Removed

### Removed Table
- Title: "Khadda Diagnostics - Employee Summary (Non-Blinkco POS)"
- Description: "Same template as Employee-wise Totals (with Shop). Khadda only (shop_id=2)."
- Location: QR Commission tab (Khadda Diagnostics section in QR tab)

Files:
- dashboard_tabs/qr_commission_tab.py (entire block removed)
- hns_dashboard_modular.py (permission option removed: "Khadda Non-Blinkco Employee Summary")

## UI Adjustments Triggered By Removals

- Overview export section now single-column Excel-only.
- Export buttons consolidated to Excel-only in shared UI components.
- Ramzan Deals tab had empty download columns removed to fix indentation errors.

Files:
- dashboard_tabs/overview_tab.py
- components/ui_components.py
- dashboard_tabs/ramzan_deals_tab.py

## Cleanup / Optimization (Imports & Dead Code)

Removed unused imports across current modules (no behavior change):
- components/new_navbar.py
- config/app_config.py
- connection_cloud.py
- daily_branch_snapshots.py
- dashboard_tabs/category_coverage_tab.py
- dashboard_tabs/chef_targets_tab.py
- dashboard_tabs/material_cost_commission_tab.py
- dashboard_tabs/order_takers_tab.py
- dashboard_tabs/overview_tab.py
- dashboard_tabs/qr_commission_tab.py
- generate_blink_report.py
- hns_dashboard_modular.py
- modules/auth.py
- modules/blink_reporting.py
- modules/connection_cloud.py
- modules/database.py
- modules/qr_tab_renderer.py
- modules/visualization.py
- services/branch_service.py
- services/chef_sales_service.py
- services/order_taker_service.py
- services/qr_commission_service.py
- services/targets_service.py

Note: These were unused-import removals only; logic preserved except where explicitly noted above.

## Summary

- PDF export: removed globally.
- CSV export: removed globally.
- QR Commission: Khadda Non-Blinkco Employee Summary table removed.
- Export UI: Excel-only.
- Misc: cleanup/unused import removal and minor layout fixes.

## Change Metadata

- Requested By: user (chat request)
- Approval: not specified
- Date Applied: 2026-03-28
- Environment: local dev (Streamlit app)
- Reason / Rationale:
  - Remove PDF and CSV export paths; keep Excel-only to simplify usage
  - Remove "Khadda Diagnostics - Employee Summary (Non-Blinkco POS)" from QR Commission tab per request
  - Clean unused imports to reduce clutter
- Impacted Areas:
  - Export UI (Overview + shared export component)
  - QR Commission tab (Khadda diagnostics section)
  - Config export formats
- Verification:
  - No automated tests run
  - Manual verification recommended: app load + Overview tab + QR Commission tab
- Rollback Plan:
  - Reintroduce removed export buttons and helpers
  - Restore QR Commission table block from version control if needed

