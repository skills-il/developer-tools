# SUMIT enums: document types, payment types, currencies, search modes

Consult this when choosing a `Type` for `documents/create` or decoding an enum returned by the API. Values may be sent as the string name or the integer in parentheses.

## Document types (`Details.Type`)
| Name | Int | Hebrew |
|------|-----|--------|
| Invoice | 0 | חשבונית עסקה |
| InvoiceAndReceipt | 1 | חשבונית מס/קבלה |
| Receipt | 2 | קבלה |
| ProformaInvoice | 3 | חשבונית פרופורמה |
| DonationReceipt | 4 | קבלה על תרומה |
| CreditInvoice | 5 | חשבונית זיכוי |
| CreditInvoiceAndReceipt | 6 | חשבונית מס/קבלה זיכוי |
| CreditReceipt | 7 | קבלת זיכוי |
| Order | 8 | הזמנה |
| DeliveryNote | 9 | תעודת משלוח |
| GoodsReturnNote | 10 | תעודת החזרה |
| PurchasingOrder | 11 | הזמנת רכש |
| PriceQuotation | 12 | הצעת מחיר |
| PaymentRequest | 13 | דרישת תשלום |
| CreditDonationReceipt | 14 | זיכוי קבלת תרומה |
| ExpenseInvoiceReceipt | 15 | חשבונית/קבלה הוצאה |
| ExpenseInvoice | 16 | חשבונית הוצאה |
| ExpenseReceipt | 17 | קבלת הוצאה |
| ExpenseRequest | 18 | בקשת הוצאה |
| CreditExpenseInvoiceReceipt | 19 | זיכוי חשבונית/קבלה הוצאה |
| CreditExpenseInvoice | 20 | זיכוי חשבונית הוצאה |
| CreditExpenseReceipt | 21 | זיכוי קבלת הוצאה |
| SupplierPayment | 22 | תשלום לספק |

Income document types (0 to 14) are for money coming in. Expense document types (15 to 22) are for money going out.

## Document payment types (`Payments[].Type`)
| Name | Int |
|------|-----|
| Automatic | 0 |
| General | 1 |
| Cash | 2 |
| BankTransfer | 3 |
| Cheque | 4 |
| CreditCard | 5 |
| Digital | 6 |
| TaxWithholding | 7 |
| Other | 8 |

Each `Payments[]` row carries exactly one matching details object: `Details_Cash`, `Details_BankTransfer`, `Details_Cheque`, `Details_CreditCard`, `Details_Digital`, `Details_TaxWithholding`, `Details_General`, or `Details_Other`.

## Saved payment method type (`PaymentMethod.Type`)
| Name | Int |
|------|-----|
| Other | 0 |
| CreditCard | 1 |
| DirectDebit | 2 |

DirectDebit (bank standing order) uses `DirectDebit_Bank`, `DirectDebit_Branch`, `DirectDebit_Account`.

## Customer search mode (`Customer.SearchMode`)
Enables create-or-find (upsert) so you avoid duplicate customers.
| Name | Int | Matches on |
|------|-----|-----------|
| Automatic | 0 | best guess from supplied fields |
| None | 1 | always create new (default) |
| ExternalIdentifier | 2 | your external id |
| Name | 3 | name |
| CompanyNumber | 4 | tax/company number |
| Phone | 5 | phone |
| EmailAddress | 6 | email |

## Response status (`Status`)
| Name | Int | Meaning |
|------|-----|---------|
| Success | 0 | operation succeeded |
| BusinessError | 1 | logical/validation problem, show UserErrorMessage |
| TechnicalError | 2 | system fault, log and retry |

## Currencies (`Currency`)
Common ISO 4217 codes, sent by name: `ILS` (default), `USD`, `EUR`, `GBP`, `AUD`, `CAD`, `CHF`, `JPY`. About 160 currencies are supported. Leave empty to use the company default currency.

## Trigger types (`triggers/subscribe`)
`CreateOrUpdate`, `Create`, `Update`, `Archive`, `Delete`.
