# HOTNSPICYHEAD - SALES ANALYSIS REPORT

**Database:** HOTNSPICYHEAD  
**Server:** 103.86.55.34,50908  
**Report Generated:** 2026-04-18  
**Analysis Period Covered:** 2020-12-09 to 2021-07-01 (~6.5 months)

---

## 1. KYA SALES HAIN? (WHAT ARE SALES?)

### Sales Tables (31 found, top 6 shown):

| Table Name | Rows | Purpose |
|------------|------|---------|
| **CustomerPOS** | 420,496 | Customer master data |
| **OrderKot** | 252,422 | Kitchen Order Tickets (KOT) - items to kitchen |
| **Order_Detail** | 236,776 | Order line items (individual products) |
| **CustomerPOS_** | 115,662 | Customer extensions/additional data |
| **OrderStatusTime** | 81,978 | Order status tracking timestamps |
| **Dine_In_Order** | 81,965 | Order headers (main order records) |

### Total Business Volume:
- **Orders Processed:** ~82,000 orders
- **Order Line Items:** ~237,000 items sold
- **KOT Generated:** ~252,000 kitchen tickets
- **Total Calculated Revenue:** **PKR 357,062,314** (from Order_Detail qty × price)
- **Average Order Value:** ~PKR 4,350 (calculated from categories total ÷ unique orders)

---

## 2. SALES METHOD / KAISE SALES HOTE HAIN? (HOW SALES WORK?)

### Order Flow Process:

```
Customer Arrives/Orders
        ↓
[CustomerPOS] → Customer info (id, name, phone, address)
        ↓
[Dine_In_Order] → Order header created (order_key, order_type, order_date, amount, discount)
        ↓
[Order_Detail] → Individual items added (category → item → qty × price)
        ↓
[OrderKot] → Kitchen ticket generated (sent to kitchen)
        ↓
[OrderStatusTime] → Status updates (ordered → preparing → served → billed)
        ↓
[Payment] (via CashReceipt/BankReceipt tables)
```

### Order Channels (Sales Methods):

| Channel | Orders | Description |
|---------|--------|-------------|
| **DELIVERY** | 81,964 | Home delivery orders (99.99%) |
| **TAKE AWAY** | 1 | Pack-and-go orders |

### Product Categories (Top 10 by Revenue):

| Rank | Category | Items Sold | Revenue (PKR) | % of Total |
|------|----------|------------|---------------|------------|
| 1 | **ROLLS** | 72,585 | 196,671,333 | 55.0% |
| 2 | **FASTFOOD** | 30,858 | 36,412,277 | 10.2% |
| 3 | **BAR B Q** | 21,113 | 29,395,986 | 8.2% |
| 4 | **TANDOOR** | 30,062 | 25,834,805 | 7.2% |
| 5 | **HANDI** | 12,573 | 18,620,216 | 5.2% |
| 6 | **RICE** | 7,515 | 17,343,980 | 4.9% |
| 7 | **KARAHI** | 3,671 | 6,878,268 | 1.9% |
| 8 | **CHINEESE** | 6,375 | 5,507,598 | 1.5% |
| 9 | **FAST FOOD** | 4,985 | 4,900,243 | 1.4% |
| 10 | **BEVARAGES** | 15,224 | 3,457,976 | 1.0% |

**Top 3 categories (ROLLS, FASTFOOD, BAR B Q) = 73.4% of total revenue**

---

## 3. LATEST SALES KAB KE HAIN? (WHEN IS THE LATEST SALES?)

### Date Range:
- **First Order:** 2020-12-09 12:08:00
- **Latest Order:** **2021-07-01 13:46:00**
- **Data Freshness:** ⚠️ **OLD DATA - Database not updated since July 2021**

### Most Recent Transactions:
```
OrderKey  Date & Time           Type      Amount
--------  -------------------   -------   ----------
545607    2021-07-01 13:46     DELIVERY   PKR 0.00 (amount field null in header)
545606    2021-07-01 13:43     DELIVERY   Line items: PISHAWARY MUTTON KARAHI (1260) + others
545605    2021-07-01 13:41     DELIVERY   CADBURY SHAKE + 7UP
545604    2021-07-01 13:40     DELIVERY   MINT LEMONADE
545603    2021-07-01 13:40     DELIVERY
```

### Hourly Sales Pattern (Peak Times):
| Hour | Revenue (PKR) | % of Daily |
|------|---------------|------------|
| 20:00-21:00 | 52,374,724 | 14.6% (PEAK) |
| 21:00-22:00 | 43,572,901 | 12.2% |
| 19:00-20:00 | 34,459,019 | 9.6% |
| 12:00-13:00 | 25,714,898 | 7.2% |
| 22:00-23:00 | 19,835,360 | 5.5% |

**Business Hours:** Active from 08:00 to 02:00 (lunch & dinner rushes)

---

## 4. ZAROORI BAATEIN / NECESSARY INFORMATION

### A. Database Structure (Key Tables)

#### Customer Tables:
- **CustomerPOS** - Main customer table (420K customers)
  - Columns: id, customer_name, phone (cell_no/tel_no), address, customer_code, active
  - FK: None (standalone)

#### Order Tables:
- **Dine_In_Order** - Order header (81K orders)
  - Key columns: order_key, order_date, order_type, amount, discount, branchId, user_id
  - Tracks: table_no, waiter_name, cover, TimeIn/TimeOut, service_status
  
- **Order_Detail** - Line items (236K items)
  - Key: order_key (links to Dine_In_Order), item_name, category_name, qty, price, Discount, tax
  - Main revenue source (qty × price = PKR 357M)
  
- **OrderKot** - Kitchen tickets (252K lines)
  - Key: OrderKey, ItemId, Qty, KotStatus, OrderDetailId
  - Links kitchen prep to orders

#### Product/Menu Tables:
- **ItemPOS** - Active menu items (1,643 items with prices)
  - Columns: item_name, category_name, cost_price, sale_price, codes, status, tiltId
  - Has commission settings (Item_Commission)
  
- **CategoryPOS** - Categories (130 categories)
- **MenuCategory** - Menu structure (3 rows)
- **MenuItem** - Menu items (4 rows - likely active menu configuration)

#### Branch/Company:
- **Branch** - 7 branches (BRId, Branch name, address, phone)
- **Company** - 1 company (COId, Company details)
- **DepartmentPOS** - 14 departments

#### Financial Tables (mostly empty - 0 rows):
- SaleInvoiceMaster/Detail
- CustomerSaleInvoiceMaster/Detail
- CashPaymentMaster/Detail
- CashReceiptMaster/Detail
- BankPaymentMaster/Detail
- GL, ChartOfAccount

⚠️ **Note:** Financial tables appear unused or data archived

---

### B. Sales Method / Business Logic

1. **Order Creation:**
   - Customer record exists in CustomerPOS
   - New order created in Dine_In_Order with order_key (sequential/incrementing)
   - order_key range: 415718 → 545607 (last ~130K keys used)

2. **Item Addition:**
   - Each item added to Order_Detail with qty and price
   - Kitchen ticket generated in OrderKot
   - item_name and category_name stored in Order_Detail (denormalized)

3. **Pricing:**
   - Price captured at time of sale (Order_Detail.price)
   - ItemPOS contains current prices (sale_price)
   - Discount stored per-line (Order_Detail.Discount) and per-order (Dine_In_Order.discount)

4. **Order Types:**
   - DELIVERY (dominant) - requires delivery address
   - TAKE AWAY

5. **Status Tracking:**
   - OrderStatusTime table tracks order progress timestamps
   - Dine_In_Order.Status (bit) indicates bill generated
   - OrderKot.KotStatus tracks kitchen completion

---

### C. Data Quality Issues Found:

| Issue | Impact | Table(s) |
|-------|--------|----------|
| ⚠️ **Old data** | No sales since July 2021 | All tables |
| ⚠️ **Dine_In_Order.amount = NULL** | Header totals not stored | Dine_In_Order |
| ⚠️ **No direct FK constraints** between sales tables | Data integrity relied on application logic | Order_Detail, Dine_In_Order, OrderKot |
| ⚠️ **Financial tables empty** | Invoicing/billing module not used | SaleInvoice*, CustomerSaleInvoice* |
| ⚠️ **Order keys not consistent** | order_key = 0.00 in Dine_In_Order for some orders | Dine_In_Order |

---

### D. Performance Observations:

1. **Heavy read operations:** Order_Detail (236K rows) + Dine_In_Order (82K) = Good for reporting
2. **Indexes likely on:** order_key, date columns, ItemId, branchId
3. **Sample data fetch confirmed:** Database responsive (sub-second queries)
4. **No compression needed:** Database size moderate (~726MB total including all 240 tables)

---

### E. Recommendations for Dashboard/Reporting:

**Available Metrics:**
- ✅ Total sales amount: PKR 357,062,314 (calculated from Order_Detail)
- ✅ Order count: ~82,000
- ✅ Sales by category, hour, day, month
- ✅ Branch performance (branchId column exists in Dine_In_Order)
- ✅ User performance (user_id column exists)
- ✅ Delivery performance (deliver_time, dispatch_time columns)

**Missing/Not Available:**
- ❌ Profit margins (cost_price in ItemPOS but not captured in sales)
- ❌ Payment method breakdown (payment tables empty)
- ❌ Customer lifetime value (customer data exists but no payment history links)
- ❌ Returns/refunds (likely separate process)

**To Refresh Data:**
- The database is from **2021** - contact database admin to restore/replicate current data
- Or check if there's an active database at different connection (103.86.55.34,50908 pointed to old HOTNSPICYHEAD)

---

## 5. QUICK QUERY REFERENCE

### Top 5 Best-Selling Items by Revenue:
```sql
SELECT TOP 5 item_name, SUM(qty) as total_qty, SUM(qty * price) as revenue
FROM Order_Detail
WHERE price IS NOT NULL
GROUP BY item_name
ORDER BY revenue DESC
```

### Daily Sales Trend:
```sql
SELECT CAST(date AS DATE) as sale_date, COUNT(DISTINCT order_key) as orders, SUM(qty * price) as revenue
FROM Order_Detail
GROUP BY CAST(date AS DATE)
ORDER BY sale_date
```

### Branch Performance:
```sql
SELECT branchId, COUNT(DISTINCT od.order_key) as orders, SUM(od.qty * od.price) as revenue
FROM Order_Detail od
JOIN Dine_In_Order dio ON od.order_key = dio.order_key
GROUP BY branchId
ORDER BY revenue DESC
```

---

## 6. FILES GENERATED

| File | Size | Purpose |
|------|------|---------|
| `DATABASE_DOCUMENTATION.md` | 196 KB | Full table-by-table documentation |
| `database_schema.json` | 726 KB | Machine-readable schema |
| `analyze_hotnspicyhead_db_optimized.py` | 15 KB | Schema analysis script |
| `analyze_sales.py` | 4 KB | Sales table discovery |
| `analyze_sales_detailed.py` | 6 KB | Column/relationship analysis |
| `sales_summary_report.py` | 6 KB | Revenue & activity report |

---

## CONCLUSION

**Sales haan, lekin data purana hai.**  
- **Total historic revenue:** PKR 357 Million  
- **Latest activity:** July 1, 2021  
- **Main products:** Rolls, Fast Food, BBQ, Tandoor items  
- **Primary channel:** Delivery (99.99%)  
- **Active branches:** 7 branches tracked  

**Next steps:**  
1. Verify if this is the correct database or if a newer one exists  
2. If dashboard needs real-time data, update connection string  
3. Build dashboards using Order_Detail + Dine_In_Order as fact tables  
4. Use ItemPOS for current product list (1,643 items, but only 1,643 rows vs 0 in Item - discrepancy noted)

---

**Report prepared by:** Automated Database Analysis  
**Confidence:** High (based on 240 tables, 87 FKs, 1.2M total rows)
