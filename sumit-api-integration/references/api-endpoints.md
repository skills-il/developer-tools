# SUMIT API: full endpoint map

All endpoints are `POST` to `https://api.sumit.co.il<path>` with a JSON body that includes the `Credentials` object. 84 operations across 27 modules. Consult this when you need an operation not covered in the main SKILL.md steps.

## Accounting: Documents
| Path | Purpose |
|------|---------|
| `/accounting/documents/create/` | Create a document (invoice, receipt, quotation, etc.) |
| `/accounting/documents/list/` | List documents by type, number range, or date range |
| `/accounting/documents/getdetails/` | Full detail of one document |
| `/accounting/documents/getpdf/` | Document PDF |
| `/accounting/documents/send/` | Email a document |
| `/accounting/documents/cancel/` | Cancel an existing document |
| `/accounting/documents/movetobooks/` | Finalize a draft (move to books) |
| `/accounting/documents/addexpense/` | Add a supplier expense with a Base64 file |
| `/accounting/documents/getdebt/` | Single customer debt |
| `/accounting/documents/getdebtreport/` | Customers debt report |

## Accounting: Customers
| Path | Purpose |
|------|---------|
| `/accounting/customers/create/` | Create or find a customer (SearchMode) |
| `/accounting/customers/update/` | Update or find a customer |
| `/accounting/customers/createremark/` | Add a remark to a customer |
| `/accounting/customers/getdetailsurl/` | Link to the customer page |

## Accounting: General
| Path | Purpose |
|------|---------|
| `/accounting/general/getvatrate/` | VAT rate by date |
| `/accounting/general/getexchangerate/` | Foreign currency exchange rate |
| `/accounting/general/getnextdocumentnumber/` | Next document number for a type |
| `/accounting/general/setnextdocumentnumber/` | Set the next document number |
| `/accounting/general/verifybankaccount/` | Verify bank account details |
| `/accounting/general/updatesettings/` | Update accounting settings |

## Accounting: Income items
| Path | Purpose |
|------|---------|
| `/accounting/incomeitems/create/` | Create a catalog item (product/service) |
| `/accounting/incomeitems/list/` | List catalog items |

## Books
| Path | Purpose |
|------|---------|
| `/books/transactions/createbatch/` | Create a batch of journal transactions |

## Payments
| Path | Purpose |
|------|---------|
| `/billing/payments/charge/` | Charge a customer and issue an invoice |
| `/billing/payments/multivendorcharge/` | Split charge across vendors (per-item credentials) |
| `/billing/payments/beginredirect/` | Start a hosted payment page (supports IPNURL) |
| `/billing/payments/get/` | Single payment detail |
| `/billing/payments/list/` | List payments |

## Payment methods (saved cards)
| Path | Purpose |
|------|---------|
| `/billing/paymentmethods/setforcustomer/` | Store a payment method (card token) on a customer |
| `/billing/paymentmethods/getforcustomer/` | Get a customer payment method |
| `/billing/paymentmethods/remove/` | Remove a payment method |

## Recurring
| Path | Purpose |
|------|---------|
| `/billing/recurring/charge/` | Charge and create a standing order |
| `/billing/recurring/listforcustomer/` | List a customer recurring items |
| `/billing/recurring/update/` | Update a recurring item |
| `/billing/recurring/cancel/` | Cancel a recurring item |
| `/billing/recurring/updatesettings/` | Recurring billing settings |

## General billing (Upay)
| Path | Purpose |
|------|---------|
| `/billing/generalbilling/openupayterminal/` | Open an instant Upay terminal |
| `/billing/generalbilling/setupaycredentials/` | Link an existing Upay account |

## Credit card terminal: Gateway
| Path | Purpose |
|------|---------|
| `/creditguy/gateway/transaction/` | Direct card transaction (rare; prefer payments/charge) |
| `/creditguy/gateway/gettransaction/` | Existing transaction detail (public key) |
| `/creditguy/gateway/getreferencenumbers/` | Reference numbers for transactions (public key) |
| `/creditguy/gateway/beginredirect/` | Start a redirect transaction |

## Credit card terminal: Vault (tokenization)
| Path | Purpose |
|------|---------|
| `/creditguy/vault/tokenize/` | Permanent token (card number to token) |
| `/creditguy/vault/tokenizesingleuse/` | Single-use token (multipart form) |
| `/creditguy/vault/tokenizesingleusejson/` | Single-use token (JSON) |

## Credit card terminal: Billing (batch)
| Path | Purpose |
|------|---------|
| `/creditguy/billing/load/` | Load batch transactions |
| `/creditguy/billing/process/` | Process the loaded batch (cannot be stopped) |
| `/creditguy/billing/getstatus/` | Batch process status |

## CRM: Data
| Path | Purpose |
|------|---------|
| `/crm/data/createentity/` | Create an entity |
| `/crm/data/updateentity/` | Update an entity (CreateIfMissing optional) |
| `/crm/data/getentity/` | Get an entity |
| `/crm/data/listentities/` | List entities (filters, order, paging, LoadProperties) |
| `/crm/data/archiveentity/` | Archive an entity |
| `/crm/data/deleteentity/` | Delete an entity |
| `/crm/data/countentityusage/` | Count entity usage |
| `/crm/data/getentityprinthtml/` | HTML to print one entity |
| `/crm/data/getentitieshtml/` | HTML to print many entities |

## CRM: Schema and Views
| Path | Purpose |
|------|---------|
| `/crm/schema/getfolder/` | Folder (entity type) schema |
| `/crm/schema/listfolders/` | List folders |
| `/crm/views/listviews/` | List views |

## SMS
| Path | Purpose |
|------|---------|
| `/sms/sms/send/` | Send one SMS |
| `/sms/sms/sendmultiple/` | Send multiple SMS |
| `/sms/sms/listsenders/` | List approved sender names |
| `/sms/mailinglists/add/` | Add a recipient to an SMS list |
| `/sms/mailinglists/list/` | List SMS mailing lists |

## Email subscriptions
| Path | Purpose |
|------|---------|
| `/emailsubscriptions/mailinglists/add/` | Add a recipient to an email list |
| `/emailsubscriptions/mailinglists/list/` | List email mailing lists |

## Triggers (webhooks)
| Path | Purpose |
|------|---------|
| `/triggers/triggers/subscribe/` | Subscribe a webhook URL to a folder and trigger type |
| `/triggers/triggers/unsubscribe/` | Remove a webhook |

## Website (organizations)
| Path | Purpose |
|------|---------|
| `/website/companies/create/` | Create a new organization |
| `/website/companies/update/` | Update organization details |
| `/website/companies/getdetails/` | Organization details |
| `/website/companies/installapplications/` | Install applications |
| `/website/companies/listquotas/` | Usage quotas |
| `/website/users/create/` | Create a user and grant permissions |
| `/website/users/loginredirect/` | Login via redirect without exposing credentials |
| `/website/permissions/set/` | Grant a user permission |
| `/website/permissions/remove/` | Remove a user permission |

## Other modules
| Path | Purpose |
|------|---------|
| `/stock/stock/list/` | List stock levels |
| `/deals/adddeal/` | Create a deal (and optionally a customer) |
| `/deals/createremark/` | Add a remark to a deal |
| `/customerservice/tickets/create/` | Open a support ticket |
| `/fax/fax/send/` | Send an outgoing fax |
| `/scheduleddocuments/documents/createfromdocument/` | Schedule a document from a template document |
