# Database Documentation: HOTNSPICYHEAD
**Generated:** 2026-04-18 16:38:31
**Server:** 103.86.55.34,50908
**Database:** HOTNSPICYHEAD

## Summary
- **Total Tables:** 240
- **Total Rows:** 1,216,773
- **Foreign Key Relationships:** 87

## Table of Contents
1. [dbo.2StepWok](#dbo-2stepwok)
2. [dbo.2StepWok_Items](#dbo-2stepwok_items)
3. [dbo.2StepWok_Items_Temp](#dbo-2stepwok_items_temp)
4. [dbo.3StepWok](#dbo-3stepwok)
5. [dbo.3StepWok_Items](#dbo-3stepwok_items)
6. [dbo.3StepWok_Items_Temp](#dbo-3stepwok_items_temp)
7. [dbo.AccountLevel](#dbo-accountlevel)
8. [dbo.AccountNature](#dbo-accountnature)
9. [dbo.AccountOpenBalance](#dbo-accountopenbalance)
10. [dbo.AccountPeriod](#dbo-accountperiod)
11. [dbo.AccountType](#dbo-accounttype)
12. [dbo.Account_Register](#dbo-account_register)
13. [dbo.AdvanceBooking](#dbo-advancebooking)
14. [dbo.AdvanceBookingDetail](#dbo-advancebookingdetail)
15. [dbo.AdvanceCustomer](#dbo-advancecustomer)
16. [dbo.AssignTableToWater](#dbo-assigntabletowater)
17. [dbo.AuditItemPOS](#dbo-audititempos)
18. [dbo.AuditOpenInventoryDepartment](#dbo-auditopeninventorydepartment)
19. [dbo.AuditOpenInventoryStore](#dbo-auditopeninventorystore)
20. [dbo.AvgRateDetail](#dbo-avgratedetail)
21. [dbo.AvgRateMaster](#dbo-avgratemaster)
22. [dbo.Backup](#dbo-backup)
23. [dbo.BankPaymentDetail](#dbo-bankpaymentdetail)
24. [dbo.BankPaymentMaster](#dbo-bankpaymentmaster)
25. [dbo.BankReceiptDetail](#dbo-bankreceiptdetail)
26. [dbo.BankReceiptMaster](#dbo-bankreceiptmaster)
27. [dbo.Bank_name](#dbo-bank_name)
28. [dbo.Branch](#dbo-branch)
29. [dbo.BuffetBooking](#dbo-buffetbooking)
30. [dbo.BuffetCustomer](#dbo-buffetcustomer)
31. [dbo.Butchery](#dbo-butchery)
32. [dbo.ButcheryReturnDetail](#dbo-butcheryreturndetail)
33. [dbo.ButcheryReturnMaster](#dbo-butcheryreturnmaster)
34. [dbo.CLI](#dbo-cli)
35. [dbo.CLI_CTI](#dbo-cli_cti)
36. [dbo.CashDeposit](#dbo-cashdeposit)
37. [dbo.CashDrawer_Logging](#dbo-cashdrawer_logging)
38. [dbo.CashDrop](#dbo-cashdrop)
39. [dbo.CashPaymentDetail](#dbo-cashpaymentdetail)
40. [dbo.CashPaymentMaster](#dbo-cashpaymentmaster)
41. [dbo.CashReceiptDetail](#dbo-cashreceiptdetail)
42. [dbo.CashReceiptMaster](#dbo-cashreceiptmaster)
43. [dbo.CashReceived](#dbo-cashreceived)
44. [dbo.Cashdrawer](#dbo-cashdrawer)
45. [dbo.Category](#dbo-category)
46. [dbo.CategoryMenu](#dbo-categorymenu)
47. [dbo.CategoryPOS](#dbo-categorypos)
48. [dbo.CategoryTiltAssign](#dbo-categorytiltassign)
49. [dbo.ChartOfAccount](#dbo-chartofaccount)
50. [dbo.Color](#dbo-color)
51. [dbo.Company](#dbo-company)
52. [dbo.CompanySetup](#dbo-companysetup)
53. [dbo.Counter_Opening_Expense_Log](#dbo-counter_opening_expense_log)
54. [dbo.Customer](#dbo-customer)
55. [dbo.CustomerLedger](#dbo-customerledger)
56. [dbo.CustomerLedgerAdvBooking](#dbo-customerledgeradvbooking)
57. [dbo.CustomerPOS](#dbo-customerpos)
58. [dbo.CustomerPOS_](#dbo-customerpos_)
59. [dbo.CustomerReciptDetail](#dbo-customerreciptdetail)
60. [dbo.CustomerReciptMaster](#dbo-customerreciptmaster)
61. [dbo.CustomerSaleInvoiceDetail](#dbo-customersaleinvoicedetail)
62. [dbo.CustomerSaleInvoiceMaster](#dbo-customersaleinvoicemaster)
63. [dbo.Deals](#dbo-deals)
64. [dbo.DealsOnSpot](#dbo-dealsonspot)
65. [dbo.DealsOnSpotItems](#dbo-dealsonspotitems)
66. [dbo.Deals_Dpt_Desc_Status](#dbo-deals_dpt_desc_status)
67. [dbo.Deals_Item](#dbo-deals_item)
68. [dbo.DeliveryCharges](#dbo-deliverycharges)
69. [dbo.DeliveryQualityPoints](#dbo-deliveryqualitypoints)
70. [dbo.DeliveryQualityPointsTable](#dbo-deliveryqualitypointstable)
71. [dbo.DemandSheetDetail_Branch](#dbo-demandsheetdetail_branch)
72. [dbo.DemandSheetDetail_Store](#dbo-demandsheetdetail_store)
73. [dbo.DemandSheetMaster_Branch](#dbo-demandsheetmaster_branch)
74. [dbo.DemandSheetMaster_Store](#dbo-demandsheetmaster_store)
75. [dbo.DepartmentPOS](#dbo-departmentpos)
76. [dbo.DeploymentDetail](#dbo-deploymentdetail)
77. [dbo.Dine_In_Order](#dbo-dine_in_order)
78. [dbo.Discount](#dbo-discount)
79. [dbo.DiscountMapping](#dbo-discountmapping)
80. [dbo.DiscountSetting](#dbo-discountsetting)
81. [dbo.Ent](#dbo-ent)
82. [dbo.EntTableLimit](#dbo-enttablelimit)
83. [dbo.Fixed_Comments_Instructions](#dbo-fixed_comments_instructions)
84. [dbo.GL](#dbo-gl)
85. [dbo.GRNDetail](#dbo-grndetail)
86. [dbo.GRNMaster](#dbo-grnmaster)
87. [dbo.Group](#dbo-group)
88. [dbo.InvAdjDetail_Branch](#dbo-invadjdetail_branch)
89. [dbo.InvAdjDetail_Store](#dbo-invadjdetail_store)
90. [dbo.InvAdjMaster_Branch](#dbo-invadjmaster_branch)
91. [dbo.InvAdjMaster_Store](#dbo-invadjmaster_store)
92. [dbo.InvoiceDetail_Company](#dbo-invoicedetail_company)
93. [dbo.InvoiceDetail_CompanyNew](#dbo-invoicedetail_companynew)
94. [dbo.InvoiceMaster_Company](#dbo-invoicemaster_company)
95. [dbo.InvoiceMaster_CompanyNew](#dbo-invoicemaster_companynew)
96. [dbo.IssuanceButcheryDetail](#dbo-issuancebutcherydetail)
97. [dbo.IssuanceButcheryMaster](#dbo-issuancebutcherymaster)
98. [dbo.IssuanceDetail_Store](#dbo-issuancedetail_store)
99. [dbo.IssuanceMaster_Store](#dbo-issuancemaster_store)
100. [dbo.IssuanceReaturnDetail](#dbo-issuancereaturndetail)
101. [dbo.IssuanceReturnMaster](#dbo-issuancereturnmaster)
102. [dbo.Item](#dbo-item)
103. [dbo.ItemComments](#dbo-itemcomments)
104. [dbo.ItemConversion](#dbo-itemconversion)
105. [dbo.ItemGroupDetail](#dbo-itemgroupdetail)
106. [dbo.ItemGroupMaster](#dbo-itemgroupmaster)
107. [dbo.ItemOrderConversion](#dbo-itemorderconversion)
108. [dbo.ItemPOS](#dbo-itempos)
109. [dbo.ItemPOS_Assign](#dbo-itempos_assign)
110. [dbo.ItemPOS_Extra](#dbo-itempos_extra)
111. [dbo.ItemPOS_finishPro](#dbo-itempos_finishpro)
112. [dbo.ItemParLevel](#dbo-itemparlevel)
113. [dbo.ItemSubGroupMaster](#dbo-itemsubgroupmaster)
114. [dbo.ItemUnit](#dbo-itemunit)
115. [dbo.Item_Delete](#dbo-item_delete)
116. [dbo.Item_Less](#dbo-item_less)
117. [dbo.Item_Transfer_Log](#dbo-item_transfer_log)
118. [dbo.Item_void](#dbo-item_void)
119. [dbo.JVDetail](#dbo-jvdetail)
120. [dbo.JVMaster](#dbo-jvmaster)
121. [dbo.KDS_Department_IP_Setting](#dbo-kds_department_ip_setting)
122. [dbo.KOTPrint](#dbo-kotprint)
123. [dbo.LoginStatus](#dbo-loginstatus)
124. [dbo.MenuCategory](#dbo-menucategory)
125. [dbo.MenuDetail](#dbo-menudetail)
126. [dbo.MenuItem](#dbo-menuitem)
127. [dbo.OpenInventoryDetail](#dbo-openinventorydetail)
128. [dbo.OpenInventoryDetail_Department](#dbo-openinventorydetail_department)
129. [dbo.OpenInventoryMaster](#dbo-openinventorymaster)
130. [dbo.OpenInventoryMaster_Department](#dbo-openinventorymaster_department)
131. [dbo.OrderKot](#dbo-orderkot)
132. [dbo.OrderMaster](#dbo-ordermaster)
133. [dbo.OrderOccassionDetail](#dbo-orderoccassiondetail)
134. [dbo.OrderServedTime](#dbo-orderservedtime)
135. [dbo.OrderStatusTime](#dbo-orderstatustime)
136. [dbo.Order_Detail](#dbo-order_detail)
137. [dbo.Order_Detail_ExtraItem](#dbo-order_detail_extraitem)
138. [dbo.Order_Detail_ExtraItem_Temp](#dbo-order_detail_extraitem_temp)
139. [dbo.Order_Payment](#dbo-order_payment)
140. [dbo.POSSaleAccount](#dbo-possaleaccount)
141. [dbo.POSSaleReturnDetail](#dbo-possalereturndetail)
142. [dbo.POSSaleReturnMaster](#dbo-possalereturnmaster)
143. [dbo.POSTransectionSetting](#dbo-postransectionsetting)
144. [dbo.POS_Default_Settings](#dbo-pos_default_settings)
145. [dbo.POS_Expense](#dbo-pos_expense)
146. [dbo.POS_Expense_Account](#dbo-pos_expense_account)
147. [dbo.POsExpenseSetting](#dbo-posexpensesetting)
148. [dbo.PaymentVoucher](#dbo-paymentvoucher)
149. [dbo.PhysicalStockDetail_Branch](#dbo-physicalstockdetail_branch)
150. [dbo.PhysicalStockDetail_Store](#dbo-physicalstockdetail_store)
151. [dbo.PhysicalStockMaster_Branch](#dbo-physicalstockmaster_branch)
152. [dbo.PhysicalStockMaster_Store](#dbo-physicalstockmaster_store)
153. [dbo.PosSale](#dbo-possale)
154. [dbo.Printer_Setup](#dbo-printer_setup)
155. [dbo.ProductSaleDetail](#dbo-productsaledetail)
156. [dbo.ProductSaleMaster](#dbo-productsalemaster)
157. [dbo.ProductionDetail](#dbo-productiondetail)
158. [dbo.ProductionDetailDepartment](#dbo-productiondetaildepartment)
159. [dbo.ProductionMaster](#dbo-productionmaster)
160. [dbo.ProductionMasterDepartment](#dbo-productionmasterdepartment)
161. [dbo.ProfitLossSettings](#dbo-profitlosssettings)
162. [dbo.PurchaseOrderDetail_Store](#dbo-purchaseorderdetail_store)
163. [dbo.PurchaseOrderMaster_Store](#dbo-purchaseordermaster_store)
164. [dbo.PurchaseReturnDetail](#dbo-purchasereturndetail)
165. [dbo.PurchaseReturnDetailNew](#dbo-purchasereturndetailnew)
166. [dbo.PurchaseReturnMaster](#dbo-purchasereturnmaster)
167. [dbo.PurchaseReturnMasterNew](#dbo-purchasereturnmasternew)
168. [dbo.Reasons](#dbo-reasons)
169. [dbo.ReceiptVoucher](#dbo-receiptvoucher)
170. [dbo.RecipeDetail](#dbo-recipedetail)
171. [dbo.RecipeMaster](#dbo-recipemaster)
172. [dbo.Reports_Settings](#dbo-reports_settings)
173. [dbo.Rider](#dbo-rider)
174. [dbo.RiderCashFloat](#dbo-ridercashfloat)
175. [dbo.SMSLog](#dbo-smslog)
176. [dbo.SMS_Setup](#dbo-sms_setup)
177. [dbo.SaleInvoiceDetail](#dbo-saleinvoicedetail)
178. [dbo.SaleInvoiceMaster](#dbo-saleinvoicemaster)
179. [dbo.ServerTiltAssign](#dbo-servertiltassign)
180. [dbo.ServiceCharges](#dbo-servicecharges)
181. [dbo.SheeshaTime](#dbo-sheeshatime)
182. [dbo.ShiftAmount](#dbo-shiftamount)
183. [dbo.ShiftClosingTime](#dbo-shiftclosingtime)
184. [dbo.Shift_Account_Detail](#dbo-shift_account_detail)
185. [dbo.Shift_Opening](#dbo-shift_opening)
186. [dbo.Shift_User](#dbo-shift_user)
187. [dbo.Shifts](#dbo-shifts)
188. [dbo.SmsSetting](#dbo-smssetting)
189. [dbo.Step_Deal](#dbo-step_deal)
190. [dbo.Step_Deal_Items](#dbo-step_deal_items)
191. [dbo.Step_Deal_Items_Temp](#dbo-step_deal_items_temp)
192. [dbo.Store](#dbo-store)
193. [dbo.SubCategory](#dbo-subcategory)
194. [dbo.SubRecipeDetail](#dbo-subrecipedetail)
195. [dbo.SubRecipeMaster](#dbo-subrecipemaster)
196. [dbo.SupplierLedger](#dbo-supplierledger)
197. [dbo.Table1](#dbo-table1)
198. [dbo.Table2](#dbo-table2)
199. [dbo.Table3](#dbo-table3)
200. [dbo.Table4](#dbo-table4)
201. [dbo.TableMerge](#dbo-tablemerge)
202. [dbo.TableTiltAssign](#dbo-tabletiltassign)
203. [dbo.Tables](#dbo-tables)
204. [dbo.TakeAway_Customer](#dbo-takeaway_customer)
205. [dbo.Tax](#dbo-tax)
206. [dbo.TaxDetail](#dbo-taxdetail)
207. [dbo.TaxInventory](#dbo-taxinventory)
208. [dbo.Tax_](#dbo-tax_)
209. [dbo.TempDealsOnSpotItems](#dbo-tempdealsonspotitems)
210. [dbo.Theme](#dbo-theme)
211. [dbo.Tilt](#dbo-tilt)
212. [dbo.TokenNo](#dbo-tokenno)
213. [dbo.Transfer](#dbo-transfer)
214. [dbo.TransferInDetail](#dbo-transferindetail)
215. [dbo.TransferInMaster](#dbo-transferinmaster)
216. [dbo.TransferOutDetail](#dbo-transferoutdetail)
217. [dbo.TransferOutMaster](#dbo-transferoutmaster)
218. [dbo.Unit](#dbo-unit)
219. [dbo.UnitConversion](#dbo-unitconversion)
220. [dbo.User](#dbo-user)
221. [dbo.UserTiltAssign](#dbo-usertiltassign)
222. [dbo.UserType](#dbo-usertype)
223. [dbo.UserTypeAccess](#dbo-usertypeaccess)
224. [dbo.Vendor](#dbo-vendor)
225. [dbo.Voucher](#dbo-voucher)
226. [dbo.VoucherDetail](#dbo-voucherdetail)
227. [dbo.Waiter](#dbo-waiter)
228. [dbo.WareHouse_Branch](#dbo-warehouse_branch)
229. [dbo.WareHouse_Store](#dbo-warehouse_store)
230. [dbo.currency_convertor](#dbo-currency_convertor)
231. [dbo.customer_group](#dbo-customer_group)
232. [dbo.device_tilt_assign](#dbo-device_tilt_assign)
233. [dbo.item_stock_detail](#dbo-item_stock_detail)
234. [dbo.item_stock_master](#dbo-item_stock_master)
235. [dbo.meal_serving_time](#dbo-meal_serving_time)
236. [dbo.sysdiagrams](#dbo-sysdiagrams)
237. [dbo.tblLuckyDraw](#dbo-tblluckydraw)
238. [dbo.tbl_user](#dbo-tbl_user)
239. [dbo.tempDine_In_Order](#dbo-tempdine_in_order)
240. [dbo.tempKeys](#dbo-tempkeys)

## Table Details

### dbo.2StepWok

**Rows:** 7  |  
**Columns:** 5  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| Step_id | int(10,0) | No | No |  |
| Step | nchar(10) | No | No |  |
| Category_id | int(10,0) | No | No |  |
| Item_Id | int(10,0) | No | No |  |

---

### dbo.2StepWok_Items

**Rows:** 0  |  
**Columns:** 10  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| Order_Key | nvarchar(50) | No | No |  |
| OrderDetail_Id | int(10,0) | No | No |  |
| Step_id | int(10,0) | No | No |  |
| Step | nchar(10) | No | No |  |
| Category_id | int(10,0) | No | No |  |
| Category | nvarchar(50) | No | No |  |
| Item_Id | int(10,0) | No | No |  |
| Item | nvarchar(50) | No | No |  |
| ItemQty | decimal(18,2) | No | No |  |

---

### dbo.2StepWok_Items_Temp

**Rows:** 0  |  
**Columns:** 10  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| Order_Key | nvarchar(50) | No | No |  |
| OrderDetail_Id | int(10,0) | No | No |  |
| Step_id | int(10,0) | No | No |  |
| Step | nchar(10) | No | No |  |
| Category_id | int(10,0) | No | No |  |
| Category | nvarchar(50) | No | No |  |
| Item_Id | int(10,0) | No | No |  |
| Item | nvarchar(50) | No | No |  |
| ItemQty | decimal(18,2) | No | No |  |

---

### dbo.3StepWok

**Rows:** 13  |  
**Columns:** 5  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| Step_id | int(10,0) | No | No |  |
| Step | nchar(10) | No | No |  |
| Category_id | int(10,0) | No | No |  |
| Item_Id | int(10,0) | No | No |  |

---

### dbo.3StepWok_Items

**Rows:** 0  |  
**Columns:** 10  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| Order_Key | nvarchar(50) | No | No |  |
| OrderDetail_Id | int(10,0) | No | No |  |
| Step_id | int(10,0) | No | No |  |
| Step | nchar(10) | No | No |  |
| Category_id | int(10,0) | No | No |  |
| Category | nvarchar(50) | No | No |  |
| Item_Id | int(10,0) | No | No |  |
| Item | nvarchar(50) | No | No |  |
| ItemQty | decimal(18,2) | No | No |  |

---

### dbo.3StepWok_Items_Temp

**Rows:** 0  |  
**Columns:** 10  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| Order_Key | nvarchar(50) | No | No |  |
| OrderDetail_Id | int(10,0) | No | No |  |
| Step_id | int(10,0) | No | No |  |
| Step | nchar(10) | No | No |  |
| Category_id | int(10,0) | No | No |  |
| Category | nvarchar(50) | No | No |  |
| Item_Id | int(10,0) | No | No |  |
| Item | nvarchar(50) | No | No |  |
| ItemQty | decimal(18,2) | No | No |  |

---

### dbo.AccountLevel

**Rows:** 3  |  
**Columns:** 4  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| LevelId | int(10,0) | No | Yes | (PK) |
| Level | int(10,0) | No | No |  |
| AccNoDigits | int(10,0) | Yes | No |  |
| COId | int(10,0) | Yes | No |  |

#### Primary Key
`LevelId`

---

### dbo.AccountNature

**Rows:** 5  |  
**Columns:** 3  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| Account | varchar(40) | Yes | No |  |
| AccNo | int(10,0) | Yes | No |  |

---

### dbo.AccountOpenBalance

**Rows:** 0  |  
**Columns:** 4  |  
**Foreign Keys:** 1

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| Amount | decimal(18,2) | Yes | No |  |
| CAId | int(10,0) | Yes | No |  |
| APId | int(10,0) | Yes | No |  |

#### Foreign Keys

| Constraint | Local Column | Referenced Table | Referenced Column |
|------------|--------------|------------------|-------------------|
| ChartOfAccount_AccountOpenBalance | CAId | dbo.ChartOfAccount | CAId |

---

### dbo.AccountPeriod

**Rows:** 2  |  
**Columns:** 5  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| ApId | int(10,0) | No | Yes | (PK) |
| From | datetime | Yes | No |  |
| To | datetime | Yes | No |  |
| COId | int(10,0) | Yes | No |  |
| IsActive | bit | Yes | No |  |

#### Primary Key
`ApId`

---

### dbo.AccountType

**Rows:** 3  |  
**Columns:** 2  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes | (PK) |
| Type | varchar(40) | Yes | No |  |

#### Primary Key
`id`

---

### dbo.Account_Register

**Rows:** 4  |  
**Columns:** 6  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| Date | datetime | No | No |  |
| Type | nvarchar(1) | No | No |  |
| Debit | decimal(18,2) | Yes | No |  |
| Credit | decimal(18,2) | Yes | No |  |
| Description | nvarchar(-1) | No | No |  |

---

### dbo.AdvanceBooking

**Rows:** 0  |  
**Columns:** 36  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| BookingCode | nvarchar(50) | Yes | No |  |
| CustomerCode | nvarchar(50) | Yes | No |  |
| DateOfReservation | datetime | Yes | No |  |
| TimeOfReservtion | datetime | Yes | No |  |
| NoOfPersons | int(10,0) | Yes | No |  |
| SittingLocation | nvarchar(100) | Yes | No |  |
| AdvancePayment | decimal(18,2) | Yes | No |  |
| Comments | nvarchar(-1) | Yes | No |  |
| Smooking-NonSmooking | nvarchar(50) | Yes | No |  |
| Event | nvarchar(50) | Yes | No |  |
| OrderDate | datetime | Yes | No |  |
| OrderTime | datetime | Yes | No |  |
| Order_Key | int(10,0) | No | No |  |
| GrossAmount | decimal(18,2) | Yes | No |  |
| Tax | decimal(18,2) | Yes | No |  |
| TaxType | nvarchar(50) | Yes | No |  |
| Discount | decimal(18,2) | Yes | No |  |
| NetAmount | decimal(18,2) | Yes | No |  |
| OrderStatus | nvarchar(50) | Yes | No |  |
| Tiltid | int(10,0) | No | No |  |
| CounterId | int(10,0) | No | No |  |
| ShiftNo | nvarchar(50) | Yes | No |  |
| LunchOrDinner | nvarchar(50) | Yes | No |  |
| is_upload | bit | No | No |  |
| is_update | bit | No | No |  |
| Branch_id | int(10,0) | Yes | No |  |
| Company_id | int(10,0) | Yes | No |  |
| branch | nvarchar(100) | Yes | No |  |
| status | nvarchar(100) | Yes | No |  |
| branch_code | nvarchar(50) | Yes | No |  |
| agent | nvarchar(50) | Yes | No |  |
| is_transfer | bit | Yes | No |  |
| Item_Total | decimal(18,2) | No | No |  |
| Item_Disocunt | decimal(18,2) | No | No |  |
| Item_Net | decimal(18,2) | No | No |  |

---

### dbo.AdvanceBookingDetail

**Rows:** 0  |  
**Columns:** 7  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| AdvanceBookingId | int(10,0) | No | No |  |
| ItemId | int(10,0) | No | No |  |
| Item | nvarchar(50) | No | No |  |
| Qty | decimal(18,2) | Yes | No |  |
| Rate | decimal(18,2) | Yes | No |  |
| Amount | decimal(18,2) | Yes | No |  |

---

### dbo.AdvanceCustomer

**Rows:** 2  |  
**Columns:** 10  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| CustomerId | int(10,0) | No | Yes |  |
| Code | nvarchar(50) | Yes | No |  |
| Customer | nvarchar(50) | Yes | No |  |
| Address | nvarchar(-1) | Yes | No |  |
| PhoneNo | nvarchar(50) | Yes | No |  |
| MobileNo | nvarchar(50) | Yes | No |  |
| Email | nvarchar(50) | Yes | No |  |
| CNIC | nvarchar(50) | Yes | No |  |
| is_upload | bit | No | No |  |
| is_update | bit | No | No |  |

---

### dbo.AssignTableToWater

**Rows:** 0  |  
**Columns:** 4  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| WaiterId | int(10,0) | No | No |  |
| TableId | int(10,0) | Yes | No |  |
| Tiltid | int(10,0) | No | No |  |

---

### dbo.AuditItemPOS

**Rows:** 8,824  |  
**Columns:** 13  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| category_name | nvarchar(50) | Yes | No |  |
| item_name | nvarchar(250) | Yes | No |  |
| cost_price | float(53,None) | Yes | No |  |
| sale_price | float(53,None) | Yes | No |  |
| codes | nvarchar(250) | Yes | No |  |
| status | bit | No | No |  |
| tiltId | int(10,0) | Yes | No |  |
| IsComment | bit | Yes | No |  |
| Date | datetime | Yes | No |  |
| User | nvarchar(100) | Yes | No |  |
| Workstation | nvarchar(50) | Yes | No |  |
| datetime | datetime | Yes | No |  |

#### Sample Data (First 3 rows)

|   id | category_name   | item_name   |   cost_price |   sale_price | codes   | status   | tiltId   | IsComment   | Date                | User   | Workstation   | datetime   |
|-----:|:----------------|:------------|-------------:|-------------:|:--------|:---------|:---------|:------------|:--------------------|:-------|:--------------|:-----------|
|    1 | Services        | Services    |            0 |            0 | None    | True     | None     | False       | 2014-06-03 00:00:00 | ammar  | None          | None       |
|    2 | Services        | Sofa Set    |            0 |         5000 | None    | True     | None     | False       | 2014-06-03 00:00:00 | ammar  | None          | None       |
|    3 | Services        | Blanket     |            0 |         5000 | None    | True     | None     | False       | 2014-06-03 00:00:00 | ammar  | None          | None       |

---

### dbo.AuditOpenInventoryDepartment

**Rows:** 0  |  
**Columns:** 8  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| Date | datetime | Yes | No |  |
| ItemId | int(10,0) | Yes | No |  |
| Qty | decimal(18,2) | Yes | No |  |
| Rate | decimal(18,2) | Yes | No |  |
| Amount | decimal(18,2) | Yes | No |  |
| Unitid | int(10,0) | Yes | No |  |
| Did | int(10,0) | Yes | No |  |

---

### dbo.AuditOpenInventoryStore

**Rows:** 368  |  
**Columns:** 7  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| Date | datetime | Yes | No |  |
| ItemId | int(10,0) | Yes | No |  |
| Qty | decimal(18,2) | Yes | No |  |
| Rate | decimal(18,2) | Yes | No |  |
| Amount | decimal(18,2) | Yes | No |  |
| Unitid | int(10,0) | Yes | No |  |

---

### dbo.AvgRateDetail

**Rows:** 0  |  
**Columns:** 7  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| Id | int(10,0) | No | Yes |  |
| ItemId | int(10,0) | No | No |  |
| AvgRateMonth | nvarchar(50) | No | No |  |
| AvgRate | decimal(18,2) | Yes | No |  |
| DateFrom | smalldatetime | Yes | No |  |
| DateTo | smalldatetime | Yes | No |  |
| AmId | int(10,0) | Yes | No |  |

---

### dbo.AvgRateMaster

**Rows:** 0  |  
**Columns:** 3  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| AMID | int(10,0) | No | Yes |  |
| AvgRateMonth | nvarchar(50) | No | No | (PK) |
| CalcDate | smalldatetime | No | No |  |

#### Primary Key
`AvgRateMonth`

---

### dbo.Backup

**Rows:** 0  |  
**Columns:** 2  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| Id | int(10,0) | No | Yes |  |
| Path | nvarchar(1000) | Yes | No |  |

---

### dbo.BankPaymentDetail

**Rows:** 0  |  
**Columns:** 6  |  
**Foreign Keys:** 2

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| Amount | decimal(18,2) | Yes | No |  |
| CAId | int(10,0) | Yes | No |  |
| Desc | nvarchar(-1) | Yes | No |  |
| BPId | int(10,0) | Yes | No |  |
| InvoiceId | int(10,0) | Yes | No |  |

#### Foreign Keys

| Constraint | Local Column | Referenced Table | Referenced Column |
|------------|--------------|------------------|-------------------|
| BankPaymentMaster_BankPaymentDetail | BPId | dbo.BankPaymentMaster | BPId |
| FK_BankPaymentDetail_ChartOfAccount | CAId | dbo.ChartOfAccount | CAId |

---

### dbo.BankPaymentMaster

**Rows:** 0  |  
**Columns:** 14  |  
**Foreign Keys:** 1

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| BPId | int(10,0) | No | Yes | (PK) |
| VN | nvarchar(40) | Yes | No |  |
| PVId | int(10,0) | Yes | No |  |
| Date | datetime | Yes | No |  |
| TotalAmount | decimal(18,2) | Yes | No |  |
| ChequeNo | nvarchar(40) | Yes | No |  |
| ChequeDate | datetime | Yes | No |  |
| CAId | int(10,0) | Yes | No |  |
| PaidTo | nvarchar(-1) | Yes | No |  |
| For | nvarchar(-1) | Yes | No |  |
| COId | int(10,0) | Yes | No |  |
| wht_caid | int(10,0) | Yes | No |  |
| Tax | decimal(18,2) | Yes | No |  |
| TaxAmount | decimal(18,2) | Yes | No |  |

#### Primary Key
`BPId`

#### Foreign Keys

| Constraint | Local Column | Referenced Table | Referenced Column |
|------------|--------------|------------------|-------------------|
| FK_BankPaymentMaster_PaymentVoucher | PVId | dbo.PaymentVoucher | PVId |

---

### dbo.BankReceiptDetail

**Rows:** 0  |  
**Columns:** 6  |  
**Foreign Keys:** 2

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| Amount | decimal(18,2) | Yes | No |  |
| CAId | int(10,0) | Yes | No |  |
| Desc | nvarchar(-1) | Yes | No |  |
| BRId | int(10,0) | Yes | No |  |
| SaleId | int(10,0) | Yes | No |  |

#### Foreign Keys

| Constraint | Local Column | Referenced Table | Referenced Column |
|------------|--------------|------------------|-------------------|
| BankReceiptMaster_BankReceiptDetail | BRId | dbo.BankReceiptMaster | BRId |
| FK_BankReceiptDetail_ChartOfAccount | CAId | dbo.ChartOfAccount | CAId |

---

### dbo.BankReceiptMaster

**Rows:** 0  |  
**Columns:** 11  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| BRId | int(10,0) | No | Yes | (PK) |
| VN | nvarchar(40) | Yes | No |  |
| RVId | int(10,0) | Yes | No |  |
| Date | datetime | Yes | No |  |
| TotalAmount | decimal(18,2) | Yes | No |  |
| ChequeNo | nvarchar(40) | Yes | No |  |
| ChequeDate | datetime | Yes | No |  |
| CAId | int(10,0) | Yes | No |  |
| ReceiveFrom | nvarchar(-1) | Yes | No |  |
| For | nvarchar(40) | Yes | No |  |
| COId | int(10,0) | Yes | No |  |

#### Primary Key
`BRId`

---

### dbo.Bank_name

**Rows:** 2  |  
**Columns:** 2  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| Bank | nvarchar(-1) | No | No |  |

---

### dbo.Branch

**Rows:** 7  |  
**Columns:** 15  |  
**Foreign Keys:** 1

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| BRId | int(10,0) | No | No | (PK) |
| COId | int(10,0) | Yes | No |  |
| Branch | nvarchar(50) | Yes | No |  |
| IsSelected | bit | Yes | No |  |
| IsPosSelected | bit | Yes | No |  |
| Address | nvarchar(-1) | Yes | No |  |
| Email | nvarchar(-1) | Yes | No |  |
| Fax | nvarchar(-1) | Yes | No |  |
| Phone1 | nvarchar(-1) | Yes | No |  |
| Phone2 | nvarchar(-1) | Yes | No |  |
| internet_status | nvarchar(100) | Yes | No |  |
| last_internet_update | nvarchar(100) | Yes | No |  |
| branch_ip | nvarchar(50) | Yes | No |  |
| is_web | bit | No | No |  |
| branch_code | nvarchar(50) | Yes | No |  |

#### Primary Key
`BRId`

#### Foreign Keys

| Constraint | Local Column | Referenced Table | Referenced Column |
|------------|--------------|------------------|-------------------|
| FK_Branch_Company | COId | dbo.Company | COId |

---

### dbo.BuffetBooking

**Rows:** 0  |  
**Columns:** 27  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| BookingCode | nvarchar(50) | Yes | No |  |
| CustomerCode | nvarchar(50) | Yes | No |  |
| DateOfReservation | datetime | Yes | No |  |
| TimeOfReservtion | datetime | Yes | No |  |
| NoOfPersons | nvarchar(50) | Yes | No |  |
| SittingLocation | nvarchar(100) | Yes | No |  |
| AdvancePayment | decimal(18,2) | Yes | No |  |
| Comments | nvarchar(-1) | Yes | No |  |
| Smooking-NonSmooking | nvarchar(50) | Yes | No |  |
| Event | nvarchar(50) | Yes | No |  |
| OrderDate | datetime | Yes | No |  |
| OrderTime | datetime | Yes | No |  |
| Order_Key | nvarchar(50) | Yes | No |  |
| GrossAmount | decimal(18,2) | Yes | No |  |
| Tax | decimal(18,2) | Yes | No |  |
| TaxType | nvarchar(50) | Yes | No |  |
| Discount | decimal(18,2) | Yes | No |  |
| NetAmount | decimal(18,2) | Yes | No |  |
| IsDelete | bit | Yes | No |  |
| service_status | nvarchar(50) | Yes | No |  |
| OrderNo | int(10,0) | Yes | No |  |
| ServiceChaerges | decimal(18,0) | No | No |  |
| Tip | decimal(18,0) | No | No |  |
| ShiftNo | nvarchar(50) | Yes | No |  |
| TiltId | int(10,0) | Yes | No |  |
| CounterId | int(10,0) | Yes | No |  |

---

### dbo.BuffetCustomer

**Rows:** 0  |  
**Columns:** 8  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| CustomerId | int(10,0) | No | Yes |  |
| Code | nvarchar(50) | Yes | No |  |
| Customer | nvarchar(50) | Yes | No |  |
| Address | nvarchar(-1) | Yes | No |  |
| PhoneNo | nvarchar(50) | Yes | No |  |
| MobileNo | nvarchar(50) | Yes | No |  |
| Email | nvarchar(50) | Yes | No |  |
| CNIC | nvarchar(50) | Yes | No |  |

---

### dbo.Butchery

**Rows:** 2  |  
**Columns:** 2  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| Id | int(10,0) | No | Yes |  |
| ItemType | nvarchar(50) | Yes | No |  |

---

### dbo.ButcheryReturnDetail

**Rows:** 0  |  
**Columns:** 9  |  
**Foreign Keys:** 1

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| Id | int(10,0) | No | Yes |  |
| BUTRId | int(10,0) | Yes | No |  |
| ItemId | int(10,0) | Yes | No |  |
| Unit | int(10,0) | Yes | No |  |
| Rate | decimal(18,2) | Yes | No |  |
| QTY | decimal(18,2) | Yes | No |  |
| WesQty | decimal(18,2) | Yes | No |  |
| Amount | decimal(18,2) | Yes | No |  |
| RawItemId | int(10,0) | Yes | No |  |

#### Foreign Keys

| Constraint | Local Column | Referenced Table | Referenced Column |
|------------|--------------|------------------|-------------------|
| FK_ButcheryReturnDetail_ButcheryReturnMaster | BUTRId | dbo.ButcheryReturnMaster | BUTRId |

---

### dbo.ButcheryReturnMaster

**Rows:** 0  |  
**Columns:** 6  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| BUTRId | int(10,0) | No | Yes | (PK) |
| Date | datetime | Yes | No |  |
| SId | int(10,0) | Yes | No |  |
| BUTId | int(10,0) | Yes | No |  |
| UserId | int(10,0) | Yes | No |  |
| BURNo | nvarchar(50) | Yes | No |  |

#### Primary Key
`BUTRId`

---

### dbo.CLI

**Rows:** 0  |  
**Columns:** 4  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| PhoneNumber | nvarchar(50) | Yes | No |  |
| Status | int(10,0) | Yes | No |  |
| systemId | nvarchar(50) | No | No |  |

---

### dbo.CLI_CTI

**Rows:** 0  |  
**Columns:** 2  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| ID | int(10,0) | No | Yes | (PK) |
| FilePath | nvarchar(100) | Yes | No |  |

#### Primary Key
`ID`

---

### dbo.CashDeposit

**Rows:** 0  |  
**Columns:** 13  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| Date | datetime | Yes | No |  |
| Z_Number | nvarchar(50) | Yes | No |  |
| Tiltid | int(10,0) | Yes | No |  |
| VoucherNo | nvarchar(50) | Yes | No |  |
| Amount | decimal(18,2) | Yes | No |  |
| CareOf | nvarchar(100) | Yes | No |  |
| Description | nvarchar(-1) | Yes | No |  |
| CounterId | int(10,0) | Yes | No |  |
| User | nvarchar(50) | Yes | No |  |
| Time | nvarchar(50) | Yes | No |  |
| is_upload | bit | No | No |  |
| is_update | bit | No | No |  |

---

### dbo.CashDrawer_Logging

**Rows:** 2  |  
**Columns:** 7  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| User | nvarchar(50) | No | No |  |
| z_number | nvarchar(50) | No | No |  |
| TiltId | int(10,0) | No | No |  |
| CounterId | int(10,0) | No | No |  |
| Date | datetime | No | No |  |
| Time | nvarchar(50) | No | No |  |

---

### dbo.CashDrop

**Rows:** 0  |  
**Columns:** 13  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| Date | datetime | Yes | No |  |
| Z_Number | nvarchar(50) | Yes | No |  |
| Tiltid | int(10,0) | Yes | No |  |
| VoucherNo | nvarchar(50) | Yes | No |  |
| Amount | decimal(18,2) | Yes | No |  |
| CareOf | nvarchar(100) | Yes | No |  |
| Description | nvarchar(-1) | Yes | No |  |
| CounterId | int(10,0) | Yes | No |  |
| User | nvarchar(50) | Yes | No |  |
| Time | nvarchar(50) | Yes | No |  |
| is_upload | bit | No | No |  |
| is_update | bit | No | No |  |

---

### dbo.CashPaymentDetail

**Rows:** 0  |  
**Columns:** 6  |  
**Foreign Keys:** 2

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| Amount | decimal(18,2) | Yes | No |  |
| CAId | int(10,0) | Yes | No |  |
| Desc | nvarchar(-1) | Yes | No |  |
| CPId | int(10,0) | Yes | No |  |
| InvoiceId | int(10,0) | Yes | No |  |

#### Foreign Keys

| Constraint | Local Column | Referenced Table | Referenced Column |
|------------|--------------|------------------|-------------------|
| FK_CashPaymentDetail_ChartOfAccount | CAId | dbo.ChartOfAccount | CAId |
| CashPaymentMaster_CashPaymentDetail | CPId | dbo.CashPaymentMaster | CPId |

---

### dbo.CashPaymentMaster

**Rows:** 0  |  
**Columns:** 12  |  
**Foreign Keys:** 1

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| CPId | int(10,0) | No | Yes | (PK) |
| VN | nvarchar(40) | Yes | No |  |
| PVId | int(10,0) | Yes | No |  |
| Date | datetime | Yes | No |  |
| TotalAmount | decimal(18,2) | Yes | No |  |
| PaidTo | nvarchar(40) | Yes | No |  |
| For | nvarchar(40) | Yes | No |  |
| CAId | int(10,0) | Yes | No |  |
| COId | int(10,0) | Yes | No |  |
| wht_caid | int(10,0) | Yes | No |  |
| Tax | decimal(18,2) | Yes | No |  |
| TaxAmount | decimal(18,2) | Yes | No |  |

#### Primary Key
`CPId`

#### Foreign Keys

| Constraint | Local Column | Referenced Table | Referenced Column |
|------------|--------------|------------------|-------------------|
| FK_CashPaymentMaster_PaymentVoucher | PVId | dbo.PaymentVoucher | PVId |

---

### dbo.CashReceiptDetail

**Rows:** 0  |  
**Columns:** 6  |  
**Foreign Keys:** 2

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| Amount | decimal(18,0) | Yes | No |  |
| CAId | int(10,0) | Yes | No |  |
| Desc | nvarchar(-1) | Yes | No |  |
| CRId | int(10,0) | Yes | No |  |
| SaleId | int(10,0) | Yes | No |  |

#### Foreign Keys

| Constraint | Local Column | Referenced Table | Referenced Column |
|------------|--------------|------------------|-------------------|
| CashReceiptMaster_CashReceiptDetail | CRId | dbo.CashReceiptMaster | CRId |
| FK_CashReceiptDetail_ChartOfAccount | CAId | dbo.ChartOfAccount | CAId |

---

### dbo.CashReceiptMaster

**Rows:** 0  |  
**Columns:** 9  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| CRId | int(10,0) | No | Yes | (PK) |
| VN | nvarchar(40) | Yes | No |  |
| RVId | int(10,0) | Yes | No |  |
| Date | datetime | Yes | No |  |
| TotalAmount | decimal(18,0) | Yes | No |  |
| ReceiveFrom | nvarchar(-1) | Yes | No |  |
| For | nvarchar(40) | Yes | No |  |
| CAId | int(10,0) | Yes | No |  |
| COId | int(10,0) | Yes | No |  |

#### Primary Key
`CRId`

---

### dbo.CashReceived

**Rows:** 0  |  
**Columns:** 11  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| Date | datetime | Yes | No |  |
| Z_Number | nvarchar(50) | Yes | No |  |
| Tiltid | int(10,0) | Yes | No |  |
| VoucherNo | nvarchar(50) | Yes | No |  |
| Amount | decimal(18,2) | Yes | No |  |
| CareOf | nvarchar(100) | Yes | No |  |
| Description | nvarchar(-1) | Yes | No |  |
| CounterId | int(10,0) | Yes | No |  |
| User | nvarchar(50) | Yes | No |  |
| Time | nvarchar(50) | Yes | No |  |

---

### dbo.Cashdrawer

**Rows:** 1  |  
**Columns:** 5  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| ComPort | nvarchar(50) | Yes | No |  |
| Tiltid | int(10,0) | Yes | No |  |
| GsmComPort | nvarchar(50) | Yes | No |  |
| DisplayComPort | nvarchar(50) | Yes | No |  |

---

### dbo.Category

**Rows:** 0  |  
**Columns:** 3  |  
**Foreign Keys:** 1

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| CId | int(10,0) | No | Yes | (PK) |
| Category | nvarchar(50) | Yes | No |  |
| COID | int(10,0) | Yes | No |  |

#### Primary Key
`CId`

#### Foreign Keys

| Constraint | Local Column | Referenced Table | Referenced Column |
|------------|--------------|------------------|-------------------|
| FK_Category_Company | COID | dbo.Company | COId |

---

### dbo.CategoryMenu

**Rows:** 1  |  
**Columns:** 2  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| Menu | bit | Yes | No |  |

---

### dbo.CategoryPOS

**Rows:** 130  |  
**Columns:** 16  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| category_name | nvarchar(50) | Yes | No |  |
| department | nvarchar(50) | Yes | No |  |
| TiltId | int(10,0) | Yes | No |  |
| Color | nvarchar(50) | Yes | No |  |
| IsComment | bit | Yes | No |  |
| orderid | int(10,0) | No | No |  |
| GetType | nvarchar(50) | Yes | No |  |
| Is_Upload | bit | No | No |  |
| Is_Update | bit | No | No |  |
| Did | int(10,0) | No | No |  |
| is_Discount | bit | No | No |  |
| is_delete | bit | Yes | No |  |
| BRid | int(10,0) | Yes | No |  |
| is_tax_apply | bit | Yes | No |  |
| is_hnh | bit | Yes | No |  |

---

### dbo.CategoryTiltAssign

**Rows:** 0  |  
**Columns:** 4  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| CategoryId | int(10,0) | Yes | No |  |
| Tiltid | int(10,0) | Yes | No |  |
| OrderType | nvarchar(50) | Yes | No |  |

---

### dbo.ChartOfAccount

**Rows:** 0  |  
**Columns:** 10  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| CAId | int(10,0) | No | Yes | (PK) |
| AccNo | int(10,0) | Yes | No |  |
| AccName | nvarchar(-1) | Yes | No |  |
| AccNature | nvarchar(-1) | Yes | No |  |
| Type | nvarchar(40) | Yes | No |  |
| Level | int(10,0) | Yes | No |  |
| ParentId | int(10,0) | Yes | No |  |
| Desc | varchar(40) | Yes | No |  |
| COId | int(10,0) | Yes | No |  |
| Op | decimal(18,2) | Yes | No |  |

#### Primary Key
`CAId`

---

### dbo.Color

**Rows:** 174  |  
**Columns:** 2  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| Color | nvarchar(50) | Yes | No |  |

---

### dbo.Company

**Rows:** 1  |  
**Columns:** 11  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| COId | int(10,0) | No | No | (PK) |
| Company | nvarchar(50) | Yes | No |  |
| IsSelected | bit | Yes | No |  |
| Address | nvarchar(50) | Yes | No |  |
| ContactNo | nvarchar(50) | Yes | No |  |
| Fax | nvarchar(50) | Yes | No |  |
| Email | nvarchar(50) | Yes | No |  |
| LogoName | nvarchar(50) | Yes | No |  |
| Logo | image(2147483647) | Yes | No |  |
| URl | nvarchar(-1) | Yes | No |  |
| WebURL | nvarchar(100) | Yes | No |  |

#### Primary Key
`COId`

---

### dbo.CompanySetup

**Rows:** 1  |  
**Columns:** 18  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| Id | int(10,0) | No | Yes |  |
| CompanyName | nvarchar(50) | Yes | No |  |
| Address | text(2147483647) | Yes | No |  |
| Phone1 | nvarchar(50) | Yes | No |  |
| Fax | nvarchar(50) | Yes | No |  |
| Email | nvarchar(50) | Yes | No |  |
| Phone2 | nvarchar(50) | Yes | No |  |
| Logo_ | nvarchar(-1) | Yes | No |  |
| Logo | image(2147483647) | Yes | No |  |
| header | bit | Yes | No |  |
| Logo2_ | nvarchar(-1) | Yes | No |  |
| Logo2 | image(2147483647) | Yes | No |  |
| ReportFooter | nvarchar(60) | Yes | No |  |
| Company_id | int(10,0) | No | No |  |
| branch_id | int(10,0) | No | No |  |
| URL | nvarchar(-1) | Yes | No |  |
| Address2 | nvarchar(-1) | Yes | No |  |
| EposURL | nvarchar(100) | Yes | No |  |

---

### dbo.Counter_Opening_Expense_Log

**Rows:** 0  |  
**Columns:** 6  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| User | nvarchar(-1) | No | No |  |
| CounterId | int(10,0) | No | No |  |
| date | datetime | No | No |  |
| Time | nvarchar(50) | No | No |  |
| Balance | decimal(18,2) | No | No |  |

---

### dbo.Customer

**Rows:** 0  |  
**Columns:** 6  |  
**Foreign Keys:** 1

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| CustId | int(10,0) | No | Yes | (PK) |
| Customer | nvarchar(-1) | Yes | No |  |
| Address | nvarchar(-1) | Yes | No |  |
| CellNo | nvarchar(-1) | Yes | No |  |
| CAId | int(10,0) | Yes | No |  |
| COId | int(10,0) | Yes | No |  |

#### Primary Key
`CustId`

#### Foreign Keys

| Constraint | Local Column | Referenced Table | Referenced Column |
|------------|--------------|------------------|-------------------|
| FK_Customer_ChartOfAccount | CAId | dbo.ChartOfAccount | CAId |

---

### dbo.CustomerLedger

**Rows:** 0  |  
**Columns:** 18  |  
**Foreign Keys:** 2

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| VoucherId | int(10,0) | Yes | No |  |
| Amount | decimal(18,2) | Yes | No |  |
| Type | varchar(40) | Yes | No |  |
| CustId | int(10,0) | Yes | No |  |
| Date | datetime | Yes | No |  |
| COId | int(10,0) | Yes | No |  |
| VoucherType | nvarchar(50) | Yes | No |  |
| VN | nvarchar(50) | Yes | No |  |
| SaleId | int(10,0) | Yes | No |  |
| date_time | datetime | Yes | No |  |
| Time | nvarchar(50) | Yes | No |  |
| BuffetBookingId | int(10,0) | Yes | No |  |
| TiltId | int(10,0) | Yes | No |  |
| CounterId | int(10,0) | Yes | No |  |
| ShiftNo | nvarchar(50) | Yes | No |  |
| OpId | int(10,0) | Yes | No |  |
| UserReceived | nvarchar(50) | Yes | No |  |

#### Foreign Keys

| Constraint | Local Column | Referenced Table | Referenced Column |
|------------|--------------|------------------|-------------------|
| FK_CustomerLedger_Company | COId | dbo.Company | COId |
| FK_CustomerLedger_Customer | CustId | dbo.Customer | CustId |

---

### dbo.CustomerLedgerAdvBooking

**Rows:** 0  |  
**Columns:** 20  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| VoucherId | int(10,0) | Yes | No |  |
| Amount | decimal(18,2) | Yes | No |  |
| Type | varchar(40) | Yes | No |  |
| CustId | int(10,0) | Yes | No |  |
| Date | datetime | Yes | No |  |
| VoucherType | nvarchar(50) | Yes | No |  |
| VN | nvarchar(50) | Yes | No |  |
| BuffetBookingId | int(10,0) | Yes | No |  |
| TiltId | int(10,0) | Yes | No |  |
| CounterId | int(10,0) | Yes | No |  |
| ShiftNo | nvarchar(50) | Yes | No |  |
| OpId | int(10,0) | Yes | No |  |
| UserReceived | nvarchar(500) | Yes | No |  |
| status | bit | Yes | No |  |
| Od | nvarchar(50) | Yes | No |  |
| is_upload | bit | No | No |  |
| is_update | bit | No | No |  |
| time | nvarchar(50) | Yes | No |  |
| Date_time | datetime | Yes | No |  |

---

### dbo.CustomerPOS

**Rows:** 420,496  |  
**Columns:** 13  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| order_key | nvarchar(50) | Yes | No |  |
| customer_name | nvarchar(50) | Yes | No |  |
| address | nvarchar(500) | Yes | No |  |
| tel_no | nvarchar(50) | Yes | No |  |
| cell_no | nvarchar(50) | Yes | No |  |
| CustomerCode | nvarchar(500) | Yes | No |  |
| Active | int(10,0) | No | No |  |
| Address2 | nvarchar(500) | Yes | No |  |
| is_upload | bit | No | No |  |
| is_update | bit | No | No |  |
| unique_key | varchar(50) | Yes | No |  |
| customer_group_id | int(10,0) | No | No |  |

#### Sample Data (First 3 rows)

|    id |   order_key | customer_name   | address     | tel_no   |      cell_no | CustomerCode   |   Active | Address2   | is_upload   | is_update   | unique_key   |   customer_group_id |
|------:|------------:|:----------------|:------------|:---------|-------------:|:---------------|---------:|:-----------|:------------|:------------|:-------------|--------------------:|
| 83848 |       76955 | ABC             | FGDFGB      |          |          213 | 2017-0001      |        1 |            | False       | False       | None         |                   0 |
| 83851 |       76958 | DRFDQW          | FGDHDFJGF   |          | 030005556555 | 2017-4         |        1 |            | False       | False       | None         |                   0 |
| 83855 |       76962 | ARIF            | KHADAMARKET |          |  03007060768 | 2017-5         |        1 |            | False       | False       | None         |                   0 |

---

### dbo.CustomerPOS_

**Rows:** 115,662  |  
**Columns:** 10  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| order_key | nvarchar(50) | Yes | No |  |
| customer_name | nvarchar(50) | Yes | No |  |
| address | nvarchar(500) | Yes | No |  |
| tel_no | nvarchar(50) | Yes | No |  |
| cell_no | nvarchar(50) | Yes | No |  |
| CustomerCode | nvarchar(500) | Yes | No |  |
| Active | int(10,0) | No | No |  |
| Address2 | nvarchar(500) | Yes | No |  |
| customer_group_id | int(10,0) | No | No |  |

#### Sample Data (First 3 rows)

|    id |   order_key | customer_name   | address   | tel_no   |      cell_no | CustomerCode   |   Active | Address2   |   customer_group_id |
|------:|------------:|:----------------|:----------|:---------|-------------:|:---------------|---------:|:-----------|--------------------:|
| 30814 |           0 | 30814           | 2017-0001 | 30814    |          213 | 2017-0001      |        0 |            |                   0 |
| 30817 |           0 | DRFDQW          | FGDHDFJGF |          | 030005556555 | 2017-4         |        0 |            |                   0 |
| 30818 |           0 | arif            |           |          |  03007060768 | 2017-5         |        0 |            |                   0 |

---

### dbo.CustomerReciptDetail

**Rows:** 0  |  
**Columns:** 7  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| CustRId | int(10,0) | Yes | No |  |
| Amount | decimal(18,2) | Yes | No |  |
| Desc | nvarchar(-1) | Yes | No |  |
| BuffetBookingId | int(10,0) | Yes | No |  |
| is_upload | bit | No | No |  |
| is_update | bit | No | No |  |

---

### dbo.CustomerReciptMaster

**Rows:** 0  |  
**Columns:** 12  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| CustRId | int(10,0) | No | Yes | (PK) |
| PaymentNo | nvarchar(50) | Yes | No |  |
| Date | datetime | Yes | No |  |
| CustId | int(10,0) | Yes | No |  |
| Amount | decimal(18,2) | Yes | No |  |
| PaymentMode | nvarchar(50) | Yes | No |  |
| ChequeNo | nvarchar(50) | Yes | No |  |
| ChequeDate | datetime | Yes | No |  |
| CreditCardNo | nvarchar(50) | Yes | No |  |
| status | bit | Yes | No |  |
| is_upload | bit | No | No |  |
| is_update | bit | No | No |  |

#### Primary Key
`CustRId`

---

### dbo.CustomerSaleInvoiceDetail

**Rows:** 0  |  
**Columns:** 15  |  
**Foreign Keys:** 2

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| SLId | int(10,0) | Yes | No |  |
| ItemId | int(10,0) | Yes | No |  |
| Unit | int(10,0) | Yes | No |  |
| Qty | decimal(18,2) | Yes | No |  |
| Rate | decimal(18,2) | Yes | No |  |
| TotalPackage | decimal(18,2) | Yes | No |  |
| PcsPerPackage | decimal(18,2) | Yes | No |  |
| RatePerPackage | decimal(18,2) | Yes | No |  |
| PackageId | int(10,0) | Yes | No |  |
| Tax | decimal(18,2) | Yes | No |  |
| Discount | decimal(18,2) | Yes | No |  |
| Amount | decimal(18,2) | Yes | No |  |
| ActualRate | decimal(18,2) | Yes | No |  |
| TaxType | nvarchar(50) | Yes | No |  |

#### Foreign Keys

| Constraint | Local Column | Referenced Table | Referenced Column |
|------------|--------------|------------------|-------------------|
| FK_CustomerSaleInvoiceDetail_Item | ItemId | dbo.Item | ItemId |
| FK_CustomerSaleInvoiceDetail_Store_CustomerSaleInvoiceMaster_Store | SLId | dbo.CustomerSaleInvoiceMaster | SLId |

---

### dbo.CustomerSaleInvoiceMaster

**Rows:** 0  |  
**Columns:** 12  |  
**Foreign Keys:** 1

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| SLId | int(10,0) | No | Yes | (PK) |
| Date | datetime | Yes | No |  |
| CustId | int(10,0) | Yes | No |  |
| SaleInvoiceNo | varchar(50) | Yes | No |  |
| SId | int(10,0) | Yes | No |  |
| BRId | int(10,0) | Yes | No |  |
| Amount | decimal(18,2) | Yes | No |  |
| Discount | decimal(18,2) | Yes | No |  |
| TotalAmount | decimal(18,2) | Yes | No |  |
| RefrenceNo | nvarchar(50) | Yes | No |  |
| TotalTax | decimal(18,2) | Yes | No |  |
| is_ob | bit | Yes | No |  |

#### Primary Key
`SLId`

#### Foreign Keys

| Constraint | Local Column | Referenced Table | Referenced Column |
|------------|--------------|------------------|-------------------|
| FK_CustomerSaleInvoiceMaster_Customer | CustId | dbo.Customer | CustId |

---

### dbo.Deals

**Rows:** 0  |  
**Columns:** 13  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| deal_name | nvarchar(50) | Yes | No |  |
| deal_price | float(53,None) | Yes | No |  |
| category_name | nvarchar(50) | Yes | No |  |
| item_name | nvarchar(50) | Yes | No |  |
| qty | float(53,None) | Yes | No |  |
| department | nvarchar(50) | Yes | No |  |
| TiltId | int(10,0) | Yes | No |  |
| Is_Upload | bit | No | No |  |
| Is_Update | bit | No | No |  |
| Deal_ItemId | int(10,0) | No | No |  |
| Cid | int(10,0) | No | No |  |
| ItemId | int(10,0) | No | No |  |

---

### dbo.DealsOnSpot

**Rows:** 0  |  
**Columns:** 17  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| deal_name | nvarchar(50) | Yes | No |  |
| deal_price | float(53,None) | Yes | No |  |
| category_name | nvarchar(50) | Yes | No |  |
| item_name | nvarchar(50) | Yes | No |  |
| qty | float(53,None) | Yes | No |  |
| ChooseAny | nvarchar(50) | Yes | No |  |
| department | nvarchar(50) | Yes | No |  |
| TiltId | int(10,0) | Yes | No |  |
| ItemQty | float(53,None) | Yes | No |  |
| orderid | int(10,0) | No | No |  |
| GetType | nvarchar(50) | Yes | No |  |
| Deal_ItemId | int(10,0) | No | No |  |
| Cid | int(10,0) | No | No |  |
| ItemId | int(10,0) | No | No |  |
| is_Upload | bit | No | No |  |
| is_Update | bit | No | No |  |

---

### dbo.DealsOnSpotItems

**Rows:** 0  |  
**Columns:** 15  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| order_key | nvarchar(50) | Yes | No |  |
| Order_detailId | int(10,0) | Yes | No |  |
| deal_name | nvarchar(50) | Yes | No |  |
| deal_price | float(53,None) | Yes | No |  |
| category_name | nvarchar(50) | Yes | No |  |
| item_name | nvarchar(50) | Yes | No |  |
| qty | float(53,None) | Yes | No |  |
| department | nvarchar(50) | Yes | No |  |
| TiltId | int(10,0) | Yes | No |  |
| Status | bit | Yes | No |  |
| ItemQty | float(53,None) | Yes | No |  |
| OrderKey_Merege | nvarchar(50) | Yes | No |  |
| Price_Item | decimal(18,2) | No | No |  |
| item_comment | nvarchar(50) | Yes | No |  |

---

### dbo.Deals_Dpt_Desc_Status

**Rows:** 0  |  
**Columns:** 2  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| Did | int(10,0) | No | No |  |

---

### dbo.Deals_Item

**Rows:** 0  |  
**Columns:** 12  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| Order_Key | nvarchar(50) | No | No |  |
| Order_Detail_id | int(10,0) | No | No |  |
| Deal_name | nvarchar(50) | No | No |  |
| deal_Price | decimal(18,2) | No | No |  |
| Deal_Qty | decimal(18,2) | No | No |  |
| Department | nvarchar(50) | No | No |  |
| Category_name | nvarchar(50) | No | No |  |
| Item_name | nvarchar(50) | No | No |  |
| Item_Qty | decimal(18,2) | No | No |  |
| Item_Price | decimal(18,2) | No | No |  |
| item_comment | nvarchar(50) | Yes | No |  |

---

### dbo.DeliveryCharges

**Rows:** 0  |  
**Columns:** 5  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| IsActive | bit | No | No |  |
| isPercent | bit | No | No |  |
| Delivery Charges | decimal(18,2) | No | No |  |
| Apply On Amount | decimal(18,2) | No | No |  |

---

### dbo.DeliveryQualityPoints

**Rows:** 3  |  
**Columns:** 8  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| ServiceSatisfactory | nvarchar(50) | Yes | No |  |
| SS_Points | decimal(18,0) | No | No |  |
| FoodQuality | nvarchar(50) | Yes | No |  |
| FQ_Points | decimal(18,0) | No | No |  |
| CorrectOrder | nvarchar(50) | Yes | No |  |
| CO_Points | decimal(18,0) | No | No |  |
| OnTimeDelivery | nvarchar(50) | Yes | No |  |
| OTD_Points | decimal(18,0) | No | No |  |

---

### dbo.DeliveryQualityPointsTable

**Rows:** 2  |  
**Columns:** 12  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| OrderKey | nvarchar(50) | Yes | No |  |
| SS_Execelent | nvarchar(50) | Yes | No |  |
| SS_Average | nvarchar(50) | Yes | No |  |
| SS_Poor | nvarchar(50) | Yes | No |  |
| FQ_Execelent | nvarchar(50) | Yes | No |  |
| FQ_Average | nvarchar(50) | Yes | No |  |
| FQ_Poor | nvarchar(50) | Yes | No |  |
| CO_Yes | nvarchar(50) | Yes | No |  |
| CO_No | nvarchar(50) | Yes | No |  |
| OTD_Yes | nvarchar(50) | Yes | No |  |
| OTD_No | nvarchar(50) | Yes | No |  |

---

### dbo.DemandSheetDetail_Branch

**Rows:** 0  |  
**Columns:** 7  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| DSId | int(10,0) | Yes | No |  |
| ItemId | int(10,0) | Yes | No |  |
| Unit | varchar(50) | Yes | No |  |
| Qty | decimal(18,2) | Yes | No |  |
| Status | bit | Yes | No |  |
| IssQty | decimal(18,2) | Yes | No |  |

---

### dbo.DemandSheetDetail_Store

**Rows:** 0  |  
**Columns:** 7  |  
**Foreign Keys:** 2

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| DSCOId | int(10,0) | Yes | No |  |
| ItemId | int(10,0) | Yes | No |  |
| Unit | int(10,0) | Yes | No |  |
| Qty | decimal(18,2) | Yes | No |  |
| Status | bit | Yes | No |  |
| POQty | decimal(18,2) | Yes | No |  |

#### Foreign Keys

| Constraint | Local Column | Referenced Table | Referenced Column |
|------------|--------------|------------------|-------------------|
| FK_DemandSheetDetail_Store_Item | ItemId | dbo.Item | ItemId |
| FK_DemandSheetDetail_Company_DemandSheetMaster_Company | DSCOId | dbo.DemandSheetMaster_Store | DSCOId |

---

### dbo.DemandSheetMaster_Branch

**Rows:** 0  |  
**Columns:** 7  |  
**Foreign Keys:** 1

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| DSId | int(10,0) | No | Yes | (PK) |
| BRId | int(10,0) | Yes | No |  |
| Date | datetime | Yes | No |  |
| DSNo | varchar(50) | Yes | No |  |
| UserId | int(10,0) | Yes | No |  |
| DId | int(10,0) | Yes | No |  |
| Desc | nvarchar(-1) | Yes | No |  |

#### Primary Key
`DSId`

#### Foreign Keys

| Constraint | Local Column | Referenced Table | Referenced Column |
|------------|--------------|------------------|-------------------|
| FK_DemandSheetMaster_Branch_Branch | BRId | dbo.Branch | BRId |

---

### dbo.DemandSheetMaster_Store

**Rows:** 0  |  
**Columns:** 7  |  
**Foreign Keys:** 2

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| DSCOId | int(10,0) | No | Yes | (PK) |
| SId | int(10,0) | Yes | No |  |
| Date | datetime | Yes | No |  |
| DSNo | varchar(50) | Yes | No |  |
| COId | int(10,0) | Yes | No |  |
| Desc | nvarchar(-1) | Yes | No |  |
| Vid | int(10,0) | Yes | No |  |

#### Primary Key
`DSCOId`

#### Foreign Keys

| Constraint | Local Column | Referenced Table | Referenced Column |
|------------|--------------|------------------|-------------------|
| FK_DemandSheetMaster_Store_Company | COId | dbo.Company | COId |
| FK_DemandSheetMaster_Store_Store | SId | dbo.Store | SId |

---

### dbo.DepartmentPOS

**Rows:** 14  |  
**Columns:** 6  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| department_name | nvarchar(50) | Yes | No |  |
| BRId | int(10,0) | Yes | No |  |
| COId | int(10,0) | Yes | No |  |
| Is_Upload | bit | No | No |  |
| Is_Update | bit | No | No |  |

---

### dbo.DeploymentDetail

**Rows:** 0  |  
**Columns:** 2  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| ID | int(10,0) | No | Yes | (PK) |
| Date | datetime | No | No |  |

#### Primary Key
`ID`

---

### dbo.Dine_In_Order

**Rows:** 81,965  |  
**Columns:** 80  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| order_key | nvarchar(50) | Yes | No |  |
| z_number | nvarchar(50) | Yes | No |  |
| order_type | nvarchar(50) | Yes | No |  |
| order_no | int(10,0) | Yes | No |  |
| order_date | datetime | Yes | No |  |
| day | nvarchar(50) | Yes | No |  |
| table_no | nvarchar(50) | Yes | No |  |
| waiter_name | nvarchar(50) | Yes | No |  |
| order_time | nvarchar(50) | Yes | No |  |
| service_time | nvarchar(50) | Yes | No |  |
| service_status | nvarchar(50) | Yes | No |  |
| account_status | nvarchar(50) | Yes | No |  |
| amount | float(53,None) | Yes | No |  |
| DiscountType | nvarchar(50) | Yes | No |  |
| discount | decimal(18,2) | Yes | No |  |
| is_delete | bit | Yes | No |  |
| cover | decimal(18,0) | No | No |  |
| estimated_time | nvarchar(50) | Yes | No |  |
| table_time | nvarchar(50) | Yes | No |  |
| kitchen_status | bit | No | No |  |
| Tiltid | int(10,0) | Yes | No |  |
| CounterId | int(10,0) | Yes | No |  |
| IsBill | bit | Yes | No |  |
| CareOff | nvarchar(100) | Yes | No |  |
| IsSelect | bit | Yes | No |  |
| Customer | nvarchar(-1) | Yes | No |  |
| Tele | nvarchar(50) | Yes | No |  |
| ExtraCharges | decimal(18,2) | Yes | No |  |
| DeleteReason | nvarchar(-1) | Yes | No |  |
| UserPunch | nvarchar(-1) | Yes | No |  |
| UserCash | nvarchar(-1) | Yes | No |  |
| UserDelete | nvarchar(-1) | Yes | No |  |
| KOT | int(10,0) | Yes | No |  |
| tableStatus | bit | Yes | No |  |
| OrderTiltId | int(10,0) | Yes | No |  |
| TimeIn | datetime | Yes | No |  |
| TimeOut | datetime | Yes | No |  |
| Status | bit | No | No |  |
| Od | int(10,0) | No | No |  |
| Itemqty | float(53,None) | No | No |  |
| Itemprice | float(53,None) | No | No |  |
| OrderKey_Merege | nvarchar(50) | Yes | No |  |
| DispatchTime | nvarchar(50) | Yes | No |  |
| OrderStatus | nvarchar(50) | Yes | No |  |
| PaymentMode | nvarchar(50) | Yes | No |  |
| isFeedback | bit | No | No |  |
| Feedback | nvarchar(-1) | Yes | No |  |
| isFeedbackDone | bit | No | No |  |
| IsServiceCharges | bit | No | No |  |
| ServiceCharges | decimal(18,2) | No | No |  |
| TabUserPunch | nvarchar(50) | Yes | No |  |
| is_upload | bit | No | No |  |
| is_update | bit | No | No |  |
| Date | datetime | Yes | No |  |
| DeleteOrderStatus | bit | No | No |  |
| DiscountId | nvarchar(50) | Yes | No |  |
| branchId | int(10,0) | No | No |  |
| is_order_TransferedTo_Branch | bit | No | No |  |
| is_Branch_Received_Order | bit | No | No |  |
| Rider_Commision | decimal(18,2) | No | No |  |
| Rider_IsPercent | bit | No | No |  |
| Rider_Commision_Percent | decimal(18,2) | No | No |  |
| CommentsForRider | nvarchar(-1) | Yes | No |  |
| Is_Manual_ExtraCharges | bit | No | No |  |
| TokenNumber | nvarchar(100) | Yes | No |  |
| is_deleted_print | int(10,0) | Yes | No |  |
| user_id | int(10,0) | No | No |  |
| FeedbackApi | bit | Yes | No |  |
| is_BillReceive | bit | Yes | No |  |
| unique_key | varchar(50) | Yes | No |  |
| advance_amount | decimal(18,2) | Yes | No |  |
| deliver_time | datetime | Yes | No |  |
| dispatch_time | datetime | Yes | No |  |
| duration | varchar(20) | Yes | No |  |
| is_table_transfer | bit | Yes | No |  |
| android_device_no | nvarchar(50) | Yes | No |  |
| new_order_no | nvarchar(50) | Yes | No |  |
| kds_done | bit | Yes | No |  |
| luckyDraw | int(10,0) | Yes | No |  |

#### Sample Data (First 3 rows)

|     id |   order_key | z_number   | order_type   |   order_no | order_date          | day       | table_no   | waiter_name   | order_time   | service_time   | service_status   | account_status   |   amount | DiscountType   |   discount | is_delete   |   cover | estimated_time   | table_time   | kitchen_status   |   Tiltid |   CounterId | IsBill   | CareOff   | IsSelect   | Customer   | Tele   |   ExtraCharges | DeleteReason   | UserPunch   | UserCash   | UserDelete   |   KOT | tableStatus   |   OrderTiltId | TimeIn              | TimeOut   | Status   |    Od |   Itemqty |   Itemprice | OrderKey_Merege   | DispatchTime   | OrderStatus   | PaymentMode   | isFeedback   | Feedback   | isFeedbackDone   | IsServiceCharges   |   ServiceCharges | TabUserPunch   | is_upload   | is_update   | Date                | DeleteOrderStatus   | DiscountId   |   branchId | is_order_TransferedTo_Branch   | is_Branch_Received_Order   |   Rider_Commision | Rider_IsPercent   |   Rider_Commision_Percent | CommentsForRider   | Is_Manual_ExtraCharges   | TokenNumber   | is_deleted_print   |   user_id | FeedbackApi   | is_BillReceive   | unique_key   |   advance_amount | deliver_time   | dispatch_time   | duration   | is_table_transfer   | android_device_no   | new_order_no   | kds_done   |   luckyDraw |
|-------:|------------:|:-----------|:-------------|-----------:|:--------------------|:----------|:-----------|:--------------|:-------------|:---------------|:-----------------|:-----------------|---------:|:---------------|-----------:|:------------|--------:|:-----------------|:-------------|:-----------------|---------:|------------:|:---------|:----------|:-----------|:-----------|:-------|---------------:|:---------------|:------------|:-----------|:-------------|------:|:--------------|--------------:|:--------------------|:----------|:---------|------:|----------:|------------:|:------------------|:---------------|:--------------|:--------------|:-------------|:-----------|:-----------------|:-------------------|-----------------:|:---------------|:------------|:------------|:--------------------|:--------------------|:-------------|-----------:|:-------------------------------|:---------------------------|------------------:|:------------------|--------------------------:|:-------------------|:-------------------------|:--------------|:-------------------|----------:|:--------------|:-----------------|:-------------|-----------------:|:---------------|:----------------|:-----------|:--------------------|:--------------------|:---------------|:-----------|------------:|
| 537206 |           0 | DAY-00001  | DELIVERY     |      77300 | 2021-06-19 21:55:00 | Wednesday |            |               | 09:52 PM     | None           |                  | Not Paid         |        0 | None           |          0 | False       |       0 | 06/19/21 9:52 PM | None         | False            |       47 |         397 | False    | None      | False      |            |        |              0 | None           | PC 2        | None       | None         |     0 | False         |             0 | 1900-01-01 21:52:00 | None      | False    | 77300 |         0 |           0 | None              | None           | None          | None          | False        | None       | False            | False              |                0 | None           | False       | False       | 2021-06-19 21:55:00 | False               | None         |          0 | False                          | False                      |                 0 | False             |                         0 | None               | False                    | None          | None               |         0 | False         | False            | None         |                0 | None           | None            | None       | False               | None                | None           | False      |           0 |
| 537749 |           0 | DAY-00001  | DELIVERY     |      77843 | 2021-06-20 21:58:00 | Wednesday |            |               | 09:55 PM     | None           |                  | Not Paid         |        0 | None           |          0 | False       |       0 | 06/20/21 9:55 PM | None         | False            |       57 |         391 | False    | None      | False      |            |        |              0 | None           | PC 5        | None       | None         |     0 | False         |             0 | 1900-01-01 21:55:00 | None      | False    | 77843 |         0 |           0 | None              | None           | None          | None          | False        | None       | False            | False              |                0 | None           | False       | False       | 2021-06-20 21:58:00 | False               | None         |          0 | False                          | False                      |                 0 | False             |                         0 | None               | False                    | None          | None               |         0 | False         | False            | None         |                0 | None           | None            | None       | False               | None                | None           | False      |           0 |
| 541158 |           0 | DAY-00001  | DELIVERY     |      79307 | 2021-06-24 21:18:00 | Wednesday |            |               | 09:17 PM     | None           |                  | Not Paid         |        0 | None           |          0 | False       |       0 | 06/24/21 9:17 PM | None         | False            |       53 |         405 | False    | None      | False      |            |        |              0 | None           | PC 4        | None       | None         |     0 | False         |             0 | 1900-01-01 21:17:00 | None      | False    | 79307 |         0 |           0 | None              | None           | None          | None          | False        | None       | False            | False              |                0 | None           | False       | False       | 2021-06-24 21:18:00 | False               | None         |          0 | False                          | False                      |                 0 | False             |                         0 | None               | False                    | None          | None               |         0 | False         | False            | None         |                0 | None           | None            | None       | False               | None                | None           | False      |           0 |

---

### dbo.Discount

**Rows:** 0  |  
**Columns:** 16  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| date | datetime | Yes | No |  |
| order_key | nvarchar(50) | Yes | No |  |
| order_num | nvarchar(50) | Yes | No |  |
| c_o | nvarchar(50) | Yes | No |  |
| payment_type | nvarchar(50) | Yes | No |  |
| order_type | nvarchar(50) | Yes | No |  |
| discount | float(53,None) | Yes | No |  |
| percent | nvarchar(50) | Yes | No |  |
| z_num | nvarchar(50) | Yes | No |  |
| order_price | float(53,None) | Yes | No |  |
| Tiltid | int(10,0) | Yes | No |  |
| CounterId | int(10,0) | Yes | No |  |
| Status | bit | No | No |  |
| is_upload | bit | No | No |  |
| is_update | bit | No | No |  |

---

### dbo.DiscountMapping

**Rows:** 7  |  
**Columns:** 5  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| Id | int(10,0) | No | Yes |  |
| CAId | int(10,0) | Yes | No |  |
| Type | nvarchar(50) | Yes | No |  |
| Transaction | nvarchar(50) | Yes | No |  |
| Form | nvarchar(50) | Yes | No |  |

---

### dbo.DiscountSetting

**Rows:** 0  |  
**Columns:** 12  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| CareOf | nvarchar(100) | Yes | No |  |
| Percentage | decimal(18,2) | Yes | No |  |
| IsPercent | bit | Yes | No |  |
| from | nvarchar(50) | Yes | No |  |
| To | nvarchar(50) | Yes | No |  |
| OrderType | nvarchar(50) | Yes | No |  |
| Is_HappyHour | bit | No | No |  |
| IsActive | bit | No | No |  |
| AutoDiscount | bit | No | No |  |
| credit_card_info | nvarchar(-1) | Yes | No |  |
| IsBank | bit | Yes | No |  |

---

### dbo.Ent

**Rows:** 0  |  
**Columns:** 11  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| order_key | nvarchar(50) | Yes | No |  |
| order_num | nvarchar(50) | Yes | No |  |
| date | datetime | Yes | No |  |
| name | nvarchar(50) | Yes | No |  |
| c_o | nvarchar(50) | Yes | No |  |
| z_num | nvarchar(50) | Yes | No |  |
| Tiltid | int(10,0) | Yes | No |  |
| CounterId | int(10,0) | Yes | No |  |
| is_upload | bit | No | No |  |
| is_update | bit | No | No |  |

---

### dbo.EntTableLimit

**Rows:** 0  |  
**Columns:** 3  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| tableNo | nvarchar(50) | Yes | No |  |
| limit | float(53,None) | Yes | No |  |

---

### dbo.Fixed_Comments_Instructions

**Rows:** 0  |  
**Columns:** 2  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes | (PK) |
| Comments | nvarchar(-1) | Yes | No |  |

#### Primary Key
`id`

---

### dbo.GL

**Rows:** 0  |  
**Columns:** 10  |  
**Foreign Keys:** 2

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| Type | varchar(40) | Yes | No |  |
| VN | nvarchar(50) | Yes | No |  |
| VoucherId | int(10,0) | Yes | No |  |
| Date | datetime | Yes | No |  |
| Amount | decimal(18,2) | Yes | No |  |
| CAId | int(10,0) | Yes | No |  |
| VoucherType | varchar(40) | Yes | No |  |
| COId | int(10,0) | Yes | No |  |
| APId | int(10,0) | Yes | No |  |

#### Foreign Keys

| Constraint | Local Column | Referenced Table | Referenced Column |
|------------|--------------|------------------|-------------------|
| FK_GL_Company | COId | dbo.Company | COId |
| ChartOfAccount_GL | CAId | dbo.ChartOfAccount | CAId |

---

### dbo.GRNDetail

**Rows:** 0  |  
**Columns:** 18  |  
**Foreign Keys:** 2

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| GRNId | int(10,0) | Yes | No |  |
| ItemId | int(10,0) | Yes | No |  |
| Unit | int(10,0) | Yes | No |  |
| Qty | decimal(18,2) | Yes | No |  |
| POId | int(10,0) | Yes | No |  |
| Rate | decimal(18,2) | Yes | No |  |
| TotalPackage | decimal(18,2) | Yes | No |  |
| PcsPerPackage | decimal(18,2) | Yes | No |  |
| RatePerPackage | decimal(18,2) | Yes | No |  |
| PackageId | int(10,0) | Yes | No |  |
| Tax | decimal(18,2) | Yes | No |  |
| Discount | decimal(18,2) | Yes | No |  |
| Amount | decimal(18,2) | Yes | No |  |
| ActualRate | decimal(18,2) | Yes | No |  |
| TaxType | nvarchar(50) | Yes | No |  |
| RatePerPcs | decimal(18,2) | No | No |  |
| Qty_Pcs | decimal(18,2) | Yes | No |  |

#### Foreign Keys

| Constraint | Local Column | Referenced Table | Referenced Column |
|------------|--------------|------------------|-------------------|
| FK_GRNDetail_Item | ItemId | dbo.Item | ItemId |
| FK_GRNDetail_Store_GRNMaster_Store | GRNId | dbo.GRNMaster | GRNId |

---

### dbo.GRNMaster

**Rows:** 0  |  
**Columns:** 13  |  
**Foreign Keys:** 1

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| GRNId | int(10,0) | No | Yes | (PK) |
| Date | datetime | Yes | No |  |
| VId | int(10,0) | Yes | No |  |
| GRNo | varchar(50) | Yes | No |  |
| SId | int(10,0) | Yes | No |  |
| BRId | int(10,0) | Yes | No |  |
| Amount | decimal(18,2) | Yes | No |  |
| Discount | decimal(18,2) | Yes | No |  |
| TotalAmount | decimal(18,2) | Yes | No |  |
| RefrenceNo | nvarchar(50) | Yes | No |  |
| TotalTax | decimal(18,2) | Yes | No |  |
| Desc | nvarchar(-1) | Yes | No |  |
| uid | int(10,0) | Yes | No |  |

#### Primary Key
`GRNId`

#### Foreign Keys

| Constraint | Local Column | Referenced Table | Referenced Column |
|------------|--------------|------------------|-------------------|
| FK_GRNMaster_Vendor | VId | dbo.Vendor | VId |

---

### dbo.Group

**Rows:** 0  |  
**Columns:** 3  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| GRId | int(10,0) | No | Yes | (PK) |
| Group | nvarchar(50) | Yes | No |  |
| COId | int(10,0) | Yes | No |  |

#### Primary Key
`GRId`

---

### dbo.InvAdjDetail_Branch

**Rows:** 0  |  
**Columns:** 7  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| AdjBRId | int(10,0) | Yes | No |  |
| ItemId | int(10,0) | Yes | No |  |
| Unit | int(10,0) | Yes | No |  |
| Qty | decimal(18,2) | Yes | No |  |
| Rate | decimal(18,2) | Yes | No |  |
| Type | nvarchar(50) | Yes | No |  |

---

### dbo.InvAdjDetail_Store

**Rows:** 0  |  
**Columns:** 7  |  
**Foreign Keys:** 1

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| AdjId | int(10,0) | Yes | No |  |
| ItemId | int(10,0) | Yes | No |  |
| Unit | int(10,0) | Yes | No |  |
| Qty | decimal(18,2) | Yes | No |  |
| Rate | decimal(18,2) | Yes | No |  |
| Type | nvarchar(50) | Yes | No |  |

#### Foreign Keys

| Constraint | Local Column | Referenced Table | Referenced Column |
|------------|--------------|------------------|-------------------|
| FK_InvAdjDetail_Store_Item | ItemId | dbo.Item | ItemId |

---

### dbo.InvAdjMaster_Branch

**Rows:** 0  |  
**Columns:** 9  |  
**Foreign Keys:** 1

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| AdjBRId | int(10,0) | No | Yes | (PK) |
| Date | datetime | Yes | No |  |
| UserId | int(10,0) | Yes | No |  |
| BRId | int(10,0) | Yes | No |  |
| IsApprove | bit | Yes | No |  |
| AdjNo | varchar(50) | Yes | No |  |
| AppById | int(10,0) | Yes | No |  |
| DId | int(10,0) | Yes | No |  |
| Desc | nvarchar(-1) | Yes | No |  |

#### Primary Key
`AdjBRId`

#### Foreign Keys

| Constraint | Local Column | Referenced Table | Referenced Column |
|------------|--------------|------------------|-------------------|
| FK_InvAdjMaster_Branch_Branch | BRId | dbo.Branch | BRId |

---

### dbo.InvAdjMaster_Store

**Rows:** 0  |  
**Columns:** 8  |  
**Foreign Keys:** 1

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| AdjId | int(10,0) | No | Yes | (PK) |
| Date | datetime | Yes | No |  |
| UserId | int(10,0) | Yes | No |  |
| SId | int(10,0) | Yes | No |  |
| IsApprove | bit | Yes | No |  |
| AdjNo | varchar(50) | Yes | No |  |
| AppById | int(10,0) | Yes | No |  |
| Desc | nvarchar(-1) | Yes | No |  |

#### Primary Key
`AdjId`

#### Foreign Keys

| Constraint | Local Column | Referenced Table | Referenced Column |
|------------|--------------|------------------|-------------------|
| FK_InvAdjMaster_Store_Store | SId | dbo.Store | SId |

---

### dbo.InvoiceDetail_Company

**Rows:** 0  |  
**Columns:** 18  |  
**Foreign Keys:** 2

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| InvoiceId | int(10,0) | Yes | No |  |
| ItemId | int(10,0) | Yes | No |  |
| Unit | int(10,0) | Yes | No |  |
| Rate | decimal(18,0) | Yes | No |  |
| Qty | decimal(18,0) | Yes | No |  |
| POId | int(10,0) | Yes | No |  |
| DiscountPerPcs | decimal(18,2) | Yes | No |  |
| TaxPerPcs | decimal(18,2) | Yes | No |  |
| TotalPackage | decimal(18,2) | Yes | No |  |
| PcsPerPackage | decimal(18,2) | Yes | No |  |
| RatePerPackage | decimal(18,2) | Yes | No |  |
| PackageId | int(10,0) | Yes | No |  |
| TaxType | nvarchar(50) | Yes | No |  |
| NetAmount | decimal(18,2) | Yes | No |  |
| Amount | decimal(18,2) | Yes | No |  |
| TaxMode | int(10,0) | Yes | No |  |
| GRNId | int(10,0) | Yes | No |  |

#### Foreign Keys

| Constraint | Local Column | Referenced Table | Referenced Column |
|------------|--------------|------------------|-------------------|
| FK_InvoiceDetail_Company_InvoiceMaster_Company | InvoiceId | dbo.InvoiceMaster_Company | InvoiceId |
| FK_InvoiceDetail_Company_Item | ItemId | dbo.Item | ItemId |

---

### dbo.InvoiceDetail_CompanyNew

**Rows:** 0  |  
**Columns:** 17  |  
**Foreign Keys:** 3

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| InvoiceId | int(10,0) | Yes | No |  |
| ItemId | int(10,0) | Yes | No |  |
| Unit | int(10,0) | Yes | No |  |
| Qty | decimal(18,2) | Yes | No |  |
| POId | int(10,0) | Yes | No |  |
| GRNId | int(10,0) | Yes | No |  |
| Rate | decimal(18,2) | Yes | No |  |
| TotalPackage | decimal(18,2) | Yes | No |  |
| PcsPerPackage | decimal(18,2) | Yes | No |  |
| RatePerPackage | decimal(18,2) | Yes | No |  |
| PackageId | int(10,0) | Yes | No |  |
| Tax | decimal(18,2) | Yes | No |  |
| Discount | decimal(18,2) | Yes | No |  |
| Amount | decimal(18,2) | Yes | No |  |
| ActualRate | decimal(18,2) | Yes | No |  |
| TaxType | nvarchar(50) | Yes | No |  |

#### Foreign Keys

| Constraint | Local Column | Referenced Table | Referenced Column |
|------------|--------------|------------------|-------------------|
| FK_InvoiceDetail_CompanyNew_Item | ItemId | dbo.Item | ItemId |
| FK_InvoiceDetail_CompanyNew_InvoiceMaster_CompanyNew | InvoiceId | dbo.InvoiceMaster_CompanyNew | InvoiceId |
| FK_InvoiceDetail_CompanyNew_GRNMaster | GRNId | dbo.GRNMaster | GRNId |

---

### dbo.InvoiceMaster_Company

**Rows:** 0  |  
**Columns:** 14  |  
**Foreign Keys:** 2

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| InvoiceId | int(10,0) | No | Yes | (PK) |
| Date | datetime | Yes | No |  |
| COId | int(10,0) | Yes | No |  |
| UserId | int(10,0) | Yes | No |  |
| VId | int(10,0) | Yes | No |  |
| InvoiceNo | varchar(50) | Yes | No |  |
| SId | int(10,0) | Yes | No |  |
| BRId | int(10,0) | Yes | No |  |
| Amount | decimal(18,2) | Yes | No |  |
| Discount | decimal(18,2) | Yes | No |  |
| TotalAmount | decimal(18,2) | Yes | No |  |
| GRNId | int(10,0) | Yes | No |  |
| RefrenceNo | nvarchar(50) | Yes | No |  |
| TotalTax | decimal(18,2) | Yes | No |  |

#### Primary Key
`InvoiceId`

#### Foreign Keys

| Constraint | Local Column | Referenced Table | Referenced Column |
|------------|--------------|------------------|-------------------|
| FK_InvoiceMaster_Company_Vendor | VId | dbo.Vendor | VId |
| FK_InvoiceMaster_Company_Company | COId | dbo.Company | COId |

---

### dbo.InvoiceMaster_CompanyNew

**Rows:** 0  |  
**Columns:** 11  |  
**Foreign Keys:** 1

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| InvoiceId | int(10,0) | No | Yes | (PK) |
| Date | datetime | Yes | No |  |
| VId | int(10,0) | Yes | No |  |
| InvoiceNo | varchar(50) | Yes | No |  |
| SId | int(10,0) | Yes | No |  |
| BRId | int(10,0) | Yes | No |  |
| Amount | decimal(18,2) | Yes | No |  |
| Discount | decimal(18,2) | Yes | No |  |
| TotalAmount | decimal(18,2) | Yes | No |  |
| RefrenceNo | nvarchar(50) | Yes | No |  |
| TotalTax | decimal(18,2) | Yes | No |  |

#### Primary Key
`InvoiceId`

#### Foreign Keys

| Constraint | Local Column | Referenced Table | Referenced Column |
|------------|--------------|------------------|-------------------|
| FK_InvoiceMaster_CompanyNew_Vendor | VId | dbo.Vendor | VId |

---

### dbo.IssuanceButcheryDetail

**Rows:** 0  |  
**Columns:** 7  |  
**Foreign Keys:** 1

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| Id | int(10,0) | No | Yes |  |
| BUTId | int(10,0) | Yes | No |  |
| ItemId | int(10,0) | Yes | No |  |
| Unit | int(10,0) | Yes | No |  |
| Rate | decimal(18,2) | Yes | No |  |
| Qty | decimal(18,2) | Yes | No |  |
| Amount | decimal(18,2) | Yes | No |  |

#### Foreign Keys

| Constraint | Local Column | Referenced Table | Referenced Column |
|------------|--------------|------------------|-------------------|
| FK_IssuanceButcheryDetail_IssuanceButcheryMaster | BUTId | dbo.IssuanceButcheryMaster | BUTId |

---

### dbo.IssuanceButcheryMaster

**Rows:** 0  |  
**Columns:** 6  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| BUTId | int(10,0) | No | Yes | (PK) |
| Date | datetime | Yes | No |  |
| SId | int(10,0) | Yes | No |  |
| UserId | int(10,0) | Yes | No |  |
| BRId | int(10,0) | Yes | No |  |
| ISSBNo | nvarchar(50) | Yes | No |  |

#### Primary Key
`BUTId`

---

### dbo.IssuanceDetail_Store

**Rows:** 0  |  
**Columns:** 9  |  
**Foreign Keys:** 1

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| IssId | int(10,0) | Yes | No |  |
| ItemId | int(10,0) | Yes | No |  |
| Unit | int(10,0) | Yes | No |  |
| Rate | decimal(18,2) | Yes | No |  |
| Qty | decimal(18,2) | Yes | No |  |
| Amount | decimal(18,2) | Yes | No |  |
| DSId | int(10,0) | Yes | No |  |
| Qty_Pcs | decimal(18,2) | Yes | No |  |

#### Foreign Keys

| Constraint | Local Column | Referenced Table | Referenced Column |
|------------|--------------|------------------|-------------------|
| FK_IssuanceDetail_Store_IssuanceMaster_Store | IssId | dbo.IssuanceMaster_Store | IssId |

---

### dbo.IssuanceMaster_Store

**Rows:** 0  |  
**Columns:** 12  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| IssId | int(10,0) | No | Yes | (PK) |
| Date | datetime | Yes | No |  |
| SId | int(10,0) | Yes | No |  |
| BRId | int(10,0) | Yes | No |  |
| UserId | int(10,0) | Yes | No |  |
| Type | varchar(50) | Yes | No |  |
| IssNo | varchar(50) | Yes | No |  |
| DSId | int(10,0) | Yes | No |  |
| PSId | int(10,0) | Yes | No |  |
| DId | int(10,0) | Yes | No |  |
| GRNId | int(10,0) | Yes | No |  |
| Desc | nvarchar(-1) | Yes | No |  |

#### Primary Key
`IssId`

---

### dbo.IssuanceReaturnDetail

**Rows:** 0  |  
**Columns:** 7  |  
**Foreign Keys:** 1

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| Id | int(10,0) | No | Yes |  |
| IssRTId | int(10,0) | Yes | No |  |
| ItemId | int(10,0) | Yes | No |  |
| Unit | int(10,0) | Yes | No |  |
| Rate | decimal(18,2) | Yes | No |  |
| QTY | decimal(18,2) | Yes | No |  |
| Amount | decimal(18,2) | Yes | No |  |

#### Foreign Keys

| Constraint | Local Column | Referenced Table | Referenced Column |
|------------|--------------|------------------|-------------------|
| FK_IssuanceReaturnDetail_IssuanceReturnMaster | IssRTId | dbo.IssuanceReturnMaster | IssRTId |

---

### dbo.IssuanceReturnMaster

**Rows:** 0  |  
**Columns:** 8  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| IssRTId | int(10,0) | No | Yes | (PK) |
| Date | datetime | Yes | No |  |
| SId | int(10,0) | Yes | No |  |
| BRId | int(10,0) | Yes | No |  |
| UserId | int(10,0) | Yes | No |  |
| IssRNo | nvarchar(50) | Yes | No |  |
| DSId | int(10,0) | Yes | No |  |
| DId | int(10,0) | Yes | No |  |

#### Primary Key
`IssRTId`

---

### dbo.Item

**Rows:** 0  |  
**Columns:** 8  |  
**Foreign Keys:** 1

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| ItemId | int(10,0) | No | Yes | (PK) |
| SBId | int(10,0) | Yes | No |  |
| Item | nvarchar(50) | Yes | No |  |
| GRId | int(10,0) | Yes | No |  |
| ItemCode | nvarchar(50) | Yes | No |  |
| Type | nvarchar(50) | Yes | No |  |
| Yield | decimal(18,2) | No | No |  |
| Vid | int(10,0) | Yes | No |  |

#### Primary Key
`ItemId`

#### Foreign Keys

| Constraint | Local Column | Referenced Table | Referenced Column |
|------------|--------------|------------------|-------------------|
| FK_Item_SubCategory | SBId | dbo.SubCategory | SBId |

---

### dbo.ItemComments

**Rows:** 0  |  
**Columns:** 3  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| ItemComments | nvarchar(-1) | Yes | No |  |
| Item | nvarchar(50) | Yes | No |  |

---

### dbo.ItemConversion

**Rows:** 0  |  
**Columns:** 4  |  
**Foreign Keys:** 1

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| ItemId | int(10,0) | Yes | No |  |
| Packing-InvUnitFactor | float(53,None) | Yes | No |  |
| InvUnit-RecepieUnitFactor | float(53,None) | Yes | No |  |

#### Foreign Keys

| Constraint | Local Column | Referenced Table | Referenced Column |
|------------|--------------|------------------|-------------------|
| FK_ItemConversion_Item | ItemId | dbo.Item | ItemId |

---

### dbo.ItemGroupDetail

**Rows:** 0  |  
**Columns:** 3  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| IGId | int(10,0) | Yes | No |  |
| ItemName | varchar(50) | Yes | No |  |
| SGId | int(10,0) | Yes | No |  |

---

### dbo.ItemGroupMaster

**Rows:** 0  |  
**Columns:** 2  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| GId | int(10,0) | No | Yes |  |
| GName | nvarchar(50) | Yes | No |  |

---

### dbo.ItemOrderConversion

**Rows:** 0  |  
**Columns:** 5  |  
**Foreign Keys:** 1

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| ItemId | int(10,0) | Yes | No |  |
| OrderQty | decimal(18,2) | Yes | No |  |
| IssUnitId | int(10,0) | Yes | No |  |
| Conversion | decimal(18,2) | Yes | No |  |

#### Foreign Keys

| Constraint | Local Column | Referenced Table | Referenced Column |
|------------|--------------|------------------|-------------------|
| FK_ItemOrderConversion_Item | ItemId | dbo.Item | ItemId |

---

### dbo.ItemPOS

**Rows:** 1,643  |  
**Columns:** 39  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| category_name | nvarchar(50) | Yes | No |  |
| item_name | nvarchar(250) | Yes | No |  |
| cost_price | float(53,None) | Yes | No |  |
| sale_price | float(53,None) | Yes | No |  |
| codes | nvarchar(250) | Yes | No |  |
| status | bit | No | No |  |
| tiltId | int(10,0) | Yes | No |  |
| IsComment | bit | Yes | No |  |
| orderid | int(10,0) | No | No |  |
| GetType | nvarchar(50) | Yes | No |  |
| Is_Open | bit | No | No |  |
| Unit | nvarchar(50) | Yes | No |  |
| ItemParLevel | decimal(18,2) | No | No |  |
| ItemBalance | decimal(18,2) | No | No |  |
| item_name_arabic | nvarchar(-1) | Yes | No |  |
| IsDate_Effective | bit | No | No |  |
| FromDate | datetime | Yes | No |  |
| ToDate | datetime | Yes | No |  |
| ByeOneGetOneFree | bit | No | No |  |
| FinalQty | decimal(18,0) | No | No |  |
| Is_AutoPunchItem | bit | No | No |  |
| AutoPunchItem_Id | int(10,0) | No | No |  |
| Is_Upload | bit | No | No |  |
| Is_Update | bit | No | No |  |
| Cid | int(10,0) | No | No |  |
| ExtraItem | bit | No | No |  |
| Item_Commission | decimal(18,2) | No | No |  |
| is_delete | bit | Yes | No |  |
| is_feedback | bit | Yes | No |  |
| BRid | int(10,0) | Yes | No |  |
| is_charity | bit | Yes | No |  |
| charity_amount | decimal(18,2) | Yes | No |  |
| meal_type_id | int(10,0) | Yes | No |  |
| discount_apply | bit | Yes | No |  |
| image_url | nvarchar(50) | Yes | No |  |
| item_name_chinese | nvarchar(50) | Yes | No |  |
| item_name_urdu | nvarchar(50) | Yes | No |  |
| is_kot | bit | Yes | No |  |

---

### dbo.ItemPOS_Assign

**Rows:** 0  |  
**Columns:** 3  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| ID | int(10,0) | No | Yes | (PK) |
| Item_ID | int(10,0) | Yes | No |  |
| Item_Finish_ID | int(10,0) | Yes | No |  |

#### Primary Key
`ID`

---

### dbo.ItemPOS_Extra

**Rows:** 0  |  
**Columns:** 4  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| ItemId | int(10,0) | No | No |  |
| Extra_Item | nvarchar(50) | No | No |  |
| Price | decimal(18,2) | No | No |  |

---

### dbo.ItemPOS_finishPro

**Rows:** 0  |  
**Columns:** 2  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| ID | int(10,0) | No | Yes | (PK) |
| Item_name | nvarchar(100) | Yes | No |  |

#### Primary Key
`ID`

---

### dbo.ItemParLevel

**Rows:** 0  |  
**Columns:** 6  |  
**Foreign Keys:** 1

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| ItemId | int(10,0) | Yes | No |  |
| BRId | int(10,0) | Yes | No |  |
| ParLevel | decimal(18,2) | Yes | No |  |
| SId | int(10,0) | Yes | No |  |
| DId | int(10,0) | Yes | No |  |

#### Foreign Keys

| Constraint | Local Column | Referenced Table | Referenced Column |
|------------|--------------|------------------|-------------------|
| FK_ItemParLevel_Item | ItemId | dbo.Item | ItemId |

---

### dbo.ItemSubGroupMaster

**Rows:** 0  |  
**Columns:** 3  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| SGId | int(10,0) | No | Yes |  |
| SGName | varchar(50) | Yes | No |  |
| GId | int(10,0) | Yes | No |  |

---

### dbo.ItemUnit

**Rows:** 0  |  
**Columns:** 10  |  
**Foreign Keys:** 1

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| ItemId | int(10,0) | Yes | No |  |
| PkUnit | int(10,0) | Yes | No |  |
| PkFactor | decimal(18,2) | Yes | No |  |
| PurUnit | int(10,0) | Yes | No |  |
| PurFactor | decimal(18,2) | Yes | No |  |
| IssUnit | int(10,0) | Yes | No |  |
| IssFactor | decimal(18,2) | Yes | No |  |
| RecpUnit | int(10,0) | Yes | No |  |
| RecpFactor | decimal(18,2) | Yes | No |  |

#### Foreign Keys

| Constraint | Local Column | Referenced Table | Referenced Column |
|------------|--------------|------------------|-------------------|
| FK_ItemUnit_Item | ItemId | dbo.Item | ItemId |

---

### dbo.Item_Delete

**Rows:** 3,034  |  
**Columns:** 21  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| order_key | nvarchar(50) | Yes | No |  |
| order_num | nvarchar(50) | Yes | No |  |
| date | datetime | Yes | No |  |
| z_num | nvarchar(50) | Yes | No |  |
| operator | nvarchar(50) | Yes | No |  |
| category | nvarchar(50) | Yes | No |  |
| item | nvarchar(50) | Yes | No |  |
| qty | float(53,None) | Yes | No |  |
| price | float(53,None) | Yes | No |  |
| waiter | nvarchar(50) | Yes | No |  |
| order_type | nvarchar(50) | Yes | No |  |
| status | nvarchar(50) | Yes | No |  |
| shift | nvarchar(50) | Yes | No |  |
| tiltId | int(10,0) | Yes | No |  |
| CounterId | int(10,0) | Yes | No |  |
| Status1 | bit | No | No |  |
| is_upload | bit | No | No |  |
| is_update | bit | No | No |  |
| head_order_key | int(10,0) | Yes | No |  |
| unique_key | varchar(50) | Yes | No |  |

#### Sample Data (First 3 rows)

|    id |   order_key |   order_num | date                | z_num     | operator   | category   | item                    |   qty |   price | waiter            | order_type   | status   | shift   |   tiltId |   CounterId | Status1   | is_upload   | is_update   | head_order_key   | unique_key   |
|------:|------------:|------------:|:--------------------|:----------|:-----------|:-----------|:------------------------|------:|--------:|:------------------|:-------------|:---------|:--------|---------:|------------:|:----------|:------------|:------------|:-----------------|:-------------|
| 27757 |      417963 |        1257 | 2020-12-09 12:02:00 | DAY-00001 | PC-15      | ROLLS      | BEEF BEHARI ROLL        |     1 |     150 |                   | DELIVERY     | PC-15    |         |       46 |         399 | False     | False       | True        | None             | None         |
| 28819 |      420261 |        2580 | 2020-12-09 12:02:00 | DAY-00001 | PC 6       | BAR B Q    | CHICKEN RESHMI KABAB    |     1 |     420 | BABAR 03072027966 | DELIVERY     | PC 6     |         |       52 |         392 | False     | False       | True        | None             | None         |
| 28830 |      421685 |        3005 | 2020-12-09 12:02:00 | DAY-00001 | PC 6       | ROLLS      | BEEF BEHARI CHATNI ROLL |     2 |     300 |                   | DELIVERY     | PC 6     |         |       52 |         392 | False     | False       | True        | None             | None         |

---

### dbo.Item_Less

**Rows:** 480  |  
**Columns:** 25  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | No |  |
| order_key | nvarchar(50) | Yes | No |  |
| date | datetime | Yes | No |  |
| z_num | nvarchar(50) | Yes | No |  |
| operator | nvarchar(50) | Yes | No |  |
| category | nvarchar(50) | Yes | No |  |
| item | nvarchar(50) | Yes | No |  |
| qty | float(53,None) | Yes | No |  |
| price | float(53,None) | Yes | No |  |
| server | nvarchar(50) | Yes | No |  |
| order_type | nvarchar(50) | Yes | No |  |
| status | nvarchar(50) | Yes | No |  |
| shift | nvarchar(50) | Yes | No |  |
| tiltId | int(10,0) | Yes | No |  |
| CounterId | int(10,0) | Yes | No |  |
| Reason | nvarchar(-1) | Yes | No |  |
| Status1 | bit | No | No |  |
| OrderKey_Merege | nvarchar(50) | Yes | No |  |
| is_upload | bit | No | No |  |
| is_update | bit | No | No |  |
| Is_Served | bit | No | No |  |
| tax | decimal(18,2) | No | No |  |
| android_detail_id | int(10,0) | Yes | No |  |
| is_print | int(10,0) | Yes | No |  |
| unique_key | varchar(50) | Yes | No |  |

---

### dbo.Item_Transfer_Log

**Rows:** 0  |  
**Columns:** 11  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| Date | datetime | No | No |  |
| Z_Number | nvarchar(50) | No | No |  |
| Order_Key_To | nvarchar(50) | No | No |  |
| Order_Key_From | nvarchar(50) | No | No |  |
| Tiltid | int(10,0) | No | No |  |
| Counter_Id | int(10,0) | No | No |  |
| Loginuser | nvarchar(50) | No | No |  |
| Authenticate_User | nvarchar(50) | No | No |  |
| ItemId | int(10,0) | No | No |  |
| Qty | decimal(18,2) | No | No |  |

---

### dbo.Item_void

**Rows:** 0  |  
**Columns:** 25  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | No |  |
| order_key | nvarchar(50) | Yes | No |  |
| date | datetime | Yes | No |  |
| z_num | nvarchar(50) | Yes | No |  |
| operator | nvarchar(50) | Yes | No |  |
| category | nvarchar(50) | Yes | No |  |
| item | nvarchar(50) | Yes | No |  |
| qty | float(53,None) | Yes | No |  |
| price | float(53,None) | Yes | No |  |
| server | nvarchar(50) | Yes | No |  |
| order_type | nvarchar(50) | Yes | No |  |
| status | nvarchar(50) | Yes | No |  |
| shift | nvarchar(50) | Yes | No |  |
| tiltId | int(10,0) | Yes | No |  |
| CounterId | int(10,0) | Yes | No |  |
| Reason | nvarchar(-1) | Yes | No |  |
| Status1 | bit | No | No |  |
| OrderKey_Merege | nvarchar(50) | Yes | No |  |
| is_upload | bit | No | No |  |
| is_update | bit | No | No |  |
| less_after_bill | bit | Yes | No |  |
| android_detail_id | int(10,0) | Yes | No |  |
| is_print | int(10,0) | Yes | No |  |
| auto_id | int(10,0) | No | Yes |  |
| od_id | int(10,0) | Yes | No |  |

---

### dbo.JVDetail

**Rows:** 0  |  
**Columns:** 6  |  
**Foreign Keys:** 1

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| Amount | decimal(18,2) | Yes | No |  |
| CAId | int(10,0) | Yes | No |  |
| Type | varchar(40) | Yes | No |  |
| Desc | nvarchar(-1) | Yes | No |  |
| JVId | int(10,0) | Yes | No |  |

#### Foreign Keys

| Constraint | Local Column | Referenced Table | Referenced Column |
|------------|--------------|------------------|-------------------|
| JVMaster_JVDetail | JVId | dbo.JVMaster | JVId |

---

### dbo.JVMaster

**Rows:** 0  |  
**Columns:** 4  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| JVId | int(10,0) | No | Yes | (PK) |
| VN | nvarchar(40) | Yes | No |  |
| Date | datetime | Yes | No |  |
| COId | int(10,0) | Yes | No |  |

#### Primary Key
`JVId`

---

### dbo.KDS_Department_IP_Setting

**Rows:** 2  |  
**Columns:** 4  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| Did | int(10,0) | No | No |  |
| KDSIP | nvarchar(50) | No | No |  |
| TiltID | int(10,0) | Yes | No |  |

---

### dbo.KOTPrint

**Rows:** 1  |  
**Columns:** 2  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| KotPrint | int(10,0) | Yes | No |  |

---

### dbo.LoginStatus

**Rows:** 4,260  |  
**Columns:** 6  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| User | nvarchar(100) | Yes | No |  |
| Type | nvarchar(50) | Yes | No |  |
| Description | nvarchar(50) | Yes | No |  |
| Date | datetime | Yes | No |  |
| Time | nvarchar(50) | Yes | No |  |

#### Sample Data (First 3 rows)

|    id | User   | Type   | Description   | Date                | Time     |
|------:|:-------|:-------|:--------------|:--------------------|:---------|
| 40441 | PC 2   | Login  | Login         | 2020-12-12 00:00:00 | 04:44 AM |
| 40442 | PC-12  | Login  | Login         | 2020-12-12 00:00:00 | 11:12 AM |
| 40453 | pc 9   | Logout | Normal        | 2020-12-13 00:00:00 | 03:40 AM |

---

### dbo.MenuCategory

**Rows:** 3  |  
**Columns:** 2  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| Category | nvarchar(50) | Yes | No |  |

---

### dbo.MenuDetail

**Rows:** 2  |  
**Columns:** 4  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| ItemId | int(10,0) | Yes | No |  |
| MenuItem | nvarchar(50) | Yes | No |  |
| Qty | float(53,None) | Yes | No |  |

---

### dbo.MenuItem

**Rows:** 4  |  
**Columns:** 6  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| CategoryId | int(10,0) | Yes | No |  |
| Item | nvarchar(50) | Yes | No |  |
| Cover | int(10,0) | Yes | No |  |
| Price | float(53,None) | Yes | No |  |
| IsOpen | bit | Yes | No |  |

---

### dbo.OpenInventoryDetail

**Rows:** 0  |  
**Columns:** 7  |  
**Foreign Keys:** 2

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| OpenInvId | int(10,0) | Yes | No |  |
| ItemId | int(10,0) | Yes | No |  |
| Qty | decimal(18,2) | Yes | No |  |
| Rate | decimal(18,2) | Yes | No |  |
| Amount | decimal(18,2) | Yes | No |  |
| Unit | int(10,0) | Yes | No |  |

#### Foreign Keys

| Constraint | Local Column | Referenced Table | Referenced Column |
|------------|--------------|------------------|-------------------|
| FK_OpenInventoryDetail_OpenInventoryMaster | OpenInvId | dbo.OpenInventoryMaster | OpenInvId |
| FK_OpenInventoryDetail_Item | ItemId | dbo.Item | ItemId |

---

### dbo.OpenInventoryDetail_Department

**Rows:** 1,632  |  
**Columns:** 7  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| OpenInvId | int(10,0) | Yes | No |  |
| ItemId | int(10,0) | Yes | No |  |
| Qty | decimal(18,2) | Yes | No |  |
| Rate | decimal(18,2) | Yes | No |  |
| Amount | decimal(18,2) | Yes | No |  |
| Unit | int(10,0) | Yes | No |  |

---

### dbo.OpenInventoryMaster

**Rows:** 0  |  
**Columns:** 3  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| OpenInvId | int(10,0) | No | Yes | (PK) |
| Date | datetime | Yes | No |  |
| Type | nvarchar(50) | Yes | No |  |

#### Primary Key
`OpenInvId`

---

### dbo.OpenInventoryMaster_Department

**Rows:** 4  |  
**Columns:** 4  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| OpenInvId | int(10,0) | No | Yes |  |
| Date | datetime | Yes | No |  |
| Did | int(10,0) | No | No |  |
| Type | nvarchar(50) | Yes | No |  |

---

### dbo.OrderKot

**Rows:** 252,422  |  
**Columns:** 18  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| OrderKey | nvarchar(50) | Yes | No |  |
| ItemId | int(10,0) | Yes | No |  |
| Qty | float(53,None) | Yes | No |  |
| KotStatus | bit | Yes | No |  |
| Comments | nvarchar(50) | Yes | No |  |
| Tiltid | int(10,0) | Yes | No |  |
| ItemComment | nvarchar(-1) | No | No |  |
| LessReason | nvarchar(-1) | Yes | No |  |
| OrderDetailId | int(10,0) | No | No |  |
| OrderKey_Merege | nvarchar(50) | Yes | No |  |
| kotFromtablet | bit | No | No |  |
| tabkot | bit | No | No |  |
| IsKDS | bit | No | No |  |
| IsDispathed | bit | No | No |  |
| Order_type | nvarchar(50) | Yes | No |  |
| is_print | bit | Yes | No |  |
| Is_KDS | bit | Yes | No |  |

#### Sample Data (First 3 rows)

|      id |   OrderKey |   ItemId |   Qty | KotStatus   | Comments   |   Tiltid | ItemComment   | LessReason   |   OrderDetailId | OrderKey_Merege   | kotFromtablet   | tabkot   | IsKDS   | IsDispathed   | Order_type   | is_print   | Is_KDS   |
|--------:|-----------:|---------:|------:|:------------|:-----------|---------:|:--------------|:-------------|----------------:|:------------------|:----------------|:---------|:--------|:--------------|:-------------|:-----------|:---------|
| 1464402 |     415850 |     2492 |     1 | True        |            |       60 |               |              |         1461454 | None              | False           | False    | False   | False         | None         | False      | False    |
| 1465655 |     416198 |     2880 |     1 | True        |            |       59 |               |              |         1462702 | None              | False           | False    | True    | False         | None         | False      | False    |
| 1465896 |     416266 |     3935 |     1 | True        |            |       46 |               |              |         1462943 | None              | False           | False    | False   | False         | None         | False      | False    |

---

### dbo.OrderMaster

**Rows:** 0  |  
**Columns:** 13  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| Id | int(10,0) | No | Yes |  |
| OrderDate | datetime | Yes | No |  |
| Time | nvarchar(50) | Yes | No |  |
| CustomerId | int(10,0) | Yes | No |  |
| OrderNo | nvarchar(50) | Yes | No |  |
| isDelete | bit | Yes | No |  |
| TotalAmount | float(53,None) | Yes | No |  |
| Discount | float(53,None) | Yes | No |  |
| AmountBeforeDiscount | float(53,None) | Yes | No |  |
| Status | nvarchar(50) | Yes | No |  |
| VAT | float(53,None) | Yes | No |  |
| CLevy | float(53,None) | Yes | No |  |
| TaxType | nvarchar(50) | Yes | No |  |

---

### dbo.OrderOccassionDetail

**Rows:** 3  |  
**Columns:** 11  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| OccassionId | int(10,0) | No | Yes |  |
| OrderNo | nvarchar(50) | Yes | No |  |
| OccasionDate | datetime | Yes | No |  |
| OccasionTime | nvarchar(50) | Yes | No |  |
| Destination | nvarchar(50) | Yes | No |  |
| NoOfPersons | nvarchar(50) | Yes | No |  |
| ItemId | int(10,0) | Yes | No |  |
| TotalAmount | float(53,None) | Yes | No |  |
| OccassionOfPerson | float(53,None) | Yes | No |  |
| MenuDetail | nvarchar(-1) | Yes | No |  |
| Occassion | nvarchar(50) | Yes | No |  |

---

### dbo.OrderServedTime

**Rows:** 3  |  
**Columns:** 4  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| OrderType | nvarchar(50) | Yes | No |  |
| ServedTime | int(10,0) | Yes | No |  |
| DeliveredTime | int(10,0) | Yes | No |  |

---

### dbo.OrderStatusTime

**Rows:** 81,978  |  
**Columns:** 8  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| Order_Key | int(10,0) | Yes | No |  |
| BookTime | nvarchar(50) | Yes | No |  |
| AssignTime | nvarchar(50) | Yes | No |  |
| AssambleTime | nvarchar(50) | Yes | No |  |
| DispatchTime | nvarchar(50) | Yes | No |  |
| CompleteTime | nvarchar(50) | Yes | No |  |
| DeliveredTime | nvarchar(50) | Yes | No |  |

#### Sample Data (First 3 rows)

|     id |   Order_Key | BookTime   | AssignTime   | AssambleTime   | DispatchTime   | CompleteTime   |   DeliveredTime |
|-------:|------------:|:-----------|:-------------|:---------------|:---------------|:---------------|----------------:|
| 415390 |      416013 | 10:33 PM   | None         | None           | None           | None           |               0 |
| 417328 |      417950 | 12:18 PM   | None         | None           | None           | None           |               0 |
| 419630 |      420251 | 01:12 PM   | 01:12 PM     | None           | None           | None           |               0 |

---

### dbo.Order_Detail

**Rows:** 236,776  |  
**Columns:** 37  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| order_key | nvarchar(50) | Yes | No |  |
| date | datetime | Yes | No |  |
| z_number | nvarchar(50) | Yes | No |  |
| category_name | nvarchar(50) | Yes | No |  |
| item_name | nvarchar(50) | Yes | No |  |
| qty | float(53,None) | Yes | No |  |
| price | float(53,None) | Yes | No |  |
| tiltId | int(10,0) | Yes | No |  |
| CounterId | int(10,0) | Yes | No |  |
| Discount | decimal(18,2) | Yes | No |  |
| PriceBeforeDiscount | decimal(18,2) | Yes | No |  |
| Status | bit | Yes | No |  |
| OrderKey_Merege | nvarchar(50) | Yes | No |  |
| is_upload | bit | No | No |  |
| is_update | bit | No | No |  |
| ItemId | int(10,0) | No | No |  |
| Is_Open | bit | No | No |  |
| Unit | nvarchar(50) | Yes | No |  |
| Is_Served | bit | No | No |  |
| IsCommplimentary | bit | No | No |  |
| Commplimentary_Id | nvarchar(50) | Yes | No |  |
| Free | bit | No | No |  |
| ItemComplimentry_Amount | decimal(18,2) | No | No |  |
| Comments | nvarchar(-1) | Yes | No |  |
| Is_IsComments | bit | Yes | No |  |
| Is_AutoPunchItem | bit | No | No |  |
| Parent_Id | int(10,0) | No | No |  |
| is_transferBranch | int(10,0) | Yes | No |  |
| tax | decimal(18,2) | No | No |  |
| android_detail_id | int(10,0) | Yes | No |  |
| unique_key | varchar(50) | Yes | No |  |
| is_additional | bit | Yes | No |  |
| is_paid | bit | Yes | No |  |
| start_time | datetime | Yes | No |  |
| end_time | datetime | Yes | No |  |
| duration | varchar(50) | Yes | No |  |

#### Sample Data (First 3 rows)

|      id |   order_key | date                | z_number   | category_name    | item_name             |   qty |   price |   tiltId |   CounterId |   Discount |   PriceBeforeDiscount | Status   | OrderKey_Merege   | is_upload   | is_update   |   ItemId | Is_Open   | Unit   | Is_Served   | IsCommplimentary   | Commplimentary_Id   | Free   |   ItemComplimentry_Amount | Comments   | Is_IsComments   | Is_AutoPunchItem   |   Parent_Id |   is_transferBranch |   tax |   android_detail_id | unique_key   | is_additional   | is_paid   | start_time   | end_time   | duration   |
|--------:|------------:|:--------------------|:-----------|:-----------------|:----------------------|------:|--------:|---------:|------------:|-----------:|----------------------:|:---------|:------------------|:------------|:------------|---------:|:----------|:-------|:------------|:-------------------|:--------------------|:-------|--------------------------:|:-----------|:----------------|:-------------------|------------:|--------------------:|------:|--------------------:|:-------------|:----------------|:----------|:-------------|:-----------|:-----------|
| 1461026 |      415719 | 2020-12-09 12:15:00 | DAY-00001  | BAR B Q          | CHICKEN TIKKA (CHEST) |     1 |     250 |       46 |         376 |          0 |                   250 | False    | None              | False       | False       |     3680 | False     | None   | False       | False              | None                | False  |                         0 | * WASH     | True            | False              |     1461026 |                   0 |     0 |                   0 | None         | False           | False     | None         | None       | None       |
| 1461379 |      415830 | 2020-12-09 19:29:00 | DAY-00001  | Fruity Beverages | OREO SHAKE            |     1 |     290 |       59 |         385 |          0 |                   290 | False    | None              | False       | False       |     2588 | False     | None   | False       | False              | None                | False  |                         0 |            | False           | False              |     1461379 |                   0 |     0 |                   0 | None         | False           | False     | None         | None       | None       |
| 1462712 |      416200 | 2020-12-10 18:53:00 | DAY-00001  | BAR B Q          | CHICKEN MASALA BOTI   |     2 |     900 |       59 |         398 |          0 |                   900 | False    | None              | False       | False       |     2650 | False     | None   | False       | False              | None                | False  |                         0 |            | False           | False              |     1462712 |                   0 |     0 |                   0 | None         | False           | False     | None         | None       | None       |

---

### dbo.Order_Detail_ExtraItem

**Rows:** 0  |  
**Columns:** 5  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| Order_Detail_Id | int(10,0) | No | No |  |
| Extra_ItemId | int(10,0) | No | No |  |
| Extra_Item | nvarchar(50) | No | No |  |
| Price | decimal(18,2) | No | No |  |

---

### dbo.Order_Detail_ExtraItem_Temp

**Rows:** 0  |  
**Columns:** 5  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| Order_Detail_Id | int(10,0) | No | No |  |
| Extra_ItemId | int(10,0) | No | No |  |
| Extra_Item | nvarchar(50) | No | No |  |
| Price | decimal(18,2) | No | No |  |

---

### dbo.Order_Payment

**Rows:** 0  |  
**Columns:** 33  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| order_key | nvarchar(50) | No | No |  |
| date | datetime | Yes | No |  |
| z_number | nvarchar(50) | Yes | No |  |
| order_type | nvarchar(50) | Yes | No |  |
| cash_sale | float(53,None) | Yes | No |  |
| credit_sale | float(53,None) | Yes | No |  |
| sub_total | float(53,None) | Yes | No |  |
| discount | float(53,None) | Yes | No |  |
| tax | float(53,None) | Yes | No |  |
| net_sale | float(53,None) | Yes | No |  |
| net_bill | float(53,None) | Yes | No |  |
| is_delete | bit | Yes | No |  |
| ent | float(53,None) | Yes | No |  |
| Tiltid | int(10,0) | Yes | No |  |
| CounterId | int(10,0) | Yes | No |  |
| ServiceCharges | decimal(18,2) | Yes | No |  |
| Tip | decimal(18,2) | Yes | No |  |
| ExtraCharges | decimal(18,2) | Yes | No |  |
| CreditCardNo | nvarchar(50) | Yes | No |  |
| Status | bit | No | No |  |
| AdvanceBookingCode | nvarchar(50) | Yes | No |  |
| Description | nvarchar(50) | Yes | No |  |
| Advance | decimal(18,2) | No | No |  |
| VoucherAmount | decimal(18,2) | Yes | No |  |
| VoucherQty | float(53,None) | Yes | No |  |
| is_upload | bit | No | No |  |
| is_update | bit | No | No |  |
| bank | nvarchar(50) | Yes | No |  |
| time | nvarchar(50) | Yes | No |  |
| Date_time | datetime | Yes | No |  |
| ItemComplimentry_Amount | decimal(18,2) | No | No |  |
| unique_key | varchar(50) | Yes | No |  |

---

### dbo.POSSaleAccount

**Rows:** 0  |  
**Columns:** 4  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| AccountNo | nvarchar(50) | Yes | No |  |
| SaleType | nvarchar(50) | Yes | No |  |
| Type | nvarchar(50) | Yes | No |  |

---

### dbo.POSSaleReturnDetail

**Rows:** 0  |  
**Columns:** 10  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| Sid | int(10,0) | Yes | No |  |
| item_name | nvarchar(50) | Yes | No |  |
| qty | float(53,None) | Yes | No |  |
| price | float(53,None) | Yes | No |  |
| Category | nvarchar(50) | Yes | No |  |
| DealDescription | nvarchar(-1) | Yes | No |  |
| is_upload | bit | No | No |  |
| is_update | bit | No | No |  |
| unique_key | varchar(50) | Yes | No |  |

---

### dbo.POSSaleReturnMaster

**Rows:** 0  |  
**Columns:** 22  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| Sid | int(10,0) | No | Yes |  |
| Date | datetime | Yes | No |  |
| SRNo | nvarchar(50) | Yes | No |  |
| OrderKey | nvarchar(50) | Yes | No |  |
| OrderType | nvarchar(50) | Yes | No |  |
| Amount | float(53,None) | Yes | No |  |
| User | nvarchar(50) | Yes | No |  |
| Tiltid | int(10,0) | Yes | No |  |
| ShiftNo | nvarchar(50) | Yes | No |  |
| CounterId | int(10,0) | Yes | No |  |
| IsComplete | bit | Yes | No |  |
| Tax | float(53,None) | Yes | No |  |
| Discount | float(53,None) | Yes | No |  |
| SCharges | float(53,None) | Yes | No |  |
| ECharges | float(53,None) | Yes | No |  |
| Reason | nvarchar(-1) | Yes | No |  |
| Status | bit | No | No |  |
| SaleReturnTime | nvarchar(50) | Yes | No |  |
| is_upload | bit | No | No |  |
| is_update | bit | No | No |  |
| Date_time | datetime | Yes | No |  |
| unique_key | varchar(50) | Yes | No |  |

---

### dbo.POSTransectionSetting

**Rows:** 96  |  
**Columns:** 3  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| type | nvarchar(50) | Yes | No |  |
| status | bit | Yes | No |  |

---

### dbo.POS_Default_Settings

**Rows:** 0  |  
**Columns:** 8  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| shift_operation | bit | No | No |  |
| company_name | nvarchar(50) | Yes | No |  |
| franchise_name | nvarchar(50) | Yes | No |  |
| opening_report | bit | Yes | No |  |
| closing_report | bit | Yes | No |  |
| no_of_z_report | int(10,0) | Yes | No |  |
| phone_no | nvarchar(50) | Yes | No |  |
| branch_id | nvarchar(50) | Yes | No |  |

---

### dbo.POS_Expense

**Rows:** 0  |  
**Columns:** 9  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| Type | nchar(10) | No | No |  |
| Vn | nvarchar(50) | No | No |  |
| VoucherId | int(10,0) | Yes | No |  |
| date | datetime | No | No |  |
| Amount | decimal(18,2) | No | No |  |
| CAId | int(10,0) | No | No |  |
| Vouchertype | nvarchar(50) | No | No |  |
| Desc | nvarchar(-1) | Yes | No |  |

---

### dbo.POS_Expense_Account

**Rows:** 0  |  
**Columns:** 3  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| Account | nvarchar(50) | No | No |  |
| CAId | int(10,0) | No | No |  |

---

### dbo.POsExpenseSetting

**Rows:** 0  |  
**Columns:** 2  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| Amount | decimal(18,2) | No | No |  |

---

### dbo.PaymentVoucher

**Rows:** 0  |  
**Columns:** 7  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| PVId | int(10,0) | No | Yes | (PK) |
| Date | datetime | Yes | No |  |
| SPId | int(10,0) | Yes | No |  |
| Amount | decimal(18,2) | Yes | No |  |
| PaymentMode | varchar(40) | Yes | No |  |
| COId | int(10,0) | Yes | No |  |
| Type | nvarchar(50) | Yes | No |  |

#### Primary Key
`PVId`

---

### dbo.PhysicalStockDetail_Branch

**Rows:** 0  |  
**Columns:** 6  |  
**Foreign Keys:** 2

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| PSBRId | int(10,0) | Yes | No |  |
| ItemId | int(10,0) | Yes | No |  |
| UnitId | int(10,0) | Yes | No |  |
| Qty | decimal(18,2) | Yes | No |  |
| Amount | decimal(18,2) | Yes | No |  |

#### Foreign Keys

| Constraint | Local Column | Referenced Table | Referenced Column |
|------------|--------------|------------------|-------------------|
| FK_PhysicalStockDetail_Branch_PhysicalStockMaster_Branch | PSBRId | dbo.PhysicalStockMaster_Branch | PSBRId |
| FK_PhysicalStockDetail_Branch_Item | ItemId | dbo.Item | ItemId |

---

### dbo.PhysicalStockDetail_Store

**Rows:** 0  |  
**Columns:** 6  |  
**Foreign Keys:** 2

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| PSId | int(10,0) | Yes | No |  |
| ItemId | int(10,0) | Yes | No |  |
| UId | int(10,0) | Yes | No |  |
| Qty | decimal(18,2) | Yes | No |  |
| Amount | decimal(18,2) | Yes | No |  |

#### Foreign Keys

| Constraint | Local Column | Referenced Table | Referenced Column |
|------------|--------------|------------------|-------------------|
| FK_PhysicalStockDetail_Store_PhysicalStockMaster_Store | PSId | dbo.PhysicalStockMaster_Store | PSId |
| FK_PhysicalStockDetail_Store_Item | ItemId | dbo.Item | ItemId |

---

### dbo.PhysicalStockMaster_Branch

**Rows:** 0  |  
**Columns:** 6  |  
**Foreign Keys:** 1

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| PSBRId | int(10,0) | No | Yes | (PK) |
| Date | datetime | Yes | No |  |
| PSNO | nvarchar(50) | Yes | No |  |
| BRId | int(10,0) | Yes | No |  |
| DId | int(10,0) | Yes | No |  |
| Desc | nvarchar(-1) | Yes | No |  |

#### Primary Key
`PSBRId`

#### Foreign Keys

| Constraint | Local Column | Referenced Table | Referenced Column |
|------------|--------------|------------------|-------------------|
| FK_PhysicalStockMaster_Branch_Branch | BRId | dbo.Branch | BRId |

---

### dbo.PhysicalStockMaster_Store

**Rows:** 0  |  
**Columns:** 5  |  
**Foreign Keys:** 1

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| PSId | int(10,0) | No | Yes | (PK) |
| Date | datetime | Yes | No |  |
| PSNO | nvarchar(50) | Yes | No |  |
| SId | int(10,0) | Yes | No |  |
| Desc | nvarchar(-1) | Yes | No |  |

#### Primary Key
`PSId`

#### Foreign Keys

| Constraint | Local Column | Referenced Table | Referenced Column |
|------------|--------------|------------------|-------------------|
| FK_PhysicalStockMaster_Store_Store | SId | dbo.Store | SId |

---

### dbo.PosSale

**Rows:** 0  |  
**Columns:** 8  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| z_num | nvarchar(50) | Yes | No |  |
| Date | datetime | Yes | No |  |
| Amount | float(53,None) | Yes | No |  |
| Type | nvarchar(50) | Yes | No |  |
| VN | nvarchar(50) | Yes | No |  |
| Desc | text(2147483647) | Yes | No |  |
| Account | nvarchar(50) | Yes | No |  |

---

### dbo.Printer_Setup

**Rows:** 0  |  
**Columns:** 5  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| printer | nvarchar(50) | Yes | No |  |
| department | nvarchar(50) | Yes | No |  |
| document | nvarchar(50) | Yes | No |  |
| TiltId | int(10,0) | Yes | No |  |

---

### dbo.ProductSaleDetail

**Rows:** 0  |  
**Columns:** 8  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| PMID | int(10,0) | Yes | No |  |
| IngredientId | int(10,0) | Yes | No |  |
| PackingRatePerPcs | decimal(18,2) | Yes | No |  |
| InventoryRatePerPcs | decimal(18,2) | Yes | No |  |
| RecipeRatePerPcs | decimal(18,2) | Yes | No |  |
| IngredientQty | decimal(18,4) | No | No |  |
| IngredientAmount | decimal(18,2) | Yes | No |  |

---

### dbo.ProductSaleMaster

**Rows:** 0  |  
**Columns:** 4  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| PMID | int(10,0) | No | Yes |  |
| ProductId | int(10,0) | Yes | No |  |
| ZNumber | nvarchar(50) | Yes | No |  |
| Date | datetime | Yes | No |  |

---

### dbo.ProductionDetail

**Rows:** 0  |  
**Columns:** 6  |  
**Foreign Keys:** 1

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| PRId | int(10,0) | Yes | No |  |
| ItemId | int(10,0) | Yes | No |  |
| UnitId | int(10,0) | Yes | No |  |
| Qty | decimal(18,2) | Yes | No |  |
| RatePerPcs | decimal(18,2) | Yes | No |  |

#### Foreign Keys

| Constraint | Local Column | Referenced Table | Referenced Column |
|------------|--------------|------------------|-------------------|
| FK_ProductionDetail_ProductionMaster | PRId | dbo.ProductionMaster | PRId |

---

### dbo.ProductionDetailDepartment

**Rows:** 18  |  
**Columns:** 6  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| PRId | int(10,0) | Yes | No |  |
| ItemId | int(10,0) | Yes | No |  |
| UnitId | int(10,0) | Yes | No |  |
| Qty | decimal(18,2) | Yes | No |  |
| RatePerPcs | decimal(18,2) | Yes | No |  |

---

### dbo.ProductionMaster

**Rows:** 0  |  
**Columns:** 5  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| PRId | int(10,0) | No | Yes | (PK) |
| Date | datetime | Yes | No |  |
| PRNo | nvarchar(50) | Yes | No |  |
| Sid | int(10,0) | Yes | No |  |
| Amount | int(10,0) | Yes | No |  |

#### Primary Key
`PRId`

---

### dbo.ProductionMasterDepartment

**Rows:** 14  |  
**Columns:** 7  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| PRId | int(10,0) | No | Yes | (PK) |
| Date | datetime | Yes | No |  |
| PRNo | nvarchar(50) | Yes | No |  |
| Sid | int(10,0) | Yes | No |  |
| Amount | int(10,0) | Yes | No |  |
| BRId | int(10,0) | Yes | No |  |
| Did | int(10,0) | Yes | No |  |

#### Primary Key
`PRId`

---

### dbo.ProfitLossSettings

**Rows:** 3  |  
**Columns:** 5  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| Section | nvarchar(50) | Yes | No |  |
| AccNoFrom | int(10,0) | Yes | No |  |
| AccNoTo | int(10,0) | Yes | No |  |
| Title | nvarchar(50) | Yes | No |  |

---

### dbo.PurchaseOrderDetail_Store

**Rows:** 0  |  
**Columns:** 10  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| POId | int(10,0) | Yes | No |  |
| ItemId | int(10,0) | Yes | No |  |
| UId | int(10,0) | Yes | No |  |
| Rate | decimal(18,2) | Yes | No |  |
| Amount | decimal(18,2) | Yes | No |  |
| Qty | decimal(18,2) | Yes | No |  |
| DSCOId | int(10,0) | Yes | No |  |
| Status | bit | Yes | No |  |
| RecQty | decimal(18,2) | Yes | No |  |

---

### dbo.PurchaseOrderMaster_Store

**Rows:** 0  |  
**Columns:** 9  |  
**Foreign Keys:** 3

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| POId | int(10,0) | No | Yes | (PK) |
| Date | datetime | Yes | No |  |
| COId | int(10,0) | Yes | No |  |
| PONo | varchar(50) | Yes | No |  |
| VId | int(10,0) | Yes | No |  |
| Status | bit | Yes | No |  |
| UserId | int(10,0) | Yes | No |  |
| SId | int(10,0) | Yes | No |  |
| Desc | nvarchar(-1) | Yes | No |  |

#### Primary Key
`POId`

#### Foreign Keys

| Constraint | Local Column | Referenced Table | Referenced Column |
|------------|--------------|------------------|-------------------|
| FK_PurchaseOrderMaster_Store_Company | COId | dbo.Company | COId |
| FK_PurchaseOrderMaster_Store_Vendor | VId | dbo.Vendor | VId |
| FK_PurchaseOrderMaster_Store_Store | SId | dbo.Store | SId |

---

### dbo.PurchaseReturnDetail

**Rows:** 0  |  
**Columns:** 19  |  
**Foreign Keys:** 1

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| Id | int(10,0) | No | Yes |  |
| PRId | int(10,0) | Yes | No |  |
| ItemId | int(10,0) | Yes | No |  |
| Unit | int(10,0) | Yes | No |  |
| Rate | decimal(18,2) | Yes | No |  |
| Qty | decimal(18,2) | Yes | No |  |
| POId | int(10,0) | Yes | No |  |
| TotalPackage | decimal(18,2) | Yes | No |  |
| PcsPerPackage | decimal(18,2) | Yes | No |  |
| RatePerPackage | decimal(18,2) | Yes | No |  |
| PackageId | int(10,0) | Yes | No |  |
| GRNId | int(10,0) | Yes | No |  |
| DSCOId | int(10,0) | Yes | No |  |
| DiscountPerPcs | decimal(18,2) | Yes | No |  |
| TaxPerPcs | decimal(18,2) | Yes | No |  |
| TaxType | nvarchar(50) | Yes | No |  |
| NetAmount | decimal(18,2) | Yes | No |  |
| Amount | decimal(18,2) | Yes | No |  |
| TaxMode | int(10,0) | Yes | No |  |

#### Foreign Keys

| Constraint | Local Column | Referenced Table | Referenced Column |
|------------|--------------|------------------|-------------------|
| FK_PurchaseReturnDetail_PurchaseReturnMaster | PRId | dbo.PurchaseReturnMaster | PRId |

---

### dbo.PurchaseReturnDetailNew

**Rows:** 0  |  
**Columns:** 16  |  
**Foreign Keys:** 2

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| PRId | int(10,0) | Yes | No |  |
| ItemId | int(10,0) | Yes | No |  |
| Unit | int(10,0) | Yes | No |  |
| Qty | decimal(18,2) | Yes | No |  |
| POId | int(10,0) | Yes | No |  |
| Rate | decimal(18,2) | Yes | No |  |
| TotalPackage | decimal(18,2) | Yes | No |  |
| PcsPerPackage | decimal(18,2) | Yes | No |  |
| RatePerPackage | decimal(18,2) | Yes | No |  |
| PackageId | int(10,0) | Yes | No |  |
| Tax | decimal(18,2) | Yes | No |  |
| Discount | decimal(18,2) | Yes | No |  |
| Amount | decimal(18,2) | Yes | No |  |
| ActualRate | decimal(18,2) | Yes | No |  |
| TaxType | nvarchar(50) | Yes | No |  |

#### Foreign Keys

| Constraint | Local Column | Referenced Table | Referenced Column |
|------------|--------------|------------------|-------------------|
| FK_PurchaseReturnDetailNew_Item | ItemId | dbo.Item | ItemId |
| FK_PurchaseReturnDetailNew_Store_PurchaseReturnMasterNew_Store | PRId | dbo.PurchaseReturnMasterNew | PRId |

---

### dbo.PurchaseReturnMaster

**Rows:** 0  |  
**Columns:** 14  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| PRId | int(10,0) | No | Yes | (PK) |
| Date | datetime | Yes | No |  |
| UserId | int(10,0) | Yes | No |  |
| VId | int(10,0) | Yes | No |  |
| PRNo | nvarchar(50) | Yes | No |  |
| SId | int(10,0) | Yes | No |  |
| BRId | int(10,0) | Yes | No |  |
| Amount | decimal(18,2) | Yes | No |  |
| Discount | decimal(18,2) | Yes | No |  |
| TotalAmount | decimal(18,2) | Yes | No |  |
| InvoiceId | int(10,0) | Yes | No |  |
| RefNo | nvarchar(50) | Yes | No |  |
| TotalTax | decimal(18,2) | Yes | No |  |
| COId | int(10,0) | Yes | No |  |

#### Primary Key
`PRId`

---

### dbo.PurchaseReturnMasterNew

**Rows:** 0  |  
**Columns:** 12  |  
**Foreign Keys:** 2

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| PRId | int(10,0) | No | Yes | (PK) |
| Date | datetime | Yes | No |  |
| VId | int(10,0) | Yes | No |  |
| GRNId | int(10,0) | Yes | No |  |
| PRNo | varchar(50) | Yes | No |  |
| SId | int(10,0) | Yes | No |  |
| BRId | int(10,0) | Yes | No |  |
| Amount | decimal(18,2) | Yes | No |  |
| Discount | decimal(18,2) | Yes | No |  |
| TotalAmount | decimal(18,2) | Yes | No |  |
| RefrenceNo | nvarchar(50) | Yes | No |  |
| TotalTax | decimal(18,2) | Yes | No |  |

#### Primary Key
`PRId`

#### Foreign Keys

| Constraint | Local Column | Referenced Table | Referenced Column |
|------------|--------------|------------------|-------------------|
| FK_PurchaseReturnMasterNew_GRNMaster | GRNId | dbo.GRNMaster | GRNId |
| FK_PurchaseReturnMasterNew_Vendor1 | VId | dbo.Vendor | VId |

---

### dbo.Reasons

**Rows:** 0  |  
**Columns:** 2  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| Reason | nvarchar(-1) | No | No |  |

---

### dbo.ReceiptVoucher

**Rows:** 0  |  
**Columns:** 7  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| RVId | int(10,0) | No | Yes | (PK) |
| Date | datetime | Yes | No |  |
| CustId | int(10,0) | Yes | No |  |
| Amount | decimal(18,2) | Yes | No |  |
| ReceiptMode | nvarchar(50) | Yes | No |  |
| COId | int(10,0) | Yes | No |  |
| Type | nvarchar(50) | Yes | No |  |

#### Primary Key
`RVId`

---

### dbo.RecipeDetail

**Rows:** 0  |  
**Columns:** 8  |  
**Foreign Keys:** 2

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| RecipeId | int(10,0) | Yes | No |  |
| IngredientId | int(10,0) | Yes | No |  |
| Qty | float(53,None) | Yes | No |  |
| IsSubRecipe | bit | Yes | No |  |
| is_DineIn | bit | Yes | No |  |
| Is_TakeAway | bit | Yes | No |  |
| Is_Delivery | bit | Yes | No |  |

#### Foreign Keys

| Constraint | Local Column | Referenced Table | Referenced Column |
|------------|--------------|------------------|-------------------|
| FK_RecipeDetail_Item | IngredientId | dbo.Item | ItemId |
| FK_RecipeDetail_RecipeMaster | RecipeId | dbo.RecipeMaster | RecipeId |

---

### dbo.RecipeMaster

**Rows:** 0  |  
**Columns:** 6  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| RecipeId | int(10,0) | No | Yes | (PK) |
| ProductId | int(10,0) | Yes | No |  |
| max_FP_Cost | decimal(18,2) | No | No |  |
| min_SP_Price | decimal(18,2) | No | No |  |
| Current_FP_Cost | decimal(18,2) | No | No |  |
| Comments | nvarchar(-1) | Yes | No |  |

#### Primary Key
`RecipeId`

---

### dbo.Reports_Settings

**Rows:** 1  |  
**Columns:** 4  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| reports_footer | nvarchar(500) | Yes | No |  |
| reports_footer2 | nvarchar(500) | Yes | No |  |
| bill1_header | varchar(50) | Yes | No |  |
| bill2_header | varchar(50) | Yes | No |  |

---

### dbo.Rider

**Rows:** 0  |  
**Columns:** 5  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| RiderId | int(10,0) | Yes | No |  |
| name | nvarchar(50) | Yes | No |  |
| Commision | decimal(18,2) | No | No |  |
| IsPercent | bit | No | No |  |

---

### dbo.RiderCashFloat

**Rows:** 0  |  
**Columns:** 14  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| ShiftNo | nvarchar(50) | Yes | No |  |
| Rider | nvarchar(-1) | Yes | No |  |
| CheackIn | nvarchar(50) | Yes | No |  |
| OpeningAmount | float(53,None) | Yes | No |  |
| CheackOut | nvarchar(50) | Yes | No |  |
| ClosingAmount | float(53,None) | Yes | No |  |
| Date | datetime | Yes | No |  |
| CheackInDate | datetime | Yes | No |  |
| CheackOutDate | datetime | Yes | No |  |
| ChkInStatus | bit | Yes | No |  |
| ChkOutStatus | bit | Yes | No |  |
| ReadingIn | int(10,0) | No | No |  |
| ReadingOut | int(10,0) | No | No |  |

---

### dbo.SMSLog

**Rows:** 6,014  |  
**Columns:** 6  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| Order_Key | int(10,0) | Yes | No |  |
| MobileNo | nvarchar(50) | Yes | No |  |
| Message | nvarchar(-1) | Yes | No |  |
| SentTime | nvarchar(50) | Yes | No |  |
| IsSent | bit | Yes | No |  |

#### Sample Data (First 3 rows)

|   id |   Order_Key |    MobileNo | Message                                            | SentTime   | IsSent   |
|-----:|------------:|------------:|:---------------------------------------------------|:-----------|:---------|
|  105 |       49019 | 03333864919 | Customer:Ali Makawa Eatoye, Order#27816, Thank You | None       | True     |
|  106 |       49020 | 03332107803 | Customer:Sana Akram FP, Order#27817, Thank You!!!  | None       | True     |
|  107 |       49021 | 03232549443 | Customer:Fahad sahib fp online payment, Order#2781 | None       | True     |

---

### dbo.SMS_Setup

**Rows:** 1  |  
**Columns:** 5  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| ID | int(10,0) | No | Yes | (PK) |
| UserID | nvarchar(-1) | No | No |  |
| Password | nvarchar(-1) | Yes | No |  |
| Mask | nvarchar(-1) | Yes | No |  |
| URL | nvarchar(-1) | Yes | No |  |

#### Primary Key
`ID`

---

### dbo.SaleInvoiceDetail

**Rows:** 0  |  
**Columns:** 5  |  
**Foreign Keys:** 1

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| Desc | nvarchar(-1) | Yes | No |  |
| Amount | decimal(18,2) | Yes | No |  |
| SaleInvoiceId | int(10,0) | Yes | No |  |
| CAId | int(10,0) | Yes | No |  |

#### Foreign Keys

| Constraint | Local Column | Referenced Table | Referenced Column |
|------------|--------------|------------------|-------------------|
| SaleInvoiceMaster_SaleInvoiceDetail | SaleInvoiceId | dbo.SaleInvoiceMaster | SaleInvoiceId |

---

### dbo.SaleInvoiceMaster

**Rows:** 0  |  
**Columns:** 11  |  
**Foreign Keys:** 3

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| SaleInvoiceId | int(10,0) | No | Yes | (PK) |
| SaleInvoiceNo | nvarchar(40) | Yes | No |  |
| UserId | int(10,0) | Yes | No |  |
| Date | datetime | Yes | No |  |
| Amount | decimal(18,2) | Yes | No |  |
| Discount | decimal(18,2) | Yes | No |  |
| TotalAmount | decimal(18,2) | Yes | No |  |
| IsFixAsset | bit | Yes | No |  |
| CustId | int(10,0) | Yes | No |  |
| COId | int(10,0) | Yes | No |  |
| ProId | int(10,0) | Yes | No |  |

#### Primary Key
`SaleInvoiceId`

#### Foreign Keys

| Constraint | Local Column | Referenced Table | Referenced Column |
|------------|--------------|------------------|-------------------|
| FK_SaleInvoiceMaster_Company | COId | dbo.Company | COId |
| FK_SaleInvoiceMaster_Customer | CustId | dbo.Customer | CustId |
| Customer_SaleInvoiceMaster | CustId | dbo.Customer | CustId |

---

### dbo.ServerTiltAssign

**Rows:** 0  |  
**Columns:** 3  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| ServerId | int(10,0) | Yes | No |  |
| Tiltid | int(10,0) | Yes | No |  |

---

### dbo.ServiceCharges

**Rows:** 1  |  
**Columns:** 9  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| Percent | decimal(18,2) | Yes | No |  |
| IsApplicable | bit | Yes | No |  |
| AppylOnCovers | bit | Yes | No |  |
| OnCovers | int(10,0) | Yes | No |  |
| ApplyOnAmount | bit | Yes | No |  |
| OnAmount | float(53,None) | Yes | No |  |
| Company_Percent | decimal(18,2) | Yes | No |  |
| Waiter_Percent | decimal(18,2) | Yes | No |  |

---

### dbo.SheeshaTime

**Rows:** 1  |  
**Columns:** 4  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| time | nvarchar(50) | Yes | No |  |
| cashDrop | decimal(18,2) | No | No |  |
| CashDropTime | int(10,0) | No | No |  |

---

### dbo.ShiftAmount

**Rows:** 17  |  
**Columns:** 26  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| TiltId | int(10,0) | Yes | No |  |
| Z_Number | nvarchar(50) | Yes | No |  |
| OpeningAmount | decimal(18,2) | Yes | No |  |
| ClosingAmount | decimal(18,2) | Yes | No |  |
| TimeIn | nvarchar(50) | Yes | No |  |
| TimeOut | nvarchar(50) | Yes | No |  |
| IsActive | bit | Yes | No |  |
| OpeningDate | datetime | Yes | No |  |
| ClosingDate | datetime | Yes | No |  |
| OpenedBy | nvarchar(50) | Yes | No |  |
| ClosedBy | nvarchar(50) | Yes | No |  |
| Ten | nvarchar(50) | Yes | No |  |
| Twenty | nvarchar(50) | Yes | No |  |
| Fifty | nvarchar(50) | Yes | No |  |
| Hundred | nvarchar(50) | Yes | No |  |
| FiveHundred | nvarchar(50) | Yes | No |  |
| Thousands | nvarchar(50) | Yes | No |  |
| FiveThousands | nvarchar(50) | Yes | No |  |
| TenThousands | nvarchar(50) | Yes | No |  |
| One | nvarchar(50) | No | No |  |
| Two | nvarchar(50) | No | No |  |
| five | nvarchar(50) | No | No |  |
| is_upload | bit | No | No |  |
| is_update | bit | No | No |  |
| id_ | int(10,0) | No | No |  |

---

### dbo.ShiftClosingTime

**Rows:** 0  |  
**Columns:** 3  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| Shift | nvarchar(50) | Yes | No |  |
| ClosingTime | nvarchar(50) | Yes | No |  |

---

### dbo.Shift_Account_Detail

**Rows:** 0  |  
**Columns:** 4  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| ID | int(10,0) | No | Yes | (PK) |
| z_number | nvarchar(50) | Yes | No |  |
| payment_type | nvarchar(50) | Yes | No |  |
| Amount | decimal(18,2) | Yes | No |  |

#### Primary Key
`ID`

---

### dbo.Shift_Opening

**Rows:** 1  |  
**Columns:** 13  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| opening_date | datetime | Yes | No |  |
| opening_day | nvarchar(50) | Yes | No |  |
| shift_name | nvarchar(50) | Yes | No |  |
| z_report_number | nvarchar(50) | Yes | No |  |
| opening_person | nvarchar(50) | Yes | No |  |
| closing_person | nvarchar(50) | Yes | No |  |
| opening_time | nvarchar(50) | Yes | No |  |
| closing_time | nvarchar(50) | Yes | No |  |
| status | bit | Yes | No |  |
| tiltid | int(10,0) | Yes | No |  |
| is_upload | bit | No | No |  |
| is_update | bit | No | No |  |

---

### dbo.Shift_User

**Rows:** 18  |  
**Columns:** 3  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| user_name | nvarchar(50) | Yes | No |  |
| shift_name | nvarchar(50) | Yes | No |  |

---

### dbo.Shifts

**Rows:** 3  |  
**Columns:** 3  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| shift_id | int(10,0) | No | Yes |  |
| shift_name | nvarchar(50) | Yes | No |  |
| z_report_prefix | nvarchar(50) | Yes | No |  |

---

### dbo.SmsSetting

**Rows:** 1  |  
**Columns:** 5  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| a | nvarchar(50) | Yes | No |  |
| b | nvarchar(-1) | Yes | No |  |
| c | nvarchar(50) | Yes | No |  |
| OrderType | nvarchar(100) | Yes | No |  |

---

### dbo.Step_Deal

**Rows:** 0  |  
**Columns:** 13  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| Deal_Id | int(10,0) | No | No |  |
| Dealname | nvarchar(50) | No | No |  |
| Steps | int(10,0) | No | No |  |
| PriceOnstep | int(10,0) | No | No |  |
| Step_id | int(10,0) | No | No |  |
| Step | nchar(10) | No | No |  |
| Category_id | int(10,0) | No | No |  |
| Item_Id | int(10,0) | No | No |  |
| Item_Qty | decimal(18,2) | No | No |  |
| Is_PriceItem | bit | No | No |  |
| Item_Price | decimal(18,2) | No | No |  |
| DealPrice | decimal(18,2) | No | No |  |

---

### dbo.Step_Deal_Items

**Rows:** 0  |  
**Columns:** 19  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| Order_key | nvarchar(50) | No | No |  |
| Order_Detail_Id | int(10,0) | No | No |  |
| Deal_Id | int(10,0) | No | No |  |
| Dealname | nvarchar(50) | No | No |  |
| Steps | int(10,0) | No | No |  |
| PriceOnstep | int(10,0) | No | No |  |
| Step_id | int(10,0) | No | No |  |
| Step | nchar(10) | No | No |  |
| Category_id | int(10,0) | No | No |  |
| Item_Id | int(10,0) | No | No |  |
| Item_Qty | decimal(18,2) | No | No |  |
| Is_PriceItem | bit | No | No |  |
| Item_Price | decimal(18,2) | No | No |  |
| DealPrice | decimal(18,2) | No | No |  |
| DealQty | decimal(18,2) | No | No |  |
| Item | nvarchar(50) | Yes | No |  |
| Price_Item | decimal(18,2) | No | No |  |
| item_comment | nvarchar(50) | Yes | No |  |

---

### dbo.Step_Deal_Items_Temp

**Rows:** 0  |  
**Columns:** 14  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| Order_key | nvarchar(50) | No | No |  |
| Order_Detail_Id | int(10,0) | No | No |  |
| Deal_Id | int(10,0) | No | No |  |
| Dealname | nvarchar(50) | No | No |  |
| Steps | int(10,0) | No | No |  |
| PriceOnstep | int(10,0) | No | No |  |
| Step_id | int(10,0) | No | No |  |
| Step | nchar(10) | No | No |  |
| Category_id | int(10,0) | No | No |  |
| Item_Id | int(10,0) | No | No |  |
| Item_Qty | decimal(18,2) | No | No |  |
| Is_PriceItem | bit | No | No |  |
| Item_Price | decimal(18,2) | No | No |  |

---

### dbo.Store

**Rows:** 0  |  
**Columns:** 6  |  
**Foreign Keys:** 1

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| SId | int(10,0) | No | Yes | (PK) |
| Store | nvarchar(50) | Yes | No |  |
| CentarlStore | bit | Yes | No |  |
| COId | int(10,0) | Yes | No |  |
| IsSelected | bit | Yes | No |  |
| BrId | int(10,0) | No | No |  |

#### Primary Key
`SId`

#### Foreign Keys

| Constraint | Local Column | Referenced Table | Referenced Column |
|------------|--------------|------------------|-------------------|
| FK_Store_Company | COId | dbo.Company | COId |

---

### dbo.SubCategory

**Rows:** 0  |  
**Columns:** 3  |  
**Foreign Keys:** 1

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| SBId | int(10,0) | No | Yes | (PK) |
| CId | int(10,0) | Yes | No |  |
| SubCategory | nvarchar(50) | Yes | No |  |

#### Primary Key
`SBId`

#### Foreign Keys

| Constraint | Local Column | Referenced Table | Referenced Column |
|------------|--------------|------------------|-------------------|
| FK_SubCategory_Category1 | CId | dbo.Category | CId |

---

### dbo.SubRecipeDetail

**Rows:** 0  |  
**Columns:** 4  |  
**Foreign Keys:** 1

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| SubRecipeId | int(10,0) | Yes | No |  |
| IngredientId | int(10,0) | Yes | No |  |
| Qty | float(53,None) | Yes | No |  |

#### Foreign Keys

| Constraint | Local Column | Referenced Table | Referenced Column |
|------------|--------------|------------------|-------------------|
| FK_SubRecipeDetail_SubRecipeMaster | SubRecipeId | dbo.SubRecipeMaster | SubRecipeId |

---

### dbo.SubRecipeMaster

**Rows:** 0  |  
**Columns:** 6  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| SubRecipeId | int(10,0) | No | Yes | (PK) |
| ProductId | int(10,0) | Yes | No |  |
| max_FP_Cost | decimal(18,2) | No | No |  |
| min_SP_Price | decimal(18,2) | No | No |  |
| Current_FP_Cost | decimal(18,2) | No | No |  |
| Comments | nvarchar(-1) | Yes | No |  |

#### Primary Key
`SubRecipeId`

---

### dbo.SupplierLedger

**Rows:** 0  |  
**Columns:** 11  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| VId | int(10,0) | Yes | No |  |
| VoucherId | int(10,0) | Yes | No |  |
| Amount | decimal(18,2) | Yes | No |  |
| Type | nvarchar(50) | Yes | No |  |
| VoucherType | nvarchar(50) | Yes | No |  |
| COId | int(10,0) | Yes | No |  |
| Date | datetime | Yes | No |  |
| VN | nvarchar(50) | Yes | No |  |
| InvoiceId | int(10,0) | Yes | No |  |
| IsAdvance | bit | Yes | No |  |

---

### dbo.Table1

**Rows:** 0  |  
**Columns:** 2  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | nvarchar(50) | Yes | No |  |
| Od | int(10,0) | No | Yes |  |

---

### dbo.Table2

**Rows:** 0  |  
**Columns:** 1  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | nvarchar(50) | Yes | No |  |

---

### dbo.Table3

**Rows:** 0  |  
**Columns:** 1  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | nvarchar(50) | Yes | No |  |

---

### dbo.Table4

**Rows:** 0  |  
**Columns:** 1  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | nvarchar(50) | Yes | No |  |

---

### dbo.TableMerge

**Rows:** 0  |  
**Columns:** 15  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| OrderkeyFrom | nvarchar(50) | Yes | No |  |
| OrderKeyTo | nvarchar(50) | Yes | No |  |
| OrderNoFrom | int(10,0) | Yes | No |  |
| OrderNoTo | int(10,0) | Yes | No |  |
| Z_Number | nvarchar(50) | Yes | No |  |
| TableNoFrom | nvarchar(50) | Yes | No |  |
| TableNoTo | nvarchar(50) | Yes | No |  |
| AmountFrom | float(53,None) | Yes | No |  |
| AmountTo | float(53,None) | Yes | No |  |
| OrderDate | datetime | Yes | No |  |
| ServerFrom | nvarchar(50) | Yes | No |  |
| ServerTo | nvarchar(50) | Yes | No |  |
| CoverFrom | int(10,0) | Yes | No |  |
| CoverTo | int(10,0) | Yes | No |  |

---

### dbo.TableTiltAssign

**Rows:** 0  |  
**Columns:** 4  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| TableId | int(10,0) | Yes | No |  |
| Tiltid | int(10,0) | Yes | No |  |
| Active | int(10,0) | Yes | No |  |

---

### dbo.Tables

**Rows:** 0  |  
**Columns:** 6  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| tables | nvarchar(50) | Yes | No |  |
| TableName | nvarchar(50) | Yes | No |  |
| table_status | nvarchar(50) | Yes | No |  |
| TiltId | int(10,0) | No | No |  |
| CurrTiltId | int(10,0) | No | No |  |

---

### dbo.TakeAway_Customer

**Rows:** 0  |  
**Columns:** 4  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| customer | nvarchar(50) | Yes | No |  |
| phone_num | nvarchar(50) | Yes | No |  |
| order_key | nvarchar(50) | Yes | No |  |

---

### dbo.Tax

**Rows:** 0  |  
**Columns:** 5  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| isApplicable | bit | Yes | No |  |
| tax_type | nvarchar(50) | Yes | No |  |
| tax_amount | float(53,None) | Yes | No |  |
| Tax | nchar(50) | Yes | No |  |

---

### dbo.TaxDetail

**Rows:** 0  |  
**Columns:** 8  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| Order_Key | nvarchar(50) | Yes | No |  |
| TaxName | nvarchar(50) | Yes | No |  |
| TaxType | nvarchar(50) | Yes | No |  |
| TaxPercent | nvarchar(50) | Yes | No |  |
| TaxAmount | decimal(18,2) | Yes | No |  |
| is_upload | bit | No | No |  |
| is_update | bit | No | No |  |

---

### dbo.TaxInventory

**Rows:** 0  |  
**Columns:** 2  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| tax_amount | float(53,None) | Yes | No |  |

---

### dbo.Tax_

**Rows:** 1  |  
**Columns:** 7  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| Id | int(10,0) | No | Yes |  |
| IsApplicable | bit | Yes | No |  |
| TaxType | nvarchar(50) | Yes | No |  |
| Tax | decimal(18,2) | Yes | No |  |
| Type | nvarchar(50) | Yes | No |  |
| CAId | int(10,0) | Yes | No |  |
| TransactionType | nvarchar(50) | Yes | No |  |

---

### dbo.TempDealsOnSpotItems

**Rows:** 0  |  
**Columns:** 12  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| order_key | nvarchar(50) | Yes | No |  |
| Order_detailId | int(10,0) | Yes | No |  |
| deal_name | nvarchar(50) | Yes | No |  |
| deal_price | float(53,None) | Yes | No |  |
| category_name | nvarchar(50) | Yes | No |  |
| item_name | nvarchar(50) | Yes | No |  |
| qty | float(53,None) | Yes | No |  |
| department | nvarchar(50) | Yes | No |  |
| TiltId | int(10,0) | Yes | No |  |
| Status | bit | Yes | No |  |
| ItemQty | float(53,None) | Yes | No |  |

---

### dbo.Theme

**Rows:** 0  |  
**Columns:** 3  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes | (PK) |
| form_name | nvarchar(50) | Yes | No |  |
| theme_name | nvarchar(50) | Yes | No |  |

#### Primary Key
`id`

---

### dbo.Tilt

**Rows:** 18  |  
**Columns:** 9  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| TilitName | nvarchar(50) | Yes | No |  |
| Serial | nvarchar(-1) | Yes | No |  |
| CounterWiseOrder | bit | Yes | No |  |
| ConSolidatedKOT | bit | Yes | No |  |
| ItemLessKOT | bit | No | No |  |
| is_upload | bit | No | No |  |
| is_update | bit | No | No |  |
| Is_Update_From_Server | bit | No | No |  |

---

### dbo.TokenNo

**Rows:** 1  |  
**Columns:** 1  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| TokenNumber | int(10,0) | No | No |  |

---

### dbo.Transfer

**Rows:** 0  |  
**Columns:** 7  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| TransferId | int(10,0) | No | Yes | (PK) |
| Date | datetime | Yes | No |  |
| TRNo | nvarchar(50) | Yes | No |  |
| UserId | int(10,0) | Yes | No |  |
| TotalAmount | decimal(18,2) | Yes | No |  |
| From | nvarchar(50) | Yes | No |  |
| To | nvarchar(50) | Yes | No |  |

#### Primary Key
`TransferId`

---

### dbo.TransferInDetail

**Rows:** 0  |  
**Columns:** 7  |  
**Foreign Keys:** 1

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| Id | int(10,0) | No | Yes |  |
| TRIId | int(10,0) | Yes | No |  |
| ItemId | int(10,0) | Yes | No |  |
| Unit | int(10,0) | Yes | No |  |
| Qty | decimal(18,2) | Yes | No |  |
| Rate | decimal(18,2) | Yes | No |  |
| PackageId | int(10,0) | Yes | No |  |

#### Foreign Keys

| Constraint | Local Column | Referenced Table | Referenced Column |
|------------|--------------|------------------|-------------------|
| FK_TransferInDetail_TransferInMaster | TRIId | dbo.TransferInMaster | TRIId |

---

### dbo.TransferInMaster

**Rows:** 0  |  
**Columns:** 3  |  
**Foreign Keys:** 1

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| TRIId | int(10,0) | No | Yes | (PK) |
| TransferId | int(10,0) | Yes | No |  |
| TRInId | int(10,0) | Yes | No |  |

#### Primary Key
`TRIId`

#### Foreign Keys

| Constraint | Local Column | Referenced Table | Referenced Column |
|------------|--------------|------------------|-------------------|
| FK_TransferInMaster_Transfer | TransferId | dbo.Transfer | TransferId |

---

### dbo.TransferOutDetail

**Rows:** 0  |  
**Columns:** 7  |  
**Foreign Keys:** 1

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| Id | int(10,0) | No | Yes |  |
| TRId | int(10,0) | Yes | No |  |
| ItemId | int(10,0) | Yes | No |  |
| Unit | int(10,0) | Yes | No |  |
| Qty | decimal(18,2) | Yes | No |  |
| Rate | decimal(18,2) | Yes | No |  |
| PackageId | int(10,0) | Yes | No |  |

#### Foreign Keys

| Constraint | Local Column | Referenced Table | Referenced Column |
|------------|--------------|------------------|-------------------|
| FK_TransferOutDetail_TransferOutMaster | TRId | dbo.TransferOutMaster | TRId |

---

### dbo.TransferOutMaster

**Rows:** 0  |  
**Columns:** 3  |  
**Foreign Keys:** 1

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| TRId | int(10,0) | No | Yes | (PK) |
| TransferId | int(10,0) | Yes | No |  |
| TROutId | int(10,0) | Yes | No |  |

#### Primary Key
`TRId`

#### Foreign Keys

| Constraint | Local Column | Referenced Table | Referenced Column |
|------------|--------------|------------------|-------------------|
| FK_TransferOutMaster_Transfer | TransferId | dbo.Transfer | TransferId |

---

### dbo.Unit

**Rows:** 0  |  
**Columns:** 2  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| UId | int(10,0) | No | Yes | (PK) |
| Unit | nvarchar(50) | Yes | No |  |

#### Primary Key
`UId`

---

### dbo.UnitConversion

**Rows:** 0  |  
**Columns:** 4  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| UnitFrom | nvarchar(50) | Yes | No |  |
| UnitTo | nvarchar(50) | Yes | No |  |
| Conversion | decimal(18,2) | Yes | No |  |

---

### dbo.User

**Rows:** 1  |  
**Columns:** 4  |  
**Foreign Keys:** 1

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| UserId | int(10,0) | No | Yes |  |
| UserName | nvarchar(-1) | Yes | No |  |
| Password | nvarchar(-1) | Yes | No |  |
| UTId | int(10,0) | Yes | No |  |

#### Foreign Keys

| Constraint | Local Column | Referenced Table | Referenced Column |
|------------|--------------|------------------|-------------------|
| FK_User_UserType | UTId | dbo.UserType | UTId |

---

### dbo.UserTiltAssign

**Rows:** 0  |  
**Columns:** 4  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| UserId | int(10,0) | Yes | No |  |
| Tiltid | int(10,0) | Yes | No |  |
| WaiterId | int(10,0) | Yes | No |  |

---

### dbo.UserType

**Rows:** 1  |  
**Columns:** 3  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| UTId | int(10,0) | No | Yes | (PK) |
| UserType | nvarchar(50) | Yes | No |  |
| COId | int(10,0) | Yes | No |  |

#### Primary Key
`UTId`

---

### dbo.UserTypeAccess

**Rows:** 1  |  
**Columns:** 4  |  
**Foreign Keys:** 1

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| UserTypeAccessId | int(10,0) | No | Yes |  |
| Functions | nvarchar(50) | Yes | No |  |
| UTId | int(10,0) | Yes | No |  |
| IsActive | bit | Yes | No |  |

#### Foreign Keys

| Constraint | Local Column | Referenced Table | Referenced Column |
|------------|--------------|------------------|-------------------|
| FK_UserTypeAccess_UserType | UTId | dbo.UserType | UTId |

---

### dbo.Vendor

**Rows:** 0  |  
**Columns:** 10  |  
**Foreign Keys:** 1

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| VId | int(10,0) | No | Yes | (PK) |
| Vendor | nvarchar(50) | Yes | No |  |
| Address | nvarchar(-1) | Yes | No |  |
| CellNo | nvarchar(50) | Yes | No |  |
| COId | int(10,0) | Yes | No |  |
| OpBalance | decimal(18,2) | Yes | No |  |
| Fax | nvarchar(50) | Yes | No |  |
| Email | nvarchar(50) | Yes | No |  |
| CAId | int(10,0) | Yes | No |  |
| PreOp | decimal(18,2) | Yes | No |  |

#### Primary Key
`VId`

#### Foreign Keys

| Constraint | Local Column | Referenced Table | Referenced Column |
|------------|--------------|------------------|-------------------|
| FK_Vendor_Company | COId | dbo.Company | COId |

---

### dbo.Voucher

**Rows:** 1  |  
**Columns:** 3  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| VoucherName | nvarchar(50) | Yes | No |  |
| Amount | decimal(18,2) | Yes | No |  |

---

### dbo.VoucherDetail

**Rows:** 0  |  
**Columns:** 6  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| Order_key | nvarchar(50) | Yes | No |  |
| VoucherName | nvarchar(500) | Yes | No |  |
| VoucherQty | float(53,None) | Yes | No |  |
| VoucherAmount | decimal(18,2) | Yes | No |  |
| VoucherSerial | nvarchar(-1) | Yes | No |  |

---

### dbo.Waiter

**Rows:** 0  |  
**Columns:** 6  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | Yes | No |  |
| waiter_name | nvarchar(50) | Yes | No |  |
| Tiltid | int(10,0) | No | No |  |
| id_ | int(10,0) | No | Yes |  |
| commission | decimal(18,2) | No | No |  |
| is_percent | bit | No | No |  |

---

### dbo.WareHouse_Branch

**Rows:** 19  |  
**Columns:** 22  |  
**Foreign Keys:** 2

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| Date | datetime | Yes | No |  |
| ItemId | int(10,0) | Yes | No |  |
| Unit | int(10,0) | Yes | No |  |
| InvoiceId | int(10,0) | Yes | No |  |
| IssId | int(10,0) | Yes | No |  |
| TRInId | int(10,0) | Yes | No |  |
| TROutId | int(10,0) | Yes | No |  |
| InvAdjId | int(10,0) | Yes | No |  |
| Qty | decimal(18,4) | No | No |  |
| Rate | decimal(18,2) | Yes | No |  |
| Type | varchar(50) | Yes | No |  |
| BRId | int(10,0) | Yes | No |  |
| IssRTId | int(10,0) | Yes | No |  |
| SId | int(10,0) | Yes | No |  |
| PDId | int(10,0) | Yes | No |  |
| PMId | int(10,0) | Yes | No |  |
| Desc | nvarchar(50) | Yes | No |  |
| DId | int(10,0) | Yes | No |  |
| Amount | decimal(18,2) | Yes | No |  |
| OpenInvId | int(10,0) | No | No |  |
| Qty_Pcs | decimal(18,2) | Yes | No |  |

#### Foreign Keys

| Constraint | Local Column | Referenced Table | Referenced Column |
|------------|--------------|------------------|-------------------|
| FK_WareHouse_Branch_Branch | BRId | dbo.Branch | BRId |
| FK_WareHouse_Branch_Item | ItemId | dbo.Item | ItemId |

---

### dbo.WareHouse_Store

**Rows:** 47  |  
**Columns:** 29  |  
**Foreign Keys:** 2

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| Date | datetime | Yes | No |  |
| ItemId | int(10,0) | Yes | No |  |
| Unit | int(10,0) | Yes | No |  |
| InvoiceId | int(10,0) | Yes | No |  |
| BUTId | int(10,0) | Yes | No |  |
| IssId | int(10,0) | Yes | No |  |
| TRInId | int(10,0) | Yes | No |  |
| TROutId | int(10,0) | Yes | No |  |
| InvAdjId | int(10,0) | Yes | No |  |
| Qty | decimal(18,4) | Yes | No |  |
| WesQty | decimal(18,4) | Yes | No |  |
| Rate | decimal(18,2) | Yes | No |  |
| Type | nvarchar(50) | Yes | No |  |
| BUTRId | int(10,0) | Yes | No |  |
| SId | int(10,0) | Yes | No |  |
| PRId | int(10,0) | Yes | No |  |
| IssRTId | int(10,0) | Yes | No |  |
| BRId | int(10,0) | No | No |  |
| PDId | int(10,0) | Yes | No |  |
| Desc | nvarchar(50) | Yes | No |  |
| DId | int(10,0) | Yes | No |  |
| Amount | decimal(18,2) | Yes | No |  |
| OpenInvId | int(10,0) | Yes | No |  |
| SLId | int(10,0) | Yes | No |  |
| AvgRate | decimal(18,2) | Yes | No |  |
| AvgRateCalc | int(10,0) | No | No |  |
| AvgRateMonth | nvarchar(50) | Yes | No |  |
| Qty_Pcs | decimal(18,2) | Yes | No |  |

#### Foreign Keys

| Constraint | Local Column | Referenced Table | Referenced Column |
|------------|--------------|------------------|-------------------|
| FK_WareHouse_Store_Store | SId | dbo.Store | SId |
| FK_WareHouse_Store_Item | ItemId | dbo.Item | ItemId |

---

### dbo.currency_convertor

**Rows:** 0  |  
**Columns:** 3  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| currency | nvarchar(50) | Yes | No |  |
| rate | decimal(18,2) | Yes | No |  |

---

### dbo.customer_group

**Rows:** 0  |  
**Columns:** 2  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| customer_group_id | int(10,0) | No | Yes |  |
| customer_group_name | nvarchar(50) | Yes | No |  |

---

### dbo.device_tilt_assign

**Rows:** 0  |  
**Columns:** 5  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| tilt_id | int(10,0) | No | No |  |
| device_no | nvarchar(50) | Yes | No |  |
| is_upload | int(10,0) | Yes | No |  |
| is_update | int(10,0) | Yes | No |  |

---

### dbo.item_stock_detail

**Rows:** 0  |  
**Columns:** 6  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes | (PK) |
| master_id | int(10,0) | No | No |  |
| item_id | int(10,0) | Yes | No |  |
| last_rate | decimal(18,2) | Yes | No |  |
| balance | decimal(18,2) | Yes | No |  |
| store_id | int(10,0) | Yes | No |  |

#### Primary Key
`id`

---

### dbo.item_stock_master

**Rows:** 0  |  
**Columns:** 2  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes | (PK) |
| date | datetime | Yes | No |  |

#### Primary Key
`id`

---

### dbo.meal_serving_time

**Rows:** 0  |  
**Columns:** 3  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| meal_type | varchar(50) | Yes | No |  |
| serving_time | int(10,0) | Yes | No |  |

---

### dbo.sysdiagrams

**Rows:** 2  |  
**Columns:** 5  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| name | nvarchar(128) | No | No |  |
| principal_id | int(10,0) | No | No |  |
| diagram_id | int(10,0) | No | Yes | (PK) |
| version | int(10,0) | Yes | No |  |
| definition | varbinary(-1) | Yes | No |  |

#### Primary Key
`diagram_id`

---

### dbo.tblLuckyDraw

**Rows:** 0  |  
**Columns:** 7  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| Name | varchar(50) | No | No |  |
| from | int(10,0) | Yes | No |  |
| to | int(10,0) | Yes | No |  |
| IsActive | bit | No | No |  |
| Date | datetime | Yes | No |  |
| Increment | int(10,0) | Yes | No |  |

---

### dbo.tbl_user

**Rows:** 17  |  
**Columns:** 90  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes | (PK) |
| username | nvarchar(50) | Yes | No |  |
| pwd | nvarchar(50) | Yes | No |  |
| adminsetting | bit | Yes | No |  |
| inventory_setting | bit | Yes | No |  |
| create_change_user | bit | Yes | No |  |
| create_change_shift | bit | Yes | No |  |
| point_of_sale | bit | Yes | No |  |
| sales_reports | bit | Yes | No |  |
| item_less | bit | Yes | No |  |
| discount | bit | Yes | No |  |
| order_delete | bit | Yes | No |  |
| ent | bit | Yes | No |  |
| RptMenu | bit | Yes | No |  |
| RptShiftWiseFinancial | bit | Yes | No |  |
| RptXReportsFinancial | bit | Yes | No |  |
| RptXReportsCategory | bit | Yes | No |  |
| RptXReportsItem | bit | Yes | No |  |
| RptRunningTables | bit | Yes | No |  |
| RptTakeAwayCustomer | bit | Yes | No |  |
| RptDeliveryCustomer | bit | Yes | No |  |
| RptDistributedReport | bit | Yes | No |  |
| RptItem | bit | Yes | No |  |
| RptFinancial | bit | Yes | No |  |
| RptCategory | bit | Yes | No |  |
| RptCovers | bit | Yes | No |  |
| RptOrderDetails | bit | Yes | No |  |
| RptDiscount | bit | Yes | No |  |
| RptEnt | bit | Yes | No |  |
| RptOrderDelete | bit | Yes | No |  |
| RptItemLess | bit | Yes | No |  |
| RptDeliveryOrders | bit | Yes | No |  |
| RptBillHistory | bit | Yes | No |  |
| RptWaiterPerformance | bit | Yes | No |  |
| RptCategoryByDepart | bit | Yes | No |  |
| OpeningAmount | bit | Yes | No |  |
| ClosingAmount | bit | Yes | No |  |
| CashDrop | bit | Yes | No |  |
| IsCash | bit | Yes | No |  |
| LoginStatus | bit | Yes | No |  |
| UserWiseOrder | bit | Yes | No |  |
| InventoryFunctional | bit | Yes | No |  |
| InventorySettings | bit | Yes | No |  |
| InventoryReports | bit | Yes | No |  |
| AccountsFunctional | bit | Yes | No |  |
| AccountsSettings | bit | Yes | No |  |
| AccountsReports | bit | Yes | No |  |
| CreateUser | bit | No | No |  |
| Tiltid | int(10,0) | No | No |  |
| CardData | nvarchar(50) | Yes | No |  |
| ReportsPOS | bit | No | No |  |
| is_upload | bit | No | No |  |
| is_update | bit | No | No |  |
| N_AdvBooking | bit | No | No |  |
| N_All_Orders | bit | No | No |  |
| n_CashDrop | bit | No | No |  |
| N_CreditSale | bit | No | No |  |
| N_DeptWise_Sale | bit | No | No |  |
| N_Financial_Running_Shift | bit | No | No |  |
| N_Item_Running_Shift | bit | No | No |  |
| N_Item_Zero | bit | No | No |  |
| N_ItemRate | bit | No | No |  |
| N_Ledger | bit | No | No |  |
| N_LoginStatus | bit | No | No |  |
| N_RiderCashFloat | bit | No | No |  |
| N_RiderPerformance | bit | No | No |  |
| N_SaleDetail | bit | No | No |  |
| N_SaleReturn | bit | No | No |  |
| N_shift_Counter_Report | bit | No | No |  |
| N_Table_Running_Shift | bit | No | No |  |
| N_Table_Summary | bit | No | No |  |
| N_table_time | bit | No | No |  |
| N_TakeAwayOrders | bit | No | No |  |
| n_Tax | bit | No | No |  |
| N_TopSale_Item | bit | No | No |  |
| N_TopSale_Item_CategoryWise | bit | No | No |  |
| ItemTransfer | bit | No | No |  |
| OrderTransfer | bit | No | No |  |
| DuplicateKOT | bit | No | No |  |
| ItemComplimentry | bit | No | No |  |
| PartyAccount | bit | No | No |  |
| SaleView | bit | No | No |  |
| IsDeliveryCharges | bit | No | No |  |
| only_bill | bit | No | No |  |
| user_wise_order | bit | No | No |  |
| dine_in | bit | Yes | No |  |
| takeaway | bit | Yes | No |  |
| delivery | bit | Yes | No |  |
| order_delete_after_bill | bit | Yes | No |  |
| item_less_after_bill | bit | Yes | No |  |

#### Primary Key
`id`

---

### dbo.tempDine_In_Order

**Rows:** 527  |  
**Columns:** 49  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| order_key | nvarchar(50) | No | No |  |
| z_number | nvarchar(50) | Yes | No |  |
| order_type | nvarchar(50) | Yes | No |  |
| order_no | int(10,0) | Yes | No |  |
| order_date | datetime | Yes | No |  |
| day | nvarchar(50) | Yes | No |  |
| table_no | nvarchar(50) | Yes | No |  |
| waiter_name | nvarchar(50) | Yes | No |  |
| order_time | nvarchar(50) | Yes | No |  |
| service_time | nvarchar(50) | Yes | No |  |
| service_status | nvarchar(50) | Yes | No |  |
| account_status | nvarchar(50) | Yes | No |  |
| amount | float(53,None) | Yes | No |  |
| DiscountType | nvarchar(50) | Yes | No |  |
| discount | decimal(18,0) | Yes | No |  |
| is_delete | bit | Yes | No |  |
| cover | decimal(18,0) | No | No |  |
| estimated_time | nvarchar(50) | Yes | No |  |
| table_time | nvarchar(50) | Yes | No |  |
| kitchen_status | bit | No | No |  |
| Tiltid | int(10,0) | Yes | No |  |
| CounterId | int(10,0) | Yes | No |  |
| IsBill | bit | Yes | No |  |
| CareOff | nvarchar(100) | Yes | No |  |
| IsSelect | bit | Yes | No |  |
| Customer | nvarchar(-1) | Yes | No |  |
| Tele | nvarchar(50) | Yes | No |  |
| ExtraCharges | decimal(18,2) | Yes | No |  |
| DeleteReason | nvarchar(-1) | Yes | No |  |
| UserPunch | nvarchar(-1) | Yes | No |  |
| UserCash | nvarchar(-1) | Yes | No |  |
| UserDelete | nvarchar(-1) | Yes | No |  |
| KOT | int(10,0) | Yes | No |  |
| tableStatus | bit | Yes | No |  |
| OrderTiltId | int(10,0) | Yes | No |  |
| TimeIn | datetime | Yes | No |  |
| TimeOut | datetime | Yes | No |  |
| Status | bit | No | No |  |
| Od | int(10,0) | No | No |  |
| Itemqty | float(53,None) | No | No |  |
| Itemprice | float(53,None) | No | No |  |
| OrderKey_Merege | nvarchar(50) | Yes | No |  |
| DispatchTime | nvarchar(50) | Yes | No |  |
| OrderStatus | nvarchar(50) | Yes | No |  |
| PaymentMode | nvarchar(50) | Yes | No |  |
| isFeedback | bit | No | No |  |
| Feedback | nvarchar(-1) | Yes | No |  |
| DiscountId | nvarchar(50) | Yes | No |  |

---

### dbo.tempKeys

**Rows:** 0  |  
**Columns:** 3  |  
**Foreign Keys:** 0

#### Columns

| Column Name | Data Type | Nullable | Identity | PK |
|-------------|-----------|----------|----------|----|
| id | int(10,0) | No | Yes |  |
| orderKey | nvarchar(50) | Yes | No |  |
| TiltId | int(10,0) | Yes | No |  |

---

## Foreign Key Relationships

| From Table | From Column | To Table | To Column | Constraint |
|------------|-------------|----------|-----------|------------|
| dbo.AccountOpenBalance | CAId | dbo.ChartOfAccount | CAId | ChartOfAccount_AccountOpenBalance |
| dbo.BankPaymentDetail | BPId | dbo.BankPaymentMaster | BPId | BankPaymentMaster_BankPaymentDetail |
| dbo.BankPaymentDetail | CAId | dbo.ChartOfAccount | CAId | FK_BankPaymentDetail_ChartOfAccount |
| dbo.BankPaymentMaster | PVId | dbo.PaymentVoucher | PVId | FK_BankPaymentMaster_PaymentVoucher |
| dbo.BankReceiptDetail | BRId | dbo.BankReceiptMaster | BRId | BankReceiptMaster_BankReceiptDetail |
| dbo.BankReceiptDetail | CAId | dbo.ChartOfAccount | CAId | FK_BankReceiptDetail_ChartOfAccount |
| dbo.Branch | COId | dbo.Company | COId | FK_Branch_Company |
| dbo.ButcheryReturnDetail | BUTRId | dbo.ButcheryReturnMaster | BUTRId | FK_ButcheryReturnDetail_ButcheryReturnMaster |
| dbo.CashPaymentDetail | CAId | dbo.ChartOfAccount | CAId | FK_CashPaymentDetail_ChartOfAccount |
| dbo.CashPaymentDetail | CPId | dbo.CashPaymentMaster | CPId | CashPaymentMaster_CashPaymentDetail |
| dbo.CashPaymentMaster | PVId | dbo.PaymentVoucher | PVId | FK_CashPaymentMaster_PaymentVoucher |
| dbo.CashReceiptDetail | CRId | dbo.CashReceiptMaster | CRId | CashReceiptMaster_CashReceiptDetail |
| dbo.CashReceiptDetail | CAId | dbo.ChartOfAccount | CAId | FK_CashReceiptDetail_ChartOfAccount |
| dbo.Category | COID | dbo.Company | COId | FK_Category_Company |
| dbo.Customer | CAId | dbo.ChartOfAccount | CAId | FK_Customer_ChartOfAccount |
| dbo.CustomerLedger | COId | dbo.Company | COId | FK_CustomerLedger_Company |
| dbo.CustomerLedger | CustId | dbo.Customer | CustId | FK_CustomerLedger_Customer |
| dbo.CustomerSaleInvoiceDetail | ItemId | dbo.Item | ItemId | FK_CustomerSaleInvoiceDetail_Item |
| dbo.CustomerSaleInvoiceDetail | SLId | dbo.CustomerSaleInvoiceMaster | SLId | FK_CustomerSaleInvoiceDetail_Store_CustomerSaleInvoiceMaster_Store |
| dbo.CustomerSaleInvoiceMaster | CustId | dbo.Customer | CustId | FK_CustomerSaleInvoiceMaster_Customer |
| dbo.DemandSheetDetail_Store | ItemId | dbo.Item | ItemId | FK_DemandSheetDetail_Store_Item |
| dbo.DemandSheetDetail_Store | DSCOId | dbo.DemandSheetMaster_Store | DSCOId | FK_DemandSheetDetail_Company_DemandSheetMaster_Company |
| dbo.DemandSheetMaster_Branch | BRId | dbo.Branch | BRId | FK_DemandSheetMaster_Branch_Branch |
| dbo.DemandSheetMaster_Store | COId | dbo.Company | COId | FK_DemandSheetMaster_Store_Company |
| dbo.DemandSheetMaster_Store | SId | dbo.Store | SId | FK_DemandSheetMaster_Store_Store |
| dbo.GL | COId | dbo.Company | COId | FK_GL_Company |
| dbo.GL | CAId | dbo.ChartOfAccount | CAId | ChartOfAccount_GL |
| dbo.GRNDetail | ItemId | dbo.Item | ItemId | FK_GRNDetail_Item |
| dbo.GRNDetail | GRNId | dbo.GRNMaster | GRNId | FK_GRNDetail_Store_GRNMaster_Store |
| dbo.GRNMaster | VId | dbo.Vendor | VId | FK_GRNMaster_Vendor |
| dbo.InvAdjDetail_Store | ItemId | dbo.Item | ItemId | FK_InvAdjDetail_Store_Item |
| dbo.InvAdjMaster_Branch | BRId | dbo.Branch | BRId | FK_InvAdjMaster_Branch_Branch |
| dbo.InvAdjMaster_Store | SId | dbo.Store | SId | FK_InvAdjMaster_Store_Store |
| dbo.InvoiceDetail_Company | InvoiceId | dbo.InvoiceMaster_Company | InvoiceId | FK_InvoiceDetail_Company_InvoiceMaster_Company |
| dbo.InvoiceDetail_Company | ItemId | dbo.Item | ItemId | FK_InvoiceDetail_Company_Item |
| dbo.InvoiceDetail_CompanyNew | ItemId | dbo.Item | ItemId | FK_InvoiceDetail_CompanyNew_Item |
| dbo.InvoiceDetail_CompanyNew | InvoiceId | dbo.InvoiceMaster_CompanyNew | InvoiceId | FK_InvoiceDetail_CompanyNew_InvoiceMaster_CompanyNew |
| dbo.InvoiceDetail_CompanyNew | GRNId | dbo.GRNMaster | GRNId | FK_InvoiceDetail_CompanyNew_GRNMaster |
| dbo.InvoiceMaster_Company | VId | dbo.Vendor | VId | FK_InvoiceMaster_Company_Vendor |
| dbo.InvoiceMaster_Company | COId | dbo.Company | COId | FK_InvoiceMaster_Company_Company |
| dbo.InvoiceMaster_CompanyNew | VId | dbo.Vendor | VId | FK_InvoiceMaster_CompanyNew_Vendor |
| dbo.IssuanceButcheryDetail | BUTId | dbo.IssuanceButcheryMaster | BUTId | FK_IssuanceButcheryDetail_IssuanceButcheryMaster |
| dbo.IssuanceDetail_Store | IssId | dbo.IssuanceMaster_Store | IssId | FK_IssuanceDetail_Store_IssuanceMaster_Store |
| dbo.IssuanceReaturnDetail | IssRTId | dbo.IssuanceReturnMaster | IssRTId | FK_IssuanceReaturnDetail_IssuanceReturnMaster |
| dbo.Item | SBId | dbo.SubCategory | SBId | FK_Item_SubCategory |
| dbo.ItemConversion | ItemId | dbo.Item | ItemId | FK_ItemConversion_Item |
| dbo.ItemOrderConversion | ItemId | dbo.Item | ItemId | FK_ItemOrderConversion_Item |
| dbo.ItemParLevel | ItemId | dbo.Item | ItemId | FK_ItemParLevel_Item |
| dbo.ItemUnit | ItemId | dbo.Item | ItemId | FK_ItemUnit_Item |
| dbo.JVDetail | JVId | dbo.JVMaster | JVId | JVMaster_JVDetail |
| dbo.OpenInventoryDetail | OpenInvId | dbo.OpenInventoryMaster | OpenInvId | FK_OpenInventoryDetail_OpenInventoryMaster |
| dbo.OpenInventoryDetail | ItemId | dbo.Item | ItemId | FK_OpenInventoryDetail_Item |
| dbo.PhysicalStockDetail_Branch | PSBRId | dbo.PhysicalStockMaster_Branch | PSBRId | FK_PhysicalStockDetail_Branch_PhysicalStockMaster_Branch |
| dbo.PhysicalStockDetail_Branch | ItemId | dbo.Item | ItemId | FK_PhysicalStockDetail_Branch_Item |
| dbo.PhysicalStockDetail_Store | PSId | dbo.PhysicalStockMaster_Store | PSId | FK_PhysicalStockDetail_Store_PhysicalStockMaster_Store |
| dbo.PhysicalStockDetail_Store | ItemId | dbo.Item | ItemId | FK_PhysicalStockDetail_Store_Item |
| dbo.PhysicalStockMaster_Branch | BRId | dbo.Branch | BRId | FK_PhysicalStockMaster_Branch_Branch |
| dbo.PhysicalStockMaster_Store | SId | dbo.Store | SId | FK_PhysicalStockMaster_Store_Store |
| dbo.ProductionDetail | PRId | dbo.ProductionMaster | PRId | FK_ProductionDetail_ProductionMaster |
| dbo.PurchaseOrderMaster_Store | COId | dbo.Company | COId | FK_PurchaseOrderMaster_Store_Company |
| dbo.PurchaseOrderMaster_Store | VId | dbo.Vendor | VId | FK_PurchaseOrderMaster_Store_Vendor |
| dbo.PurchaseOrderMaster_Store | SId | dbo.Store | SId | FK_PurchaseOrderMaster_Store_Store |
| dbo.PurchaseReturnDetail | PRId | dbo.PurchaseReturnMaster | PRId | FK_PurchaseReturnDetail_PurchaseReturnMaster |
| dbo.PurchaseReturnDetailNew | ItemId | dbo.Item | ItemId | FK_PurchaseReturnDetailNew_Item |
| dbo.PurchaseReturnDetailNew | PRId | dbo.PurchaseReturnMasterNew | PRId | FK_PurchaseReturnDetailNew_Store_PurchaseReturnMasterNew_Store |
| dbo.PurchaseReturnMasterNew | GRNId | dbo.GRNMaster | GRNId | FK_PurchaseReturnMasterNew_GRNMaster |
| dbo.PurchaseReturnMasterNew | VId | dbo.Vendor | VId | FK_PurchaseReturnMasterNew_Vendor1 |
| dbo.RecipeDetail | IngredientId | dbo.Item | ItemId | FK_RecipeDetail_Item |
| dbo.RecipeDetail | RecipeId | dbo.RecipeMaster | RecipeId | FK_RecipeDetail_RecipeMaster |
| dbo.SaleInvoiceDetail | SaleInvoiceId | dbo.SaleInvoiceMaster | SaleInvoiceId | SaleInvoiceMaster_SaleInvoiceDetail |
| dbo.SaleInvoiceMaster | COId | dbo.Company | COId | FK_SaleInvoiceMaster_Company |
| dbo.SaleInvoiceMaster | CustId | dbo.Customer | CustId | FK_SaleInvoiceMaster_Customer |
| dbo.SaleInvoiceMaster | CustId | dbo.Customer | CustId | Customer_SaleInvoiceMaster |
| dbo.Store | COId | dbo.Company | COId | FK_Store_Company |
| dbo.SubCategory | CId | dbo.Category | CId | FK_SubCategory_Category1 |
| dbo.SubRecipeDetail | SubRecipeId | dbo.SubRecipeMaster | SubRecipeId | FK_SubRecipeDetail_SubRecipeMaster |
| dbo.TransferInDetail | TRIId | dbo.TransferInMaster | TRIId | FK_TransferInDetail_TransferInMaster |
| dbo.TransferInMaster | TransferId | dbo.Transfer | TransferId | FK_TransferInMaster_Transfer |
| dbo.TransferOutDetail | TRId | dbo.TransferOutMaster | TRId | FK_TransferOutDetail_TransferOutMaster |
| dbo.TransferOutMaster | TransferId | dbo.Transfer | TransferId | FK_TransferOutMaster_Transfer |
| dbo.User | UTId | dbo.UserType | UTId | FK_User_UserType |
| dbo.UserTypeAccess | UTId | dbo.UserType | UTId | FK_UserTypeAccess_UserType |
| dbo.Vendor | COId | dbo.Company | COId | FK_Vendor_Company |
| dbo.WareHouse_Branch | BRId | dbo.Branch | BRId | FK_WareHouse_Branch_Branch |
| dbo.WareHouse_Branch | ItemId | dbo.Item | ItemId | FK_WareHouse_Branch_Item |
| dbo.WareHouse_Store | SId | dbo.Store | SId | FK_WareHouse_Store_Store |
| dbo.WareHouse_Store | ItemId | dbo.Item | ItemId | FK_WareHouse_Store_Item |
