# HOTNSPICYHEAD Database Documentation

Generated at: 2026-04-18 16:30:31

## Connection Profile

- Server: `103.86.55.34,50908`
- Database: `HOTNSPICYHEAD`
- Auth: SQL Login (`sa`) 
- Encryption: `Encrypt=True`, `TrustServerCertificate=True`

## High-Level Summary

- Total tables: **240**
- Total columns: **2173**
- Approximate total rows across tables: **1216773**
- Primary key entries: **62**
- Foreign key mappings: **87**

## Largest Tables (Top 25 by row count)

| Schema | Table | Rows | Columns | PK |
|---|---|---:|---:|---|
| dbo | CustomerPOS | 420496 | 13 | - |
| dbo | OrderKot | 252422 | 18 | - |
| dbo | Order_Detail | 236776 | 37 | - |
| dbo | CustomerPOS_ | 115662 | 10 | - |
| dbo | OrderStatusTime | 81978 | 8 | - |
| dbo | Dine_In_Order | 81965 | 80 | - |
| dbo | AuditItemPOS | 8824 | 13 | - |
| dbo | SMSLog | 6014 | 6 | - |
| dbo | LoginStatus | 4260 | 6 | - |
| dbo | Item_Delete | 3034 | 21 | - |
| dbo | ItemPOS | 1643 | 39 | - |
| dbo | OpenInventoryDetail_Department | 1632 | 7 | - |
| dbo | tempDine_In_Order | 527 | 49 | - |
| dbo | Item_Less | 480 | 25 | - |
| dbo | AuditOpenInventoryStore | 368 | 7 | - |
| dbo | Color | 174 | 2 | - |
| dbo | CategoryPOS | 130 | 16 | - |
| dbo | POSTransectionSetting | 96 | 3 | - |
| dbo | WareHouse_Store | 47 | 29 | - |
| dbo | WareHouse_Branch | 19 | 22 | - |
| dbo | ProductionDetailDepartment | 18 | 6 | - |
| dbo | Shift_User | 18 | 3 | - |
| dbo | Tilt | 18 | 9 | - |
| dbo | ShiftAmount | 17 | 26 | - |
| dbo | tbl_user | 17 | 90 | id |

## Relation Map (Foreign Keys)

| FK Name | From (Child) | To (Parent) |
|---|---|---|
| ChartOfAccount_AccountOpenBalance | dbo.AccountOpenBalance.CAId | dbo.ChartOfAccount.CAId |
| BankPaymentMaster_BankPaymentDetail | dbo.BankPaymentDetail.BPId | dbo.BankPaymentMaster.BPId |
| FK_BankPaymentDetail_ChartOfAccount | dbo.BankPaymentDetail.CAId | dbo.ChartOfAccount.CAId |
| FK_BankPaymentMaster_PaymentVoucher | dbo.BankPaymentMaster.PVId | dbo.PaymentVoucher.PVId |
| BankReceiptMaster_BankReceiptDetail | dbo.BankReceiptDetail.BRId | dbo.BankReceiptMaster.BRId |
| FK_BankReceiptDetail_ChartOfAccount | dbo.BankReceiptDetail.CAId | dbo.ChartOfAccount.CAId |
| FK_Branch_Company | dbo.Branch.COId | dbo.Company.COId |
| FK_ButcheryReturnDetail_ButcheryReturnMaster | dbo.ButcheryReturnDetail.BUTRId | dbo.ButcheryReturnMaster.BUTRId |
| CashPaymentMaster_CashPaymentDetail | dbo.CashPaymentDetail.CPId | dbo.CashPaymentMaster.CPId |
| FK_CashPaymentDetail_ChartOfAccount | dbo.CashPaymentDetail.CAId | dbo.ChartOfAccount.CAId |
| FK_CashPaymentMaster_PaymentVoucher | dbo.CashPaymentMaster.PVId | dbo.PaymentVoucher.PVId |
| CashReceiptMaster_CashReceiptDetail | dbo.CashReceiptDetail.CRId | dbo.CashReceiptMaster.CRId |
| FK_CashReceiptDetail_ChartOfAccount | dbo.CashReceiptDetail.CAId | dbo.ChartOfAccount.CAId |
| FK_Category_Company | dbo.Category.COID | dbo.Company.COId |
| FK_Customer_ChartOfAccount | dbo.Customer.CAId | dbo.ChartOfAccount.CAId |
| FK_CustomerLedger_Company | dbo.CustomerLedger.COId | dbo.Company.COId |
| FK_CustomerLedger_Customer | dbo.CustomerLedger.CustId | dbo.Customer.CustId |
| FK_CustomerSaleInvoiceDetail_Item | dbo.CustomerSaleInvoiceDetail.ItemId | dbo.Item.ItemId |
| FK_CustomerSaleInvoiceDetail_Store_CustomerSaleInvoiceMaster_Store | dbo.CustomerSaleInvoiceDetail.SLId | dbo.CustomerSaleInvoiceMaster.SLId |
| FK_CustomerSaleInvoiceMaster_Customer | dbo.CustomerSaleInvoiceMaster.CustId | dbo.Customer.CustId |
| FK_DemandSheetDetail_Company_DemandSheetMaster_Company | dbo.DemandSheetDetail_Store.DSCOId | dbo.DemandSheetMaster_Store.DSCOId |
| FK_DemandSheetDetail_Store_Item | dbo.DemandSheetDetail_Store.ItemId | dbo.Item.ItemId |
| FK_DemandSheetMaster_Branch_Branch | dbo.DemandSheetMaster_Branch.BRId | dbo.Branch.BRId |
| FK_DemandSheetMaster_Store_Company | dbo.DemandSheetMaster_Store.COId | dbo.Company.COId |
| FK_DemandSheetMaster_Store_Store | dbo.DemandSheetMaster_Store.SId | dbo.Store.SId |
| ChartOfAccount_GL | dbo.GL.CAId | dbo.ChartOfAccount.CAId |
| FK_GL_Company | dbo.GL.COId | dbo.Company.COId |
| FK_GRNDetail_Item | dbo.GRNDetail.ItemId | dbo.Item.ItemId |
| FK_GRNDetail_Store_GRNMaster_Store | dbo.GRNDetail.GRNId | dbo.GRNMaster.GRNId |
| FK_GRNMaster_Vendor | dbo.GRNMaster.VId | dbo.Vendor.VId |
| FK_InvAdjDetail_Store_Item | dbo.InvAdjDetail_Store.ItemId | dbo.Item.ItemId |
| FK_InvAdjMaster_Branch_Branch | dbo.InvAdjMaster_Branch.BRId | dbo.Branch.BRId |
| FK_InvAdjMaster_Store_Store | dbo.InvAdjMaster_Store.SId | dbo.Store.SId |
| FK_InvoiceDetail_Company_InvoiceMaster_Company | dbo.InvoiceDetail_Company.InvoiceId | dbo.InvoiceMaster_Company.InvoiceId |
| FK_InvoiceDetail_Company_Item | dbo.InvoiceDetail_Company.ItemId | dbo.Item.ItemId |
| FK_InvoiceDetail_CompanyNew_GRNMaster | dbo.InvoiceDetail_CompanyNew.GRNId | dbo.GRNMaster.GRNId |
| FK_InvoiceDetail_CompanyNew_InvoiceMaster_CompanyNew | dbo.InvoiceDetail_CompanyNew.InvoiceId | dbo.InvoiceMaster_CompanyNew.InvoiceId |
| FK_InvoiceDetail_CompanyNew_Item | dbo.InvoiceDetail_CompanyNew.ItemId | dbo.Item.ItemId |
| FK_InvoiceMaster_Company_Company | dbo.InvoiceMaster_Company.COId | dbo.Company.COId |
| FK_InvoiceMaster_Company_Vendor | dbo.InvoiceMaster_Company.VId | dbo.Vendor.VId |
| FK_InvoiceMaster_CompanyNew_Vendor | dbo.InvoiceMaster_CompanyNew.VId | dbo.Vendor.VId |
| FK_IssuanceButcheryDetail_IssuanceButcheryMaster | dbo.IssuanceButcheryDetail.BUTId | dbo.IssuanceButcheryMaster.BUTId |
| FK_IssuanceDetail_Store_IssuanceMaster_Store | dbo.IssuanceDetail_Store.IssId | dbo.IssuanceMaster_Store.IssId |
| FK_IssuanceReaturnDetail_IssuanceReturnMaster | dbo.IssuanceReaturnDetail.IssRTId | dbo.IssuanceReturnMaster.IssRTId |
| FK_Item_SubCategory | dbo.Item.SBId | dbo.SubCategory.SBId |
| FK_ItemConversion_Item | dbo.ItemConversion.ItemId | dbo.Item.ItemId |
| FK_ItemOrderConversion_Item | dbo.ItemOrderConversion.ItemId | dbo.Item.ItemId |
| FK_ItemParLevel_Item | dbo.ItemParLevel.ItemId | dbo.Item.ItemId |
| FK_ItemUnit_Item | dbo.ItemUnit.ItemId | dbo.Item.ItemId |
| JVMaster_JVDetail | dbo.JVDetail.JVId | dbo.JVMaster.JVId |
| FK_OpenInventoryDetail_Item | dbo.OpenInventoryDetail.ItemId | dbo.Item.ItemId |
| FK_OpenInventoryDetail_OpenInventoryMaster | dbo.OpenInventoryDetail.OpenInvId | dbo.OpenInventoryMaster.OpenInvId |
| FK_PhysicalStockDetail_Branch_Item | dbo.PhysicalStockDetail_Branch.ItemId | dbo.Item.ItemId |
| FK_PhysicalStockDetail_Branch_PhysicalStockMaster_Branch | dbo.PhysicalStockDetail_Branch.PSBRId | dbo.PhysicalStockMaster_Branch.PSBRId |
| FK_PhysicalStockDetail_Store_Item | dbo.PhysicalStockDetail_Store.ItemId | dbo.Item.ItemId |
| FK_PhysicalStockDetail_Store_PhysicalStockMaster_Store | dbo.PhysicalStockDetail_Store.PSId | dbo.PhysicalStockMaster_Store.PSId |
| FK_PhysicalStockMaster_Branch_Branch | dbo.PhysicalStockMaster_Branch.BRId | dbo.Branch.BRId |
| FK_PhysicalStockMaster_Store_Store | dbo.PhysicalStockMaster_Store.SId | dbo.Store.SId |
| FK_ProductionDetail_ProductionMaster | dbo.ProductionDetail.PRId | dbo.ProductionMaster.PRId |
| FK_PurchaseOrderMaster_Store_Company | dbo.PurchaseOrderMaster_Store.COId | dbo.Company.COId |
| FK_PurchaseOrderMaster_Store_Store | dbo.PurchaseOrderMaster_Store.SId | dbo.Store.SId |
| FK_PurchaseOrderMaster_Store_Vendor | dbo.PurchaseOrderMaster_Store.VId | dbo.Vendor.VId |
| FK_PurchaseReturnDetail_PurchaseReturnMaster | dbo.PurchaseReturnDetail.PRId | dbo.PurchaseReturnMaster.PRId |
| FK_PurchaseReturnDetailNew_Item | dbo.PurchaseReturnDetailNew.ItemId | dbo.Item.ItemId |
| FK_PurchaseReturnDetailNew_Store_PurchaseReturnMasterNew_Store | dbo.PurchaseReturnDetailNew.PRId | dbo.PurchaseReturnMasterNew.PRId |
| FK_PurchaseReturnMasterNew_GRNMaster | dbo.PurchaseReturnMasterNew.GRNId | dbo.GRNMaster.GRNId |
| FK_PurchaseReturnMasterNew_Vendor1 | dbo.PurchaseReturnMasterNew.VId | dbo.Vendor.VId |
| FK_RecipeDetail_Item | dbo.RecipeDetail.IngredientId | dbo.Item.ItemId |
| FK_RecipeDetail_RecipeMaster | dbo.RecipeDetail.RecipeId | dbo.RecipeMaster.RecipeId |
| SaleInvoiceMaster_SaleInvoiceDetail | dbo.SaleInvoiceDetail.SaleInvoiceId | dbo.SaleInvoiceMaster.SaleInvoiceId |
| Customer_SaleInvoiceMaster | dbo.SaleInvoiceMaster.CustId | dbo.Customer.CustId |
| FK_SaleInvoiceMaster_Company | dbo.SaleInvoiceMaster.COId | dbo.Company.COId |
| FK_SaleInvoiceMaster_Customer | dbo.SaleInvoiceMaster.CustId | dbo.Customer.CustId |
| FK_Store_Company | dbo.Store.COId | dbo.Company.COId |
| FK_SubCategory_Category1 | dbo.SubCategory.CId | dbo.Category.CId |
| FK_SubRecipeDetail_SubRecipeMaster | dbo.SubRecipeDetail.SubRecipeId | dbo.SubRecipeMaster.SubRecipeId |
| FK_TransferInDetail_TransferInMaster | dbo.TransferInDetail.TRIId | dbo.TransferInMaster.TRIId |
| FK_TransferInMaster_Transfer | dbo.TransferInMaster.TransferId | dbo.Transfer.TransferId |
| FK_TransferOutDetail_TransferOutMaster | dbo.TransferOutDetail.TRId | dbo.TransferOutMaster.TRId |
| FK_TransferOutMaster_Transfer | dbo.TransferOutMaster.TransferId | dbo.Transfer.TransferId |
| FK_User_UserType | dbo.User.UTId | dbo.UserType.UTId |
| FK_UserTypeAccess_UserType | dbo.UserTypeAccess.UTId | dbo.UserType.UTId |
| FK_Vendor_Company | dbo.Vendor.COId | dbo.Company.COId |
| FK_WareHouse_Branch_Branch | dbo.WareHouse_Branch.BRId | dbo.Branch.BRId |
| FK_WareHouse_Branch_Item | dbo.WareHouse_Branch.ItemId | dbo.Item.ItemId |
| FK_WareHouse_Store_Item | dbo.WareHouse_Store.ItemId | dbo.Item.ItemId |
| FK_WareHouse_Store_Store | dbo.WareHouse_Store.SId | dbo.Store.SId |

## Inferred Relations (Heuristic)

These are possible relationships inferred from matching column names/types to single-column primary keys.

- Total inferred links: **289**
- Confidence level shown is heuristic, not enforced by SQL constraints.
- Full list is available in `docs/hotnspicyhead/inferred_relations.csv`.

| Confidence | From | To | Rule |
|---|---|---|---|
| high | dbo.AccountLevel.COId | dbo.Company.COId | same_column_name_and_type_to_single_column_pk |
| high | dbo.AccountOpenBalance.APId | dbo.AccountPeriod.ApId | same_column_name_and_type_to_single_column_pk |
| high | dbo.AccountOpenBalance.CAId | dbo.ChartOfAccount.CAId | same_column_name_and_type_to_single_column_pk |
| high | dbo.AccountPeriod.COId | dbo.Company.COId | same_column_name_and_type_to_single_column_pk |
| high | dbo.AdvanceBookingDetail.ItemId | dbo.Item.ItemId | same_column_name_and_type_to_single_column_pk |
| high | dbo.AuditOpenInventoryDepartment.ItemId | dbo.Item.ItemId | same_column_name_and_type_to_single_column_pk |
| high | dbo.AuditOpenInventoryStore.ItemId | dbo.Item.ItemId | same_column_name_and_type_to_single_column_pk |
| high | dbo.AvgRateDetail.AvgRateMonth | dbo.AvgRateMaster.AvgRateMonth | same_column_name_and_type_to_single_column_pk |
| high | dbo.AvgRateDetail.ItemId | dbo.Item.ItemId | same_column_name_and_type_to_single_column_pk |
| high | dbo.BankPaymentDetail.BPId | dbo.BankPaymentMaster.BPId | same_column_name_and_type_to_single_column_pk |
| high | dbo.BankPaymentDetail.CAId | dbo.ChartOfAccount.CAId | same_column_name_and_type_to_single_column_pk |
| high | dbo.BankPaymentDetail.InvoiceId | dbo.InvoiceMaster_Company.InvoiceId | same_column_name_and_type_to_single_column_pk |
| high | dbo.BankPaymentDetail.InvoiceId | dbo.InvoiceMaster_CompanyNew.InvoiceId | same_column_name_and_type_to_single_column_pk |
| high | dbo.BankPaymentMaster.CAId | dbo.ChartOfAccount.CAId | same_column_name_and_type_to_single_column_pk |
| high | dbo.BankPaymentMaster.COId | dbo.Company.COId | same_column_name_and_type_to_single_column_pk |
| high | dbo.BankPaymentMaster.PVId | dbo.PaymentVoucher.PVId | same_column_name_and_type_to_single_column_pk |
| high | dbo.BankReceiptDetail.BRId | dbo.BankReceiptMaster.BRId | same_column_name_and_type_to_single_column_pk |
| high | dbo.BankReceiptDetail.BRId | dbo.Branch.BRId | same_column_name_and_type_to_single_column_pk |
| high | dbo.BankReceiptDetail.CAId | dbo.ChartOfAccount.CAId | same_column_name_and_type_to_single_column_pk |
| high | dbo.BankReceiptMaster.BRId | dbo.Branch.BRId | same_column_name_and_type_to_single_column_pk |
| high | dbo.BankReceiptMaster.CAId | dbo.ChartOfAccount.CAId | same_column_name_and_type_to_single_column_pk |
| high | dbo.BankReceiptMaster.COId | dbo.Company.COId | same_column_name_and_type_to_single_column_pk |
| high | dbo.BankReceiptMaster.RVId | dbo.ReceiptVoucher.RVId | same_column_name_and_type_to_single_column_pk |
| high | dbo.Branch.BRId | dbo.BankReceiptMaster.BRId | same_column_name_and_type_to_single_column_pk |
| high | dbo.Branch.COId | dbo.Company.COId | same_column_name_and_type_to_single_column_pk |
| high | dbo.ButcheryReturnDetail.BUTRId | dbo.ButcheryReturnMaster.BUTRId | same_column_name_and_type_to_single_column_pk |
| high | dbo.ButcheryReturnDetail.ItemId | dbo.Item.ItemId | same_column_name_and_type_to_single_column_pk |
| high | dbo.ButcheryReturnMaster.BUTId | dbo.IssuanceButcheryMaster.BUTId | same_column_name_and_type_to_single_column_pk |
| high | dbo.ButcheryReturnMaster.SId | dbo.Store.SId | same_column_name_and_type_to_single_column_pk |
| high | dbo.CashPaymentDetail.CAId | dbo.ChartOfAccount.CAId | same_column_name_and_type_to_single_column_pk |
| high | dbo.CashPaymentDetail.CPId | dbo.CashPaymentMaster.CPId | same_column_name_and_type_to_single_column_pk |
| high | dbo.CashPaymentDetail.InvoiceId | dbo.InvoiceMaster_Company.InvoiceId | same_column_name_and_type_to_single_column_pk |
| high | dbo.CashPaymentDetail.InvoiceId | dbo.InvoiceMaster_CompanyNew.InvoiceId | same_column_name_and_type_to_single_column_pk |
| high | dbo.CashPaymentMaster.CAId | dbo.ChartOfAccount.CAId | same_column_name_and_type_to_single_column_pk |
| high | dbo.CashPaymentMaster.COId | dbo.Company.COId | same_column_name_and_type_to_single_column_pk |
| high | dbo.CashPaymentMaster.PVId | dbo.PaymentVoucher.PVId | same_column_name_and_type_to_single_column_pk |
| high | dbo.CashReceiptDetail.CAId | dbo.ChartOfAccount.CAId | same_column_name_and_type_to_single_column_pk |
| high | dbo.CashReceiptDetail.CRId | dbo.CashReceiptMaster.CRId | same_column_name_and_type_to_single_column_pk |
| high | dbo.CashReceiptMaster.CAId | dbo.ChartOfAccount.CAId | same_column_name_and_type_to_single_column_pk |
| high | dbo.CashReceiptMaster.COId | dbo.Company.COId | same_column_name_and_type_to_single_column_pk |
| high | dbo.CashReceiptMaster.RVId | dbo.ReceiptVoucher.RVId | same_column_name_and_type_to_single_column_pk |
| high | dbo.Category.COID | dbo.Company.COId | same_column_name_and_type_to_single_column_pk |
| high | dbo.CategoryPOS.BRid | dbo.BankReceiptMaster.BRId | same_column_name_and_type_to_single_column_pk |
| high | dbo.CategoryPOS.BRid | dbo.Branch.BRId | same_column_name_and_type_to_single_column_pk |
| high | dbo.ChartOfAccount.COId | dbo.Company.COId | same_column_name_and_type_to_single_column_pk |
| high | dbo.Customer.CAId | dbo.ChartOfAccount.CAId | same_column_name_and_type_to_single_column_pk |
| high | dbo.Customer.COId | dbo.Company.COId | same_column_name_and_type_to_single_column_pk |
| high | dbo.CustomerLedger.COId | dbo.Company.COId | same_column_name_and_type_to_single_column_pk |
| high | dbo.CustomerLedger.CustId | dbo.Customer.CustId | same_column_name_and_type_to_single_column_pk |
| high | dbo.CustomerLedgerAdvBooking.CustId | dbo.Customer.CustId | same_column_name_and_type_to_single_column_pk |
| high | dbo.CustomerReciptDetail.CustRId | dbo.CustomerReciptMaster.CustRId | same_column_name_and_type_to_single_column_pk |
| high | dbo.CustomerReciptMaster.CustId | dbo.Customer.CustId | same_column_name_and_type_to_single_column_pk |
| high | dbo.CustomerSaleInvoiceDetail.ItemId | dbo.Item.ItemId | same_column_name_and_type_to_single_column_pk |
| high | dbo.CustomerSaleInvoiceDetail.SLId | dbo.CustomerSaleInvoiceMaster.SLId | same_column_name_and_type_to_single_column_pk |
| high | dbo.CustomerSaleInvoiceMaster.BRId | dbo.BankReceiptMaster.BRId | same_column_name_and_type_to_single_column_pk |
| high | dbo.CustomerSaleInvoiceMaster.BRId | dbo.Branch.BRId | same_column_name_and_type_to_single_column_pk |
| high | dbo.CustomerSaleInvoiceMaster.CustId | dbo.Customer.CustId | same_column_name_and_type_to_single_column_pk |
| high | dbo.CustomerSaleInvoiceMaster.SId | dbo.Store.SId | same_column_name_and_type_to_single_column_pk |
| high | dbo.Deals.Cid | dbo.Category.CId | same_column_name_and_type_to_single_column_pk |
| high | dbo.Deals.ItemId | dbo.Item.ItemId | same_column_name_and_type_to_single_column_pk |
| high | dbo.DealsOnSpot.Cid | dbo.Category.CId | same_column_name_and_type_to_single_column_pk |
| high | dbo.DealsOnSpot.ItemId | dbo.Item.ItemId | same_column_name_and_type_to_single_column_pk |
| high | dbo.DemandSheetDetail_Branch.DSId | dbo.DemandSheetMaster_Branch.DSId | same_column_name_and_type_to_single_column_pk |
| high | dbo.DemandSheetDetail_Branch.ItemId | dbo.Item.ItemId | same_column_name_and_type_to_single_column_pk |
| high | dbo.DemandSheetDetail_Store.DSCOId | dbo.DemandSheetMaster_Store.DSCOId | same_column_name_and_type_to_single_column_pk |
| high | dbo.DemandSheetDetail_Store.ItemId | dbo.Item.ItemId | same_column_name_and_type_to_single_column_pk |
| high | dbo.DemandSheetMaster_Branch.BRId | dbo.BankReceiptMaster.BRId | same_column_name_and_type_to_single_column_pk |
| high | dbo.DemandSheetMaster_Branch.BRId | dbo.Branch.BRId | same_column_name_and_type_to_single_column_pk |
| high | dbo.DemandSheetMaster_Store.COId | dbo.Company.COId | same_column_name_and_type_to_single_column_pk |
| high | dbo.DemandSheetMaster_Store.SId | dbo.Store.SId | same_column_name_and_type_to_single_column_pk |
| high | dbo.DemandSheetMaster_Store.Vid | dbo.Vendor.VId | same_column_name_and_type_to_single_column_pk |
| high | dbo.DepartmentPOS.BRId | dbo.BankReceiptMaster.BRId | same_column_name_and_type_to_single_column_pk |
| high | dbo.DepartmentPOS.BRId | dbo.Branch.BRId | same_column_name_and_type_to_single_column_pk |
| high | dbo.DepartmentPOS.COId | dbo.Company.COId | same_column_name_and_type_to_single_column_pk |
| high | dbo.DiscountMapping.CAId | dbo.ChartOfAccount.CAId | same_column_name_and_type_to_single_column_pk |
| high | dbo.GL.APId | dbo.AccountPeriod.ApId | same_column_name_and_type_to_single_column_pk |
| high | dbo.GL.CAId | dbo.ChartOfAccount.CAId | same_column_name_and_type_to_single_column_pk |
| high | dbo.GL.COId | dbo.Company.COId | same_column_name_and_type_to_single_column_pk |
| high | dbo.GRNDetail.GRNId | dbo.GRNMaster.GRNId | same_column_name_and_type_to_single_column_pk |
| high | dbo.GRNDetail.ItemId | dbo.Item.ItemId | same_column_name_and_type_to_single_column_pk |
| high | dbo.GRNDetail.POId | dbo.PurchaseOrderMaster_Store.POId | same_column_name_and_type_to_single_column_pk |
| high | dbo.GRNMaster.BRId | dbo.BankReceiptMaster.BRId | same_column_name_and_type_to_single_column_pk |
| high | dbo.GRNMaster.BRId | dbo.Branch.BRId | same_column_name_and_type_to_single_column_pk |
| high | dbo.GRNMaster.SId | dbo.Store.SId | same_column_name_and_type_to_single_column_pk |
| high | dbo.GRNMaster.VId | dbo.Vendor.VId | same_column_name_and_type_to_single_column_pk |
| high | dbo.GRNMaster.uid | dbo.Unit.UId | same_column_name_and_type_to_single_column_pk |
| high | dbo.Group.COId | dbo.Company.COId | same_column_name_and_type_to_single_column_pk |
| high | dbo.InvAdjDetail_Branch.AdjBRId | dbo.InvAdjMaster_Branch.AdjBRId | same_column_name_and_type_to_single_column_pk |
| high | dbo.InvAdjDetail_Branch.ItemId | dbo.Item.ItemId | same_column_name_and_type_to_single_column_pk |
| high | dbo.InvAdjDetail_Store.AdjId | dbo.InvAdjMaster_Store.AdjId | same_column_name_and_type_to_single_column_pk |
| high | dbo.InvAdjDetail_Store.ItemId | dbo.Item.ItemId | same_column_name_and_type_to_single_column_pk |
| high | dbo.InvAdjMaster_Branch.BRId | dbo.BankReceiptMaster.BRId | same_column_name_and_type_to_single_column_pk |
| high | dbo.InvAdjMaster_Branch.BRId | dbo.Branch.BRId | same_column_name_and_type_to_single_column_pk |
| high | dbo.InvAdjMaster_Store.SId | dbo.Store.SId | same_column_name_and_type_to_single_column_pk |
| high | dbo.InvoiceDetail_Company.GRNId | dbo.GRNMaster.GRNId | same_column_name_and_type_to_single_column_pk |
| high | dbo.InvoiceDetail_Company.InvoiceId | dbo.InvoiceMaster_Company.InvoiceId | same_column_name_and_type_to_single_column_pk |
| high | dbo.InvoiceDetail_Company.InvoiceId | dbo.InvoiceMaster_CompanyNew.InvoiceId | same_column_name_and_type_to_single_column_pk |
| high | dbo.InvoiceDetail_Company.ItemId | dbo.Item.ItemId | same_column_name_and_type_to_single_column_pk |
| high | dbo.InvoiceDetail_Company.POId | dbo.PurchaseOrderMaster_Store.POId | same_column_name_and_type_to_single_column_pk |
| high | dbo.InvoiceDetail_CompanyNew.GRNId | dbo.GRNMaster.GRNId | same_column_name_and_type_to_single_column_pk |

## Per-Table Catalog

### dbo.2StepWok

- Row count: **7**
- Columns: **5**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | Step_id | int(10,0) | NO |  |
| 3 | Step | nchar(10) | NO |  |
| 4 | Category_id | int(10,0) | NO |  |
| 5 | Item_Id | int(10,0) | NO |  |

Sample data (`TOP 3`):

```json
[
  {
    "id": 1,
    "Step_id": 1,
    "Step": "Step 1    ",
    "Category_id": 38,
    "Item_Id": 272
  },
  {
    "id": 2,
    "Step_id": 1,
    "Step": "Step 1    ",
    "Category_id": 38,
    "Item_Id": 275
  },
  {
    "id": 3,
    "Step_id": 2,
    "Step": "Step 2    ",
    "Category_id": 34,
    "Item_Id": 260
  }
]
```

### dbo.2StepWok_Items

- Row count: **0**
- Columns: **10**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | Order_Key | nvarchar(50) | NO |  |
| 3 | OrderDetail_Id | int(10,0) | NO |  |
| 4 | Step_id | int(10,0) | NO |  |
| 5 | Step | nchar(10) | NO |  |
| 6 | Category_id | int(10,0) | NO |  |
| 7 | Category | nvarchar(50) | NO |  |
| 8 | Item_Id | int(10,0) | NO |  |
| 9 | Item | nvarchar(50) | NO |  |
| 10 | ItemQty | decimal(18,2) | NO |  |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.2StepWok_Items_Temp

- Row count: **0**
- Columns: **10**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | Order_Key | nvarchar(50) | NO |  |
| 3 | OrderDetail_Id | int(10,0) | NO |  |
| 4 | Step_id | int(10,0) | NO |  |
| 5 | Step | nchar(10) | NO |  |
| 6 | Category_id | int(10,0) | NO |  |
| 7 | Category | nvarchar(50) | NO |  |
| 8 | Item_Id | int(10,0) | NO |  |
| 9 | Item | nvarchar(50) | NO |  |
| 10 | ItemQty | decimal(18,2) | NO |  |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.3StepWok

- Row count: **13**
- Columns: **5**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | Step_id | int(10,0) | NO |  |
| 3 | Step | nchar(10) | NO |  |
| 4 | Category_id | int(10,0) | NO |  |
| 5 | Item_Id | int(10,0) | NO |  |

Sample data (`TOP 3`):

```json
[
  {
    "id": 2,
    "Step_id": 1,
    "Step": "Step 1    ",
    "Category_id": 40,
    "Item_Id": 280
  },
  {
    "id": 3,
    "Step_id": 1,
    "Step": "Step 1    ",
    "Category_id": 40,
    "Item_Id": 281
  },
  {
    "id": 4,
    "Step_id": 1,
    "Step": "Step 1    ",
    "Category_id": 40,
    "Item_Id": 282
  }
]
```

### dbo.3StepWok_Items

- Row count: **0**
- Columns: **10**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | Order_Key | nvarchar(50) | NO |  |
| 3 | OrderDetail_Id | int(10,0) | NO |  |
| 4 | Step_id | int(10,0) | NO |  |
| 5 | Step | nchar(10) | NO |  |
| 6 | Category_id | int(10,0) | NO |  |
| 7 | Category | nvarchar(50) | NO |  |
| 8 | Item_Id | int(10,0) | NO |  |
| 9 | Item | nvarchar(50) | NO |  |
| 10 | ItemQty | decimal(18,2) | NO |  |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.3StepWok_Items_Temp

- Row count: **0**
- Columns: **10**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | Order_Key | nvarchar(50) | NO |  |
| 3 | OrderDetail_Id | int(10,0) | NO |  |
| 4 | Step_id | int(10,0) | NO |  |
| 5 | Step | nchar(10) | NO |  |
| 6 | Category_id | int(10,0) | NO |  |
| 7 | Category | nvarchar(50) | NO |  |
| 8 | Item_Id | int(10,0) | NO |  |
| 9 | Item | nvarchar(50) | NO |  |
| 10 | ItemQty | decimal(18,2) | NO |  |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.Account_Register

- Row count: **4**
- Columns: **6**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | Date | datetime | NO |  |
| 3 | Type | nvarchar(1) | NO |  |
| 4 | Debit | decimal(18,2) | YES | ((0)) |
| 5 | Credit | decimal(18,2) | YES | ((0)) |
| 6 | Description | nvarchar | NO |  |

Sample data (`TOP 3`):

```json
[
  {
    "id": 5,
    "Date": "2015-06-05T00:00:00",
    "Type": "D",
    "Debit": 1000.0,
    "Credit": 0.0,
    "Description": "Cash Deposited To Bank Alfalah"
  },
  {
    "id": 6,
    "Date": "2015-06-05T00:00:00",
    "Type": "C",
    "Debit": 0.0,
    "Credit": 500.0,
    "Description": "Cash Withdraw From Bank Alfalah"
  },
  {
    "id": 7,
    "Date": "2015-06-06T00:00:00",
    "Type": "D",
    "Debit": 5000.0,
    "Credit": 0.0,
    "Description": "Received Payment from xyz"
  }
]
```

### dbo.AccountLevel

- Row count: **3**
- Columns: **4**
- Primary key: LevelId
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | LevelId | int(10,0) | NO |  |
| 2 | Level | int(10,0) | NO |  |
| 3 | AccNoDigits | int(10,0) | YES | ((1)) |
| 4 | COId | int(10,0) | YES |  |

Sample data (`TOP 3`):

```json
[
  {
    "LevelId": 1,
    "Level": 1,
    "AccNoDigits": 2,
    "COId": 0
  },
  {
    "LevelId": 2,
    "Level": 2,
    "AccNoDigits": 4,
    "COId": 0
  },
  {
    "LevelId": 3,
    "Level": 3,
    "AccNoDigits": 7,
    "COId": 0
  }
]
```

### dbo.AccountNature

- Row count: **5**
- Columns: **3**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | Account | varchar(40) | YES |  |
| 3 | AccNo | int(10,0) | YES |  |

Sample data (`TOP 3`):

```json
[
  {
    "id": 1,
    "Account": "ASSETS",
    "AccNo": 1
  },
  {
    "id": 2,
    "Account": "LIABILITIES",
    "AccNo": 2
  },
  {
    "id": 3,
    "Account": "OWNER EQUITY",
    "AccNo": 3
  }
]
```

### dbo.AccountOpenBalance

- Row count: **0**
- Columns: **4**
- Primary key: None
- Outgoing foreign keys: **1**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | Amount | decimal(18,2) | YES |  |
| 3 | CAId | int(10,0) | YES |  |
| 4 | APId | int(10,0) | YES |  |

Foreign key links:
- `CAId` -> `dbo.ChartOfAccount.CAId` (ChartOfAccount_AccountOpenBalance)

Sample data (`TOP 3`):

```text
No rows
```

### dbo.AccountPeriod

- Row count: **2**
- Columns: **5**
- Primary key: ApId
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | ApId | int(10,0) | NO |  |
| 2 | From | datetime | YES |  |
| 3 | To | datetime | YES |  |
| 4 | COId | int(10,0) | YES |  |
| 5 | IsActive | bit | YES | ((1)) |

Sample data (`TOP 3`):

```json
[
  {
    "ApId": 2,
    "From": "2013-07-01T00:00:00",
    "To": "2014-10-16T00:00:00",
    "COId": 78,
    "IsActive": false
  },
  {
    "ApId": 5,
    "From": "2014-10-17T00:00:00",
    "To": null,
    "COId": 78,
    "IsActive": true
  }
]
```

### dbo.AccountType

- Row count: **3**
- Columns: **2**
- Primary key: id
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | Type | varchar(40) | YES |  |

Sample data (`TOP 3`):

```json
[
  {
    "id": 1,
    "Type": "GROUP"
  },
  {
    "id": 2,
    "Type": "DETAIL"
  },
  {
    "id": 3,
    "Type": "SUB GROUP"
  }
]
```

### dbo.AdvanceBooking

- Row count: **0**
- Columns: **36**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | BookingCode | nvarchar(50) | YES |  |
| 3 | CustomerCode | nvarchar(50) | YES |  |
| 4 | DateOfReservation | datetime | YES |  |
| 5 | TimeOfReservtion | datetime | YES |  |
| 6 | NoOfPersons | int(10,0) | YES |  |
| 7 | SittingLocation | nvarchar(100) | YES |  |
| 8 | AdvancePayment | decimal(18,2) | YES | ((0)) |
| 9 | Comments | nvarchar | YES |  |
| 10 | Smooking-NonSmooking | nvarchar(50) | YES |  |
| 11 | Event | nvarchar(50) | YES |  |
| 12 | OrderDate | datetime | YES |  |
| 13 | OrderTime | datetime | YES |  |
| 14 | Order_Key | int(10,0) | NO | ((0)) |
| 15 | GrossAmount | decimal(18,2) | YES | ((0)) |
| 16 | Tax | decimal(18,2) | YES | ((0)) |
| 17 | TaxType | nvarchar(50) | YES |  |
| 18 | Discount | decimal(18,2) | YES | ((0)) |
| 19 | NetAmount | decimal(18,2) | YES | ((0)) |
| 20 | OrderStatus | nvarchar(50) | YES |  |
| 21 | Tiltid | int(10,0) | NO | ((0)) |
| 22 | CounterId | int(10,0) | NO | ((0)) |
| 23 | ShiftNo | nvarchar(50) | YES |  |
| 24 | LunchOrDinner | nvarchar(50) | YES |  |
| 25 | is_upload | bit | NO | ((0)) |
| 26 | is_update | bit | NO | ((0)) |
| 27 | Branch_id | int(10,0) | YES | ((0)) |
| 28 | Company_id | int(10,0) | YES | ((0)) |
| 29 | branch | nvarchar(100) | YES |  |
| 30 | status | nvarchar(100) | YES |  |
| 31 | branch_code | nvarchar(50) | YES |  |
| 32 | agent | nvarchar(50) | YES |  |
| 33 | is_transfer | bit | YES |  |
| 34 | Item_Total | decimal(18,2) | NO | ((0)) |
| 35 | Item_Disocunt | decimal(18,2) | NO | ((0)) |
| 36 | Item_Net | decimal(18,2) | NO | ((0)) |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.AdvanceBookingDetail

- Row count: **0**
- Columns: **7**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | AdvanceBookingId | int(10,0) | NO |  |
| 3 | ItemId | int(10,0) | NO |  |
| 4 | Item | nvarchar(50) | NO |  |
| 5 | Qty | decimal(18,2) | YES |  |
| 6 | Rate | decimal(18,2) | YES |  |
| 7 | Amount | decimal(18,2) | YES |  |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.AdvanceCustomer

- Row count: **2**
- Columns: **10**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | CustomerId | int(10,0) | NO |  |
| 2 | Code | nvarchar(50) | YES |  |
| 3 | Customer | nvarchar(50) | YES |  |
| 4 | Address | nvarchar | YES |  |
| 5 | PhoneNo | nvarchar(50) | YES |  |
| 6 | MobileNo | nvarchar(50) | YES |  |
| 7 | Email | nvarchar(50) | YES |  |
| 8 | CNIC | nvarchar(50) | YES |  |
| 9 | is_upload | bit | NO | ((0)) |
| 10 | is_update | bit | NO | ((0)) |

Sample data (`TOP 3`):

```json
[
  {
    "CustomerId": 52,
    "Code": "CUST-0001",
    "Customer": "MR RAHEEM RAJA ",
    "Address": null,
    "PhoneNo": null,
    "MobileNo": "03312187052",
    "Email": null,
    "CNIC": null,
    "is_upload": false,
    "is_update": false
  },
  {
    "CustomerId": 53,
    "Code": "CUST-0002",
    "Customer": "NIAZ KHAN",
    "Address": null,
    "PhoneNo": null,
    "MobileNo": "03213461961",
    "Email": null,
    "CNIC": null,
    "is_upload": false,
    "is_update": false
  }
]
```

### dbo.AssignTableToWater

- Row count: **0**
- Columns: **4**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | WaiterId | int(10,0) | NO |  |
| 3 | TableId | int(10,0) | YES |  |
| 4 | Tiltid | int(10,0) | NO |  |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.AuditItemPOS

- Row count: **8824**
- Columns: **13**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | category_name | nvarchar(50) | YES |  |
| 3 | item_name | nvarchar(250) | YES |  |
| 4 | cost_price | float(53,0) | YES |  |
| 5 | sale_price | float(53,0) | YES |  |
| 6 | codes | nvarchar(250) | YES |  |
| 7 | status | bit | NO | ((1)) |
| 8 | tiltId | int(10,0) | YES |  |
| 9 | IsComment | bit | YES | ((0)) |
| 10 | Date | datetime | YES |  |
| 11 | User | nvarchar(100) | YES |  |
| 12 | Workstation | nvarchar(50) | YES | (host_name()) |
| 13 | datetime | datetime | YES | (getdate()) |

Sample data (`TOP 3`):

```json
[
  {
    "id": 1,
    "category_name": "Services",
    "item_name": "Services",
    "cost_price": 0.0,
    "sale_price": 0.0,
    "codes": null,
    "status": true,
    "tiltId": null,
    "IsComment": false,
    "Date": "2014-06-03T00:00:00",
    "User": "ammar",
    "Workstation": null,
    "datetime": null
  },
  {
    "id": 2,
    "category_name": "Services",
    "item_name": "Sofa Set",
    "cost_price": 0.0,
    "sale_price": 5000.0,
    "codes": null,
    "status": true,
    "tiltId": null,
    "IsComment": false,
    "Date": "2014-06-03T00:00:00",
    "User": "ammar",
    "Workstation": null,
    "datetime": null
  },
  {
    "id": 3,
    "category_name": "Services",
    "item_name": "Blanket",
    "cost_price": 0.0,
    "sale_price": 5000.0,
    "codes": null,
    "status": true,
    "tiltId": null,
    "IsComment": false,
    "Date": "2014-06-03T00:00:00",
    "User": "ammar",
    "Workstation": null,
    "datetime": null
  }
]
```

### dbo.AuditOpenInventoryDepartment

- Row count: **0**
- Columns: **8**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | Date | datetime | YES |  |
| 3 | ItemId | int(10,0) | YES |  |
| 4 | Qty | decimal(18,2) | YES |  |
| 5 | Rate | decimal(18,2) | YES |  |
| 6 | Amount | decimal(18,2) | YES |  |
| 7 | Unitid | int(10,0) | YES |  |
| 8 | Did | int(10,0) | YES |  |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.AuditOpenInventoryStore

- Row count: **368**
- Columns: **7**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | Date | datetime | YES |  |
| 3 | ItemId | int(10,0) | YES |  |
| 4 | Qty | decimal(18,2) | YES |  |
| 5 | Rate | decimal(18,2) | YES |  |
| 6 | Amount | decimal(18,2) | YES |  |
| 7 | Unitid | int(10,0) | YES |  |

Sample data (`TOP 3`):

```json
[
  {
    "id": 1,
    "Date": "2014-08-14T00:00:00",
    "ItemId": 144,
    "Qty": 61.0,
    "Rate": 0.0,
    "Amount": 0.0,
    "Unitid": 62
  },
  {
    "id": 2,
    "Date": "2014-08-14T00:00:00",
    "ItemId": 145,
    "Qty": 46.0,
    "Rate": 0.0,
    "Amount": 0.0,
    "Unitid": 62
  },
  {
    "id": 3,
    "Date": "2014-08-14T00:00:00",
    "ItemId": 146,
    "Qty": 81.0,
    "Rate": 0.0,
    "Amount": 0.0,
    "Unitid": 62
  }
]
```

### dbo.AvgRateDetail

- Row count: **0**
- Columns: **7**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | Id | int(10,0) | NO |  |
| 2 | ItemId | int(10,0) | NO |  |
| 3 | AvgRateMonth | nvarchar(50) | NO |  |
| 4 | AvgRate | decimal(18,2) | YES |  |
| 5 | DateFrom | smalldatetime | YES |  |
| 6 | DateTo | smalldatetime | YES |  |
| 7 | AmId | int(10,0) | YES |  |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.AvgRateMaster

- Row count: **0**
- Columns: **3**
- Primary key: AvgRateMonth
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | AMID | int(10,0) | NO |  |
| 2 | AvgRateMonth | nvarchar(50) | NO |  |
| 3 | CalcDate | smalldatetime | NO |  |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.Backup

- Row count: **0**
- Columns: **2**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | Id | int(10,0) | NO |  |
| 2 | Path | nvarchar(1000) | YES |  |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.Bank_name

- Row count: **2**
- Columns: **2**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | Bank | nvarchar | NO |  |

Sample data (`TOP 3`):

```json
[
  {
    "id": 2,
    "Bank": "Babib Bank Ltd."
  },
  {
    "id": 3,
    "Bank": "Mezan Bank Ltd."
  }
]
```

### dbo.BankPaymentDetail

- Row count: **0**
- Columns: **6**
- Primary key: None
- Outgoing foreign keys: **2**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | Amount | decimal(18,2) | YES |  |
| 3 | CAId | int(10,0) | YES |  |
| 4 | Desc | nvarchar | YES |  |
| 5 | BPId | int(10,0) | YES |  |
| 6 | InvoiceId | int(10,0) | YES | ((0)) |

Foreign key links:
- `BPId` -> `dbo.BankPaymentMaster.BPId` (BankPaymentMaster_BankPaymentDetail)
- `CAId` -> `dbo.ChartOfAccount.CAId` (FK_BankPaymentDetail_ChartOfAccount)

Sample data (`TOP 3`):

```text
No rows
```

### dbo.BankPaymentMaster

- Row count: **0**
- Columns: **14**
- Primary key: BPId
- Outgoing foreign keys: **1**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | BPId | int(10,0) | NO |  |
| 2 | VN | nvarchar(40) | YES |  |
| 3 | PVId | int(10,0) | YES |  |
| 4 | Date | datetime | YES |  |
| 5 | TotalAmount | decimal(18,2) | YES |  |
| 6 | ChequeNo | nvarchar(40) | YES |  |
| 7 | ChequeDate | datetime | YES |  |
| 8 | CAId | int(10,0) | YES |  |
| 9 | PaidTo | nvarchar | YES |  |
| 10 | For | nvarchar | YES |  |
| 11 | COId | int(10,0) | YES |  |
| 12 | wht_caid | int(10,0) | YES | ((0)) |
| 13 | Tax | decimal(18,2) | YES | ((0)) |
| 14 | TaxAmount | decimal(18,2) | YES | ((0)) |

Foreign key links:
- `PVId` -> `dbo.PaymentVoucher.PVId` (FK_BankPaymentMaster_PaymentVoucher)

Sample data (`TOP 3`):

```text
No rows
```

### dbo.BankReceiptDetail

- Row count: **0**
- Columns: **6**
- Primary key: None
- Outgoing foreign keys: **2**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | Amount | decimal(18,2) | YES |  |
| 3 | CAId | int(10,0) | YES |  |
| 4 | Desc | nvarchar | YES |  |
| 5 | BRId | int(10,0) | YES |  |
| 6 | SaleId | int(10,0) | YES | ((0)) |

Foreign key links:
- `BRId` -> `dbo.BankReceiptMaster.BRId` (BankReceiptMaster_BankReceiptDetail)
- `CAId` -> `dbo.ChartOfAccount.CAId` (FK_BankReceiptDetail_ChartOfAccount)

Sample data (`TOP 3`):

```text
No rows
```

### dbo.BankReceiptMaster

- Row count: **0**
- Columns: **11**
- Primary key: BRId
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | BRId | int(10,0) | NO |  |
| 2 | VN | nvarchar(40) | YES |  |
| 3 | RVId | int(10,0) | YES |  |
| 4 | Date | datetime | YES |  |
| 5 | TotalAmount | decimal(18,2) | YES |  |
| 6 | ChequeNo | nvarchar(40) | YES |  |
| 7 | ChequeDate | datetime | YES |  |
| 8 | CAId | int(10,0) | YES |  |
| 9 | ReceiveFrom | nvarchar | YES |  |
| 10 | For | nvarchar(40) | YES |  |
| 11 | COId | int(10,0) | YES |  |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.Branch

- Row count: **7**
- Columns: **15**
- Primary key: BRId
- Outgoing foreign keys: **1**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | BRId | int(10,0) | NO |  |
| 2 | COId | int(10,0) | YES |  |
| 3 | Branch | nvarchar(50) | YES |  |
| 4 | IsSelected | bit | YES | ((1)) |
| 5 | IsPosSelected | bit | YES |  |
| 6 | Address | nvarchar | YES |  |
| 7 | Email | nvarchar | YES |  |
| 8 | Fax | nvarchar | YES |  |
| 9 | Phone1 | nvarchar | YES |  |
| 10 | Phone2 | nvarchar | YES |  |
| 11 | internet_status | nvarchar(100) | YES |  |
| 12 | last_internet_update | nvarchar(100) | YES |  |
| 13 | branch_ip | nvarchar(50) | YES |  |
| 14 | is_web | bit | NO | ((0)) |
| 15 | branch_code | nvarchar(50) | YES |  |

Foreign key links:
- `COId` -> `dbo.Company.COId` (FK_Branch_Company)

Sample data (`TOP 3`):

```json
[
  {
    "BRId": 161,
    "COId": 126,
    "Branch": "Khadda Market",
    "IsSelected": true,
    "IsPosSelected": false,
    "Address": "",
    "Email": "",
    "Fax": "",
    "Phone1": "",
    "Phone2": "",
    "internet_status": "False",
    "last_internet_update": "06/23/18 04:11 AM",
    "branch_ip": "",
    "is_web": false,
    "branch_code": ""
  },
  {
    "BRId": 191,
    "COId": 126,
    "Branch": "Malir",
    "IsSelected": true,
    "IsPosSelected": false,
    "Address": "",
    "Email": "",
    "Fax": "",
    "Phone1": "",
    "Phone2": "",
    "internet_status": "False",
    "last_internet_update": "11/19/18 06:45 PM",
    "branch_ip": "",
    "is_web": false,
    "branch_code": ""
  },
  {
    "BRId": 192,
    "COId": 126,
    "Branch": "Nazimabad",
    "IsSelected": true,
    "IsPosSelected": false,
    "Address": "",
    "Email": "",
    "Fax": "",
    "Phone1": "",
    "Phone2": "",
    "internet_status": "False",
    "last_internet_update": "11/19/18 06:25 PM",
    "branch_ip": "",
    "is_web": false,
    "branch_code": ""
  }
]
```

### dbo.BuffetBooking

- Row count: **0**
- Columns: **27**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | BookingCode | nvarchar(50) | YES |  |
| 3 | CustomerCode | nvarchar(50) | YES |  |
| 4 | DateOfReservation | datetime | YES |  |
| 5 | TimeOfReservtion | datetime | YES |  |
| 6 | NoOfPersons | nvarchar(50) | YES |  |
| 7 | SittingLocation | nvarchar(100) | YES |  |
| 8 | AdvancePayment | decimal(18,2) | YES | ((0)) |
| 9 | Comments | nvarchar | YES |  |
| 10 | Smooking-NonSmooking | nvarchar(50) | YES |  |
| 11 | Event | nvarchar(50) | YES |  |
| 12 | OrderDate | datetime | YES |  |
| 13 | OrderTime | datetime | YES |  |
| 14 | Order_Key | nvarchar(50) | YES | ((0)) |
| 15 | GrossAmount | decimal(18,2) | YES | ((0)) |
| 16 | Tax | decimal(18,2) | YES | ((0)) |
| 17 | TaxType | nvarchar(50) | YES |  |
| 18 | Discount | decimal(18,2) | YES | ((0)) |
| 19 | NetAmount | decimal(18,2) | YES | ((0)) |
| 20 | IsDelete | bit | YES | ((0)) |
| 21 | service_status | nvarchar(50) | YES |  |
| 22 | OrderNo | int(10,0) | YES |  |
| 23 | ServiceChaerges | decimal(18,0) | NO | ((0)) |
| 24 | Tip | decimal(18,0) | NO | ((0)) |
| 25 | ShiftNo | nvarchar(50) | YES |  |
| 26 | TiltId | int(10,0) | YES | ((0)) |
| 27 | CounterId | int(10,0) | YES | ((0)) |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.BuffetCustomer

- Row count: **0**
- Columns: **8**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | CustomerId | int(10,0) | NO |  |
| 2 | Code | nvarchar(50) | YES |  |
| 3 | Customer | nvarchar(50) | YES |  |
| 4 | Address | nvarchar | YES |  |
| 5 | PhoneNo | nvarchar(50) | YES |  |
| 6 | MobileNo | nvarchar(50) | YES |  |
| 7 | Email | nvarchar(50) | YES |  |
| 8 | CNIC | nvarchar(50) | YES |  |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.Butchery

- Row count: **2**
- Columns: **2**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | Id | int(10,0) | NO |  |
| 2 | ItemType | nvarchar(50) | YES |  |

Sample data (`TOP 3`):

```json
[
  {
    "Id": 6,
    "ItemType": "Butchery"
  },
  {
    "Id": 5,
    "ItemType": "Non Butchery"
  }
]
```

### dbo.ButcheryReturnDetail

- Row count: **0**
- Columns: **9**
- Primary key: None
- Outgoing foreign keys: **1**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | Id | int(10,0) | NO |  |
| 2 | BUTRId | int(10,0) | YES |  |
| 3 | ItemId | int(10,0) | YES |  |
| 4 | Unit | int(10,0) | YES |  |
| 5 | Rate | decimal(18,2) | YES |  |
| 6 | QTY | decimal(18,2) | YES |  |
| 7 | WesQty | decimal(18,2) | YES | ((0)) |
| 8 | Amount | decimal(18,2) | YES |  |
| 9 | RawItemId | int(10,0) | YES |  |

Foreign key links:
- `BUTRId` -> `dbo.ButcheryReturnMaster.BUTRId` (FK_ButcheryReturnDetail_ButcheryReturnMaster)

Sample data (`TOP 3`):

```text
No rows
```

### dbo.ButcheryReturnMaster

- Row count: **0**
- Columns: **6**
- Primary key: BUTRId
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | BUTRId | int(10,0) | NO |  |
| 2 | Date | datetime | YES |  |
| 3 | SId | int(10,0) | YES |  |
| 4 | BUTId | int(10,0) | YES |  |
| 5 | UserId | int(10,0) | YES |  |
| 6 | BURNo | nvarchar(50) | YES |  |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.CashDeposit

- Row count: **0**
- Columns: **13**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | Date | datetime | YES |  |
| 3 | Z_Number | nvarchar(50) | YES |  |
| 4 | Tiltid | int(10,0) | YES |  |
| 5 | VoucherNo | nvarchar(50) | YES |  |
| 6 | Amount | decimal(18,2) | YES |  |
| 7 | CareOf | nvarchar(100) | YES |  |
| 8 | Description | nvarchar | YES |  |
| 9 | CounterId | int(10,0) | YES |  |
| 10 | User | nvarchar(50) | YES |  |
| 11 | Time | nvarchar(50) | YES |  |
| 12 | is_upload | bit | NO | ((0)) |
| 13 | is_update | bit | NO | ((0)) |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.Cashdrawer

- Row count: **1**
- Columns: **5**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | ComPort | nvarchar(50) | YES |  |
| 3 | Tiltid | int(10,0) | YES |  |
| 4 | GsmComPort | nvarchar(50) | YES |  |
| 5 | DisplayComPort | nvarchar(50) | YES |  |

Sample data (`TOP 3`):

```json
[
  {
    "id": 3,
    "ComPort": "",
    "Tiltid": 2,
    "GsmComPort": "COM4",
    "DisplayComPort": null
  }
]
```

### dbo.CashDrawer_Logging

- Row count: **2**
- Columns: **7**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | User | nvarchar(50) | NO |  |
| 3 | z_number | nvarchar(50) | NO |  |
| 4 | TiltId | int(10,0) | NO |  |
| 5 | CounterId | int(10,0) | NO |  |
| 6 | Date | datetime | NO |  |
| 7 | Time | nvarchar(50) | NO |  |

Sample data (`TOP 3`):

```json
[
  {
    "id": 1,
    "User": "ddd",
    "z_number": "DAY-00001",
    "TiltId": 3,
    "CounterId": 198,
    "Date": "2015-06-08T00:00:00",
    "Time": "12:02 PM"
  },
  {
    "id": 2,
    "User": "ddd",
    "z_number": "DAY-00001",
    "TiltId": 3,
    "CounterId": 198,
    "Date": "2015-06-08T00:00:00",
    "Time": "12:02 PM"
  }
]
```

### dbo.CashDrop

- Row count: **0**
- Columns: **13**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | Date | datetime | YES |  |
| 3 | Z_Number | nvarchar(50) | YES |  |
| 4 | Tiltid | int(10,0) | YES |  |
| 5 | VoucherNo | nvarchar(50) | YES |  |
| 6 | Amount | decimal(18,2) | YES |  |
| 7 | CareOf | nvarchar(100) | YES |  |
| 8 | Description | nvarchar | YES |  |
| 9 | CounterId | int(10,0) | YES |  |
| 10 | User | nvarchar(50) | YES |  |
| 11 | Time | nvarchar(50) | YES |  |
| 12 | is_upload | bit | NO | ((0)) |
| 13 | is_update | bit | NO | ((0)) |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.CashPaymentDetail

- Row count: **0**
- Columns: **6**
- Primary key: None
- Outgoing foreign keys: **2**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | Amount | decimal(18,2) | YES |  |
| 3 | CAId | int(10,0) | YES |  |
| 4 | Desc | nvarchar | YES |  |
| 5 | CPId | int(10,0) | YES |  |
| 6 | InvoiceId | int(10,0) | YES | ((0)) |

Foreign key links:
- `CPId` -> `dbo.CashPaymentMaster.CPId` (CashPaymentMaster_CashPaymentDetail)
- `CAId` -> `dbo.ChartOfAccount.CAId` (FK_CashPaymentDetail_ChartOfAccount)

Sample data (`TOP 3`):

```text
No rows
```

### dbo.CashPaymentMaster

- Row count: **0**
- Columns: **12**
- Primary key: CPId
- Outgoing foreign keys: **1**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | CPId | int(10,0) | NO |  |
| 2 | VN | nvarchar(40) | YES |  |
| 3 | PVId | int(10,0) | YES |  |
| 4 | Date | datetime | YES |  |
| 5 | TotalAmount | decimal(18,2) | YES |  |
| 6 | PaidTo | nvarchar(40) | YES |  |
| 7 | For | nvarchar(40) | YES |  |
| 8 | CAId | int(10,0) | YES |  |
| 9 | COId | int(10,0) | YES |  |
| 10 | wht_caid | int(10,0) | YES | ((0)) |
| 11 | Tax | decimal(18,2) | YES | ((0)) |
| 12 | TaxAmount | decimal(18,2) | YES | ((0)) |

Foreign key links:
- `PVId` -> `dbo.PaymentVoucher.PVId` (FK_CashPaymentMaster_PaymentVoucher)

Sample data (`TOP 3`):

```text
No rows
```

### dbo.CashReceiptDetail

- Row count: **0**
- Columns: **6**
- Primary key: None
- Outgoing foreign keys: **2**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | Amount | decimal(18,0) | YES |  |
| 3 | CAId | int(10,0) | YES |  |
| 4 | Desc | nvarchar | YES |  |
| 5 | CRId | int(10,0) | YES |  |
| 6 | SaleId | int(10,0) | YES | ((0)) |

Foreign key links:
- `CRId` -> `dbo.CashReceiptMaster.CRId` (CashReceiptMaster_CashReceiptDetail)
- `CAId` -> `dbo.ChartOfAccount.CAId` (FK_CashReceiptDetail_ChartOfAccount)

Sample data (`TOP 3`):

```text
No rows
```

### dbo.CashReceiptMaster

- Row count: **0**
- Columns: **9**
- Primary key: CRId
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | CRId | int(10,0) | NO |  |
| 2 | VN | nvarchar(40) | YES |  |
| 3 | RVId | int(10,0) | YES |  |
| 4 | Date | datetime | YES |  |
| 5 | TotalAmount | decimal(18,0) | YES |  |
| 6 | ReceiveFrom | nvarchar | YES |  |
| 7 | For | nvarchar(40) | YES |  |
| 8 | CAId | int(10,0) | YES |  |
| 9 | COId | int(10,0) | YES |  |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.CashReceived

- Row count: **0**
- Columns: **11**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | Date | datetime | YES |  |
| 3 | Z_Number | nvarchar(50) | YES |  |
| 4 | Tiltid | int(10,0) | YES |  |
| 5 | VoucherNo | nvarchar(50) | YES |  |
| 6 | Amount | decimal(18,2) | YES |  |
| 7 | CareOf | nvarchar(100) | YES |  |
| 8 | Description | nvarchar | YES |  |
| 9 | CounterId | int(10,0) | YES |  |
| 10 | User | nvarchar(50) | YES |  |
| 11 | Time | nvarchar(50) | YES |  |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.Category

- Row count: **0**
- Columns: **3**
- Primary key: CId
- Outgoing foreign keys: **1**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | CId | int(10,0) | NO |  |
| 2 | Category | nvarchar(50) | YES |  |
| 3 | COID | int(10,0) | YES |  |

Foreign key links:
- `COID` -> `dbo.Company.COId` (FK_Category_Company)

Sample data (`TOP 3`):

```text
No rows
```

### dbo.CategoryMenu

- Row count: **1**
- Columns: **2**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | Menu | bit | YES | ((0)) |

Sample data (`TOP 3`):

```json
[
  {
    "id": 1,
    "Menu": true
  }
]
```

### dbo.CategoryPOS

- Row count: **130**
- Columns: **16**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | category_name | nvarchar(50) | YES |  |
| 3 | department | nvarchar(50) | YES |  |
| 4 | TiltId | int(10,0) | YES |  |
| 5 | Color | nvarchar(50) | YES |  |
| 6 | IsComment | bit | YES | ((0)) |
| 7 | orderid | int(10,0) | NO | ((0)) |
| 8 | GetType | nvarchar(50) | YES |  |
| 9 | Is_Upload | bit | NO | ((0)) |
| 10 | Is_Update | bit | NO | ((0)) |
| 11 | Did | int(10,0) | NO |  |
| 12 | is_Discount | bit | NO | ((0)) |
| 13 | is_delete | bit | YES | ((0)) |
| 14 | BRid | int(10,0) | YES |  |
| 15 | is_tax_apply | bit | YES | ((0)) |
| 16 | is_hnh | bit | YES | ((0)) |

Sample data (`TOP 3`):

```json
[
  {
    "id": 422,
    "category_name": "Soups",
    "department": "Kitchen",
    "TiltId": null,
    "Color": "ActiveBorder",
    "IsComment": false,
    "orderid": 1,
    "GetType": "MODIFIED",
    "Is_Upload": true,
    "Is_Update": false,
    "Did": 277,
    "is_Discount": false,
    "is_delete": false,
    "BRid": 191,
    "is_tax_apply": null,
    "is_hnh": false
  },
  {
    "id": 423,
    "category_name": "Rolls",
    "department": "Kitchen",
    "TiltId": null,
    "Color": "ActiveBorder",
    "IsComment": false,
    "orderid": 2,
    "GetType": "MODIFIED",
    "Is_Upload": true,
    "Is_Update": false,
    "Did": 277,
    "is_Discount": false,
    "is_delete": false,
    "BRid": 191,
    "is_tax_apply": null,
    "is_hnh": false
  },
  {
    "id": 424,
    "category_name": "Bar B Q",
    "department": "Kitchen",
    "TiltId": null,
    "Color": "ActiveBorder",
    "IsComment": false,
    "orderid": 3,
    "GetType": "MODIFIED",
    "Is_Upload": true,
    "Is_Update": false,
    "Did": 277,
    "is_Discount": false,
    "is_delete": false,
    "BRid": 191,
    "is_tax_apply": null,
    "is_hnh": false
  }
]
```

### dbo.CategoryTiltAssign

- Row count: **0**
- Columns: **4**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | CategoryId | int(10,0) | YES |  |
| 3 | Tiltid | int(10,0) | YES |  |
| 4 | OrderType | nvarchar(50) | YES |  |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.ChartOfAccount

- Row count: **0**
- Columns: **10**
- Primary key: CAId
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | CAId | int(10,0) | NO |  |
| 2 | AccNo | int(10,0) | YES |  |
| 3 | AccName | nvarchar | YES |  |
| 4 | AccNature | nvarchar | YES |  |
| 5 | Type | nvarchar(40) | YES |  |
| 6 | Level | int(10,0) | YES |  |
| 7 | ParentId | int(10,0) | YES | ((0)) |
| 8 | Desc | varchar(40) | YES |  |
| 9 | COId | int(10,0) | YES |  |
| 10 | Op | decimal(18,2) | YES | ((0)) |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.CLI

- Row count: **0**
- Columns: **4**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | PhoneNumber | nvarchar(50) | YES |  |
| 3 | Status | int(10,0) | YES |  |
| 4 | systemId | nvarchar(50) | NO |  |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.CLI_CTI

- Row count: **0**
- Columns: **2**
- Primary key: ID
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | ID | int(10,0) | NO |  |
| 2 | FilePath | nvarchar(100) | YES |  |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.Color

- Row count: **174**
- Columns: **2**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | Color | nvarchar(50) | YES |  |

Sample data (`TOP 3`):

```json
[
  {
    "id": 1,
    "Color": "ActiveBorder"
  },
  {
    "id": 2,
    "Color": "ActiveCaption"
  },
  {
    "id": 3,
    "Color": "ActiveCaptionText"
  }
]
```

### dbo.Company

- Row count: **1**
- Columns: **11**
- Primary key: COId
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | COId | int(10,0) | NO |  |
| 2 | Company | nvarchar(50) | YES |  |
| 3 | IsSelected | bit | YES | ((1)) |
| 4 | Address | nvarchar(50) | YES |  |
| 5 | ContactNo | nvarchar(50) | YES |  |
| 6 | Fax | nvarchar(50) | YES |  |
| 7 | Email | nvarchar(50) | YES |  |
| 8 | LogoName | nvarchar(50) | YES |  |
| 9 | Logo | image(2147483647) | YES |  |
| 10 | URl | nvarchar | YES |  |
| 11 | WebURL | nvarchar(100) | YES |  |

Sample data (`TOP 3`):

```json
[
  {
    "COId": 126,
    "Company": "Hot N Spicy",
    "IsSelected": true,
    "Address": "Karachi",
    "ContactNo": "1111111111",
    "Fax": "1111111111",
    "Email": "1111111111",
    "LogoName": "Desert.jpg",
    "Logo": null,
    "URl": "http://72.52.142.19/sandbox/pos-khi/webservice/",
    "WebURL": "http://72.52.142.19/sandbox/pos-khi/webservice/"
  }
]
```

### dbo.CompanySetup

- Row count: **1**
- Columns: **18**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | Id | int(10,0) | NO |  |
| 2 | CompanyName | nvarchar(50) | YES |  |
| 3 | Address | text(2147483647) | YES |  |
| 4 | Phone1 | nvarchar(50) | YES |  |
| 5 | Fax | nvarchar(50) | YES |  |
| 6 | Email | nvarchar(50) | YES |  |
| 7 | Phone2 | nvarchar(50) | YES |  |
| 8 | Logo_ | nvarchar | YES |  |
| 9 | Logo | image(2147483647) | YES |  |
| 10 | header | bit | YES |  |
| 11 | Logo2_ | nvarchar | YES |  |
| 12 | Logo2 | image(2147483647) | YES |  |
| 13 | ReportFooter | nvarchar(60) | YES |  |
| 14 | Company_id | int(10,0) | NO | ((0)) |
| 15 | branch_id | int(10,0) | NO | ((0)) |
| 16 | URL | nvarchar | YES |  |
| 17 | Address2 | nvarchar | YES |  |
| 18 | EposURL | nvarchar(100) | YES |  |

Sample data (`TOP 3`):

```json
[
  {
    "Id": 15,
    "CompanyName": "",
    "Address": "",
    "Phone1": "",
    "Fax": "",
    "Email": "",
    "Phone2": "",
    "Logo_": "logo pos.jpg",
    "Logo": null,
    "header": true,
    "Logo2_": "logo pos.jpg",
    "Logo2": null,
    "ReportFooter": "",
    "Company_id": 0,
    "branch_id": 0,
    "URL": "",
    "Address2": null,
    "EposURL": null
  }
]
```

### dbo.Counter_Opening_Expense_Log

- Row count: **0**
- Columns: **6**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | User | nvarchar | NO |  |
| 3 | CounterId | int(10,0) | NO |  |
| 4 | date | datetime | NO |  |
| 5 | Time | nvarchar(50) | NO |  |
| 6 | Balance | decimal(18,2) | NO |  |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.currency_convertor

- Row count: **0**
- Columns: **3**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | currency | nvarchar(50) | YES |  |
| 3 | rate | decimal(18,2) | YES |  |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.Customer

- Row count: **0**
- Columns: **6**
- Primary key: CustId
- Outgoing foreign keys: **1**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | CustId | int(10,0) | NO |  |
| 2 | Customer | nvarchar | YES |  |
| 3 | Address | nvarchar | YES |  |
| 4 | CellNo | nvarchar | YES |  |
| 5 | CAId | int(10,0) | YES |  |
| 6 | COId | int(10,0) | YES |  |

Foreign key links:
- `CAId` -> `dbo.ChartOfAccount.CAId` (FK_Customer_ChartOfAccount)

Sample data (`TOP 3`):

```text
No rows
```

### dbo.customer_group

- Row count: **0**
- Columns: **2**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | customer_group_id | int(10,0) | NO |  |
| 2 | customer_group_name | nvarchar(50) | YES |  |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.CustomerLedger

- Row count: **0**
- Columns: **18**
- Primary key: None
- Outgoing foreign keys: **2**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | VoucherId | int(10,0) | YES |  |
| 3 | Amount | decimal(18,2) | YES |  |
| 4 | Type | varchar(40) | YES |  |
| 5 | CustId | int(10,0) | YES |  |
| 6 | Date | datetime | YES |  |
| 7 | COId | int(10,0) | YES |  |
| 8 | VoucherType | nvarchar(50) | YES |  |
| 9 | VN | nvarchar(50) | YES |  |
| 10 | SaleId | int(10,0) | YES |  |
| 11 | date_time | datetime | YES |  |
| 12 | Time | nvarchar(50) | YES |  |
| 13 | BuffetBookingId | int(10,0) | YES |  |
| 14 | TiltId | int(10,0) | YES |  |
| 15 | CounterId | int(10,0) | YES |  |
| 16 | ShiftNo | nvarchar(50) | YES |  |
| 17 | OpId | int(10,0) | YES |  |
| 18 | UserReceived | nvarchar(50) | YES |  |

Foreign key links:
- `COId` -> `dbo.Company.COId` (FK_CustomerLedger_Company)
- `CustId` -> `dbo.Customer.CustId` (FK_CustomerLedger_Customer)

Sample data (`TOP 3`):

```text
No rows
```

### dbo.CustomerLedgerAdvBooking

- Row count: **0**
- Columns: **20**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | VoucherId | int(10,0) | YES |  |
| 3 | Amount | decimal(18,2) | YES |  |
| 4 | Type | varchar(40) | YES |  |
| 5 | CustId | int(10,0) | YES |  |
| 6 | Date | datetime | YES |  |
| 7 | VoucherType | nvarchar(50) | YES |  |
| 8 | VN | nvarchar(50) | YES |  |
| 9 | BuffetBookingId | int(10,0) | YES |  |
| 10 | TiltId | int(10,0) | YES | ((0)) |
| 11 | CounterId | int(10,0) | YES | ((0)) |
| 12 | ShiftNo | nvarchar(50) | YES |  |
| 13 | OpId | int(10,0) | YES | ((0)) |
| 14 | UserReceived | nvarchar(500) | YES |  |
| 15 | status | bit | YES | ((0)) |
| 16 | Od | nvarchar(50) | YES |  |
| 17 | is_upload | bit | NO | ((0)) |
| 18 | is_update | bit | NO | ((0)) |
| 19 | time | nvarchar(50) | YES |  |
| 20 | Date_time | datetime | YES |  |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.CustomerPOS

- Row count: **420496**
- Columns: **13**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | order_key | nvarchar(50) | YES |  |
| 3 | customer_name | nvarchar(50) | YES |  |
| 4 | address | nvarchar(500) | YES |  |
| 5 | tel_no | nvarchar(50) | YES |  |
| 6 | cell_no | nvarchar(50) | YES |  |
| 7 | CustomerCode | nvarchar(500) | YES |  |
| 8 | Active | int(10,0) | NO | ((1)) |
| 9 | Address2 | nvarchar(500) | YES |  |
| 10 | is_upload | bit | NO | ((0)) |
| 11 | is_update | bit | NO | ((0)) |
| 12 | unique_key | varchar(50) | YES |  |
| 13 | customer_group_id | int(10,0) | NO | ((0)) |

Sample data (`TOP 3`):

```json
[
  {
    "id": 83848,
    "order_key": "76955",
    "customer_name": "ABC",
    "address": "FGDFGB",
    "tel_no": "",
    "cell_no": "213",
    "CustomerCode": "2017-0001",
    "Active": 1,
    "Address2": "",
    "is_upload": false,
    "is_update": false,
    "unique_key": null,
    "customer_group_id": 0
  },
  {
    "id": 83851,
    "order_key": "76958",
    "customer_name": "DRFDQW",
    "address": "FGDHDFJGF",
    "tel_no": "",
    "cell_no": "030005556555",
    "CustomerCode": "2017-4",
    "Active": 1,
    "Address2": "",
    "is_upload": false,
    "is_update": false,
    "unique_key": null,
    "customer_group_id": 0
  },
  {
    "id": 83855,
    "order_key": "76962",
    "customer_name": "ARIF",
    "address": "KHADAMARKET",
    "tel_no": "",
    "cell_no": "03007060768",
    "CustomerCode": "2017-5",
    "Active": 1,
    "Address2": "",
    "is_upload": false,
    "is_update": false,
    "unique_key": null,
    "customer_group_id": 0
  }
]
```

### dbo.CustomerPOS_

- Row count: **115662**
- Columns: **10**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | order_key | nvarchar(50) | YES |  |
| 3 | customer_name | nvarchar(50) | YES |  |
| 4 | address | nvarchar(500) | YES |  |
| 5 | tel_no | nvarchar(50) | YES |  |
| 6 | cell_no | nvarchar(50) | YES |  |
| 7 | CustomerCode | nvarchar(500) | YES |  |
| 8 | Active | int(10,0) | NO | ((1)) |
| 9 | Address2 | nvarchar(500) | YES |  |
| 10 | customer_group_id | int(10,0) | NO | ((0)) |

Sample data (`TOP 3`):

```json
[
  {
    "id": 30814,
    "order_key": "0",
    "customer_name": "30814",
    "address": "2017-0001",
    "tel_no": "30814",
    "cell_no": "213",
    "CustomerCode": "2017-0001",
    "Active": 0,
    "Address2": "",
    "customer_group_id": 0
  },
  {
    "id": 30817,
    "order_key": "0",
    "customer_name": "DRFDQW",
    "address": "FGDHDFJGF",
    "tel_no": "",
    "cell_no": "030005556555",
    "CustomerCode": "2017-4",
    "Active": 0,
    "Address2": "",
    "customer_group_id": 0
  },
  {
    "id": 30818,
    "order_key": "0",
    "customer_name": "arif",
    "address": "",
    "tel_no": "",
    "cell_no": "03007060768",
    "CustomerCode": "2017-5",
    "Active": 0,
    "Address2": "",
    "customer_group_id": 0
  }
]
```

### dbo.CustomerReciptDetail

- Row count: **0**
- Columns: **7**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | CustRId | int(10,0) | YES |  |
| 3 | Amount | decimal(18,2) | YES |  |
| 4 | Desc | nvarchar | YES |  |
| 5 | BuffetBookingId | int(10,0) | YES |  |
| 6 | is_upload | bit | NO | ((0)) |
| 7 | is_update | bit | NO | ((0)) |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.CustomerReciptMaster

- Row count: **0**
- Columns: **12**
- Primary key: CustRId
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | CustRId | int(10,0) | NO |  |
| 2 | PaymentNo | nvarchar(50) | YES |  |
| 3 | Date | datetime | YES |  |
| 4 | CustId | int(10,0) | YES |  |
| 5 | Amount | decimal(18,2) | YES |  |
| 6 | PaymentMode | nvarchar(50) | YES |  |
| 7 | ChequeNo | nvarchar(50) | YES |  |
| 8 | ChequeDate | datetime | YES |  |
| 9 | CreditCardNo | nvarchar(50) | YES |  |
| 10 | status | bit | YES | ((0)) |
| 11 | is_upload | bit | NO | ((0)) |
| 12 | is_update | bit | NO | ((0)) |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.CustomerSaleInvoiceDetail

- Row count: **0**
- Columns: **15**
- Primary key: None
- Outgoing foreign keys: **2**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | SLId | int(10,0) | YES |  |
| 3 | ItemId | int(10,0) | YES |  |
| 4 | Unit | int(10,0) | YES |  |
| 5 | Qty | decimal(18,2) | YES |  |
| 6 | Rate | decimal(18,2) | YES |  |
| 7 | TotalPackage | decimal(18,2) | YES |  |
| 8 | PcsPerPackage | decimal(18,2) | YES |  |
| 9 | RatePerPackage | decimal(18,2) | YES |  |
| 10 | PackageId | int(10,0) | YES |  |
| 11 | Tax | decimal(18,2) | YES | ((0)) |
| 12 | Discount | decimal(18,2) | YES | ((0)) |
| 13 | Amount | decimal(18,2) | YES | ((0)) |
| 14 | ActualRate | decimal(18,2) | YES | ((0)) |
| 15 | TaxType | nvarchar(50) | YES |  |

Foreign key links:
- `ItemId` -> `dbo.Item.ItemId` (FK_CustomerSaleInvoiceDetail_Item)
- `SLId` -> `dbo.CustomerSaleInvoiceMaster.SLId` (FK_CustomerSaleInvoiceDetail_Store_CustomerSaleInvoiceMaster_Store)

Sample data (`TOP 3`):

```text
No rows
```

### dbo.CustomerSaleInvoiceMaster

- Row count: **0**
- Columns: **12**
- Primary key: SLId
- Outgoing foreign keys: **1**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | SLId | int(10,0) | NO |  |
| 2 | Date | datetime | YES |  |
| 3 | CustId | int(10,0) | YES |  |
| 4 | SaleInvoiceNo | varchar(50) | YES |  |
| 5 | SId | int(10,0) | YES | ((0)) |
| 6 | BRId | int(10,0) | YES | ((0)) |
| 7 | Amount | decimal(18,2) | YES |  |
| 8 | Discount | decimal(18,2) | YES |  |
| 9 | TotalAmount | decimal(18,2) | YES |  |
| 10 | RefrenceNo | nvarchar(50) | YES |  |
| 11 | TotalTax | decimal(18,2) | YES |  |
| 12 | is_ob | bit | YES | ((0)) |

Foreign key links:
- `CustId` -> `dbo.Customer.CustId` (FK_CustomerSaleInvoiceMaster_Customer)

Sample data (`TOP 3`):

```text
No rows
```

### dbo.Deals

- Row count: **0**
- Columns: **13**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | deal_name | nvarchar(50) | YES |  |
| 3 | deal_price | float(53,0) | YES |  |
| 4 | category_name | nvarchar(50) | YES |  |
| 5 | item_name | nvarchar(50) | YES |  |
| 6 | qty | float(53,0) | YES |  |
| 7 | department | nvarchar(50) | YES |  |
| 8 | TiltId | int(10,0) | YES |  |
| 9 | Is_Upload | bit | NO | ((0)) |
| 10 | Is_Update | bit | NO | ((0)) |
| 11 | Deal_ItemId | int(10,0) | NO |  |
| 12 | Cid | int(10,0) | NO |  |
| 13 | ItemId | int(10,0) | NO |  |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.Deals_Dpt_Desc_Status

- Row count: **0**
- Columns: **2**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | Did | int(10,0) | NO |  |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.Deals_Item

- Row count: **0**
- Columns: **12**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | Order_Key | nvarchar(50) | NO |  |
| 3 | Order_Detail_id | int(10,0) | NO |  |
| 4 | Deal_name | nvarchar(50) | NO |  |
| 5 | deal_Price | decimal(18,2) | NO |  |
| 6 | Deal_Qty | decimal(18,2) | NO |  |
| 7 | Department | nvarchar(50) | NO |  |
| 8 | Category_name | nvarchar(50) | NO |  |
| 9 | Item_name | nvarchar(50) | NO |  |
| 10 | Item_Qty | decimal(18,2) | NO |  |
| 11 | Item_Price | decimal(18,2) | NO |  |
| 12 | item_comment | nvarchar(50) | YES |  |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.DealsOnSpot

- Row count: **0**
- Columns: **17**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | deal_name | nvarchar(50) | YES |  |
| 3 | deal_price | float(53,0) | YES |  |
| 4 | category_name | nvarchar(50) | YES |  |
| 5 | item_name | nvarchar(50) | YES |  |
| 6 | qty | float(53,0) | YES |  |
| 7 | ChooseAny | nvarchar(50) | YES |  |
| 8 | department | nvarchar(50) | YES |  |
| 9 | TiltId | int(10,0) | YES |  |
| 10 | ItemQty | float(53,0) | YES |  |
| 11 | orderid | int(10,0) | NO | ((0)) |
| 12 | GetType | nvarchar(50) | YES |  |
| 13 | Deal_ItemId | int(10,0) | NO |  |
| 14 | Cid | int(10,0) | NO |  |
| 15 | ItemId | int(10,0) | NO |  |
| 16 | is_Upload | bit | NO | ((0)) |
| 17 | is_Update | bit | NO | ((0)) |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.DealsOnSpotItems

- Row count: **0**
- Columns: **15**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | order_key | nvarchar(50) | YES |  |
| 3 | Order_detailId | int(10,0) | YES |  |
| 4 | deal_name | nvarchar(50) | YES |  |
| 5 | deal_price | float(53,0) | YES |  |
| 6 | category_name | nvarchar(50) | YES |  |
| 7 | item_name | nvarchar(50) | YES |  |
| 8 | qty | float(53,0) | YES |  |
| 9 | department | nvarchar(50) | YES |  |
| 10 | TiltId | int(10,0) | YES |  |
| 11 | Status | bit | YES | ((0)) |
| 12 | ItemQty | float(53,0) | YES |  |
| 13 | OrderKey_Merege | nvarchar(50) | YES |  |
| 14 | Price_Item | decimal(18,2) | NO | ((0)) |
| 15 | item_comment | nvarchar(50) | YES |  |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.DeliveryCharges

- Row count: **0**
- Columns: **5**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | IsActive | bit | NO | ((0)) |
| 3 | isPercent | bit | NO | ((0)) |
| 4 | Delivery Charges | decimal(18,2) | NO | ((0)) |
| 5 | Apply On Amount | decimal(18,2) | NO | ((0)) |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.DeliveryQualityPoints

- Row count: **3**
- Columns: **8**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | ServiceSatisfactory | nvarchar(50) | YES |  |
| 2 | SS_Points | decimal(18,0) | NO | ((0)) |
| 3 | FoodQuality | nvarchar(50) | YES |  |
| 4 | FQ_Points | decimal(18,0) | NO | ((0)) |
| 5 | CorrectOrder | nvarchar(50) | YES |  |
| 6 | CO_Points | decimal(18,0) | NO | ((0)) |
| 7 | OnTimeDelivery | nvarchar(50) | YES |  |
| 8 | OTD_Points | decimal(18,0) | NO | ((0)) |

Sample data (`TOP 3`):

```json
[
  {
    "ServiceSatisfactory": "Excelent",
    "SS_Points": 1.0,
    "FoodQuality": "Excelent",
    "FQ_Points": 1.0,
    "CorrectOrder": "Yes",
    "CO_Points": 1.0,
    "OnTimeDelivery": "Yes",
    "OTD_Points": 1.0
  },
  {
    "ServiceSatisfactory": "Average",
    "SS_Points": 0.0,
    "FoodQuality": "Average",
    "FQ_Points": 0.0,
    "CorrectOrder": "No",
    "CO_Points": 0.0,
    "OnTimeDelivery": "No",
    "OTD_Points": 0.0
  },
  {
    "ServiceSatisfactory": "Poor",
    "SS_Points": -1.0,
    "FoodQuality": "Poor",
    "FQ_Points": -1.0,
    "CorrectOrder": "-",
    "CO_Points": 0.0,
    "OnTimeDelivery": "-",
    "OTD_Points": 0.0
  }
]
```

### dbo.DeliveryQualityPointsTable

- Row count: **2**
- Columns: **12**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | OrderKey | nvarchar(50) | YES |  |
| 3 | SS_Execelent | nvarchar(50) | YES |  |
| 4 | SS_Average | nvarchar(50) | YES |  |
| 5 | SS_Poor | nvarchar(50) | YES |  |
| 6 | FQ_Execelent | nvarchar(50) | YES |  |
| 7 | FQ_Average | nvarchar(50) | YES |  |
| 8 | FQ_Poor | nvarchar(50) | YES |  |
| 9 | CO_Yes | nvarchar(50) | YES |  |
| 10 | CO_No | nvarchar(50) | YES |  |
| 11 | OTD_Yes | nvarchar(50) | YES |  |
| 12 | OTD_No | nvarchar(50) | YES |  |

Sample data (`TOP 3`):

```json
[
  {
    "id": 1,
    "OrderKey": "135",
    "SS_Execelent": "",
    "SS_Average": "1",
    "SS_Poor": "",
    "FQ_Execelent": "",
    "FQ_Average": "",
    "FQ_Poor": "-1",
    "CO_Yes": "-1",
    "CO_No": "0",
    "OTD_Yes": "1",
    "OTD_No": ""
  },
  {
    "id": 3,
    "OrderKey": "141",
    "SS_Execelent": "",
    "SS_Average": "0",
    "SS_Poor": "",
    "FQ_Execelent": "1",
    "FQ_Average": "",
    "FQ_Poor": "",
    "CO_Yes": "1",
    "CO_No": "",
    "OTD_Yes": "-2",
    "OTD_No": ""
  }
]
```

### dbo.DemandSheetDetail_Branch

- Row count: **0**
- Columns: **7**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | DSId | int(10,0) | YES |  |
| 3 | ItemId | int(10,0) | YES |  |
| 4 | Unit | varchar(50) | YES |  |
| 5 | Qty | decimal(18,2) | YES |  |
| 6 | Status | bit | YES | ((0)) |
| 7 | IssQty | decimal(18,2) | YES | ((0)) |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.DemandSheetDetail_Store

- Row count: **0**
- Columns: **7**
- Primary key: None
- Outgoing foreign keys: **2**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | DSCOId | int(10,0) | YES |  |
| 3 | ItemId | int(10,0) | YES |  |
| 4 | Unit | int(10,0) | YES |  |
| 5 | Qty | decimal(18,2) | YES |  |
| 6 | Status | bit | YES | ((0)) |
| 7 | POQty | decimal(18,2) | YES | ((0)) |

Foreign key links:
- `DSCOId` -> `dbo.DemandSheetMaster_Store.DSCOId` (FK_DemandSheetDetail_Company_DemandSheetMaster_Company)
- `ItemId` -> `dbo.Item.ItemId` (FK_DemandSheetDetail_Store_Item)

Sample data (`TOP 3`):

```text
No rows
```

### dbo.DemandSheetMaster_Branch

- Row count: **0**
- Columns: **7**
- Primary key: DSId
- Outgoing foreign keys: **1**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | DSId | int(10,0) | NO |  |
| 2 | BRId | int(10,0) | YES |  |
| 3 | Date | datetime | YES |  |
| 4 | DSNo | varchar(50) | YES |  |
| 5 | UserId | int(10,0) | YES |  |
| 6 | DId | int(10,0) | YES | ((0)) |
| 7 | Desc | nvarchar | YES |  |

Foreign key links:
- `BRId` -> `dbo.Branch.BRId` (FK_DemandSheetMaster_Branch_Branch)

Sample data (`TOP 3`):

```text
No rows
```

### dbo.DemandSheetMaster_Store

- Row count: **0**
- Columns: **7**
- Primary key: DSCOId
- Outgoing foreign keys: **2**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | DSCOId | int(10,0) | NO |  |
| 2 | SId | int(10,0) | YES |  |
| 3 | Date | datetime | YES |  |
| 4 | DSNo | varchar(50) | YES |  |
| 5 | COId | int(10,0) | YES |  |
| 6 | Desc | nvarchar | YES |  |
| 7 | Vid | int(10,0) | YES | ((0)) |

Foreign key links:
- `COId` -> `dbo.Company.COId` (FK_DemandSheetMaster_Store_Company)
- `SId` -> `dbo.Store.SId` (FK_DemandSheetMaster_Store_Store)

Sample data (`TOP 3`):

```text
No rows
```

### dbo.DepartmentPOS

- Row count: **14**
- Columns: **6**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | department_name | nvarchar(50) | YES |  |
| 3 | BRId | int(10,0) | YES | ((0)) |
| 4 | COId | int(10,0) | YES | ((0)) |
| 5 | Is_Upload | bit | NO | ((0)) |
| 6 | Is_Update | bit | NO | ((0)) |

Sample data (`TOP 3`):

```json
[
  {
    "id": 277,
    "department_name": "Kitchen",
    "BRId": 191,
    "COId": 126,
    "Is_Upload": true,
    "Is_Update": false
  },
  {
    "id": 278,
    "department_name": "Bar",
    "BRId": 191,
    "COId": 126,
    "Is_Upload": true,
    "Is_Update": false
  },
  {
    "id": 279,
    "department_name": "KITCHEN",
    "BRId": 161,
    "COId": 126,
    "Is_Upload": true,
    "Is_Update": false
  }
]
```

### dbo.DeploymentDetail

- Row count: **0**
- Columns: **2**
- Primary key: ID
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | ID | int(10,0) | NO |  |
| 2 | Date | datetime | NO |  |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.device_tilt_assign

- Row count: **0**
- Columns: **5**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | tilt_id | int(10,0) | NO |  |
| 3 | device_no | nvarchar(50) | YES |  |
| 4 | is_upload | int(10,0) | YES | ((0)) |
| 5 | is_update | int(10,0) | YES | ((0)) |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.Dine_In_Order

- Row count: **81965**
- Columns: **80**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | order_key | nvarchar(50) | YES |  |
| 3 | z_number | nvarchar(50) | YES |  |
| 4 | order_type | nvarchar(50) | YES |  |
| 5 | order_no | int(10,0) | YES |  |
| 6 | order_date | datetime | YES |  |
| 7 | day | nvarchar(50) | YES |  |
| 8 | table_no | nvarchar(50) | YES |  |
| 9 | waiter_name | nvarchar(50) | YES |  |
| 10 | order_time | nvarchar(50) | YES |  |
| 11 | service_time | nvarchar(50) | YES |  |
| 12 | service_status | nvarchar(50) | YES |  |
| 13 | account_status | nvarchar(50) | YES |  |
| 14 | amount | float(53,0) | YES |  |
| 15 | DiscountType | nvarchar(50) | YES |  |
| 16 | discount | decimal(18,2) | YES | ((0)) |
| 17 | is_delete | bit | YES | ((0)) |
| 18 | cover | decimal(18,0) | NO | ('0') |
| 19 | estimated_time | nvarchar(50) | YES |  |
| 20 | table_time | nvarchar(50) | YES |  |
| 21 | kitchen_status | bit | NO | ((0)) |
| 22 | Tiltid | int(10,0) | YES |  |
| 23 | CounterId | int(10,0) | YES |  |
| 24 | IsBill | bit | YES | ((0)) |
| 25 | CareOff | nvarchar(100) | YES |  |
| 26 | IsSelect | bit | YES | ((0)) |
| 27 | Customer | nvarchar | YES |  |
| 28 | Tele | nvarchar(50) | YES |  |
| 29 | ExtraCharges | decimal(18,2) | YES | ((0)) |
| 30 | DeleteReason | nvarchar | YES |  |
| 31 | UserPunch | nvarchar | YES |  |
| 32 | UserCash | nvarchar | YES |  |
| 33 | UserDelete | nvarchar | YES |  |
| 34 | KOT | int(10,0) | YES | ((0)) |
| 35 | tableStatus | bit | YES | ((0)) |
| 36 | OrderTiltId | int(10,0) | YES | ((0)) |
| 37 | TimeIn | datetime | YES |  |
| 38 | TimeOut | datetime | YES |  |
| 39 | Status | bit | NO | ((0)) |
| 40 | Od | int(10,0) | NO | ((0)) |
| 41 | Itemqty | float(53,0) | NO | ((0)) |
| 42 | Itemprice | float(53,0) | NO | ((0)) |
| 43 | OrderKey_Merege | nvarchar(50) | YES |  |
| 44 | DispatchTime | nvarchar(50) | YES |  |
| 45 | OrderStatus | nvarchar(50) | YES |  |
| 46 | PaymentMode | nvarchar(50) | YES |  |
| 47 | isFeedback | bit | NO | ((0)) |
| 48 | Feedback | nvarchar | YES |  |
| 49 | isFeedbackDone | bit | NO | ((0)) |
| 50 | IsServiceCharges | bit | NO | ((0)) |
| 51 | ServiceCharges | decimal(18,2) | NO | ((0)) |
| 52 | TabUserPunch | nvarchar(50) | YES |  |
| 53 | is_upload | bit | NO | ((0)) |
| 54 | is_update | bit | NO | ((0)) |
| 55 | Date | datetime | YES |  |
| 56 | DeleteOrderStatus | bit | NO | ((0)) |
| 57 | DiscountId | nvarchar(50) | YES |  |
| 58 | branchId | int(10,0) | NO | ((0)) |
| 59 | is_order_TransferedTo_Branch | bit | NO | ((0)) |
| 60 | is_Branch_Received_Order | bit | NO | ((0)) |
| 61 | Rider_Commision | decimal(18,2) | NO | ((0)) |
| 62 | Rider_IsPercent | bit | NO | ((0)) |
| 63 | Rider_Commision_Percent | decimal(18,2) | NO | ((0)) |
| 64 | CommentsForRider | nvarchar | YES |  |
| 65 | Is_Manual_ExtraCharges | bit | NO | ((0)) |
| 66 | TokenNumber | nvarchar(100) | YES |  |
| 67 | is_deleted_print | int(10,0) | YES |  |
| 68 | user_id | int(10,0) | NO | ((0)) |
| 69 | FeedbackApi | bit | YES | ((0)) |
| 70 | is_BillReceive | bit | YES | ((0)) |
| 71 | unique_key | varchar(50) | YES |  |
| 72 | advance_amount | decimal(18,2) | YES | ((0)) |
| 73 | deliver_time | datetime | YES |  |
| 74 | dispatch_time | datetime | YES |  |
| 75 | duration | varchar(20) | YES |  |
| 76 | is_table_transfer | bit | YES | ((0)) |
| 77 | android_device_no | nvarchar(50) | YES |  |
| 78 | new_order_no | nvarchar(50) | YES |  |
| 79 | kds_done | bit | YES | ((0)) |
| 80 | luckyDraw | int(10,0) | YES | ((0)) |

Sample data (`TOP 3`):

```json
[
  {
    "id": 537206,
    "order_key": "0.00",
    "z_number": "DAY-00001",
    "order_type": "DELIVERY",
    "order_no": 77300,
    "order_date": "2021-06-19T21:55:00",
    "day": "Wednesday",
    "table_no": "",
    "waiter_name": "",
    "order_time": "09:52 PM",
    "service_time": null,
    "service_status": "",
    "account_status": "Not Paid",
    "amount": 0.0,
    "DiscountType": null,
    "discount": 0.0,
    "is_delete": false,
    "cover": 0.0,
    "estimated_time": "06/19/21 9:52 PM",
    "table_time": null,
    "kitchen_status": false,
    "Tiltid": 47,
    "CounterId": 397,
    "IsBill": false,
    "CareOff": null,
    "IsSelect": false,
    "Customer": "",
    "Tele": "",
    "ExtraCharges": 0.0,
    "DeleteReason": null,
    "UserPunch": "PC 2",
    "UserCash": null,
    "UserDelete": null,
    "KOT": 0,
    "tableStatus": false,
    "OrderTiltId": 0,
    "TimeIn": "1900-01-01T21:52:00",
    "TimeOut": null,
    "Status": false,
    "Od": 77300,
    "Itemqty": 0.0,
    "Itemprice": 0.0,
    "OrderKey_Merege": null,
    "DispatchTime": null,
    "OrderStatus": null,
    "PaymentMode": null,
    "isFeedback": false,
    "Feedback": null,
    "isFeedbackDone": false,
    "IsServiceCharges": false,
    "ServiceCharges": 0.0,
    "TabUserPunch": null,
    "is_upload": false,
    "is_update": false,
    "Date": "2021-06-19T21:55:00",
    "DeleteOrderStatus": false,
    "DiscountId": null,
    "branchId": 0,
    "is_order_TransferedTo_Branch": false,
    "is_Branch_Received_Order": false,
    "Rider_Commision": 0.0,
    "Rider_IsPercent": false,
    "Rider_Commision_Percent": 0.0,
    "CommentsForRider": null,
    "Is_Manual_ExtraCharges": false,
    "TokenNumber": null,
    "is_deleted_print": null,
    "user_id": 0,
    "FeedbackApi": false,
    "is_BillReceive": false,
    "unique_key": null,
    "advance_amount": 0.0,
    "deliver_time": null,
    "dispatch_time": null,
    "duration": null,
    "is_table_transfer": false,
    "android_device_no": null,
    "new_order_no": null,
    "kds_done": false,
    "luckyDraw": 0
  },
  {
    "id": 537749,
    "order_key": "0.00",
    "z_number": "DAY-00001",
    "order_type": "DELIVERY",
    "order_no": 77843,
    "order_date": "2021-06-20T21:58:00",
    "day": "Wednesday",
    "table_no": "",
    "waiter_name": "",
    "order_time": "09:55 PM",
    "service_time": null,
    "service_status": "",
    "account_status": "Not Paid",
    "amount": 0.0,
    "DiscountType": null,
    "discount": 0.0,
    "is_delete": false,
    "cover": 0.0,
    "estimated_time": "06/20/21 9:55 PM",
    "table_time": null,
    "kitchen_status": false,
    "Tiltid": 57,
    "CounterId": 391,
    "IsBill": false,
    "CareOff": null,
    "IsSelect": false,
    "Customer": "",
    "Tele": "",
    "ExtraCharges": 0.0,
    "DeleteReason": null,
    "UserPunch": "PC 5",
    "UserCash": null,
    "UserDelete": null,
    "KOT": 0,
    "tableStatus": false,
    "OrderTiltId": 0,
    "TimeIn": "1900-01-01T21:55:00",
    "TimeOut": null,
    "Status": false,
    "Od": 77843,
    "Itemqty": 0.0,
    "Itemprice": 0.0,
    "OrderKey_Merege": null,
    "DispatchTime": null,
    "OrderStatus": null,
    "PaymentMode": null,
    "isFeedback": false,
    "Feedback": null,
    "isFeedbackDone": false,
    "IsServiceCharges": false,
    "ServiceCharges": 0.0,
    "TabUserPunch": null,
    "is_upload": false,
    "is_update": false,
    "Date": "2021-06-20T21:58:00",
    "DeleteOrderStatus": false,
    "DiscountId": null,
    "branchId": 0,
    "is_order_TransferedTo_Branch": false,
    "is_Branch_Received_Order": false,
    "Rider_Commision": 0.0,
    "Rider_IsPercent": false,
    "Rider_Commision_Percent": 0.0,
    "CommentsForRider": null,
    "Is_Manual_ExtraCharges": false,
    "TokenNumber": null,
    "is_deleted_print": null,
    "user_id": 0,
    "FeedbackApi": false,
    "is_BillReceive": false,
    "unique_key": null,
    "advance_amount": 0.0,
    "deliver_time": null,
    "dispatch_time": null,
    "duration": null,
    "is_table_transfer": false,
    "android_device_no": null,
    "new_order_no": null,
    "kds_done": false,
    "luckyDraw": 0
  },
  {
    "id": 541158,
    "order_key": "0.00",
    "z_number": "DAY-00001",
    "order_type": "DELIVERY",
    "order_no": 79307,
    "order_date": "2021-06-24T21:18:00",
    "day": "Wednesday",
    "table_no": "",
    "waiter_name": "",
    "order_time": "09:17 PM",
    "service_time": null,
    "service_status": "",
    "account_status": "Not Paid",
    "amount": 0.0,
    "DiscountType": null,
    "discount": 0.0,
    "is_delete": false,
    "cover": 0.0,
    "estimated_time": "06/24/21 9:17 PM",
    "table_time": null,
    "kitchen_status": false,
    "Tiltid": 53,
    "CounterId": 405,
    "IsBill": false,
    "CareOff": null,
    "IsSelect": false,
    "Customer": "",
    "Tele": "",
    "ExtraCharges": 0.0,
    "DeleteReason": null,
    "UserPunch": "PC 4",
    "UserCash": null,
    "UserDelete": null,
    "KOT": 0,
    "tableStatus": false,
    "OrderTiltId": 0,
    "TimeIn": "1900-01-01T21:17:00",
    "TimeOut": null,
    "Status": false,
    "Od": 79307,
    "Itemqty": 0.0,
    "Itemprice": 0.0,
    "OrderKey_Merege": null,
    "DispatchTime": null,
    "OrderStatus": null,
    "PaymentMode": null,
    "isFeedback": false,
    "Feedback": null,
    "isFeedbackDone": false,
    "IsServiceCharges": false,
    "ServiceCharges": 0.0,
    "TabUserPunch": null,
    "is_upload": false,
    "is_update": false,
    "Date": "2021-06-24T21:18:00",
    "DeleteOrderStatus": false,
    "DiscountId": null,
    "branchId": 0,
    "is_order_TransferedTo_Branch": false,
    "is_Branch_Received_Order": false,
    "Rider_Commision": 0.0,
    "Rider_IsPercent": false,
    "Rider_Commision_Percent": 0.0,
    "CommentsForRider": null,
    "Is_Manual_ExtraCharges": false,
    "TokenNumber": null,
    "is_deleted_print": null,
    "user_id": 0,
    "FeedbackApi": false,
    "is_BillReceive": false,
    "unique_key": null,
    "advance_amount": 0.0,
    "deliver_time": null,
    "dispatch_time": null,
    "duration": null,
    "is_table_transfer": false,
    "android_device_no": null,
    "new_order_no": null,
    "kds_done": false,
    "luckyDraw": 0
  }
]
```

### dbo.Discount

- Row count: **0**
- Columns: **16**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | date | datetime | YES |  |
| 3 | order_key | nvarchar(50) | YES |  |
| 4 | order_num | nvarchar(50) | YES |  |
| 5 | c_o | nvarchar(50) | YES |  |
| 6 | payment_type | nvarchar(50) | YES |  |
| 7 | order_type | nvarchar(50) | YES |  |
| 8 | discount | float(53,0) | YES |  |
| 9 | percent | nvarchar(50) | YES |  |
| 10 | z_num | nvarchar(50) | YES |  |
| 11 | order_price | float(53,0) | YES |  |
| 12 | Tiltid | int(10,0) | YES |  |
| 13 | CounterId | int(10,0) | YES |  |
| 14 | Status | bit | NO | ((0)) |
| 15 | is_upload | bit | NO | ((0)) |
| 16 | is_update | bit | NO | ((0)) |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.DiscountMapping

- Row count: **7**
- Columns: **5**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | Id | int(10,0) | NO |  |
| 2 | CAId | int(10,0) | YES |  |
| 3 | Type | nvarchar(50) | YES |  |
| 4 | Transaction | nvarchar(50) | YES |  |
| 5 | Form | nvarchar(50) | YES |  |

Sample data (`TOP 3`):

```json
[
  {
    "Id": 1,
    "CAId": 23,
    "Type": "D",
    "Transaction": "STOCK",
    "Form": "PURCHASE"
  },
  {
    "Id": 2,
    "CAId": 23,
    "Type": "C",
    "Transaction": "STOCK STORE",
    "Form": "ISSUANCE"
  },
  {
    "Id": 3,
    "CAId": 33,
    "Type": "D",
    "Transaction": "STOCK KITCHEN",
    "Form": "ISSUANCE"
  }
]
```

### dbo.DiscountSetting

- Row count: **0**
- Columns: **12**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | CareOf | nvarchar(100) | YES |  |
| 3 | Percentage | decimal(18,2) | YES |  |
| 4 | IsPercent | bit | YES | ((0)) |
| 5 | from | nvarchar(50) | YES |  |
| 6 | To | nvarchar(50) | YES |  |
| 7 | OrderType | nvarchar(50) | YES |  |
| 8 | Is_HappyHour | bit | NO | ((0)) |
| 9 | IsActive | bit | NO | ((0)) |
| 10 | AutoDiscount | bit | NO | ((0)) |
| 11 | credit_card_info | nvarchar | YES |  |
| 12 | IsBank | bit | YES | ((0)) |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.Ent

- Row count: **0**
- Columns: **11**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | order_key | nvarchar(50) | YES |  |
| 3 | order_num | nvarchar(50) | YES |  |
| 4 | date | datetime | YES |  |
| 5 | name | nvarchar(50) | YES |  |
| 6 | c_o | nvarchar(50) | YES |  |
| 7 | z_num | nvarchar(50) | YES |  |
| 8 | Tiltid | int(10,0) | YES |  |
| 9 | CounterId | int(10,0) | YES |  |
| 10 | is_upload | bit | NO | ((0)) |
| 11 | is_update | bit | NO | ((0)) |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.EntTableLimit

- Row count: **0**
- Columns: **3**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | tableNo | nvarchar(50) | YES |  |
| 3 | limit | float(53,0) | YES |  |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.Fixed_Comments_Instructions

- Row count: **0**
- Columns: **2**
- Primary key: id
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | Comments | nvarchar | YES |  |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.GL

- Row count: **0**
- Columns: **10**
- Primary key: None
- Outgoing foreign keys: **2**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | Type | varchar(40) | YES |  |
| 3 | VN | nvarchar(50) | YES |  |
| 4 | VoucherId | int(10,0) | YES |  |
| 5 | Date | datetime | YES |  |
| 6 | Amount | decimal(18,2) | YES |  |
| 7 | CAId | int(10,0) | YES |  |
| 8 | VoucherType | varchar(40) | YES |  |
| 9 | COId | int(10,0) | YES |  |
| 10 | APId | int(10,0) | YES | ((0)) |

Foreign key links:
- `CAId` -> `dbo.ChartOfAccount.CAId` (ChartOfAccount_GL)
- `COId` -> `dbo.Company.COId` (FK_GL_Company)

Sample data (`TOP 3`):

```text
No rows
```

### dbo.GRNDetail

- Row count: **0**
- Columns: **18**
- Primary key: None
- Outgoing foreign keys: **2**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | GRNId | int(10,0) | YES |  |
| 3 | ItemId | int(10,0) | YES |  |
| 4 | Unit | int(10,0) | YES |  |
| 5 | Qty | decimal(18,2) | YES |  |
| 6 | POId | int(10,0) | YES |  |
| 7 | Rate | decimal(18,2) | YES |  |
| 8 | TotalPackage | decimal(18,2) | YES |  |
| 9 | PcsPerPackage | decimal(18,2) | YES |  |
| 10 | RatePerPackage | decimal(18,2) | YES |  |
| 11 | PackageId | int(10,0) | YES |  |
| 12 | Tax | decimal(18,2) | YES | ((0)) |
| 13 | Discount | decimal(18,2) | YES | ((0)) |
| 14 | Amount | decimal(18,2) | YES | ((0)) |
| 15 | ActualRate | decimal(18,2) | YES | ((0)) |
| 16 | TaxType | nvarchar(50) | YES |  |
| 17 | RatePerPcs | decimal(18,2) | NO | ((0)) |
| 18 | Qty_Pcs | decimal(18,2) | YES | ((0)) |

Foreign key links:
- `ItemId` -> `dbo.Item.ItemId` (FK_GRNDetail_Item)
- `GRNId` -> `dbo.GRNMaster.GRNId` (FK_GRNDetail_Store_GRNMaster_Store)

Sample data (`TOP 3`):

```text
No rows
```

### dbo.GRNMaster

- Row count: **0**
- Columns: **13**
- Primary key: GRNId
- Outgoing foreign keys: **1**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | GRNId | int(10,0) | NO |  |
| 2 | Date | datetime | YES |  |
| 3 | VId | int(10,0) | YES |  |
| 4 | GRNo | varchar(50) | YES |  |
| 5 | SId | int(10,0) | YES | ((0)) |
| 6 | BRId | int(10,0) | YES | ((0)) |
| 7 | Amount | decimal(18,2) | YES |  |
| 8 | Discount | decimal(18,2) | YES |  |
| 9 | TotalAmount | decimal(18,2) | YES |  |
| 10 | RefrenceNo | nvarchar(50) | YES |  |
| 11 | TotalTax | decimal(18,2) | YES |  |
| 12 | Desc | nvarchar | YES |  |
| 13 | uid | int(10,0) | YES | ((0)) |

Foreign key links:
- `VId` -> `dbo.Vendor.VId` (FK_GRNMaster_Vendor)

Sample data (`TOP 3`):

```text
No rows
```

### dbo.Group

- Row count: **0**
- Columns: **3**
- Primary key: GRId
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | GRId | int(10,0) | NO |  |
| 2 | Group | nvarchar(50) | YES |  |
| 3 | COId | int(10,0) | YES |  |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.InvAdjDetail_Branch

- Row count: **0**
- Columns: **7**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | AdjBRId | int(10,0) | YES |  |
| 3 | ItemId | int(10,0) | YES |  |
| 4 | Unit | int(10,0) | YES |  |
| 5 | Qty | decimal(18,2) | YES |  |
| 6 | Rate | decimal(18,2) | YES |  |
| 7 | Type | nvarchar(50) | YES |  |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.InvAdjDetail_Store

- Row count: **0**
- Columns: **7**
- Primary key: None
- Outgoing foreign keys: **1**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | AdjId | int(10,0) | YES |  |
| 3 | ItemId | int(10,0) | YES |  |
| 4 | Unit | int(10,0) | YES |  |
| 5 | Qty | decimal(18,2) | YES |  |
| 6 | Rate | decimal(18,2) | YES |  |
| 7 | Type | nvarchar(50) | YES |  |

Foreign key links:
- `ItemId` -> `dbo.Item.ItemId` (FK_InvAdjDetail_Store_Item)

Sample data (`TOP 3`):

```text
No rows
```

### dbo.InvAdjMaster_Branch

- Row count: **0**
- Columns: **9**
- Primary key: AdjBRId
- Outgoing foreign keys: **1**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | AdjBRId | int(10,0) | NO |  |
| 2 | Date | datetime | YES |  |
| 3 | UserId | int(10,0) | YES |  |
| 4 | BRId | int(10,0) | YES |  |
| 5 | IsApprove | bit | YES |  |
| 6 | AdjNo | varchar(50) | YES |  |
| 7 | AppById | int(10,0) | YES | ((0)) |
| 8 | DId | int(10,0) | YES | ((0)) |
| 9 | Desc | nvarchar | YES |  |

Foreign key links:
- `BRId` -> `dbo.Branch.BRId` (FK_InvAdjMaster_Branch_Branch)

Sample data (`TOP 3`):

```text
No rows
```

### dbo.InvAdjMaster_Store

- Row count: **0**
- Columns: **8**
- Primary key: AdjId
- Outgoing foreign keys: **1**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | AdjId | int(10,0) | NO |  |
| 2 | Date | datetime | YES |  |
| 3 | UserId | int(10,0) | YES |  |
| 4 | SId | int(10,0) | YES |  |
| 5 | IsApprove | bit | YES |  |
| 6 | AdjNo | varchar(50) | YES |  |
| 7 | AppById | int(10,0) | YES | ((0)) |
| 8 | Desc | nvarchar | YES |  |

Foreign key links:
- `SId` -> `dbo.Store.SId` (FK_InvAdjMaster_Store_Store)

Sample data (`TOP 3`):

```text
No rows
```

### dbo.InvoiceDetail_Company

- Row count: **0**
- Columns: **18**
- Primary key: None
- Outgoing foreign keys: **2**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | InvoiceId | int(10,0) | YES |  |
| 3 | ItemId | int(10,0) | YES |  |
| 4 | Unit | int(10,0) | YES |  |
| 5 | Rate | decimal(18,0) | YES |  |
| 6 | Qty | decimal(18,0) | YES |  |
| 7 | POId | int(10,0) | YES |  |
| 8 | DiscountPerPcs | decimal(18,2) | YES |  |
| 9 | TaxPerPcs | decimal(18,2) | YES |  |
| 10 | TotalPackage | decimal(18,2) | YES |  |
| 11 | PcsPerPackage | decimal(18,2) | YES |  |
| 12 | RatePerPackage | decimal(18,2) | YES |  |
| 13 | PackageId | int(10,0) | YES |  |
| 14 | TaxType | nvarchar(50) | YES |  |
| 15 | NetAmount | decimal(18,2) | YES |  |
| 16 | Amount | decimal(18,2) | YES |  |
| 17 | TaxMode | int(10,0) | YES |  |
| 18 | GRNId | int(10,0) | YES | ((0)) |

Foreign key links:
- `InvoiceId` -> `dbo.InvoiceMaster_Company.InvoiceId` (FK_InvoiceDetail_Company_InvoiceMaster_Company)
- `ItemId` -> `dbo.Item.ItemId` (FK_InvoiceDetail_Company_Item)

Sample data (`TOP 3`):

```text
No rows
```

### dbo.InvoiceDetail_CompanyNew

- Row count: **0**
- Columns: **17**
- Primary key: None
- Outgoing foreign keys: **3**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | InvoiceId | int(10,0) | YES |  |
| 3 | ItemId | int(10,0) | YES |  |
| 4 | Unit | int(10,0) | YES |  |
| 5 | Qty | decimal(18,2) | YES |  |
| 6 | POId | int(10,0) | YES |  |
| 7 | GRNId | int(10,0) | YES |  |
| 8 | Rate | decimal(18,2) | YES |  |
| 9 | TotalPackage | decimal(18,2) | YES |  |
| 10 | PcsPerPackage | decimal(18,2) | YES |  |
| 11 | RatePerPackage | decimal(18,2) | YES |  |
| 12 | PackageId | int(10,0) | YES |  |
| 13 | Tax | decimal(18,2) | YES | ((0)) |
| 14 | Discount | decimal(18,2) | YES | ((0)) |
| 15 | Amount | decimal(18,2) | YES | ((0)) |
| 16 | ActualRate | decimal(18,2) | YES | ((0)) |
| 17 | TaxType | nvarchar(50) | YES |  |

Foreign key links:
- `GRNId` -> `dbo.GRNMaster.GRNId` (FK_InvoiceDetail_CompanyNew_GRNMaster)
- `InvoiceId` -> `dbo.InvoiceMaster_CompanyNew.InvoiceId` (FK_InvoiceDetail_CompanyNew_InvoiceMaster_CompanyNew)
- `ItemId` -> `dbo.Item.ItemId` (FK_InvoiceDetail_CompanyNew_Item)

Sample data (`TOP 3`):

```text
No rows
```

### dbo.InvoiceMaster_Company

- Row count: **0**
- Columns: **14**
- Primary key: InvoiceId
- Outgoing foreign keys: **2**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | InvoiceId | int(10,0) | NO |  |
| 2 | Date | datetime | YES |  |
| 3 | COId | int(10,0) | YES |  |
| 4 | UserId | int(10,0) | YES |  |
| 5 | VId | int(10,0) | YES |  |
| 6 | InvoiceNo | varchar(50) | YES |  |
| 7 | SId | int(10,0) | YES |  |
| 8 | BRId | int(10,0) | YES |  |
| 9 | Amount | decimal(18,2) | YES |  |
| 10 | Discount | decimal(18,2) | YES |  |
| 11 | TotalAmount | decimal(18,2) | YES |  |
| 12 | GRNId | int(10,0) | YES |  |
| 13 | RefrenceNo | nvarchar(50) | YES |  |
| 14 | TotalTax | decimal(18,2) | YES |  |

Foreign key links:
- `COId` -> `dbo.Company.COId` (FK_InvoiceMaster_Company_Company)
- `VId` -> `dbo.Vendor.VId` (FK_InvoiceMaster_Company_Vendor)

Sample data (`TOP 3`):

```text
No rows
```

### dbo.InvoiceMaster_CompanyNew

- Row count: **0**
- Columns: **11**
- Primary key: InvoiceId
- Outgoing foreign keys: **1**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | InvoiceId | int(10,0) | NO |  |
| 2 | Date | datetime | YES |  |
| 3 | VId | int(10,0) | YES |  |
| 4 | InvoiceNo | varchar(50) | YES |  |
| 5 | SId | int(10,0) | YES | ((0)) |
| 6 | BRId | int(10,0) | YES | ((0)) |
| 7 | Amount | decimal(18,2) | YES |  |
| 8 | Discount | decimal(18,2) | YES |  |
| 9 | TotalAmount | decimal(18,2) | YES |  |
| 10 | RefrenceNo | nvarchar(50) | YES |  |
| 11 | TotalTax | decimal(18,2) | YES |  |

Foreign key links:
- `VId` -> `dbo.Vendor.VId` (FK_InvoiceMaster_CompanyNew_Vendor)

Sample data (`TOP 3`):

```text
No rows
```

### dbo.IssuanceButcheryDetail

- Row count: **0**
- Columns: **7**
- Primary key: None
- Outgoing foreign keys: **1**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | Id | int(10,0) | NO |  |
| 2 | BUTId | int(10,0) | YES |  |
| 3 | ItemId | int(10,0) | YES |  |
| 4 | Unit | int(10,0) | YES |  |
| 5 | Rate | decimal(18,2) | YES |  |
| 6 | Qty | decimal(18,2) | YES |  |
| 7 | Amount | decimal(18,2) | YES |  |

Foreign key links:
- `BUTId` -> `dbo.IssuanceButcheryMaster.BUTId` (FK_IssuanceButcheryDetail_IssuanceButcheryMaster)

Sample data (`TOP 3`):

```text
No rows
```

### dbo.IssuanceButcheryMaster

- Row count: **0**
- Columns: **6**
- Primary key: BUTId
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | BUTId | int(10,0) | NO |  |
| 2 | Date | datetime | YES |  |
| 3 | SId | int(10,0) | YES |  |
| 4 | UserId | int(10,0) | YES |  |
| 5 | BRId | int(10,0) | YES |  |
| 6 | ISSBNo | nvarchar(50) | YES |  |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.IssuanceDetail_Store

- Row count: **0**
- Columns: **9**
- Primary key: None
- Outgoing foreign keys: **1**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | IssId | int(10,0) | YES |  |
| 3 | ItemId | int(10,0) | YES |  |
| 4 | Unit | int(10,0) | YES |  |
| 5 | Rate | decimal(18,2) | YES |  |
| 6 | Qty | decimal(18,2) | YES |  |
| 7 | Amount | decimal(18,2) | YES |  |
| 8 | DSId | int(10,0) | YES | ((0)) |
| 9 | Qty_Pcs | decimal(18,2) | YES | ((0)) |

Foreign key links:
- `IssId` -> `dbo.IssuanceMaster_Store.IssId` (FK_IssuanceDetail_Store_IssuanceMaster_Store)

Sample data (`TOP 3`):

```text
No rows
```

### dbo.IssuanceMaster_Store

- Row count: **0**
- Columns: **12**
- Primary key: IssId
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | IssId | int(10,0) | NO |  |
| 2 | Date | datetime | YES |  |
| 3 | SId | int(10,0) | YES |  |
| 4 | BRId | int(10,0) | YES |  |
| 5 | UserId | int(10,0) | YES |  |
| 6 | Type | varchar(50) | YES |  |
| 7 | IssNo | varchar(50) | YES |  |
| 8 | DSId | int(10,0) | YES |  |
| 9 | PSId | int(10,0) | YES | ((0)) |
| 10 | DId | int(10,0) | YES | ((0)) |
| 11 | GRNId | int(10,0) | YES | ((0)) |
| 12 | Desc | nvarchar | YES |  |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.IssuanceReaturnDetail

- Row count: **0**
- Columns: **7**
- Primary key: None
- Outgoing foreign keys: **1**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | Id | int(10,0) | NO |  |
| 2 | IssRTId | int(10,0) | YES |  |
| 3 | ItemId | int(10,0) | YES |  |
| 4 | Unit | int(10,0) | YES |  |
| 5 | Rate | decimal(18,2) | YES |  |
| 6 | QTY | decimal(18,2) | YES |  |
| 7 | Amount | decimal(18,2) | YES |  |

Foreign key links:
- `IssRTId` -> `dbo.IssuanceReturnMaster.IssRTId` (FK_IssuanceReaturnDetail_IssuanceReturnMaster)

Sample data (`TOP 3`):

```text
No rows
```

### dbo.IssuanceReturnMaster

- Row count: **0**
- Columns: **8**
- Primary key: IssRTId
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | IssRTId | int(10,0) | NO |  |
| 2 | Date | datetime | YES |  |
| 3 | SId | int(10,0) | YES |  |
| 4 | BRId | int(10,0) | YES |  |
| 5 | UserId | int(10,0) | YES |  |
| 6 | IssRNo | nvarchar(50) | YES |  |
| 7 | DSId | int(10,0) | YES |  |
| 8 | DId | int(10,0) | YES | ((0)) |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.Item

- Row count: **0**
- Columns: **8**
- Primary key: ItemId
- Outgoing foreign keys: **1**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | ItemId | int(10,0) | NO |  |
| 2 | SBId | int(10,0) | YES |  |
| 3 | Item | nvarchar(50) | YES |  |
| 4 | GRId | int(10,0) | YES | ((0)) |
| 5 | ItemCode | nvarchar(50) | YES |  |
| 6 | Type | nvarchar(50) | YES |  |
| 7 | Yield | decimal(18,2) | NO | ((0)) |
| 8 | Vid | int(10,0) | YES | ((0)) |

Foreign key links:
- `SBId` -> `dbo.SubCategory.SBId` (FK_Item_SubCategory)

Sample data (`TOP 3`):

```text
No rows
```

### dbo.Item_Delete

- Row count: **3034**
- Columns: **21**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | order_key | nvarchar(50) | YES |  |
| 3 | order_num | nvarchar(50) | YES |  |
| 4 | date | datetime | YES |  |
| 5 | z_num | nvarchar(50) | YES |  |
| 6 | operator | nvarchar(50) | YES |  |
| 7 | category | nvarchar(50) | YES |  |
| 8 | item | nvarchar(50) | YES |  |
| 9 | qty | float(53,0) | YES |  |
| 10 | price | float(53,0) | YES |  |
| 11 | waiter | nvarchar(50) | YES |  |
| 12 | order_type | nvarchar(50) | YES |  |
| 13 | status | nvarchar(50) | YES |  |
| 14 | shift | nvarchar(50) | YES |  |
| 15 | tiltId | int(10,0) | YES |  |
| 16 | CounterId | int(10,0) | YES |  |
| 17 | Status1 | bit | NO | ((0)) |
| 18 | is_upload | bit | NO | ((0)) |
| 19 | is_update | bit | NO | ((0)) |
| 20 | head_order_key | int(10,0) | YES |  |
| 21 | unique_key | varchar(50) | YES |  |

Sample data (`TOP 3`):

```json
[
  {
    "id": 27757,
    "order_key": "417963",
    "order_num": "1257",
    "date": "2020-12-09T12:02:00",
    "z_num": "DAY-00001",
    "operator": "PC-15",
    "category": "ROLLS",
    "item": "BEEF BEHARI ROLL",
    "qty": 1.0,
    "price": 150.0,
    "waiter": "",
    "order_type": "DELIVERY",
    "status": "PC-15",
    "shift": "",
    "tiltId": 46,
    "CounterId": 399,
    "Status1": false,
    "is_upload": false,
    "is_update": true,
    "head_order_key": null,
    "unique_key": null
  },
  {
    "id": 28819,
    "order_key": "420261",
    "order_num": "2580",
    "date": "2020-12-09T12:02:00",
    "z_num": "DAY-00001",
    "operator": "PC 6",
    "category": "BAR B Q",
    "item": "CHICKEN RESHMI KABAB",
    "qty": 1.0,
    "price": 420.0,
    "waiter": "BABAR 03072027966",
    "order_type": "DELIVERY",
    "status": "PC 6",
    "shift": "",
    "tiltId": 52,
    "CounterId": 392,
    "Status1": false,
    "is_upload": false,
    "is_update": true,
    "head_order_key": null,
    "unique_key": null
  },
  {
    "id": 28830,
    "order_key": "421685",
    "order_num": "3005",
    "date": "2020-12-09T12:02:00",
    "z_num": "DAY-00001",
    "operator": "PC 6",
    "category": "ROLLS",
    "item": "BEEF BEHARI CHATNI ROLL",
    "qty": 2.0,
    "price": 300.0,
    "waiter": "",
    "order_type": "DELIVERY",
    "status": "PC 6",
    "shift": "",
    "tiltId": 52,
    "CounterId": 392,
    "Status1": false,
    "is_upload": false,
    "is_update": true,
    "head_order_key": null,
    "unique_key": null
  }
]
```

### dbo.Item_Less

- Row count: **480**
- Columns: **25**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | order_key | nvarchar(50) | YES |  |
| 3 | date | datetime | YES |  |
| 4 | z_num | nvarchar(50) | YES |  |
| 5 | operator | nvarchar(50) | YES |  |
| 6 | category | nvarchar(50) | YES |  |
| 7 | item | nvarchar(50) | YES |  |
| 8 | qty | float(53,0) | YES |  |
| 9 | price | float(53,0) | YES |  |
| 10 | server | nvarchar(50) | YES |  |
| 11 | order_type | nvarchar(50) | YES |  |
| 12 | status | nvarchar(50) | YES |  |
| 13 | shift | nvarchar(50) | YES |  |
| 14 | tiltId | int(10,0) | YES |  |
| 15 | CounterId | int(10,0) | YES |  |
| 16 | Reason | nvarchar | YES |  |
| 17 | Status1 | bit | NO | ((0)) |
| 18 | OrderKey_Merege | nvarchar(50) | YES |  |
| 19 | is_upload | bit | NO | ((0)) |
| 20 | is_update | bit | NO | ((0)) |
| 21 | Is_Served | bit | NO | ((0)) |
| 22 | tax | decimal(18,2) | NO | ((0)) |
| 23 | android_detail_id | int(10,0) | YES | ((0)) |
| 24 | is_print | int(10,0) | YES | ((0)) |
| 25 | unique_key | varchar(50) | YES |  |

Sample data (`TOP 3`):

```json
[
  {
    "id": 1468285,
    "order_key": "418380",
    "date": "2020-12-13T01:23:00",
    "z_num": "DAY-00001",
    "operator": "PC 6",
    "category": "ROLLS",
    "item": "CHICKEN ROLL",
    "qty": 1.0,
    "price": 130.0,
    "server": "",
    "order_type": "DELIVERY",
    "status": "PC-12",
    "shift": "01:23 AM",
    "tiltId": 59,
    "CounterId": 398,
    "Reason": "TYDU",
    "Status1": false,
    "OrderKey_Merege": null,
    "is_upload": false,
    "is_update": false,
    "Is_Served": false,
    "tax": 0.0,
    "android_detail_id": 0,
    "is_print": 0,
    "unique_key": null
  },
  {
    "id": 1472580,
    "order_key": "420257",
    "date": "2020-12-15T13:31:00",
    "z_num": "DAY-00001",
    "operator": "PC 6",
    "category": "FAST FOOD",
    "item": "SP GARLIC FRIES",
    "qty": 1.0,
    "price": 270.0,
    "server": "",
    "order_type": "DELIVERY",
    "status": "PC 6",
    "shift": "01:31 PM",
    "tiltId": 52,
    "CounterId": 392,
    "Reason": "JNGH",
    "Status1": false,
    "OrderKey_Merege": null,
    "is_upload": false,
    "is_update": false,
    "Is_Served": false,
    "tax": 0.0,
    "android_detail_id": 0,
    "is_print": 0,
    "unique_key": null
  },
  {
    "id": 1474916,
    "order_key": "421653",
    "date": "2020-12-16T14:38:00",
    "z_num": "DAY-00001",
    "operator": "PC-15",
    "category": "ROLLS",
    "item": "CHICKEN ROLL",
    "qty": 2.0,
    "price": 260.0,
    "server": "FARHAN03059372445",
    "order_type": "DELIVERY",
    "status": "PC-15",
    "shift": "02:37 PM",
    "tiltId": 46,
    "CounterId": 399,
    "Reason": ";H",
    "Status1": false,
    "OrderKey_Merege": null,
    "is_upload": false,
    "is_update": false,
    "Is_Served": false,
    "tax": 0.0,
    "android_detail_id": 0,
    "is_print": 0,
    "unique_key": null
  }
]
```

### dbo.item_stock_detail

- Row count: **0**
- Columns: **6**
- Primary key: id
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | master_id | int(10,0) | NO |  |
| 3 | item_id | int(10,0) | YES |  |
| 4 | last_rate | decimal(18,2) | YES |  |
| 5 | balance | decimal(18,2) | YES |  |
| 6 | store_id | int(10,0) | YES |  |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.item_stock_master

- Row count: **0**
- Columns: **2**
- Primary key: id
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | date | datetime | YES |  |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.Item_Transfer_Log

- Row count: **0**
- Columns: **11**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | Date | datetime | NO |  |
| 3 | Z_Number | nvarchar(50) | NO |  |
| 4 | Order_Key_To | nvarchar(50) | NO |  |
| 5 | Order_Key_From | nvarchar(50) | NO |  |
| 6 | Tiltid | int(10,0) | NO |  |
| 7 | Counter_Id | int(10,0) | NO |  |
| 8 | Loginuser | nvarchar(50) | NO |  |
| 9 | Authenticate_User | nvarchar(50) | NO |  |
| 10 | ItemId | int(10,0) | NO |  |
| 11 | Qty | decimal(18,2) | NO |  |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.Item_void

- Row count: **0**
- Columns: **25**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | order_key | nvarchar(50) | YES |  |
| 3 | date | datetime | YES |  |
| 4 | z_num | nvarchar(50) | YES |  |
| 5 | operator | nvarchar(50) | YES |  |
| 6 | category | nvarchar(50) | YES |  |
| 7 | item | nvarchar(50) | YES |  |
| 8 | qty | float(53,0) | YES |  |
| 9 | price | float(53,0) | YES |  |
| 10 | server | nvarchar(50) | YES |  |
| 11 | order_type | nvarchar(50) | YES |  |
| 12 | status | nvarchar(50) | YES |  |
| 13 | shift | nvarchar(50) | YES |  |
| 14 | tiltId | int(10,0) | YES |  |
| 15 | CounterId | int(10,0) | YES |  |
| 16 | Reason | nvarchar | YES |  |
| 17 | Status1 | bit | NO | ((0)) |
| 18 | OrderKey_Merege | nvarchar(50) | YES |  |
| 19 | is_upload | bit | NO | ((0)) |
| 20 | is_update | bit | NO | ((0)) |
| 21 | less_after_bill | bit | YES | ((0)) |
| 22 | android_detail_id | int(10,0) | YES | ((0)) |
| 23 | is_print | int(10,0) | YES | ((0)) |
| 24 | auto_id | int(10,0) | NO |  |
| 25 | od_id | int(10,0) | YES |  |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.ItemComments

- Row count: **0**
- Columns: **3**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | ItemComments | nvarchar | YES |  |
| 3 | Item | nvarchar(50) | YES |  |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.ItemConversion

- Row count: **0**
- Columns: **4**
- Primary key: None
- Outgoing foreign keys: **1**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | ItemId | int(10,0) | YES |  |
| 3 | Packing-InvUnitFactor | float(53,0) | YES |  |
| 4 | InvUnit-RecepieUnitFactor | float(53,0) | YES |  |

Foreign key links:
- `ItemId` -> `dbo.Item.ItemId` (FK_ItemConversion_Item)

Sample data (`TOP 3`):

```text
No rows
```

### dbo.ItemGroupDetail

- Row count: **0**
- Columns: **3**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | IGId | int(10,0) | YES |  |
| 2 | ItemName | varchar(50) | YES |  |
| 3 | SGId | int(10,0) | YES |  |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.ItemGroupMaster

- Row count: **0**
- Columns: **2**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | GId | int(10,0) | NO |  |
| 2 | GName | nvarchar(50) | YES |  |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.ItemOrderConversion

- Row count: **0**
- Columns: **5**
- Primary key: None
- Outgoing foreign keys: **1**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | ItemId | int(10,0) | YES |  |
| 3 | OrderQty | decimal(18,2) | YES |  |
| 4 | IssUnitId | int(10,0) | YES |  |
| 5 | Conversion | decimal(18,2) | YES |  |

Foreign key links:
- `ItemId` -> `dbo.Item.ItemId` (FK_ItemOrderConversion_Item)

Sample data (`TOP 3`):

```text
No rows
```

### dbo.ItemParLevel

- Row count: **0**
- Columns: **6**
- Primary key: None
- Outgoing foreign keys: **1**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | ItemId | int(10,0) | YES |  |
| 3 | BRId | int(10,0) | YES |  |
| 4 | ParLevel | decimal(18,2) | YES |  |
| 5 | SId | int(10,0) | YES | ((0)) |
| 6 | DId | int(10,0) | YES | ((0)) |

Foreign key links:
- `ItemId` -> `dbo.Item.ItemId` (FK_ItemParLevel_Item)

Sample data (`TOP 3`):

```text
No rows
```

### dbo.ItemPOS

- Row count: **1643**
- Columns: **39**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | category_name | nvarchar(50) | YES |  |
| 3 | item_name | nvarchar(250) | YES |  |
| 4 | cost_price | float(53,0) | YES |  |
| 5 | sale_price | float(53,0) | YES |  |
| 6 | codes | nvarchar(250) | YES |  |
| 7 | status | bit | NO | ((1)) |
| 8 | tiltId | int(10,0) | YES |  |
| 9 | IsComment | bit | YES | ((0)) |
| 10 | orderid | int(10,0) | NO | ((0)) |
| 11 | GetType | nvarchar(50) | YES |  |
| 12 | Is_Open | bit | NO | ((0)) |
| 13 | Unit | nvarchar(50) | YES |  |
| 14 | ItemParLevel | decimal(18,2) | NO | ((0)) |
| 15 | ItemBalance | decimal(18,2) | NO | ((0)) |
| 16 | item_name_arabic | nvarchar | YES |  |
| 17 | IsDate_Effective | bit | NO | ((0)) |
| 18 | FromDate | datetime | YES |  |
| 19 | ToDate | datetime | YES |  |
| 20 | ByeOneGetOneFree | bit | NO | ((0)) |
| 21 | FinalQty | decimal(18,0) | NO | ((0)) |
| 22 | Is_AutoPunchItem | bit | NO | ((0)) |
| 23 | AutoPunchItem_Id | int(10,0) | NO | ((0)) |
| 24 | Is_Upload | bit | NO | ((0)) |
| 25 | Is_Update | bit | NO | ((0)) |
| 26 | Cid | int(10,0) | NO |  |
| 27 | ExtraItem | bit | NO | ((0)) |
| 28 | Item_Commission | decimal(18,2) | NO | ((0)) |
| 29 | is_delete | bit | YES | ((0)) |
| 30 | is_feedback | bit | YES | ((0)) |
| 31 | BRid | int(10,0) | YES |  |
| 32 | is_charity | bit | YES | ((0)) |
| 33 | charity_amount | decimal(18,2) | YES | ((0)) |
| 34 | meal_type_id | int(10,0) | YES | ((0)) |
| 35 | discount_apply | bit | YES | ((0)) |
| 36 | image_url | nvarchar(50) | YES |  |
| 37 | item_name_chinese | nvarchar(50) | YES |  |
| 38 | item_name_urdu | nvarchar(50) | YES |  |
| 39 | is_kot | bit | YES | ((0)) |

Sample data (`TOP 3`):

```json
[
  {
    "id": 2472,
    "category_name": "Soups",
    "item_name": "CHICKEN CORN SOUPS",
    "cost_price": 0.0,
    "sale_price": 130.0,
    "codes": "1",
    "status": true,
    "tiltId": null,
    "IsComment": false,
    "orderid": 0,
    "GetType": null,
    "Is_Open": false,
    "Unit": "",
    "ItemParLevel": 0.0,
    "ItemBalance": 0.0,
    "item_name_arabic": null,
    "IsDate_Effective": false,
    "FromDate": "2021-03-13T00:00:00",
    "ToDate": "2021-03-13T00:00:00",
    "ByeOneGetOneFree": false,
    "FinalQty": 0.0,
    "Is_AutoPunchItem": false,
    "AutoPunchItem_Id": 0,
    "Is_Upload": true,
    "Is_Update": false,
    "Cid": 422,
    "ExtraItem": false,
    "Item_Commission": 0.0,
    "is_delete": false,
    "is_feedback": false,
    "BRid": 191,
    "is_charity": null,
    "charity_amount": null,
    "meal_type_id": null,
    "discount_apply": null,
    "image_url": null,
    "item_name_chinese": null,
    "item_name_urdu": null,
    "is_kot": null
  },
  {
    "id": 2521,
    "category_name": "Rice",
    "item_name": "CHICKEN FRIED RICE",
    "cost_price": 0.0,
    "sale_price": 320.0,
    "codes": "50",
    "status": true,
    "tiltId": null,
    "IsComment": false,
    "orderid": 0,
    "GetType": null,
    "Is_Open": false,
    "Unit": "",
    "ItemParLevel": 0.0,
    "ItemBalance": 0.0,
    "item_name_arabic": null,
    "IsDate_Effective": false,
    "FromDate": "2021-03-13T00:00:00",
    "ToDate": "2021-03-13T00:00:00",
    "ByeOneGetOneFree": false,
    "FinalQty": 0.0,
    "Is_AutoPunchItem": false,
    "AutoPunchItem_Id": 0,
    "Is_Upload": true,
    "Is_Update": false,
    "Cid": 428,
    "ExtraItem": false,
    "Item_Commission": 0.0,
    "is_delete": false,
    "is_feedback": false,
    "BRid": 191,
    "is_charity": null,
    "charity_amount": null,
    "meal_type_id": null,
    "discount_apply": null,
    "image_url": null,
    "item_name_chinese": null,
    "item_name_urdu": null,
    "is_kot": null
  },
  {
    "id": 2552,
    "category_name": "FastFood",
    "item_name": "CHICKEN SANDWICH",
    "cost_price": 0.0,
    "sale_price": 280.0,
    "codes": "81",
    "status": true,
    "tiltId": null,
    "IsComment": false,
    "orderid": 2,
    "GetType": "MODIFIED",
    "Is_Open": false,
    "Unit": "",
    "ItemParLevel": 0.0,
    "ItemBalance": 0.0,
    "item_name_arabic": null,
    "IsDate_Effective": false,
    "FromDate": "2021-03-13T00:00:00",
    "ToDate": "2021-03-13T00:00:00",
    "ByeOneGetOneFree": false,
    "FinalQty": 0.0,
    "Is_AutoPunchItem": false,
    "AutoPunchItem_Id": 0,
    "Is_Upload": true,
    "Is_Update": false,
    "Cid": 431,
    "ExtraItem": false,
    "Item_Commission": 0.0,
    "is_delete": false,
    "is_feedback": false,
    "BRid": 191,
    "is_charity": null,
    "charity_amount": null,
    "meal_type_id": null,
    "discount_apply": null,
    "image_url": null,
    "item_name_chinese": null,
    "item_name_urdu": null,
    "is_kot": null
  }
]
```

### dbo.ItemPOS_Assign

- Row count: **0**
- Columns: **3**
- Primary key: ID
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | ID | int(10,0) | NO |  |
| 2 | Item_ID | int(10,0) | YES |  |
| 3 | Item_Finish_ID | int(10,0) | YES |  |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.ItemPOS_Extra

- Row count: **0**
- Columns: **4**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | ItemId | int(10,0) | NO |  |
| 3 | Extra_Item | nvarchar(50) | NO |  |
| 4 | Price | decimal(18,2) | NO | ((0)) |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.ItemPOS_finishPro

- Row count: **0**
- Columns: **2**
- Primary key: ID
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | ID | int(10,0) | NO |  |
| 2 | Item_name | nvarchar(100) | YES |  |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.ItemSubGroupMaster

- Row count: **0**
- Columns: **3**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | SGId | int(10,0) | NO |  |
| 2 | SGName | varchar(50) | YES |  |
| 3 | GId | int(10,0) | YES |  |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.ItemUnit

- Row count: **0**
- Columns: **10**
- Primary key: None
- Outgoing foreign keys: **1**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | ItemId | int(10,0) | YES |  |
| 3 | PkUnit | int(10,0) | YES |  |
| 4 | PkFactor | decimal(18,2) | YES |  |
| 5 | PurUnit | int(10,0) | YES |  |
| 6 | PurFactor | decimal(18,2) | YES |  |
| 7 | IssUnit | int(10,0) | YES |  |
| 8 | IssFactor | decimal(18,2) | YES |  |
| 9 | RecpUnit | int(10,0) | YES |  |
| 10 | RecpFactor | decimal(18,2) | YES |  |

Foreign key links:
- `ItemId` -> `dbo.Item.ItemId` (FK_ItemUnit_Item)

Sample data (`TOP 3`):

```text
No rows
```

### dbo.JVDetail

- Row count: **0**
- Columns: **6**
- Primary key: None
- Outgoing foreign keys: **1**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | Amount | decimal(18,2) | YES |  |
| 3 | CAId | int(10,0) | YES |  |
| 4 | Type | varchar(40) | YES |  |
| 5 | Desc | nvarchar | YES |  |
| 6 | JVId | int(10,0) | YES |  |

Foreign key links:
- `JVId` -> `dbo.JVMaster.JVId` (JVMaster_JVDetail)

Sample data (`TOP 3`):

```text
No rows
```

### dbo.JVMaster

- Row count: **0**
- Columns: **4**
- Primary key: JVId
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | JVId | int(10,0) | NO |  |
| 2 | VN | nvarchar(40) | YES |  |
| 3 | Date | datetime | YES |  |
| 4 | COId | int(10,0) | YES |  |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.KDS_Department_IP_Setting

- Row count: **2**
- Columns: **4**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | Did | int(10,0) | NO |  |
| 3 | KDSIP | nvarchar(50) | NO |  |
| 4 | TiltID | int(10,0) | YES |  |

Sample data (`TOP 3`):

```json
[
  {
    "id": 12,
    "Did": 40,
    "KDSIP": "192.168.1.60",
    "TiltID": null
  },
  {
    "id": 13,
    "Did": 39,
    "KDSIP": "192.168.1.60",
    "TiltID": null
  }
]
```

### dbo.KOTPrint

- Row count: **1**
- Columns: **2**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | KotPrint | int(10,0) | YES |  |

Sample data (`TOP 3`):

```json
[
  {
    "id": 1,
    "KotPrint": 1
  }
]
```

### dbo.LoginStatus

- Row count: **4260**
- Columns: **6**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | User | nvarchar(100) | YES |  |
| 3 | Type | nvarchar(50) | YES |  |
| 4 | Description | nvarchar(50) | YES |  |
| 5 | Date | datetime | YES |  |
| 6 | Time | nvarchar(50) | YES |  |

Sample data (`TOP 3`):

```json
[
  {
    "id": 40441,
    "User": "PC 2",
    "Type": "Login",
    "Description": "Login",
    "Date": "2020-12-12T00:00:00",
    "Time": "04:44 AM"
  },
  {
    "id": 40442,
    "User": "PC-12",
    "Type": "Login",
    "Description": "Login",
    "Date": "2020-12-12T00:00:00",
    "Time": "11:12 AM"
  },
  {
    "id": 40453,
    "User": "pc 9",
    "Type": "Logout",
    "Description": "Normal",
    "Date": "2020-12-13T00:00:00",
    "Time": "03:40 AM"
  }
]
```

### dbo.meal_serving_time

- Row count: **0**
- Columns: **3**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | meal_type | varchar(50) | YES |  |
| 3 | serving_time | int(10,0) | YES |  |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.MenuCategory

- Row count: **3**
- Columns: **2**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | Category | nvarchar(50) | YES |  |

Sample data (`TOP 3`):

```json
[
  {
    "id": 1,
    "Category": "Menu "
  },
  {
    "id": 2,
    "Category": "BBQ"
  },
  {
    "id": 3,
    "Category": "Salad"
  }
]
```

### dbo.MenuDetail

- Row count: **2**
- Columns: **4**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | ItemId | int(10,0) | YES |  |
| 3 | MenuItem | nvarchar(50) | YES |  |
| 4 | Qty | float(53,0) | YES |  |

Sample data (`TOP 3`):

```json
[
  {
    "id": 1,
    "ItemId": 4,
    "MenuItem": "Malai Boti",
    "Qty": 1.0
  },
  {
    "id": 2,
    "ItemId": 4,
    "MenuItem": "Russian Salad",
    "Qty": 1.0
  }
]
```

### dbo.MenuItem

- Row count: **4**
- Columns: **6**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | CategoryId | int(10,0) | YES |  |
| 3 | Item | nvarchar(50) | YES |  |
| 4 | Cover | int(10,0) | YES |  |
| 5 | Price | float(53,0) | YES |  |
| 6 | IsOpen | bit | YES | ((0)) |

Sample data (`TOP 3`):

```json
[
  {
    "id": 1,
    "CategoryId": 2,
    "Item": "Malai Boti",
    "Cover": 1,
    "Price": 150.0,
    "IsOpen": true
  },
  {
    "id": 2,
    "CategoryId": 2,
    "Item": "Behari Boti",
    "Cover": 1,
    "Price": 150.0,
    "IsOpen": true
  },
  {
    "id": 3,
    "CategoryId": 3,
    "Item": "Russian Salad",
    "Cover": 1,
    "Price": 150.0,
    "IsOpen": true
  }
]
```

### dbo.OpenInventoryDetail

- Row count: **0**
- Columns: **7**
- Primary key: None
- Outgoing foreign keys: **2**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | OpenInvId | int(10,0) | YES |  |
| 3 | ItemId | int(10,0) | YES |  |
| 4 | Qty | decimal(18,2) | YES |  |
| 5 | Rate | decimal(18,2) | YES |  |
| 6 | Amount | decimal(18,2) | YES |  |
| 7 | Unit | int(10,0) | YES | ((0)) |

Foreign key links:
- `ItemId` -> `dbo.Item.ItemId` (FK_OpenInventoryDetail_Item)
- `OpenInvId` -> `dbo.OpenInventoryMaster.OpenInvId` (FK_OpenInventoryDetail_OpenInventoryMaster)

Sample data (`TOP 3`):

```text
No rows
```

### dbo.OpenInventoryDetail_Department

- Row count: **1632**
- Columns: **7**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | OpenInvId | int(10,0) | YES |  |
| 3 | ItemId | int(10,0) | YES |  |
| 4 | Qty | decimal(18,2) | YES |  |
| 5 | Rate | decimal(18,2) | YES |  |
| 6 | Amount | decimal(18,2) | YES |  |
| 7 | Unit | int(10,0) | YES |  |

Sample data (`TOP 3`):

```json
[
  {
    "id": 1,
    "OpenInvId": 1,
    "ItemId": 520,
    "Qty": 1.0,
    "Rate": 1.0,
    "Amount": 1.0,
    "Unit": 50
  },
  {
    "id": 2,
    "OpenInvId": 1,
    "ItemId": 147,
    "Qty": 0.0,
    "Rate": 335.96,
    "Amount": 0.0,
    "Unit": 48
  },
  {
    "id": 3,
    "OpenInvId": 1,
    "ItemId": 178,
    "Qty": 0.0,
    "Rate": 400.0,
    "Amount": 0.0,
    "Unit": 46
  }
]
```

### dbo.OpenInventoryMaster

- Row count: **0**
- Columns: **3**
- Primary key: OpenInvId
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | OpenInvId | int(10,0) | NO |  |
| 2 | Date | datetime | YES |  |
| 3 | Type | nvarchar(50) | YES |  |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.OpenInventoryMaster_Department

- Row count: **4**
- Columns: **4**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | OpenInvId | int(10,0) | NO |  |
| 2 | Date | datetime | YES |  |
| 3 | Did | int(10,0) | NO |  |
| 4 | Type | nvarchar(50) | YES |  |

Sample data (`TOP 3`):

```json
[
  {
    "OpenInvId": 1,
    "Date": "2014-07-05T00:00:00",
    "Did": 26,
    "Type": "Delete"
  },
  {
    "OpenInvId": 2,
    "Date": "2014-07-05T00:00:00",
    "Did": 26,
    "Type": "Delete"
  },
  {
    "OpenInvId": 3,
    "Date": "2014-07-05T00:00:00",
    "Did": 26,
    "Type": "Delete"
  }
]
```

### dbo.Order_Detail

- Row count: **236776**
- Columns: **37**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | order_key | nvarchar(50) | YES |  |
| 3 | date | datetime | YES |  |
| 4 | z_number | nvarchar(50) | YES |  |
| 5 | category_name | nvarchar(50) | YES |  |
| 6 | item_name | nvarchar(50) | YES |  |
| 7 | qty | float(53,0) | YES |  |
| 8 | price | float(53,0) | YES |  |
| 9 | tiltId | int(10,0) | YES |  |
| 10 | CounterId | int(10,0) | YES |  |
| 11 | Discount | decimal(18,2) | YES | ((0)) |
| 12 | PriceBeforeDiscount | decimal(18,2) | YES | ((0)) |
| 13 | Status | bit | YES | ((0)) |
| 14 | OrderKey_Merege | nvarchar(50) | YES |  |
| 15 | is_upload | bit | NO | ((0)) |
| 16 | is_update | bit | NO | ((0)) |
| 17 | ItemId | int(10,0) | NO | ((0)) |
| 18 | Is_Open | bit | NO | ((0)) |
| 19 | Unit | nvarchar(50) | YES |  |
| 20 | Is_Served | bit | NO | ((0)) |
| 21 | IsCommplimentary | bit | NO | ((0)) |
| 22 | Commplimentary_Id | nvarchar(50) | YES |  |
| 23 | Free | bit | NO | ((0)) |
| 24 | ItemComplimentry_Amount | decimal(18,2) | NO | ((0)) |
| 25 | Comments | nvarchar | YES |  |
| 26 | Is_IsComments | bit | YES | ((0)) |
| 27 | Is_AutoPunchItem | bit | NO | ((0)) |
| 28 | Parent_Id | int(10,0) | NO | ((0)) |
| 29 | is_transferBranch | int(10,0) | YES | ((0)) |
| 30 | tax | decimal(18,2) | NO | ((0)) |
| 31 | android_detail_id | int(10,0) | YES | ((0)) |
| 32 | unique_key | varchar(50) | YES |  |
| 33 | is_additional | bit | YES | ((0)) |
| 34 | is_paid | bit | YES | ((0)) |
| 35 | start_time | datetime | YES |  |
| 36 | end_time | datetime | YES |  |
| 37 | duration | varchar(50) | YES |  |

Sample data (`TOP 3`):

```json
[
  {
    "id": 1461026,
    "order_key": "415719",
    "date": "2020-12-09T12:15:00",
    "z_number": "DAY-00001",
    "category_name": "BAR B Q",
    "item_name": "CHICKEN TIKKA (CHEST)",
    "qty": 1.0,
    "price": 250.0,
    "tiltId": 46,
    "CounterId": 376,
    "Discount": 0.0,
    "PriceBeforeDiscount": 250.0,
    "Status": false,
    "OrderKey_Merege": null,
    "is_upload": false,
    "is_update": false,
    "ItemId": 3680,
    "Is_Open": false,
    "Unit": null,
    "Is_Served": false,
    "IsCommplimentary": false,
    "Commplimentary_Id": null,
    "Free": false,
    "ItemComplimentry_Amount": 0.0,
    "Comments": "* WASH",
    "Is_IsComments": true,
    "Is_AutoPunchItem": false,
    "Parent_Id": 1461026,
    "is_transferBranch": 0,
    "tax": 0.0,
    "android_detail_id": 0,
    "unique_key": null,
    "is_additional": false,
    "is_paid": false,
    "start_time": null,
    "end_time": null,
    "duration": null
  },
  {
    "id": 1461379,
    "order_key": "415830",
    "date": "2020-12-09T19:29:00",
    "z_number": "DAY-00001",
    "category_name": "Fruity Beverages",
    "item_name": "OREO SHAKE",
    "qty": 1.0,
    "price": 290.0,
    "tiltId": 59,
    "CounterId": 385,
    "Discount": 0.0,
    "PriceBeforeDiscount": 290.0,
    "Status": false,
    "OrderKey_Merege": null,
    "is_upload": false,
    "is_update": false,
    "ItemId": 2588,
    "Is_Open": false,
    "Unit": null,
    "Is_Served": false,
    "IsCommplimentary": false,
    "Commplimentary_Id": null,
    "Free": false,
    "ItemComplimentry_Amount": 0.0,
    "Comments": "",
    "Is_IsComments": false,
    "Is_AutoPunchItem": false,
    "Parent_Id": 1461379,
    "is_transferBranch": 0,
    "tax": 0.0,
    "android_detail_id": 0,
    "unique_key": null,
    "is_additional": false,
    "is_paid": false,
    "start_time": null,
    "end_time": null,
    "duration": null
  },
  {
    "id": 1462712,
    "order_key": "416200",
    "date": "2020-12-10T18:53:00",
    "z_number": "DAY-00001",
    "category_name": "BAR B Q",
    "item_name": "CHICKEN MASALA BOTI",
    "qty": 2.0,
    "price": 900.0,
    "tiltId": 59,
    "CounterId": 398,
    "Discount": 0.0,
    "PriceBeforeDiscount": 900.0,
    "Status": false,
    "OrderKey_Merege": null,
    "is_upload": false,
    "is_update": false,
    "ItemId": 2650,
    "Is_Open": false,
    "Unit": null,
    "Is_Served": false,
    "IsCommplimentary": false,
    "Commplimentary_Id": null,
    "Free": false,
    "ItemComplimentry_Amount": 0.0,
    "Comments": "",
    "Is_IsComments": false,
    "Is_AutoPunchItem": false,
    "Parent_Id": 1462712,
    "is_transferBranch": 0,
    "tax": 0.0,
    "android_detail_id": 0,
    "unique_key": null,
    "is_additional": false,
    "is_paid": false,
    "start_time": null,
    "end_time": null,
    "duration": null
  }
]
```

### dbo.Order_Detail_ExtraItem

- Row count: **0**
- Columns: **5**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | Order_Detail_Id | int(10,0) | NO |  |
| 3 | Extra_ItemId | int(10,0) | NO |  |
| 4 | Extra_Item | nvarchar(50) | NO |  |
| 5 | Price | decimal(18,2) | NO | ((0)) |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.Order_Detail_ExtraItem_Temp

- Row count: **0**
- Columns: **5**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | Order_Detail_Id | int(10,0) | NO |  |
| 3 | Extra_ItemId | int(10,0) | NO |  |
| 4 | Extra_Item | nvarchar(50) | NO |  |
| 5 | Price | decimal(18,2) | NO | ((0)) |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.Order_Payment

- Row count: **0**
- Columns: **33**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | order_key | nvarchar(50) | NO |  |
| 3 | date | datetime | YES |  |
| 4 | z_number | nvarchar(50) | YES |  |
| 5 | order_type | nvarchar(50) | YES |  |
| 6 | cash_sale | float(53,0) | YES |  |
| 7 | credit_sale | float(53,0) | YES |  |
| 8 | sub_total | float(53,0) | YES |  |
| 9 | discount | float(53,0) | YES |  |
| 10 | tax | float(53,0) | YES |  |
| 11 | net_sale | float(53,0) | YES |  |
| 12 | net_bill | float(53,0) | YES |  |
| 13 | is_delete | bit | YES | ((0)) |
| 14 | ent | float(53,0) | YES |  |
| 15 | Tiltid | int(10,0) | YES |  |
| 16 | CounterId | int(10,0) | YES |  |
| 17 | ServiceCharges | decimal(18,2) | YES | ((0)) |
| 18 | Tip | decimal(18,2) | YES | ((0)) |
| 19 | ExtraCharges | decimal(18,2) | YES | ((0)) |
| 20 | CreditCardNo | nvarchar(50) | YES |  |
| 21 | Status | bit | NO | ((0)) |
| 22 | AdvanceBookingCode | nvarchar(50) | YES |  |
| 23 | Description | nvarchar(50) | YES |  |
| 24 | Advance | decimal(18,2) | NO | ((0)) |
| 25 | VoucherAmount | decimal(18,2) | YES | ((0)) |
| 26 | VoucherQty | float(53,0) | YES | ((0)) |
| 27 | is_upload | bit | NO | ((0)) |
| 28 | is_update | bit | NO | ((0)) |
| 29 | bank | nvarchar(50) | YES |  |
| 30 | time | nvarchar(50) | YES |  |
| 31 | Date_time | datetime | YES |  |
| 32 | ItemComplimentry_Amount | decimal(18,2) | NO | ((0)) |
| 33 | unique_key | varchar(50) | YES |  |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.OrderKot

- Row count: **252422**
- Columns: **18**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | OrderKey | nvarchar(50) | YES |  |
| 3 | ItemId | int(10,0) | YES |  |
| 4 | Qty | float(53,0) | YES |  |
| 5 | KotStatus | bit | YES | ((0)) |
| 6 | Comments | nvarchar(50) | YES |  |
| 7 | Tiltid | int(10,0) | YES |  |
| 8 | ItemComment | nvarchar | NO |  |
| 9 | LessReason | nvarchar | YES |  |
| 10 | OrderDetailId | int(10,0) | NO | ((0)) |
| 11 | OrderKey_Merege | nvarchar(50) | YES |  |
| 12 | kotFromtablet | bit | NO | ((0)) |
| 13 | tabkot | bit | NO | ((0)) |
| 14 | IsKDS | bit | NO | ((0)) |
| 15 | IsDispathed | bit | NO | ((0)) |
| 16 | Order_type | nvarchar(50) | YES |  |
| 17 | is_print | bit | YES | ((0)) |
| 18 | Is_KDS | bit | YES | ((0)) |

Sample data (`TOP 3`):

```json
[
  {
    "id": 1464402,
    "OrderKey": "415850",
    "ItemId": 2492,
    "Qty": 1.0,
    "KotStatus": true,
    "Comments": "",
    "Tiltid": 60,
    "ItemComment": "",
    "LessReason": "",
    "OrderDetailId": 1461454,
    "OrderKey_Merege": null,
    "kotFromtablet": false,
    "tabkot": false,
    "IsKDS": false,
    "IsDispathed": false,
    "Order_type": null,
    "is_print": false,
    "Is_KDS": false
  },
  {
    "id": 1465655,
    "OrderKey": "416198",
    "ItemId": 2880,
    "Qty": 1.0,
    "KotStatus": true,
    "Comments": "",
    "Tiltid": 59,
    "ItemComment": "",
    "LessReason": "",
    "OrderDetailId": 1462702,
    "OrderKey_Merege": null,
    "kotFromtablet": false,
    "tabkot": false,
    "IsKDS": true,
    "IsDispathed": false,
    "Order_type": null,
    "is_print": false,
    "Is_KDS": false
  },
  {
    "id": 1465896,
    "OrderKey": "416266",
    "ItemId": 3935,
    "Qty": 1.0,
    "KotStatus": true,
    "Comments": "",
    "Tiltid": 46,
    "ItemComment": "",
    "LessReason": "",
    "OrderDetailId": 1462943,
    "OrderKey_Merege": null,
    "kotFromtablet": false,
    "tabkot": false,
    "IsKDS": false,
    "IsDispathed": false,
    "Order_type": null,
    "is_print": false,
    "Is_KDS": false
  }
]
```

### dbo.OrderMaster

- Row count: **0**
- Columns: **13**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | Id | int(10,0) | NO |  |
| 2 | OrderDate | datetime | YES |  |
| 3 | Time | nvarchar(50) | YES |  |
| 4 | CustomerId | int(10,0) | YES |  |
| 5 | OrderNo | nvarchar(50) | YES |  |
| 6 | isDelete | bit | YES | ((0)) |
| 7 | TotalAmount | float(53,0) | YES |  |
| 8 | Discount | float(53,0) | YES |  |
| 9 | AmountBeforeDiscount | float(53,0) | YES |  |
| 10 | Status | nvarchar(50) | YES |  |
| 11 | VAT | float(53,0) | YES |  |
| 12 | CLevy | float(53,0) | YES |  |
| 13 | TaxType | nvarchar(50) | YES |  |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.OrderOccassionDetail

- Row count: **3**
- Columns: **11**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | OccassionId | int(10,0) | NO |  |
| 2 | OrderNo | nvarchar(50) | YES |  |
| 3 | OccasionDate | datetime | YES |  |
| 4 | OccasionTime | nvarchar(50) | YES |  |
| 5 | Destination | nvarchar(50) | YES |  |
| 6 | NoOfPersons | nvarchar(50) | YES |  |
| 7 | ItemId | int(10,0) | YES |  |
| 8 | TotalAmount | float(53,0) | YES |  |
| 9 | OccassionOfPerson | float(53,0) | YES |  |
| 10 | MenuDetail | nvarchar | YES |  |
| 11 | Occassion | nvarchar(50) | YES |  |

Sample data (`TOP 3`):

```json
[
  {
    "OccassionId": 8,
    "OrderNo": "ORD-1401-0001",
    "OccasionDate": "2014-01-03T00:00:00",
    "OccasionTime": "9:00 PM",
    "Destination": "Beach View Club",
    "NoOfPersons": "6",
    "ItemId": 4,
    "TotalAmount": 1200.0,
    "OccassionOfPerson": 10.0,
    "MenuDetail": "1 - Malai Boti , 1 - Russian Salad",
    "Occassion": "Dance Party"
  },
  {
    "OccassionId": 9,
    "OrderNo": "ORD-1401-0002",
    "OccasionDate": "2014-01-18T00:00:00",
    "OccasionTime": "10 PM",
    "Destination": "Khi",
    "NoOfPersons": "25",
    "ItemId": 4,
    "TotalAmount": 5000.0,
    "OccassionOfPerson": 50.0,
    "MenuDetail": "1 - Malai Boti , 1 - Russian Salad",
    "Occassion": "Mehndi"
  },
  {
    "OccassionId": 10,
    "OrderNo": "ORD-1401-0002",
    "OccasionDate": "2014-01-18T00:00:00",
    "OccasionTime": "10 PM",
    "Destination": "Khi",
    "NoOfPersons": "50",
    "ItemId": 3,
    "TotalAmount": 7500.0,
    "OccassionOfPerson": 50.0,
    "MenuDetail": "",
    "Occassion": "Mehndi"
  }
]
```

### dbo.OrderServedTime

- Row count: **3**
- Columns: **4**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | OrderType | nvarchar(50) | YES |  |
| 3 | ServedTime | int(10,0) | YES |  |
| 4 | DeliveredTime | int(10,0) | YES | ((0)) |

Sample data (`TOP 3`):

```json
[
  {
    "id": 8,
    "OrderType": "DINE IN",
    "ServedTime": 5,
    "DeliveredTime": null
  },
  {
    "id": 9,
    "OrderType": "TAKE AWAY",
    "ServedTime": 1,
    "DeliveredTime": null
  },
  {
    "id": 10,
    "OrderType": "DELIVERY",
    "ServedTime": 10,
    "DeliveredTime": null
  }
]
```

### dbo.OrderStatusTime

- Row count: **81978**
- Columns: **8**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | Order_Key | int(10,0) | YES |  |
| 3 | BookTime | nvarchar(50) | YES |  |
| 4 | AssignTime | nvarchar(50) | YES |  |
| 5 | AssambleTime | nvarchar(50) | YES |  |
| 6 | DispatchTime | nvarchar(50) | YES |  |
| 7 | CompleteTime | nvarchar(50) | YES |  |
| 8 | DeliveredTime | nvarchar(50) | YES | ((0)) |

Sample data (`TOP 3`):

```json
[
  {
    "id": 415390,
    "Order_Key": 416013,
    "BookTime": "10:33 PM",
    "AssignTime": null,
    "AssambleTime": null,
    "DispatchTime": null,
    "CompleteTime": null,
    "DeliveredTime": "0"
  },
  {
    "id": 417328,
    "Order_Key": 417950,
    "BookTime": "12:18 PM",
    "AssignTime": null,
    "AssambleTime": null,
    "DispatchTime": null,
    "CompleteTime": null,
    "DeliveredTime": "0"
  },
  {
    "id": 419630,
    "Order_Key": 420251,
    "BookTime": "01:12 PM",
    "AssignTime": "01:12 PM",
    "AssambleTime": null,
    "DispatchTime": null,
    "CompleteTime": null,
    "DeliveredTime": "0"
  }
]
```

### dbo.PaymentVoucher

- Row count: **0**
- Columns: **7**
- Primary key: PVId
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | PVId | int(10,0) | NO |  |
| 2 | Date | datetime | YES |  |
| 3 | SPId | int(10,0) | YES | ((0)) |
| 4 | Amount | decimal(18,2) | YES |  |
| 5 | PaymentMode | varchar(40) | YES |  |
| 6 | COId | int(10,0) | YES |  |
| 7 | Type | nvarchar(50) | YES |  |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.PhysicalStockDetail_Branch

- Row count: **0**
- Columns: **6**
- Primary key: None
- Outgoing foreign keys: **2**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | PSBRId | int(10,0) | YES |  |
| 3 | ItemId | int(10,0) | YES |  |
| 4 | UnitId | int(10,0) | YES |  |
| 5 | Qty | decimal(18,2) | YES |  |
| 6 | Amount | decimal(18,2) | YES |  |

Foreign key links:
- `ItemId` -> `dbo.Item.ItemId` (FK_PhysicalStockDetail_Branch_Item)
- `PSBRId` -> `dbo.PhysicalStockMaster_Branch.PSBRId` (FK_PhysicalStockDetail_Branch_PhysicalStockMaster_Branch)

Sample data (`TOP 3`):

```text
No rows
```

### dbo.PhysicalStockDetail_Store

- Row count: **0**
- Columns: **6**
- Primary key: None
- Outgoing foreign keys: **2**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | PSId | int(10,0) | YES |  |
| 3 | ItemId | int(10,0) | YES |  |
| 4 | UId | int(10,0) | YES |  |
| 5 | Qty | decimal(18,2) | YES |  |
| 6 | Amount | decimal(18,2) | YES |  |

Foreign key links:
- `ItemId` -> `dbo.Item.ItemId` (FK_PhysicalStockDetail_Store_Item)
- `PSId` -> `dbo.PhysicalStockMaster_Store.PSId` (FK_PhysicalStockDetail_Store_PhysicalStockMaster_Store)

Sample data (`TOP 3`):

```text
No rows
```

### dbo.PhysicalStockMaster_Branch

- Row count: **0**
- Columns: **6**
- Primary key: PSBRId
- Outgoing foreign keys: **1**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | PSBRId | int(10,0) | NO |  |
| 2 | Date | datetime | YES |  |
| 3 | PSNO | nvarchar(50) | YES |  |
| 4 | BRId | int(10,0) | YES |  |
| 5 | DId | int(10,0) | YES | ((0)) |
| 6 | Desc | nvarchar | YES |  |

Foreign key links:
- `BRId` -> `dbo.Branch.BRId` (FK_PhysicalStockMaster_Branch_Branch)

Sample data (`TOP 3`):

```text
No rows
```

### dbo.PhysicalStockMaster_Store

- Row count: **0**
- Columns: **5**
- Primary key: PSId
- Outgoing foreign keys: **1**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | PSId | int(10,0) | NO |  |
| 2 | Date | datetime | YES |  |
| 3 | PSNO | nvarchar(50) | YES |  |
| 4 | SId | int(10,0) | YES |  |
| 5 | Desc | nvarchar | YES |  |

Foreign key links:
- `SId` -> `dbo.Store.SId` (FK_PhysicalStockMaster_Store_Store)

Sample data (`TOP 3`):

```text
No rows
```

### dbo.POS_Default_Settings

- Row count: **0**
- Columns: **8**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | shift_operation | bit | NO |  |
| 2 | company_name | nvarchar(50) | YES |  |
| 3 | franchise_name | nvarchar(50) | YES |  |
| 4 | opening_report | bit | YES |  |
| 5 | closing_report | bit | YES |  |
| 6 | no_of_z_report | int(10,0) | YES |  |
| 7 | phone_no | nvarchar(50) | YES |  |
| 8 | branch_id | nvarchar(50) | YES |  |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.POS_Expense

- Row count: **0**
- Columns: **9**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | Type | nchar(10) | NO |  |
| 3 | Vn | nvarchar(50) | NO |  |
| 4 | VoucherId | int(10,0) | YES | ((0)) |
| 5 | date | datetime | NO |  |
| 6 | Amount | decimal(18,2) | NO |  |
| 7 | CAId | int(10,0) | NO |  |
| 8 | Vouchertype | nvarchar(50) | NO |  |
| 9 | Desc | nvarchar | YES |  |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.POS_Expense_Account

- Row count: **0**
- Columns: **3**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | Account | nvarchar(50) | NO |  |
| 3 | CAId | int(10,0) | NO |  |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.POsExpenseSetting

- Row count: **0**
- Columns: **2**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | Amount | decimal(18,2) | NO |  |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.PosSale

- Row count: **0**
- Columns: **8**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | z_num | nvarchar(50) | YES |  |
| 3 | Date | datetime | YES |  |
| 4 | Amount | float(53,0) | YES |  |
| 5 | Type | nvarchar(50) | YES |  |
| 6 | VN | nvarchar(50) | YES |  |
| 7 | Desc | text(2147483647) | YES |  |
| 8 | Account | nvarchar(50) | YES |  |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.POSSaleAccount

- Row count: **0**
- Columns: **4**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | AccountNo | nvarchar(50) | YES |  |
| 3 | SaleType | nvarchar(50) | YES |  |
| 4 | Type | nvarchar(50) | YES |  |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.POSSaleReturnDetail

- Row count: **0**
- Columns: **10**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | Sid | int(10,0) | YES |  |
| 3 | item_name | nvarchar(50) | YES |  |
| 4 | qty | float(53,0) | YES |  |
| 5 | price | float(53,0) | YES |  |
| 6 | Category | nvarchar(50) | YES |  |
| 7 | DealDescription | nvarchar | YES |  |
| 8 | is_upload | bit | NO | ((0)) |
| 9 | is_update | bit | NO | ((0)) |
| 10 | unique_key | varchar(50) | YES |  |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.POSSaleReturnMaster

- Row count: **0**
- Columns: **22**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | Sid | int(10,0) | NO |  |
| 2 | Date | datetime | YES |  |
| 3 | SRNo | nvarchar(50) | YES |  |
| 4 | OrderKey | nvarchar(50) | YES |  |
| 5 | OrderType | nvarchar(50) | YES |  |
| 6 | Amount | float(53,0) | YES |  |
| 7 | User | nvarchar(50) | YES |  |
| 8 | Tiltid | int(10,0) | YES |  |
| 9 | ShiftNo | nvarchar(50) | YES |  |
| 10 | CounterId | int(10,0) | YES |  |
| 11 | IsComplete | bit | YES | ((0)) |
| 12 | Tax | float(53,0) | YES | ((0)) |
| 13 | Discount | float(53,0) | YES | ((0)) |
| 14 | SCharges | float(53,0) | YES | ((0)) |
| 15 | ECharges | float(53,0) | YES | ((0)) |
| 16 | Reason | nvarchar | YES |  |
| 17 | Status | bit | NO | ((0)) |
| 18 | SaleReturnTime | nvarchar(50) | YES |  |
| 19 | is_upload | bit | NO | ((0)) |
| 20 | is_update | bit | NO | ((0)) |
| 21 | Date_time | datetime | YES |  |
| 22 | unique_key | varchar(50) | YES |  |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.POSTransectionSetting

- Row count: **96**
- Columns: **3**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | type | nvarchar(50) | YES |  |
| 3 | status | bit | YES | ((0)) |

Sample data (`TOP 3`):

```json
[
  {
    "id": 16,
    "type": "TaxBeforeDiscount",
    "status": true
  },
  {
    "id": 17,
    "type": "ServiceChargesOnGross",
    "status": false
  },
  {
    "id": 18,
    "type": "DineInCustomerInfo",
    "status": false
  }
]
```

### dbo.Printer_Setup

- Row count: **0**
- Columns: **5**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | printer | nvarchar(50) | YES |  |
| 3 | department | nvarchar(50) | YES |  |
| 4 | document | nvarchar(50) | YES |  |
| 5 | TiltId | int(10,0) | YES |  |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.ProductionDetail

- Row count: **0**
- Columns: **6**
- Primary key: None
- Outgoing foreign keys: **1**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | PRId | int(10,0) | YES |  |
| 3 | ItemId | int(10,0) | YES |  |
| 4 | UnitId | int(10,0) | YES |  |
| 5 | Qty | decimal(18,2) | YES |  |
| 6 | RatePerPcs | decimal(18,2) | YES |  |

Foreign key links:
- `PRId` -> `dbo.ProductionMaster.PRId` (FK_ProductionDetail_ProductionMaster)

Sample data (`TOP 3`):

```text
No rows
```

### dbo.ProductionDetailDepartment

- Row count: **18**
- Columns: **6**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | PRId | int(10,0) | YES |  |
| 3 | ItemId | int(10,0) | YES |  |
| 4 | UnitId | int(10,0) | YES |  |
| 5 | Qty | decimal(18,2) | YES |  |
| 6 | RatePerPcs | decimal(18,2) | YES |  |

Sample data (`TOP 3`):

```json
[
  {
    "id": 26,
    "PRId": 11,
    "ItemId": 776,
    "UnitId": 65,
    "Qty": 1.0,
    "RatePerPcs": 15.57
  },
  {
    "id": 62,
    "PRId": 20,
    "ItemId": 776,
    "UnitId": 65,
    "Qty": 20.0,
    "RatePerPcs": 15.57
  },
  {
    "id": 63,
    "PRId": 21,
    "ItemId": 728,
    "UnitId": 65,
    "Qty": 20.0,
    "RatePerPcs": 85.24
  }
]
```

### dbo.ProductionMaster

- Row count: **0**
- Columns: **5**
- Primary key: PRId
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | PRId | int(10,0) | NO |  |
| 2 | Date | datetime | YES |  |
| 3 | PRNo | nvarchar(50) | YES |  |
| 4 | Sid | int(10,0) | YES |  |
| 5 | Amount | int(10,0) | YES |  |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.ProductionMasterDepartment

- Row count: **14**
- Columns: **7**
- Primary key: PRId
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | PRId | int(10,0) | NO |  |
| 2 | Date | datetime | YES |  |
| 3 | PRNo | nvarchar(50) | YES |  |
| 4 | Sid | int(10,0) | YES |  |
| 5 | Amount | int(10,0) | YES |  |
| 6 | BRId | int(10,0) | YES |  |
| 7 | Did | int(10,0) | YES |  |

Sample data (`TOP 3`):

```json
[
  {
    "PRId": 11,
    "Date": "2015-02-14T00:00:00",
    "PRNo": "PD-0001",
    "Sid": 146,
    "Amount": 16,
    "BRId": 51,
    "Did": 26
  },
  {
    "PRId": 19,
    "Date": "2015-02-14T00:00:00",
    "PRNo": "PD-0002",
    "Sid": 146,
    "Amount": 16,
    "BRId": 51,
    "Did": 26
  },
  {
    "PRId": 20,
    "Date": "2015-02-14T00:00:00",
    "PRNo": "PD-0003",
    "Sid": 146,
    "Amount": 311,
    "BRId": 51,
    "Did": 26
  }
]
```

### dbo.ProductSaleDetail

- Row count: **0**
- Columns: **8**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | PMID | int(10,0) | YES |  |
| 3 | IngredientId | int(10,0) | YES |  |
| 4 | PackingRatePerPcs | decimal(18,2) | YES |  |
| 5 | InventoryRatePerPcs | decimal(18,2) | YES |  |
| 6 | RecipeRatePerPcs | decimal(18,2) | YES |  |
| 7 | IngredientQty | decimal(18,4) | NO |  |
| 8 | IngredientAmount | decimal(18,2) | YES |  |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.ProductSaleMaster

- Row count: **0**
- Columns: **4**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | PMID | int(10,0) | NO |  |
| 2 | ProductId | int(10,0) | YES |  |
| 3 | ZNumber | nvarchar(50) | YES |  |
| 4 | Date | datetime | YES |  |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.ProfitLossSettings

- Row count: **3**
- Columns: **5**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | Section | nvarchar(50) | YES |  |
| 3 | AccNoFrom | int(10,0) | YES |  |
| 4 | AccNoTo | int(10,0) | YES |  |
| 5 | Title | nvarchar(50) | YES |  |

Sample data (`TOP 3`):

```json
[
  {
    "id": 31,
    "Section": "Section 1",
    "AccNoFrom": 5101001,
    "AccNoTo": 5102001,
    "Title": "SALE"
  },
  {
    "id": 32,
    "Section": "Section 2",
    "AccNoFrom": 1103002,
    "AccNoTo": 1103002,
    "Title": "COST OF PRODUCTION"
  },
  {
    "id": 33,
    "Section": "Section 3",
    "AccNoFrom": 4101001,
    "AccNoTo": 4104005,
    "Title": "EXPENSES"
  }
]
```

### dbo.PurchaseOrderDetail_Store

- Row count: **0**
- Columns: **10**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | POId | int(10,0) | YES |  |
| 3 | ItemId | int(10,0) | YES |  |
| 4 | UId | int(10,0) | YES |  |
| 5 | Rate | decimal(18,2) | YES |  |
| 6 | Amount | decimal(18,2) | YES |  |
| 7 | Qty | decimal(18,2) | YES |  |
| 8 | DSCOId | int(10,0) | YES |  |
| 9 | Status | bit | YES | ((0)) |
| 10 | RecQty | decimal(18,2) | YES | ((0)) |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.PurchaseOrderMaster_Store

- Row count: **0**
- Columns: **9**
- Primary key: POId
- Outgoing foreign keys: **3**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | POId | int(10,0) | NO |  |
| 2 | Date | datetime | YES |  |
| 3 | COId | int(10,0) | YES |  |
| 4 | PONo | varchar(50) | YES |  |
| 5 | VId | int(10,0) | YES |  |
| 6 | Status | bit | YES | ((0)) |
| 7 | UserId | int(10,0) | YES |  |
| 8 | SId | int(10,0) | YES |  |
| 9 | Desc | nvarchar | YES |  |

Foreign key links:
- `COId` -> `dbo.Company.COId` (FK_PurchaseOrderMaster_Store_Company)
- `SId` -> `dbo.Store.SId` (FK_PurchaseOrderMaster_Store_Store)
- `VId` -> `dbo.Vendor.VId` (FK_PurchaseOrderMaster_Store_Vendor)

Sample data (`TOP 3`):

```text
No rows
```

### dbo.PurchaseReturnDetail

- Row count: **0**
- Columns: **19**
- Primary key: None
- Outgoing foreign keys: **1**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | Id | int(10,0) | NO |  |
| 2 | PRId | int(10,0) | YES |  |
| 3 | ItemId | int(10,0) | YES |  |
| 4 | Unit | int(10,0) | YES |  |
| 5 | Rate | decimal(18,2) | YES |  |
| 6 | Qty | decimal(18,2) | YES |  |
| 7 | POId | int(10,0) | YES |  |
| 8 | TotalPackage | decimal(18,2) | YES |  |
| 9 | PcsPerPackage | decimal(18,2) | YES |  |
| 10 | RatePerPackage | decimal(18,2) | YES |  |
| 11 | PackageId | int(10,0) | YES |  |
| 12 | GRNId | int(10,0) | YES |  |
| 13 | DSCOId | int(10,0) | YES |  |
| 14 | DiscountPerPcs | decimal(18,2) | YES |  |
| 15 | TaxPerPcs | decimal(18,2) | YES |  |
| 16 | TaxType | nvarchar(50) | YES |  |
| 17 | NetAmount | decimal(18,2) | YES |  |
| 18 | Amount | decimal(18,2) | YES |  |
| 19 | TaxMode | int(10,0) | YES | ((0)) |

Foreign key links:
- `PRId` -> `dbo.PurchaseReturnMaster.PRId` (FK_PurchaseReturnDetail_PurchaseReturnMaster)

Sample data (`TOP 3`):

```text
No rows
```

### dbo.PurchaseReturnDetailNew

- Row count: **0**
- Columns: **16**
- Primary key: None
- Outgoing foreign keys: **2**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | PRId | int(10,0) | YES |  |
| 3 | ItemId | int(10,0) | YES |  |
| 4 | Unit | int(10,0) | YES |  |
| 5 | Qty | decimal(18,2) | YES |  |
| 6 | POId | int(10,0) | YES |  |
| 7 | Rate | decimal(18,2) | YES |  |
| 8 | TotalPackage | decimal(18,2) | YES |  |
| 9 | PcsPerPackage | decimal(18,2) | YES |  |
| 10 | RatePerPackage | decimal(18,2) | YES |  |
| 11 | PackageId | int(10,0) | YES |  |
| 12 | Tax | decimal(18,2) | YES | ((0)) |
| 13 | Discount | decimal(18,2) | YES | ((0)) |
| 14 | Amount | decimal(18,2) | YES | ((0)) |
| 15 | ActualRate | decimal(18,2) | YES | ((0)) |
| 16 | TaxType | nvarchar(50) | YES |  |

Foreign key links:
- `ItemId` -> `dbo.Item.ItemId` (FK_PurchaseReturnDetailNew_Item)
- `PRId` -> `dbo.PurchaseReturnMasterNew.PRId` (FK_PurchaseReturnDetailNew_Store_PurchaseReturnMasterNew_Store)

Sample data (`TOP 3`):

```text
No rows
```

### dbo.PurchaseReturnMaster

- Row count: **0**
- Columns: **14**
- Primary key: PRId
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | PRId | int(10,0) | NO |  |
| 2 | Date | datetime | YES |  |
| 3 | UserId | int(10,0) | YES |  |
| 4 | VId | int(10,0) | YES |  |
| 5 | PRNo | nvarchar(50) | YES |  |
| 6 | SId | int(10,0) | YES |  |
| 7 | BRId | int(10,0) | YES |  |
| 8 | Amount | decimal(18,2) | YES |  |
| 9 | Discount | decimal(18,2) | YES |  |
| 10 | TotalAmount | decimal(18,2) | YES |  |
| 11 | InvoiceId | int(10,0) | YES |  |
| 12 | RefNo | nvarchar(50) | YES |  |
| 13 | TotalTax | decimal(18,2) | YES |  |
| 14 | COId | int(10,0) | YES | ((0)) |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.PurchaseReturnMasterNew

- Row count: **0**
- Columns: **12**
- Primary key: PRId
- Outgoing foreign keys: **2**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | PRId | int(10,0) | NO |  |
| 2 | Date | datetime | YES |  |
| 3 | VId | int(10,0) | YES |  |
| 4 | GRNId | int(10,0) | YES |  |
| 5 | PRNo | varchar(50) | YES |  |
| 6 | SId | int(10,0) | YES | ((0)) |
| 7 | BRId | int(10,0) | YES | ((0)) |
| 8 | Amount | decimal(18,2) | YES |  |
| 9 | Discount | decimal(18,2) | YES |  |
| 10 | TotalAmount | decimal(18,2) | YES |  |
| 11 | RefrenceNo | nvarchar(50) | YES |  |
| 12 | TotalTax | decimal(18,2) | YES |  |

Foreign key links:
- `GRNId` -> `dbo.GRNMaster.GRNId` (FK_PurchaseReturnMasterNew_GRNMaster)
- `VId` -> `dbo.Vendor.VId` (FK_PurchaseReturnMasterNew_Vendor1)

Sample data (`TOP 3`):

```text
No rows
```

### dbo.Reasons

- Row count: **0**
- Columns: **2**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | Reason | nvarchar | NO |  |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.ReceiptVoucher

- Row count: **0**
- Columns: **7**
- Primary key: RVId
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | RVId | int(10,0) | NO |  |
| 2 | Date | datetime | YES |  |
| 3 | CustId | int(10,0) | YES |  |
| 4 | Amount | decimal(18,2) | YES |  |
| 5 | ReceiptMode | nvarchar(50) | YES |  |
| 6 | COId | int(10,0) | YES |  |
| 7 | Type | nvarchar(50) | YES |  |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.RecipeDetail

- Row count: **0**
- Columns: **8**
- Primary key: None
- Outgoing foreign keys: **2**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | RecipeId | int(10,0) | YES |  |
| 3 | IngredientId | int(10,0) | YES |  |
| 4 | Qty | float(53,0) | YES |  |
| 5 | IsSubRecipe | bit | YES | ((0)) |
| 6 | is_DineIn | bit | YES | ((0)) |
| 7 | Is_TakeAway | bit | YES | ((0)) |
| 8 | Is_Delivery | bit | YES | ((0)) |

Foreign key links:
- `IngredientId` -> `dbo.Item.ItemId` (FK_RecipeDetail_Item)
- `RecipeId` -> `dbo.RecipeMaster.RecipeId` (FK_RecipeDetail_RecipeMaster)

Sample data (`TOP 3`):

```text
No rows
```

### dbo.RecipeMaster

- Row count: **0**
- Columns: **6**
- Primary key: RecipeId
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | RecipeId | int(10,0) | NO |  |
| 2 | ProductId | int(10,0) | YES |  |
| 3 | max_FP_Cost | decimal(18,2) | NO | ((0)) |
| 4 | min_SP_Price | decimal(18,2) | NO | ((0)) |
| 5 | Current_FP_Cost | decimal(18,2) | NO | ((0)) |
| 6 | Comments | nvarchar | YES |  |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.Reports_Settings

- Row count: **1**
- Columns: **4**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | reports_footer | nvarchar(500) | YES |  |
| 2 | reports_footer2 | nvarchar(500) | YES |  |
| 3 | bill1_header | varchar(50) | YES |  |
| 4 | bill2_header | varchar(50) | YES |  |

Sample data (`TOP 3`):

```json
[
  {
    "reports_footer": "Thank You!!!!!\r\nPlease Join Us Again.dfiljghrjkgkljgdlskgfladkgjd\r\nahsd;fj\r\n[asdhfkljasdgfkjasdgfsdjkgfsdjklfgkjfgkjgtkljasdbfjk\r\nasdhfjsdhfkjhl;khasdfj\r\njkasdhfkl;jhapsdofhjk\r\nadfhjsdfjkasdgfasdjkgfsdkljfghfjgasdlfjkgasdfjk\r\n\\ahsd;fkhasdl;kfhsdklfh\r\nahsdfklsdhafklhsdfklhsdfkl;hasdfl;kahfl;asdfhalsdfhasdl;kfh\r\nasdl;jfasekfjasdfsdaafsdf\r\nksdag;lj;sdflgjfgdfgdfg\r\nsdflgjksdfl;gj;dfgj;dgj;sdfjgsdfkglsdfkghsdlfkg\r\nsgklhsdflghsdf;kgh;lsdfkhg;sdfklghsdfklg\r\nsdfklghsl;dfkghdfl;kghdfkl;hgl;sdfkgh;lsdfghl",
    "reports_footer2": "Thank You!!!!!\r\nPlease Join Us Again.dfiljghrjkgkljgdlskgfladkgjd\r\nahsd;fj\r\n[asdhfkljasdgfkjasdgfsdjkgfsdjklfgkjfgkjgtkljasdbfjk\r\nasdhfjsdhfkjhl;khasdfj\r\njkasdhfkl;jhapsdofhjk\r\nadfhjsdfjkasdgfasdjkgfsdkljfghfjgasdlfjkgasdfjk\r\n\\ahsd;fkhasdl;kfhsdklfh\r\nahsdfklsdhafklhsdfklhsdfkl;hasdfl;kahfl;asdfhalsdfhasdl;kfh\r\nasdl;jfasekfjasdfsdaafsdf\r\nksdag;lj;sdflgjfgdfgdfg\r\nsdflgjksdfl;gj;dfgj;dgj;sdfjgsdfkglsdfkghsdlfkg\r\nsgklhsdflghsdf;kgh;lsdfkhg;sdfklghsdfklg\r\nsdfklghsl;dfkghdfl;kghdfkl;hgl;sdfkgh;lsdfghl",
    "bill1_header": null,
    "bill2_header": null
  }
]
```

### dbo.Rider

- Row count: **0**
- Columns: **5**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | RiderId | int(10,0) | YES | ((0)) |
| 3 | name | nvarchar(50) | YES |  |
| 4 | Commision | decimal(18,2) | NO | ((0)) |
| 5 | IsPercent | bit | NO | ((0)) |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.RiderCashFloat

- Row count: **0**
- Columns: **14**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | ShiftNo | nvarchar(50) | YES |  |
| 3 | Rider | nvarchar | YES |  |
| 4 | CheackIn | nvarchar(50) | YES |  |
| 5 | OpeningAmount | float(53,0) | YES |  |
| 6 | CheackOut | nvarchar(50) | YES |  |
| 7 | ClosingAmount | float(53,0) | YES |  |
| 8 | Date | datetime | YES |  |
| 9 | CheackInDate | datetime | YES |  |
| 10 | CheackOutDate | datetime | YES |  |
| 11 | ChkInStatus | bit | YES | ((0)) |
| 12 | ChkOutStatus | bit | YES | ((0)) |
| 13 | ReadingIn | int(10,0) | NO | ((0)) |
| 14 | ReadingOut | int(10,0) | NO | ((0)) |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.SaleInvoiceDetail

- Row count: **0**
- Columns: **5**
- Primary key: None
- Outgoing foreign keys: **1**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | Desc | nvarchar | YES |  |
| 3 | Amount | decimal(18,2) | YES |  |
| 4 | SaleInvoiceId | int(10,0) | YES |  |
| 5 | CAId | int(10,0) | YES |  |

Foreign key links:
- `SaleInvoiceId` -> `dbo.SaleInvoiceMaster.SaleInvoiceId` (SaleInvoiceMaster_SaleInvoiceDetail)

Sample data (`TOP 3`):

```text
No rows
```

### dbo.SaleInvoiceMaster

- Row count: **0**
- Columns: **11**
- Primary key: SaleInvoiceId
- Outgoing foreign keys: **3**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | SaleInvoiceId | int(10,0) | NO |  |
| 2 | SaleInvoiceNo | nvarchar(40) | YES |  |
| 3 | UserId | int(10,0) | YES |  |
| 4 | Date | datetime | YES |  |
| 5 | Amount | decimal(18,2) | YES |  |
| 6 | Discount | decimal(18,2) | YES |  |
| 7 | TotalAmount | decimal(18,2) | YES |  |
| 8 | IsFixAsset | bit | YES |  |
| 9 | CustId | int(10,0) | YES |  |
| 10 | COId | int(10,0) | YES |  |
| 11 | ProId | int(10,0) | YES | ((0)) |

Foreign key links:
- `CustId` -> `dbo.Customer.CustId` (Customer_SaleInvoiceMaster)
- `COId` -> `dbo.Company.COId` (FK_SaleInvoiceMaster_Company)
- `CustId` -> `dbo.Customer.CustId` (FK_SaleInvoiceMaster_Customer)

Sample data (`TOP 3`):

```text
No rows
```

### dbo.ServerTiltAssign

- Row count: **0**
- Columns: **3**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | ServerId | int(10,0) | YES |  |
| 3 | Tiltid | int(10,0) | YES |  |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.ServiceCharges

- Row count: **1**
- Columns: **9**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | Percent | decimal(18,2) | YES |  |
| 3 | IsApplicable | bit | YES | ((0)) |
| 4 | AppylOnCovers | bit | YES | ((0)) |
| 5 | OnCovers | int(10,0) | YES | ((0)) |
| 6 | ApplyOnAmount | bit | YES | ((0)) |
| 7 | OnAmount | float(53,0) | YES | ((0)) |
| 8 | Company_Percent | decimal(18,2) | YES | ((0)) |
| 9 | Waiter_Percent | decimal(18,2) | YES | ((0)) |

Sample data (`TOP 3`):

```json
[
  {
    "id": 8,
    "Percent": 10.0,
    "IsApplicable": true,
    "AppylOnCovers": false,
    "OnCovers": 0,
    "ApplyOnAmount": false,
    "OnAmount": 0.0,
    "Company_Percent": null,
    "Waiter_Percent": null
  }
]
```

### dbo.SheeshaTime

- Row count: **1**
- Columns: **4**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | time | nvarchar(50) | YES |  |
| 3 | cashDrop | decimal(18,2) | NO | ((0)) |
| 4 | CashDropTime | int(10,0) | NO | ((0)) |

Sample data (`TOP 3`):

```json
[
  {
    "id": 2,
    "time": "0",
    "cashDrop": 0.0,
    "CashDropTime": 0
  }
]
```

### dbo.Shift_Account_Detail

- Row count: **0**
- Columns: **4**
- Primary key: ID
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | ID | int(10,0) | NO |  |
| 2 | z_number | nvarchar(50) | YES |  |
| 3 | payment_type | nvarchar(50) | YES |  |
| 4 | Amount | decimal(18,2) | YES |  |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.Shift_Opening

- Row count: **1**
- Columns: **13**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | opening_date | datetime | YES |  |
| 3 | opening_day | nvarchar(50) | YES |  |
| 4 | shift_name | nvarchar(50) | YES |  |
| 5 | z_report_number | nvarchar(50) | YES |  |
| 6 | opening_person | nvarchar(50) | YES |  |
| 7 | closing_person | nvarchar(50) | YES |  |
| 8 | opening_time | nvarchar(50) | YES |  |
| 9 | closing_time | nvarchar(50) | YES |  |
| 10 | status | bit | YES |  |
| 11 | tiltid | int(10,0) | YES |  |
| 12 | is_upload | bit | NO | ((0)) |
| 13 | is_update | bit | NO | ((0)) |

Sample data (`TOP 3`):

```json
[
  {
    "id": 55,
    "opening_date": "2020-12-09T12:02:00",
    "opening_day": null,
    "shift_name": "DAY",
    "z_report_number": "DAY-00001",
    "opening_person": "admin",
    "closing_person": null,
    "opening_time": "",
    "closing_time": null,
    "status": true,
    "tiltid": null,
    "is_upload": false,
    "is_update": false
  }
]
```

### dbo.Shift_User

- Row count: **18**
- Columns: **3**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | user_name | nvarchar(50) | YES |  |
| 3 | shift_name | nvarchar(50) | YES |  |

Sample data (`TOP 3`):

```json
[
  {
    "id": 106,
    "user_name": "PC 1",
    "shift_name": "Day"
  },
  {
    "id": 108,
    "user_name": "PC 2",
    "shift_name": "Day"
  },
  {
    "id": 70,
    "user_name": "PC 3",
    "shift_name": "Day"
  }
]
```

### dbo.ShiftAmount

- Row count: **17**
- Columns: **26**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | TiltId | int(10,0) | YES |  |
| 3 | Z_Number | nvarchar(50) | YES |  |
| 4 | OpeningAmount | decimal(18,2) | YES |  |
| 5 | ClosingAmount | decimal(18,2) | YES |  |
| 6 | TimeIn | nvarchar(50) | YES |  |
| 7 | TimeOut | nvarchar(50) | YES |  |
| 8 | IsActive | bit | YES | ((0)) |
| 9 | OpeningDate | datetime | YES |  |
| 10 | ClosingDate | datetime | YES |  |
| 11 | OpenedBy | nvarchar(50) | YES |  |
| 12 | ClosedBy | nvarchar(50) | YES |  |
| 13 | Ten | nvarchar(50) | YES |  |
| 14 | Twenty | nvarchar(50) | YES |  |
| 15 | Fifty | nvarchar(50) | YES |  |
| 16 | Hundred | nvarchar(50) | YES |  |
| 17 | FiveHundred | nvarchar(50) | YES |  |
| 18 | Thousands | nvarchar(50) | YES |  |
| 19 | FiveThousands | nvarchar(50) | YES |  |
| 20 | TenThousands | nvarchar(50) | YES |  |
| 21 | One | nvarchar(50) | NO | ((0)) |
| 22 | Two | nvarchar(50) | NO | ((0)) |
| 23 | five | nvarchar(50) | NO | ((0)) |
| 24 | is_upload | bit | NO | ((0)) |
| 25 | is_update | bit | NO | ((0)) |
| 26 | id_ | int(10,0) | NO | ((0)) |

Sample data (`TOP 3`):

```json
[
  {
    "id": 390,
    "TiltId": 62,
    "Z_Number": "DAY-00001",
    "OpeningAmount": 1.0,
    "ClosingAmount": null,
    "TimeIn": "12:02 PM",
    "TimeOut": null,
    "IsActive": true,
    "OpeningDate": "2020-12-09T12:02:00",
    "ClosingDate": null,
    "OpenedBy": "server",
    "ClosedBy": null,
    "Ten": null,
    "Twenty": null,
    "Fifty": null,
    "Hundred": null,
    "FiveHundred": null,
    "Thousands": null,
    "FiveThousands": null,
    "TenThousands": null,
    "One": "0",
    "Two": "0",
    "five": "0",
    "is_upload": false,
    "is_update": false,
    "id_": 0
  },
  {
    "id": 392,
    "TiltId": 52,
    "Z_Number": "DAY-00001",
    "OpeningAmount": 1.0,
    "ClosingAmount": null,
    "TimeIn": "12:04 PM",
    "TimeOut": null,
    "IsActive": true,
    "OpeningDate": "2020-12-09T12:04:10",
    "ClosingDate": null,
    "OpenedBy": "PC 6",
    "ClosedBy": null,
    "Ten": null,
    "Twenty": null,
    "Fifty": null,
    "Hundred": null,
    "FiveHundred": null,
    "Thousands": null,
    "FiveThousands": null,
    "TenThousands": null,
    "One": "0",
    "Two": "0",
    "five": "0",
    "is_upload": false,
    "is_update": false,
    "id_": 0
  },
  {
    "id": 393,
    "TiltId": 60,
    "Z_Number": "DAY-00001",
    "OpeningAmount": 1.0,
    "ClosingAmount": null,
    "TimeIn": "5:55 PM",
    "TimeOut": null,
    "IsActive": true,
    "OpeningDate": "2020-12-09T17:55:00",
    "ClosingDate": null,
    "OpenedBy": "PC 7",
    "ClosedBy": null,
    "Ten": null,
    "Twenty": null,
    "Fifty": null,
    "Hundred": null,
    "FiveHundred": null,
    "Thousands": null,
    "FiveThousands": null,
    "TenThousands": null,
    "One": "0",
    "Two": "0",
    "five": "0",
    "is_upload": false,
    "is_update": false,
    "id_": 0
  }
]
```

### dbo.ShiftClosingTime

- Row count: **0**
- Columns: **3**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | Shift | nvarchar(50) | YES |  |
| 3 | ClosingTime | nvarchar(50) | YES |  |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.Shifts

- Row count: **3**
- Columns: **3**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | shift_id | int(10,0) | NO |  |
| 2 | shift_name | nvarchar(50) | YES |  |
| 3 | z_report_prefix | nvarchar(50) | YES |  |

Sample data (`TOP 3`):

```json
[
  {
    "shift_id": 1,
    "shift_name": "Morning",
    "z_report_prefix": "MRN-"
  },
  {
    "shift_id": 2,
    "shift_name": "Evening",
    "z_report_prefix": "ENV-"
  },
  {
    "shift_id": 3,
    "shift_name": "Day",
    "z_report_prefix": "DAY-"
  }
]
```

### dbo.SMS_Setup

- Row count: **1**
- Columns: **5**
- Primary key: ID
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | ID | int(10,0) | NO |  |
| 2 | UserID | nvarchar | NO |  |
| 3 | Password | nvarchar | YES |  |
| 4 | Mask | nvarchar | YES |  |
| 5 | URL | nvarchar | YES |  |

Sample data (`TOP 3`):

```json
[
  {
    "ID": 5,
    "UserID": "rchkababjees",
    "Password": "karachi58",
    "Mask": "Kababjees",
    "URL": "http://www.outreach.pk/api/sendsms.php/sendsms/url"
  }
]
```

### dbo.SMSLog

- Row count: **6014**
- Columns: **6**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | Order_Key | int(10,0) | YES |  |
| 3 | MobileNo | nvarchar(50) | YES |  |
| 4 | Message | nvarchar | YES |  |
| 5 | SentTime | nvarchar(50) | YES |  |
| 6 | IsSent | bit | YES | ((0)) |

Sample data (`TOP 3`):

```json
[
  {
    "id": 105,
    "Order_Key": 49019,
    "MobileNo": "03333864919",
    "Message": "Customer:Ali Makawa Eatoye, Order#27816, Thank You!!! Try Us Again ;)",
    "SentTime": null,
    "IsSent": true
  },
  {
    "id": 106,
    "Order_Key": 49020,
    "MobileNo": "03332107803",
    "Message": "Customer:Sana Akram FP, Order#27817, Thank You!!! Try Us Again ;)",
    "SentTime": null,
    "IsSent": true
  },
  {
    "id": 107,
    "Order_Key": 49021,
    "MobileNo": "03232549443",
    "Message": "Customer:Fahad sahib fp online payment, Order#27818, Thank You!!! Try Us Again ;)",
    "SentTime": null,
    "IsSent": true
  }
]
```

### dbo.SmsSetting

- Row count: **1**
- Columns: **5**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | a | nvarchar(50) | YES |  |
| 3 | b | nvarchar | YES |  |
| 4 | c | nvarchar(50) | YES |  |
| 5 | OrderType | nvarchar(100) | YES |  |

Sample data (`TOP 3`):

```json
[
  {
    "id": 15,
    "a": "HOT N SPICY",
    "b": "",
    "c": "Thank You For Ordering us. ",
    "OrderType": null
  }
]
```

### dbo.Step_Deal

- Row count: **0**
- Columns: **13**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | Deal_Id | int(10,0) | NO |  |
| 3 | Dealname | nvarchar(50) | NO |  |
| 4 | Steps | int(10,0) | NO |  |
| 5 | PriceOnstep | int(10,0) | NO |  |
| 6 | Step_id | int(10,0) | NO |  |
| 7 | Step | nchar(10) | NO |  |
| 8 | Category_id | int(10,0) | NO |  |
| 9 | Item_Id | int(10,0) | NO |  |
| 10 | Item_Qty | decimal(18,2) | NO |  |
| 11 | Is_PriceItem | bit | NO | ((0)) |
| 12 | Item_Price | decimal(18,2) | NO | ((0)) |
| 13 | DealPrice | decimal(18,2) | NO | ((0)) |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.Step_Deal_Items

- Row count: **0**
- Columns: **19**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | Order_key | nvarchar(50) | NO |  |
| 3 | Order_Detail_Id | int(10,0) | NO |  |
| 4 | Deal_Id | int(10,0) | NO |  |
| 5 | Dealname | nvarchar(50) | NO |  |
| 6 | Steps | int(10,0) | NO |  |
| 7 | PriceOnstep | int(10,0) | NO |  |
| 8 | Step_id | int(10,0) | NO |  |
| 9 | Step | nchar(10) | NO |  |
| 10 | Category_id | int(10,0) | NO |  |
| 11 | Item_Id | int(10,0) | NO |  |
| 12 | Item_Qty | decimal(18,2) | NO |  |
| 13 | Is_PriceItem | bit | NO | ((0)) |
| 14 | Item_Price | decimal(18,2) | NO | ((0)) |
| 15 | DealPrice | decimal(18,2) | NO | ((0)) |
| 16 | DealQty | decimal(18,2) | NO | ((0)) |
| 17 | Item | nvarchar(50) | YES |  |
| 18 | Price_Item | decimal(18,2) | NO | ((0)) |
| 19 | item_comment | nvarchar(50) | YES |  |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.Step_Deal_Items_Temp

- Row count: **0**
- Columns: **14**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | Order_key | nvarchar(50) | NO |  |
| 3 | Order_Detail_Id | int(10,0) | NO |  |
| 4 | Deal_Id | int(10,0) | NO |  |
| 5 | Dealname | nvarchar(50) | NO |  |
| 6 | Steps | int(10,0) | NO |  |
| 7 | PriceOnstep | int(10,0) | NO |  |
| 8 | Step_id | int(10,0) | NO |  |
| 9 | Step | nchar(10) | NO |  |
| 10 | Category_id | int(10,0) | NO |  |
| 11 | Item_Id | int(10,0) | NO |  |
| 12 | Item_Qty | decimal(18,2) | NO |  |
| 13 | Is_PriceItem | bit | NO | ((0)) |
| 14 | Item_Price | decimal(18,2) | NO | ((0)) |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.Store

- Row count: **0**
- Columns: **6**
- Primary key: SId
- Outgoing foreign keys: **1**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | SId | int(10,0) | NO |  |
| 2 | Store | nvarchar(50) | YES |  |
| 3 | CentarlStore | bit | YES | ((1)) |
| 4 | COId | int(10,0) | YES |  |
| 5 | IsSelected | bit | YES | ((1)) |
| 6 | BrId | int(10,0) | NO | ((0)) |

Foreign key links:
- `COId` -> `dbo.Company.COId` (FK_Store_Company)

Sample data (`TOP 3`):

```text
No rows
```

### dbo.SubCategory

- Row count: **0**
- Columns: **3**
- Primary key: SBId
- Outgoing foreign keys: **1**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | SBId | int(10,0) | NO |  |
| 2 | CId | int(10,0) | YES |  |
| 3 | SubCategory | nvarchar(50) | YES |  |

Foreign key links:
- `CId` -> `dbo.Category.CId` (FK_SubCategory_Category1)

Sample data (`TOP 3`):

```text
No rows
```

### dbo.SubRecipeDetail

- Row count: **0**
- Columns: **4**
- Primary key: None
- Outgoing foreign keys: **1**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | SubRecipeId | int(10,0) | YES |  |
| 3 | IngredientId | int(10,0) | YES |  |
| 4 | Qty | float(53,0) | YES |  |

Foreign key links:
- `SubRecipeId` -> `dbo.SubRecipeMaster.SubRecipeId` (FK_SubRecipeDetail_SubRecipeMaster)

Sample data (`TOP 3`):

```text
No rows
```

### dbo.SubRecipeMaster

- Row count: **0**
- Columns: **6**
- Primary key: SubRecipeId
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | SubRecipeId | int(10,0) | NO |  |
| 2 | ProductId | int(10,0) | YES |  |
| 3 | max_FP_Cost | decimal(18,2) | NO | ((0)) |
| 4 | min_SP_Price | decimal(18,2) | NO | ((0)) |
| 5 | Current_FP_Cost | decimal(18,2) | NO | ((0)) |
| 6 | Comments | nvarchar | YES |  |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.SupplierLedger

- Row count: **0**
- Columns: **11**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | VId | int(10,0) | YES |  |
| 3 | VoucherId | int(10,0) | YES |  |
| 4 | Amount | decimal(18,2) | YES |  |
| 5 | Type | nvarchar(50) | YES |  |
| 6 | VoucherType | nvarchar(50) | YES |  |
| 7 | COId | int(10,0) | YES |  |
| 8 | Date | datetime | YES |  |
| 9 | VN | nvarchar(50) | YES |  |
| 10 | InvoiceId | int(10,0) | YES | ((0)) |
| 11 | IsAdvance | bit | YES | ((0)) |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.sysdiagrams

- Row count: **2**
- Columns: **5**
- Primary key: diagram_id
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | name | nvarchar(128) | NO |  |
| 2 | principal_id | int(10,0) | NO |  |
| 3 | diagram_id | int(10,0) | NO |  |
| 4 | version | int(10,0) | YES |  |
| 5 | definition | varbinary | YES |  |

Sample data (`TOP 3`):

```json
[
  {
    "name": "Diagram_0",
    "principal_id": 1,
    "diagram_id": 1,
    "version": 1,
    "definition": "<bytes:48132>"
  },
  {
    "name": "Diagram_1",
    "principal_id": 1,
    "diagram_id": 2,
    "version": 1,
    "definition": "<bytes:56324>"
  }
]
```

### dbo.Table1

- Row count: **0**
- Columns: **2**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | nvarchar(50) | YES |  |
| 2 | Od | int(10,0) | NO |  |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.Table2

- Row count: **0**
- Columns: **1**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | nvarchar(50) | YES |  |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.Table3

- Row count: **0**
- Columns: **1**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | nvarchar(50) | YES |  |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.Table4

- Row count: **0**
- Columns: **1**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | nvarchar(50) | YES |  |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.TableMerge

- Row count: **0**
- Columns: **15**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | OrderkeyFrom | nvarchar(50) | YES |  |
| 3 | OrderKeyTo | nvarchar(50) | YES |  |
| 4 | OrderNoFrom | int(10,0) | YES |  |
| 5 | OrderNoTo | int(10,0) | YES |  |
| 6 | Z_Number | nvarchar(50) | YES |  |
| 7 | TableNoFrom | nvarchar(50) | YES |  |
| 8 | TableNoTo | nvarchar(50) | YES |  |
| 9 | AmountFrom | float(53,0) | YES |  |
| 10 | AmountTo | float(53,0) | YES |  |
| 11 | OrderDate | datetime | YES |  |
| 12 | ServerFrom | nvarchar(50) | YES |  |
| 13 | ServerTo | nvarchar(50) | YES |  |
| 14 | CoverFrom | int(10,0) | YES |  |
| 15 | CoverTo | int(10,0) | YES |  |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.Tables

- Row count: **0**
- Columns: **6**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | tables | nvarchar(50) | YES |  |
| 3 | TableName | nvarchar(50) | YES |  |
| 4 | table_status | nvarchar(50) | YES |  |
| 5 | TiltId | int(10,0) | NO | ((0)) |
| 6 | CurrTiltId | int(10,0) | NO | ((0)) |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.TableTiltAssign

- Row count: **0**
- Columns: **4**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | TableId | int(10,0) | YES |  |
| 3 | Tiltid | int(10,0) | YES |  |
| 4 | Active | int(10,0) | YES | ((1)) |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.TakeAway_Customer

- Row count: **0**
- Columns: **4**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | customer | nvarchar(50) | YES |  |
| 3 | phone_num | nvarchar(50) | YES |  |
| 4 | order_key | nvarchar(50) | YES |  |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.Tax

- Row count: **0**
- Columns: **5**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | isApplicable | bit | YES |  |
| 3 | tax_type | nvarchar(50) | YES |  |
| 4 | tax_amount | float(53,0) | YES |  |
| 5 | Tax | nchar(50) | YES |  |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.Tax_

- Row count: **1**
- Columns: **7**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | Id | int(10,0) | NO |  |
| 2 | IsApplicable | bit | YES |  |
| 3 | TaxType | nvarchar(50) | YES |  |
| 4 | Tax | decimal(18,2) | YES |  |
| 5 | Type | nvarchar(50) | YES |  |
| 6 | CAId | int(10,0) | YES | ((0)) |
| 7 | TransactionType | nvarchar(50) | YES |  |

Sample data (`TOP 3`):

```json
[
  {
    "Id": 10,
    "IsApplicable": true,
    "TaxType": "GST",
    "Tax": 17.0,
    "Type": "Exclusive",
    "CAId": 0,
    "TransactionType": null
  }
]
```

### dbo.TaxDetail

- Row count: **0**
- Columns: **8**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | Order_Key | nvarchar(50) | YES |  |
| 3 | TaxName | nvarchar(50) | YES |  |
| 4 | TaxType | nvarchar(50) | YES |  |
| 5 | TaxPercent | nvarchar(50) | YES |  |
| 6 | TaxAmount | decimal(18,2) | YES |  |
| 7 | is_upload | bit | NO | ((0)) |
| 8 | is_update | bit | NO | ((0)) |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.TaxInventory

- Row count: **0**
- Columns: **2**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | tax_amount | float(53,0) | YES |  |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.tbl_user

- Row count: **17**
- Columns: **90**
- Primary key: id
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | username | nvarchar(50) | YES |  |
| 3 | pwd | nvarchar(50) | YES |  |
| 4 | adminsetting | bit | YES |  |
| 5 | inventory_setting | bit | YES | ((0)) |
| 6 | create_change_user | bit | YES |  |
| 7 | create_change_shift | bit | YES |  |
| 8 | point_of_sale | bit | YES |  |
| 9 | sales_reports | bit | YES | ((0)) |
| 10 | item_less | bit | YES | ((0)) |
| 11 | discount | bit | YES | ((0)) |
| 12 | order_delete | bit | YES | ((0)) |
| 13 | ent | bit | YES | ((0)) |
| 14 | RptMenu | bit | YES | ((0)) |
| 15 | RptShiftWiseFinancial | bit | YES | ((0)) |
| 16 | RptXReportsFinancial | bit | YES | ((0)) |
| 17 | RptXReportsCategory | bit | YES | ((0)) |
| 18 | RptXReportsItem | bit | YES | ((0)) |
| 19 | RptRunningTables | bit | YES | ((0)) |
| 20 | RptTakeAwayCustomer | bit | YES | ((0)) |
| 21 | RptDeliveryCustomer | bit | YES | ((0)) |
| 22 | RptDistributedReport | bit | YES | ((0)) |
| 23 | RptItem | bit | YES | ((0)) |
| 24 | RptFinancial | bit | YES | ((0)) |
| 25 | RptCategory | bit | YES | ((0)) |
| 26 | RptCovers | bit | YES | ((0)) |
| 27 | RptOrderDetails | bit | YES | ((0)) |
| 28 | RptDiscount | bit | YES | ((0)) |
| 29 | RptEnt | bit | YES | ((0)) |
| 30 | RptOrderDelete | bit | YES | ((0)) |
| 31 | RptItemLess | bit | YES | ((0)) |
| 32 | RptDeliveryOrders | bit | YES | ((0)) |
| 33 | RptBillHistory | bit | YES | ((0)) |
| 34 | RptWaiterPerformance | bit | YES | ((0)) |
| 35 | RptCategoryByDepart | bit | YES | ((0)) |
| 36 | OpeningAmount | bit | YES | ((0)) |
| 37 | ClosingAmount | bit | YES | ((0)) |
| 38 | CashDrop | bit | YES | ((0)) |
| 39 | IsCash | bit | YES | ((0)) |
| 40 | LoginStatus | bit | YES | ((0)) |
| 41 | UserWiseOrder | bit | YES | ((0)) |
| 42 | InventoryFunctional | bit | YES | ((0)) |
| 43 | InventorySettings | bit | YES | ((0)) |
| 44 | InventoryReports | bit | YES | ((0)) |
| 45 | AccountsFunctional | bit | YES | ((0)) |
| 46 | AccountsSettings | bit | YES | ((0)) |
| 47 | AccountsReports | bit | YES | ((0)) |
| 48 | CreateUser | bit | NO | ((0)) |
| 49 | Tiltid | int(10,0) | NO | ((0)) |
| 50 | CardData | nvarchar(50) | YES |  |
| 51 | ReportsPOS | bit | NO | ((1)) |
| 52 | is_upload | bit | NO | ((0)) |
| 53 | is_update | bit | NO | ((0)) |
| 54 | N_AdvBooking | bit | NO | ((0)) |
| 55 | N_All_Orders | bit | NO | ((0)) |
| 56 | n_CashDrop | bit | NO | ((0)) |
| 57 | N_CreditSale | bit | NO | ((0)) |
| 58 | N_DeptWise_Sale | bit | NO | ((0)) |
| 59 | N_Financial_Running_Shift | bit | NO | ((0)) |
| 60 | N_Item_Running_Shift | bit | NO | ((0)) |
| 61 | N_Item_Zero | bit | NO | ((0)) |
| 62 | N_ItemRate | bit | NO | ((0)) |
| 63 | N_Ledger | bit | NO | ((0)) |
| 64 | N_LoginStatus | bit | NO | ((0)) |
| 65 | N_RiderCashFloat | bit | NO | ((0)) |
| 66 | N_RiderPerformance | bit | NO | ((0)) |
| 67 | N_SaleDetail | bit | NO | ((0)) |
| 68 | N_SaleReturn | bit | NO | ((0)) |
| 69 | N_shift_Counter_Report | bit | NO | ((0)) |
| 70 | N_Table_Running_Shift | bit | NO | ((0)) |
| 71 | N_Table_Summary | bit | NO | ((0)) |
| 72 | N_table_time | bit | NO | ((0)) |
| 73 | N_TakeAwayOrders | bit | NO | ((0)) |
| 74 | n_Tax | bit | NO | ((0)) |
| 75 | N_TopSale_Item | bit | NO | ((0)) |
| 76 | N_TopSale_Item_CategoryWise | bit | NO | ((0)) |
| 77 | ItemTransfer | bit | NO | ((0)) |
| 78 | OrderTransfer | bit | NO | ((0)) |
| 79 | DuplicateKOT | bit | NO | ((0)) |
| 80 | ItemComplimentry | bit | NO | ((0)) |
| 81 | PartyAccount | bit | NO | ((0)) |
| 82 | SaleView | bit | NO | ((0)) |
| 83 | IsDeliveryCharges | bit | NO | ((0)) |
| 84 | only_bill | bit | NO | ((0)) |
| 85 | user_wise_order | bit | NO | ((0)) |
| 86 | dine_in | bit | YES | ((0)) |
| 87 | takeaway | bit | YES | ((0)) |
| 88 | delivery | bit | YES | ((0)) |
| 89 | order_delete_after_bill | bit | YES | ((0)) |
| 90 | item_less_after_bill | bit | YES | ((0)) |

Sample data (`TOP 3`):

```json
[
  {
    "id": 133,
    "username": "PC 3",
    "pwd": "123",
    "adminsetting": false,
    "inventory_setting": false,
    "create_change_user": true,
    "create_change_shift": true,
    "point_of_sale": true,
    "sales_reports": true,
    "item_less": true,
    "discount": true,
    "order_delete": true,
    "ent": true,
    "RptMenu": true,
    "RptShiftWiseFinancial": true,
    "RptXReportsFinancial": true,
    "RptXReportsCategory": true,
    "RptXReportsItem": true,
    "RptRunningTables": true,
    "RptTakeAwayCustomer": true,
    "RptDeliveryCustomer": true,
    "RptDistributedReport": true,
    "RptItem": true,
    "RptFinancial": true,
    "RptCategory": true,
    "RptCovers": true,
    "RptOrderDetails": true,
    "RptDiscount": true,
    "RptEnt": true,
    "RptOrderDelete": true,
    "RptItemLess": true,
    "RptDeliveryOrders": true,
    "RptBillHistory": true,
    "RptWaiterPerformance": true,
    "RptCategoryByDepart": true,
    "OpeningAmount": true,
    "ClosingAmount": true,
    "CashDrop": true,
    "IsCash": true,
    "LoginStatus": true,
    "UserWiseOrder": false,
    "InventoryFunctional": true,
    "InventorySettings": true,
    "InventoryReports": true,
    "AccountsFunctional": true,
    "AccountsSettings": true,
    "AccountsReports": true,
    "CreateUser": true,
    "Tiltid": 0,
    "CardData": null,
    "ReportsPOS": true,
    "is_upload": false,
    "is_update": false,
    "N_AdvBooking": true,
    "N_All_Orders": true,
    "n_CashDrop": true,
    "N_CreditSale": true,
    "N_DeptWise_Sale": true,
    "N_Financial_Running_Shift": true,
    "N_Item_Running_Shift": true,
    "N_Item_Zero": true,
    "N_ItemRate": true,
    "N_Ledger": true,
    "N_LoginStatus": true,
    "N_RiderCashFloat": true,
    "N_RiderPerformance": true,
    "N_SaleDetail": true,
    "N_SaleReturn": true,
    "N_shift_Counter_Report": true,
    "N_Table_Running_Shift": true,
    "N_Table_Summary": true,
    "N_table_time": true,
    "N_TakeAwayOrders": true,
    "n_Tax": true,
    "N_TopSale_Item": true,
    "N_TopSale_Item_CategoryWise": true,
    "ItemTransfer": false,
    "OrderTransfer": false,
    "DuplicateKOT": false,
    "ItemComplimentry": false,
    "PartyAccount": false,
    "SaleView": false,
    "IsDeliveryCharges": false,
    "only_bill": false,
    "user_wise_order": false,
    "dine_in": null,
    "takeaway": null,
    "delivery": null,
    "order_delete_after_bill": null,
    "item_less_after_bill": null
  },
  {
    "id": 136,
    "username": "PC 4",
    "pwd": "123",
    "adminsetting": false,
    "inventory_setting": false,
    "create_change_user": true,
    "create_change_shift": true,
    "point_of_sale": true,
    "sales_reports": true,
    "item_less": true,
    "discount": true,
    "order_delete": true,
    "ent": true,
    "RptMenu": true,
    "RptShiftWiseFinancial": true,
    "RptXReportsFinancial": true,
    "RptXReportsCategory": true,
    "RptXReportsItem": true,
    "RptRunningTables": true,
    "RptTakeAwayCustomer": true,
    "RptDeliveryCustomer": true,
    "RptDistributedReport": true,
    "RptItem": true,
    "RptFinancial": true,
    "RptCategory": true,
    "RptCovers": true,
    "RptOrderDetails": true,
    "RptDiscount": true,
    "RptEnt": true,
    "RptOrderDelete": true,
    "RptItemLess": true,
    "RptDeliveryOrders": true,
    "RptBillHistory": true,
    "RptWaiterPerformance": true,
    "RptCategoryByDepart": true,
    "OpeningAmount": true,
    "ClosingAmount": true,
    "CashDrop": true,
    "IsCash": true,
    "LoginStatus": true,
    "UserWiseOrder": false,
    "InventoryFunctional": true,
    "InventorySettings": true,
    "InventoryReports": true,
    "AccountsFunctional": true,
    "AccountsSettings": true,
    "AccountsReports": true,
    "CreateUser": true,
    "Tiltid": 53,
    "CardData": null,
    "ReportsPOS": true,
    "is_upload": false,
    "is_update": false,
    "N_AdvBooking": true,
    "N_All_Orders": true,
    "n_CashDrop": true,
    "N_CreditSale": true,
    "N_DeptWise_Sale": true,
    "N_Financial_Running_Shift": true,
    "N_Item_Running_Shift": true,
    "N_Item_Zero": true,
    "N_ItemRate": true,
    "N_Ledger": true,
    "N_LoginStatus": true,
    "N_RiderCashFloat": true,
    "N_RiderPerformance": true,
    "N_SaleDetail": true,
    "N_SaleReturn": true,
    "N_shift_Counter_Report": true,
    "N_Table_Running_Shift": true,
    "N_Table_Summary": true,
    "N_table_time": true,
    "N_TakeAwayOrders": true,
    "n_Tax": true,
    "N_TopSale_Item": true,
    "N_TopSale_Item_CategoryWise": true,
    "ItemTransfer": false,
    "OrderTransfer": false,
    "DuplicateKOT": false,
    "ItemComplimentry": false,
    "PartyAccount": false,
    "SaleView": false,
    "IsDeliveryCharges": false,
    "only_bill": false,
    "user_wise_order": false,
    "dine_in": null,
    "takeaway": null,
    "delivery": null,
    "order_delete_after_bill": null,
    "item_less_after_bill": null
  },
  {
    "id": 139,
    "username": "PC 6",
    "pwd": "123",
    "adminsetting": false,
    "inventory_setting": false,
    "create_change_user": true,
    "create_change_shift": true,
    "point_of_sale": true,
    "sales_reports": true,
    "item_less": true,
    "discount": true,
    "order_delete": true,
    "ent": true,
    "RptMenu": true,
    "RptShiftWiseFinancial": true,
    "RptXReportsFinancial": true,
    "RptXReportsCategory": true,
    "RptXReportsItem": true,
    "RptRunningTables": true,
    "RptTakeAwayCustomer": true,
    "RptDeliveryCustomer": true,
    "RptDistributedReport": true,
    "RptItem": true,
    "RptFinancial": true,
    "RptCategory": true,
    "RptCovers": true,
    "RptOrderDetails": true,
    "RptDiscount": true,
    "RptEnt": true,
    "RptOrderDelete": true,
    "RptItemLess": true,
    "RptDeliveryOrders": true,
    "RptBillHistory": true,
    "RptWaiterPerformance": true,
    "RptCategoryByDepart": true,
    "OpeningAmount": true,
    "ClosingAmount": true,
    "CashDrop": true,
    "IsCash": true,
    "LoginStatus": true,
    "UserWiseOrder": false,
    "InventoryFunctional": true,
    "InventorySettings": true,
    "InventoryReports": true,
    "AccountsFunctional": true,
    "AccountsSettings": true,
    "AccountsReports": true,
    "CreateUser": true,
    "Tiltid": 51,
    "CardData": null,
    "ReportsPOS": true,
    "is_upload": false,
    "is_update": false,
    "N_AdvBooking": true,
    "N_All_Orders": true,
    "n_CashDrop": true,
    "N_CreditSale": true,
    "N_DeptWise_Sale": true,
    "N_Financial_Running_Shift": true,
    "N_Item_Running_Shift": true,
    "N_Item_Zero": true,
    "N_ItemRate": true,
    "N_Ledger": true,
    "N_LoginStatus": true,
    "N_RiderCashFloat": true,
    "N_RiderPerformance": true,
    "N_SaleDetail": true,
    "N_SaleReturn": true,
    "N_shift_Counter_Report": true,
    "N_Table_Running_Shift": true,
    "N_Table_Summary": true,
    "N_table_time": true,
    "N_TakeAwayOrders": true,
    "n_Tax": true,
    "N_TopSale_Item": true,
    "N_TopSale_Item_CategoryWise": true,
    "ItemTransfer": false,
    "OrderTransfer": false,
    "DuplicateKOT": false,
    "ItemComplimentry": false,
    "PartyAccount": false,
    "SaleView": false,
    "IsDeliveryCharges": false,
    "only_bill": false,
    "user_wise_order": false,
    "dine_in": null,
    "takeaway": null,
    "delivery": null,
    "order_delete_after_bill": null,
    "item_less_after_bill": null
  }
]
```

### dbo.tblLuckyDraw

- Row count: **0**
- Columns: **7**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | Name | varchar(50) | NO |  |
| 3 | from | int(10,0) | YES |  |
| 4 | to | int(10,0) | YES |  |
| 5 | IsActive | bit | NO |  |
| 6 | Date | datetime | YES |  |
| 7 | Increment | int(10,0) | YES |  |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.TempDealsOnSpotItems

- Row count: **0**
- Columns: **12**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | order_key | nvarchar(50) | YES |  |
| 3 | Order_detailId | int(10,0) | YES |  |
| 4 | deal_name | nvarchar(50) | YES |  |
| 5 | deal_price | float(53,0) | YES |  |
| 6 | category_name | nvarchar(50) | YES |  |
| 7 | item_name | nvarchar(50) | YES |  |
| 8 | qty | float(53,0) | YES |  |
| 9 | department | nvarchar(50) | YES |  |
| 10 | TiltId | int(10,0) | YES |  |
| 11 | Status | bit | YES | ((0)) |
| 12 | ItemQty | float(53,0) | YES |  |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.tempDine_In_Order

- Row count: **527**
- Columns: **49**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | order_key | nvarchar(50) | NO |  |
| 3 | z_number | nvarchar(50) | YES |  |
| 4 | order_type | nvarchar(50) | YES |  |
| 5 | order_no | int(10,0) | YES |  |
| 6 | order_date | datetime | YES |  |
| 7 | day | nvarchar(50) | YES |  |
| 8 | table_no | nvarchar(50) | YES |  |
| 9 | waiter_name | nvarchar(50) | YES |  |
| 10 | order_time | nvarchar(50) | YES |  |
| 11 | service_time | nvarchar(50) | YES |  |
| 12 | service_status | nvarchar(50) | YES |  |
| 13 | account_status | nvarchar(50) | YES |  |
| 14 | amount | float(53,0) | YES |  |
| 15 | DiscountType | nvarchar(50) | YES |  |
| 16 | discount | decimal(18,0) | YES | ((0)) |
| 17 | is_delete | bit | YES | ((0)) |
| 18 | cover | decimal(18,0) | NO | ('0') |
| 19 | estimated_time | nvarchar(50) | YES |  |
| 20 | table_time | nvarchar(50) | YES |  |
| 21 | kitchen_status | bit | NO | ((0)) |
| 22 | Tiltid | int(10,0) | YES |  |
| 23 | CounterId | int(10,0) | YES |  |
| 24 | IsBill | bit | YES | ((0)) |
| 25 | CareOff | nvarchar(100) | YES |  |
| 26 | IsSelect | bit | YES | ((0)) |
| 27 | Customer | nvarchar | YES |  |
| 28 | Tele | nvarchar(50) | YES |  |
| 29 | ExtraCharges | decimal(18,2) | YES | ((0)) |
| 30 | DeleteReason | nvarchar | YES |  |
| 31 | UserPunch | nvarchar | YES |  |
| 32 | UserCash | nvarchar | YES |  |
| 33 | UserDelete | nvarchar | YES |  |
| 34 | KOT | int(10,0) | YES | ((0)) |
| 35 | tableStatus | bit | YES | ((0)) |
| 36 | OrderTiltId | int(10,0) | YES | ((0)) |
| 37 | TimeIn | datetime | YES |  |
| 38 | TimeOut | datetime | YES |  |
| 39 | Status | bit | NO | ((0)) |
| 40 | Od | int(10,0) | NO | ((0)) |
| 41 | Itemqty | float(53,0) | NO | ((0)) |
| 42 | Itemprice | float(53,0) | NO | ((0)) |
| 43 | OrderKey_Merege | nvarchar(50) | YES |  |
| 44 | DispatchTime | nvarchar(50) | YES |  |
| 45 | OrderStatus | nvarchar(50) | YES |  |
| 46 | PaymentMode | nvarchar(50) | YES |  |
| 47 | isFeedback | bit | NO | ((0)) |
| 48 | Feedback | nvarchar | YES |  |
| 49 | DiscountId | nvarchar(50) | YES |  |

Sample data (`TOP 3`):

```json
[
  {
    "id": 530224,
    "order_key": "530224-0",
    "z_number": "DAY-00001",
    "order_type": "DELIVERY",
    "order_no": 0,
    "order_date": "2021-02-20T00:00:00",
    "day": "Wednesday",
    "table_no": "",
    "waiter_name": "",
    "order_time": "02:20 PM",
    "service_time": "02:20 PM",
    "service_status": "",
    "account_status": "Not Paid",
    "amount": 0.0,
    "DiscountType": null,
    "discount": 0.0,
    "is_delete": false,
    "cover": 0.0,
    "estimated_time": "02/20/21 2:20 PM",
    "table_time": null,
    "kitchen_status": false,
    "Tiltid": 57,
    "CounterId": 391,
    "IsBill": false,
    "CareOff": null,
    "IsSelect": false,
    "Customer": null,
    "Tele": null,
    "ExtraCharges": 0.0,
    "DeleteReason": null,
    "UserPunch": "PC-14",
    "UserCash": null,
    "UserDelete": null,
    "KOT": 0,
    "tableStatus": false,
    "OrderTiltId": 57,
    "TimeIn": null,
    "TimeOut": null,
    "Status": false,
    "Od": 0,
    "Itemqty": 0.0,
    "Itemprice": 0.0,
    "OrderKey_Merege": null,
    "DispatchTime": null,
    "OrderStatus": null,
    "PaymentMode": null,
    "isFeedback": false,
    "Feedback": null,
    "DiscountId": null
  },
  {
    "id": 551214,
    "order_key": "551214-0",
    "z_number": "DAY-00001",
    "order_type": "DELIVERY",
    "order_no": 0,
    "order_date": "2021-04-03T00:00:00",
    "day": "Wednesday",
    "table_no": "",
    "waiter_name": "",
    "order_time": "01:52 PM",
    "service_time": "01:52 PM",
    "service_status": "",
    "account_status": "Not Paid",
    "amount": 0.0,
    "DiscountType": null,
    "discount": 0.0,
    "is_delete": false,
    "cover": 0.0,
    "estimated_time": "04/03/21 1:52 PM",
    "table_time": null,
    "kitchen_status": false,
    "Tiltid": 52,
    "CounterId": 392,
    "IsBill": false,
    "CareOff": null,
    "IsSelect": false,
    "Customer": null,
    "Tele": null,
    "ExtraCharges": 0.0,
    "DeleteReason": null,
    "UserPunch": "PC 6",
    "UserCash": null,
    "UserDelete": null,
    "KOT": 0,
    "tableStatus": false,
    "OrderTiltId": 52,
    "TimeIn": null,
    "TimeOut": null,
    "Status": false,
    "Od": 0,
    "Itemqty": 0.0,
    "Itemprice": 0.0,
    "OrderKey_Merege": null,
    "DispatchTime": null,
    "OrderStatus": null,
    "PaymentMode": null,
    "isFeedback": false,
    "Feedback": null,
    "DiscountId": null
  },
  {
    "id": 483460,
    "order_key": "483460-0",
    "z_number": "DAY-00001",
    "order_type": "DELIVERY",
    "order_no": 0,
    "order_date": "2020-12-28T00:00:00",
    "day": "Wednesday",
    "table_no": "",
    "waiter_name": "",
    "order_time": "09:47 PM",
    "service_time": "09:47 PM",
    "service_status": "",
    "account_status": "Not Paid",
    "amount": 0.0,
    "DiscountType": null,
    "discount": 0.0,
    "is_delete": false,
    "cover": 0.0,
    "estimated_time": "12/28/20 9:47 PM",
    "table_time": null,
    "kitchen_status": false,
    "Tiltid": 46,
    "CounterId": 399,
    "IsBill": false,
    "CareOff": null,
    "IsSelect": false,
    "Customer": null,
    "Tele": null,
    "ExtraCharges": 0.0,
    "DeleteReason": null,
    "UserPunch": "PC-15",
    "UserCash": null,
    "UserDelete": null,
    "KOT": 0,
    "tableStatus": false,
    "OrderTiltId": 46,
    "TimeIn": null,
    "TimeOut": null,
    "Status": false,
    "Od": 0,
    "Itemqty": 0.0,
    "Itemprice": 0.0,
    "OrderKey_Merege": null,
    "DispatchTime": null,
    "OrderStatus": null,
    "PaymentMode": null,
    "isFeedback": false,
    "Feedback": null,
    "DiscountId": null
  }
]
```

### dbo.tempKeys

- Row count: **0**
- Columns: **3**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | orderKey | nvarchar(50) | YES |  |
| 3 | TiltId | int(10,0) | YES |  |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.Theme

- Row count: **0**
- Columns: **3**
- Primary key: id
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | form_name | nvarchar(50) | YES |  |
| 3 | theme_name | nvarchar(50) | YES |  |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.Tilt

- Row count: **18**
- Columns: **9**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | TilitName | nvarchar(50) | YES |  |
| 3 | Serial | nvarchar | YES |  |
| 4 | CounterWiseOrder | bit | YES | ((0)) |
| 5 | ConSolidatedKOT | bit | YES | ((0)) |
| 6 | ItemLessKOT | bit | NO | ((1)) |
| 7 | is_upload | bit | NO | ((0)) |
| 8 | is_update | bit | NO | ((0)) |
| 9 | Is_Update_From_Server | bit | NO | ((0)) |

Sample data (`TOP 3`):

```json
[
  {
    "id": 46,
    "TilitName": "PC-01",
    "Serial": "PC-01",
    "CounterWiseOrder": false,
    "ConSolidatedKOT": false,
    "ItemLessKOT": true,
    "is_upload": false,
    "is_update": true,
    "Is_Update_From_Server": false
  },
  {
    "id": 47,
    "TilitName": "PC-02",
    "Serial": "192.168.1.204",
    "CounterWiseOrder": false,
    "ConSolidatedKOT": false,
    "ItemLessKOT": true,
    "is_upload": false,
    "is_update": true,
    "Is_Update_From_Server": false
  },
  {
    "id": 48,
    "TilitName": "PC-03",
    "Serial": "PC-03",
    "CounterWiseOrder": false,
    "ConSolidatedKOT": false,
    "ItemLessKOT": true,
    "is_upload": false,
    "is_update": true,
    "Is_Update_From_Server": false
  }
]
```

### dbo.TokenNo

- Row count: **1**
- Columns: **1**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | TokenNumber | int(10,0) | NO |  |

Sample data (`TOP 3`):

```json
[
  {
    "TokenNumber": 0
  }
]
```

### dbo.Transfer

- Row count: **0**
- Columns: **7**
- Primary key: TransferId
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | TransferId | int(10,0) | NO |  |
| 2 | Date | datetime | YES |  |
| 3 | TRNo | nvarchar(50) | YES |  |
| 4 | UserId | int(10,0) | YES |  |
| 5 | TotalAmount | decimal(18,2) | YES |  |
| 6 | From | nvarchar(50) | YES |  |
| 7 | To | nvarchar(50) | YES |  |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.TransferInDetail

- Row count: **0**
- Columns: **7**
- Primary key: None
- Outgoing foreign keys: **1**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | Id | int(10,0) | NO |  |
| 2 | TRIId | int(10,0) | YES |  |
| 3 | ItemId | int(10,0) | YES |  |
| 4 | Unit | int(10,0) | YES |  |
| 5 | Qty | decimal(18,2) | YES |  |
| 6 | Rate | decimal(18,2) | YES |  |
| 7 | PackageId | int(10,0) | YES | ((0)) |

Foreign key links:
- `TRIId` -> `dbo.TransferInMaster.TRIId` (FK_TransferInDetail_TransferInMaster)

Sample data (`TOP 3`):

```text
No rows
```

### dbo.TransferInMaster

- Row count: **0**
- Columns: **3**
- Primary key: TRIId
- Outgoing foreign keys: **1**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | TRIId | int(10,0) | NO |  |
| 2 | TransferId | int(10,0) | YES |  |
| 3 | TRInId | int(10,0) | YES |  |

Foreign key links:
- `TransferId` -> `dbo.Transfer.TransferId` (FK_TransferInMaster_Transfer)

Sample data (`TOP 3`):

```text
No rows
```

### dbo.TransferOutDetail

- Row count: **0**
- Columns: **7**
- Primary key: None
- Outgoing foreign keys: **1**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | Id | int(10,0) | NO |  |
| 2 | TRId | int(10,0) | YES |  |
| 3 | ItemId | int(10,0) | YES |  |
| 4 | Unit | int(10,0) | YES | ((0)) |
| 5 | Qty | decimal(18,2) | YES |  |
| 6 | Rate | decimal(18,2) | YES |  |
| 7 | PackageId | int(10,0) | YES | ((0)) |

Foreign key links:
- `TRId` -> `dbo.TransferOutMaster.TRId` (FK_TransferOutDetail_TransferOutMaster)

Sample data (`TOP 3`):

```text
No rows
```

### dbo.TransferOutMaster

- Row count: **0**
- Columns: **3**
- Primary key: TRId
- Outgoing foreign keys: **1**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | TRId | int(10,0) | NO |  |
| 2 | TransferId | int(10,0) | YES |  |
| 3 | TROutId | int(10,0) | YES |  |

Foreign key links:
- `TransferId` -> `dbo.Transfer.TransferId` (FK_TransferOutMaster_Transfer)

Sample data (`TOP 3`):

```text
No rows
```

### dbo.Unit

- Row count: **0**
- Columns: **2**
- Primary key: UId
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | UId | int(10,0) | NO |  |
| 2 | Unit | nvarchar(50) | YES |  |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.UnitConversion

- Row count: **0**
- Columns: **4**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | UnitFrom | nvarchar(50) | YES |  |
| 3 | UnitTo | nvarchar(50) | YES |  |
| 4 | Conversion | decimal(18,2) | YES |  |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.User

- Row count: **1**
- Columns: **4**
- Primary key: None
- Outgoing foreign keys: **1**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | UserId | int(10,0) | NO |  |
| 2 | UserName | nvarchar | YES |  |
| 3 | Password | nvarchar | YES |  |
| 4 | UTId | int(10,0) | YES |  |

Foreign key links:
- `UTId` -> `dbo.UserType.UTId` (FK_User_UserType)

Sample data (`TOP 3`):

```json
[
  {
    "UserId": 10,
    "UserName": "admin",
    "Password": "123",
    "UTId": 7
  }
]
```

### dbo.UserTiltAssign

- Row count: **0**
- Columns: **4**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | UserId | int(10,0) | YES | ((0)) |
| 3 | Tiltid | int(10,0) | YES | ((0)) |
| 4 | WaiterId | int(10,0) | YES | ((0)) |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.UserType

- Row count: **1**
- Columns: **3**
- Primary key: UTId
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | UTId | int(10,0) | NO |  |
| 2 | UserType | nvarchar(50) | YES |  |
| 3 | COId | int(10,0) | YES |  |

Sample data (`TOP 3`):

```json
[
  {
    "UTId": 7,
    "UserType": "Admin",
    "COId": 76
  }
]
```

### dbo.UserTypeAccess

- Row count: **1**
- Columns: **4**
- Primary key: None
- Outgoing foreign keys: **1**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | UserTypeAccessId | int(10,0) | NO |  |
| 2 | Functions | nvarchar(50) | YES |  |
| 3 | UTId | int(10,0) | YES |  |
| 4 | IsActive | bit | YES | ((1)) |

Foreign key links:
- `UTId` -> `dbo.UserType.UTId` (FK_UserTypeAccess_UserType)

Sample data (`TOP 3`):

```json
[
  {
    "UserTypeAccessId": 5,
    "Functions": "All",
    "UTId": 7,
    "IsActive": true
  }
]
```

### dbo.Vendor

- Row count: **0**
- Columns: **10**
- Primary key: VId
- Outgoing foreign keys: **1**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | VId | int(10,0) | NO |  |
| 2 | Vendor | nvarchar(50) | YES |  |
| 3 | Address | nvarchar | YES |  |
| 4 | CellNo | nvarchar(50) | YES |  |
| 5 | COId | int(10,0) | YES |  |
| 6 | OpBalance | decimal(18,2) | YES |  |
| 7 | Fax | nvarchar(50) | YES |  |
| 8 | Email | nvarchar(50) | YES |  |
| 9 | CAId | int(10,0) | YES | ((0)) |
| 10 | PreOp | decimal(18,2) | YES | ((0)) |

Foreign key links:
- `COId` -> `dbo.Company.COId` (FK_Vendor_Company)

Sample data (`TOP 3`):

```text
No rows
```

### dbo.Voucher

- Row count: **1**
- Columns: **3**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | VoucherName | nvarchar(50) | YES |  |
| 3 | Amount | decimal(18,2) | YES |  |

Sample data (`TOP 3`):

```json
[
  {
    "id": 1,
    "VoucherName": "Voucher",
    "Amount": 50.0
  }
]
```

### dbo.VoucherDetail

- Row count: **0**
- Columns: **6**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | Order_key | nvarchar(50) | YES |  |
| 3 | VoucherName | nvarchar(500) | YES |  |
| 4 | VoucherQty | float(53,0) | YES |  |
| 5 | VoucherAmount | decimal(18,2) | YES |  |
| 6 | VoucherSerial | nvarchar | YES |  |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.Waiter

- Row count: **0**
- Columns: **6**
- Primary key: None
- Outgoing foreign keys: **0**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | YES |  |
| 2 | waiter_name | nvarchar(50) | YES |  |
| 3 | Tiltid | int(10,0) | NO | ((0)) |
| 4 | id_ | int(10,0) | NO |  |
| 5 | commission | decimal(18,2) | NO | ((0)) |
| 6 | is_percent | bit | NO | ((0)) |

Sample data (`TOP 3`):

```text
No rows
```

### dbo.WareHouse_Branch

- Row count: **19**
- Columns: **22**
- Primary key: None
- Outgoing foreign keys: **2**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | Date | datetime | YES |  |
| 3 | ItemId | int(10,0) | YES |  |
| 4 | Unit | int(10,0) | YES |  |
| 5 | InvoiceId | int(10,0) | YES | ((0)) |
| 6 | IssId | int(10,0) | YES | ((0)) |
| 7 | TRInId | int(10,0) | YES | ((0)) |
| 8 | TROutId | int(10,0) | YES | ((0)) |
| 9 | InvAdjId | int(10,0) | YES | ((0)) |
| 10 | Qty | decimal(18,4) | NO |  |
| 11 | Rate | decimal(18,2) | YES |  |
| 12 | Type | varchar(50) | YES |  |
| 13 | BRId | int(10,0) | YES |  |
| 14 | IssRTId | int(10,0) | YES | ((0)) |
| 15 | SId | int(10,0) | YES | ((0)) |
| 16 | PDId | int(10,0) | YES | ((0)) |
| 17 | PMId | int(10,0) | YES | ((0)) |
| 18 | Desc | nvarchar(50) | YES |  |
| 19 | DId | int(10,0) | YES | ((0)) |
| 20 | Amount | decimal(18,2) | YES | ((0)) |
| 21 | OpenInvId | int(10,0) | NO | ((0)) |
| 22 | Qty_Pcs | decimal(18,2) | YES | ((0)) |

Foreign key links:
- `BRId` -> `dbo.Branch.BRId` (FK_WareHouse_Branch_Branch)
- `ItemId` -> `dbo.Item.ItemId` (FK_WareHouse_Branch_Item)

Sample data (`TOP 3`):

```text
No rows
```

### dbo.WareHouse_Store

- Row count: **47**
- Columns: **29**
- Primary key: None
- Outgoing foreign keys: **2**

| # | Column | Type | Nullable | Default |
|---:|---|---|---|---|
| 1 | id | int(10,0) | NO |  |
| 2 | Date | datetime | YES |  |
| 3 | ItemId | int(10,0) | YES |  |
| 4 | Unit | int(10,0) | YES | ((0)) |
| 5 | InvoiceId | int(10,0) | YES | ((0)) |
| 6 | BUTId | int(10,0) | YES | ((0)) |
| 7 | IssId | int(10,0) | YES | ((0)) |
| 8 | TRInId | int(10,0) | YES | ((0)) |
| 9 | TROutId | int(10,0) | YES | ((0)) |
| 10 | InvAdjId | int(10,0) | YES | ((0)) |
| 11 | Qty | decimal(18,4) | YES |  |
| 12 | WesQty | decimal(18,4) | YES | ((0)) |
| 13 | Rate | decimal(18,2) | YES |  |
| 14 | Type | nvarchar(50) | YES |  |
| 15 | BUTRId | int(10,0) | YES | ((0)) |
| 16 | SId | int(10,0) | YES |  |
| 17 | PRId | int(10,0) | YES | ((0)) |
| 18 | IssRTId | int(10,0) | YES | ((0)) |
| 19 | BRId | int(10,0) | NO | ((0)) |
| 20 | PDId | int(10,0) | YES | ((0)) |
| 21 | Desc | nvarchar(50) | YES |  |
| 22 | DId | int(10,0) | YES | ((0)) |
| 23 | Amount | decimal(18,2) | YES | ((0)) |
| 24 | OpenInvId | int(10,0) | YES | ((0)) |
| 25 | SLId | int(10,0) | YES | ((0)) |
| 26 | AvgRate | decimal(18,2) | YES |  |
| 27 | AvgRateCalc | int(10,0) | NO | ((0)) |
| 28 | AvgRateMonth | nvarchar(50) | YES |  |
| 29 | Qty_Pcs | decimal(18,2) | YES | ((0)) |

Foreign key links:
- `ItemId` -> `dbo.Item.ItemId` (FK_WareHouse_Store_Item)
- `SId` -> `dbo.Store.SId` (FK_WareHouse_Store_Store)

Sample data (`TOP 3`):

```text
No rows
```
