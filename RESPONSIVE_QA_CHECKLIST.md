# Responsive QA Checklist

## Goal
Use this checklist to verify the Streamlit dashboard remains usable on desktop, tablet, and phone after responsive layout changes.

## Recommended test widths
- Desktop: `1366x768` or wider
- Tablet: `820x1180` or similar
- Phone: `390x844` or similar

## App shell
- Launch the app and confirm it loads without Python errors.
- On desktop, confirm the sidebar is visible on first load.
- On phone, confirm the sidebar starts collapsed.
- On phone, confirm the `Filters & Controls` expander is visible near the top of the page.
- Switch `Layout Mode` between `Auto`, `Desktop`, `Tablet`, and `Phone` and confirm the page rerenders without breaking widgets.
- Confirm `Logout`, `Dark Mode`, date range, branch filters, target period, refresh, and snapshot controls remain reachable.

## Navigation
- Desktop/tablet: confirm navigation still works across the main tabs.
- Phone: confirm navigation uses the compact select-style control and still switches tabs correctly.
- Change filters, then switch tabs, and confirm the active tab state is preserved sensibly.

## Core tabs
### Overview
- Confirm KPI cards stack correctly on phone.
- Confirm the gauge, heatmap, waterfall, and sankey charts remain readable without obvious clipping.
- Confirm branch cards do not overflow horizontally on phone.

### Order Takers
- Confirm summary metrics stack correctly.
- Confirm the top performers chart remains readable on phone.
- Confirm the detailed table uses a smaller mobile-friendly height.

### Food Panda
- Confirm the top summary metrics stack correctly.
- Confirm `By Branch`, `Top Employees`, and `All Food Panda Transactions` remain usable on phone.
- Confirm reconciliation tables still render and export buttons still work.
- Confirm the `Reconciliation` / `Cancellation` sub-navigation works on phone.

### QR Commission
- Confirm top KPI cards stack correctly.
- Confirm split report filters remain usable on phone.
- Confirm large tables still render with mobile-sized heights instead of oversized desktop heights.
- Confirm diagnostics sections expand and remain readable.

### Category Filters & Coverage
- Confirm configuration buttons stack correctly on phone.
- Confirm included/excluded/detail tables render without oversized height.
- Confirm blocked transactions and unmapped items sections remain usable.

### Trends & Analytics
- Confirm summary charts resize cleanly.
- Confirm trend/forecast sections stack on smaller screens.
- Confirm top/bottom product trend charts and product explorer remain readable.
- Confirm the branch filter becomes usable on phone.

### Database Health / Admin & Snapshots
- Confirm metric cards stack on phone.
- Confirm snapshot viewer tables and file metrics do not overflow badly.
- Confirm user management forms remain usable on narrow screens.

## Regression checks
- Change filters on phone and confirm the same filters are reflected after rerun.
- Use `Refresh` and confirm the app reruns without losing essential state.
- Toggle `Dark Mode` and confirm custom cards/tables remain legible.
- Confirm downloads still work for CSV/Excel/JSON outputs.

## Known limitation
- A real Playwright device pass from this environment is currently blocked by an MCP permission issue creating:
  `C:\Program Files\Microsoft VS Code\.playwright-mcp`
- Until that is fixed, visual QA should be done manually in a browser using device emulation.
