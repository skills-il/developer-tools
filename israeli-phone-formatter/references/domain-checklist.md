# Domain checklist: israeli-phone-formatter

What a skill that validates, formats and converts Israeli phone numbers for developers has to cover. Sources: [PLAN] MoC numbering plan, Feb 2023. [ALLOC] MoC allocation dataset, data.gov.il resource caa80822-5880-4bbf-808a-06d7f53c4ae5 (461 records). [DIAL] MoC dialing-plan dataset, data.gov.il resource f5e57cec-4af9-488e-94b5-53f948a3cec3 (330 records). [LPN] libphonenumber PhoneNumberMetadata.xml, territory IL. [META] WhatsApp Cloud API phone-number formats page.

## Must cover (core)

### Number structure
| # | Item | Source |
|---|------|--------|
| M1 | Geographic: `0A-NXX-XXXX`, 9 digits, A in {2,3,4,8,9}, N = 2-9 | PLAN 2.1.2(a) |
| M2 | Mobile: `05R-NXX-XXXX`, 10 digits, N = 2-9; N = 0-1 only for M2M | PLAN 2.1.2(b) |
| M3 | National (non-geographic): `07P-NXX-XXXX`, 10 digits, P = 2-9, N = 2-9 | PLAN 2.1.2(c) |
| M4 | Service-area numbers `1SYZ-WWWWWW`, 10 digits, dialled in full | PLAN 2.1.2(d)(1), 2.2.6 |
| M5 | From abroad: 972 then drop the leading 0, only for geographic, mobile and national numbers | PLAN 2.2.7 |
| M6 | A=6 (06) is reserved and has no numbers | PLAN 2.1.1 |

### Number classes in the official tables (one row each)
| # | Class | Status | Source |
|---|-------|--------|--------|
| C1 | 02 Jerusalem | geographic | ALLOC, PLAN 2.1.1 |
| C2 | 03 Tel Aviv | geographic | ALLOC |
| C3 | 04 Haifa and North | geographic | ALLOC |
| C4 | 08 Shfela and South | geographic | ALLOC |
| C5 | 09 Sharon | geographic | ALLOC |
| C6 | 02-2, 04-2, 08-2, 09-2 | Palestinian operators | ALLOC (Notes: Palestinian Authority) |
| C7 | 050 | Pelephone; 050-1 is M2M | ALLOC |
| C8 | 051 | WeCom Mobile, only 051-2/5/6 | ALLOC |
| C9 | 052 | Cellcom; 052-1 is M2M | ALLOC |
| C10 | 053 | Hot Mobile, 053-2 to 053-9 | ALLOC |
| C11 | 054 | Partner; 054-0 and 054-1 are M2M | ALLOC |
| C12 | 055 | multi-operator sub-blocks; 055-16 to 055-19 are M2M; 055-91 is prepaid only | ALLOC |
| C13 | 056 | whole range Palestinian operators | ALLOC |
| C14 | 057 | unallocated | ALLOC (absent) |
| C15 | 058 | Cellcom 058-3 to 058-7; 058-0 and 058-1 are M2M; 058-2 and 058-8/9 unallocated | ALLOC |
| C16 | 059 | Jawwal (Palestinian), 059-2 to 059-9 | ALLOC |
| C17 | 070, 071, 075, 078 | unallocated (070 and 071 also fall outside P = 2-9) | ALLOC, PLAN |
| C18 | 072 | Partner (072-2/3), 072-800/801 | ALLOC |
| C19 | 073 | Cellcom (073-2/3/7), 073-8xx small operators | ALLOC |
| C20 | 074 | Partner, 074-7 | ALLOC |
| C21 | 076 | Bezeq International 076-5, Bezeq 076-80/81/86/88 | ALLOC |
| C22 | 077 | Hot Telecom, 077-2 to 077-9 | ALLOC |
| C23 | 079 | Widely, Binat, 015, Cellact, Annatel, 019 | ALLOC |
| C24 | NDC 13: `13-0XXXXXXX`, 8 digits after 13 (+972 13 ...) | IoT/M2M only (Partner, Cellcom, Simpracy) | ALLOC |
| C25 | 1-800, 1-801; 1-809 | toll-free; 1-809 for international operators | DIAL |
| C26 | 1-700 | shared cost ("local call, split charging"), NOT premium | DIAL |
| C27 | 1-599 | business call router | DIAL |
| C28 | 1-900, 1-901, 1-902 | premium rate | DIAL |
| C29 | 1-919 | adult services | DIAL |
| C30 | 1-956, 1-957 | voice entertainment / voice information | DIAL |
| C31 | 1-200, 1-212 | televoting / public polls | DIAL |
| C32 | 1-705 | paging | DIAL |
| C33 | 1-255-XXX | essential emergency centres, 7 digits | DIAL, PLAN 2.1.2(d)(3), LPN tollFree |
| C34 | `*XXXX` | star business numbers; 1222 replaces the star on phones without one | PLAN 2.1.2 fn 3, DIAL |
| C35 | 100-106, 110, 112, 115, 118, 119 | emergency short codes (112 is future; 107-109 being cancelled) | DIAL |
| C36 | 1201, 1202, 1207, 1220, 1221, 1111 and others | 4-digit emergency / welfare codes | DIAL |
| C37 | 151 / 153 | number-attached services, 11 to 13 digits per the plan (libphonenumber models 11-12) | PLAN 2.1.2(d)(4), DIAL, LPN voicemail |
| C38 | `00`, `012`-`019`, `0100`-`0109`; `00 000 000` | international access prefixes; affiliation check | DIAL, PLAN 2.1.3 |

### Input normalisation (what real forms and spreadsheets send)
| # | Item | Source |
|---|------|--------|
| N1 | Prefixes `+972`, `00972`, `972` | PLAN 2.2.7 |
| N2 | Extra zero after the country code: `+972 (0)52...`, `+9720...`, `009720...` | LPN (parses these) |
| N3 | Leading zero stripped by Excel (`523456789`, `26251111`); flag scientific notation (`5.23457E+08`) as unrecoverable | LPN (accepts it for region IL) |
| N4 | Invisible direction marks from Hebrew RTL apps (U+200E, U+200F, U+202A-U+202E), NBSP | LPN normalisation |
| N5 | Unicode dashes (U+2010-U+2015, U+2011), slashes, dots, parentheses | LPN |
| N6 | Non-ASCII digits (Arabic-Indic, full-width) | LPN |
| N7 | Surrounding text (`Tel: ...`, `... (mobile)`) and extensions | LPN |
| N8 | Foreign numbers (+1, +44, +970) get their own "non-Israeli" class, not "invalid" | LPN |
| N9 | 7-digit local dialing `NXX-XXXX` inside an area: ask for the area code, do not silently reject | PLAN 2.2.4 |

### Output and semantics
| # | Item | Source |
|---|------|--------|
| O1 | Store E.164: `+972` plus the national number without its 0, digits only | PLAN 2.2.7, LPN |
| O2 | No +972 form for 1-XXX, star and short codes (LPN marks 1700 noInternationalDialling) | PLAN 2.2.6/2.2.7, LPN |
| O3 | Display formats: `0X-XXX-XXXX`, `05X-XXX-XXXX`, `1-800-XXX-XXX` | LPN availableFormats |
| O4 | Say whether "valid" means shape or allocated block, and how that differs from libphonenumber `is_valid_number` (LPN rejects 05X-1 M2M and 058-2) | ALLOC, LPN |
| O5 | MNP: the prefix shows the issuing operator, not the current one | PLAN 2.1.1 note |
| O6 | Person signup rejects or flags M2M (05X-0/1, NDC 13), Palestinian ranges (business rule), and service / short numbers | ALLOC, DIAL |

## Should cover (advanced)
| # | Item | Source |
|---|------|--------|
| S1 | WhatsApp accepts `+`, hyphens, parentheses and spaces. Without the `+` it prepends the business number's country code and can misdeliver | META |
| S2 | Validation is not reachability: confirm with an OTP; only some numbers have WhatsApp | practice |
| S3 | Marketing SMS and WhatsApp to Israelis need prior consent under Communications Law s.30A | statute |
| S4 | Batch mode: choose the column, detect the delimiter (`;` in some Excel locales), dedupe after normalising, write a normalised column for re-import | practice |
| S5 | libphonenumber recipe and where its metadata disagrees with the MoC (071/078 blocks, 1-200/1-212 as premium, 1212 length) | LPN, ALLOC |
| S6 | Refresh by querying the data.gov.il API resource IDs (the dataset HTML pages return 403 to scripts) | ALLOC, DIAL |
| S7 | Prepaid-only block 055-91 | ALLOC |

## Out of scope (explicit)
Reviewed 2026-10-12 (v1.3.0). Each row states why it stays out.
- Live carrier or HLR lookups and MNP database queries.
- Sub-block allocation precision (e.g. 058-2 or 055-0 unassigned): the skill validates the class shape and says so; libphonenumber or the MoC allocation API answer the sub-block question. Users do ask "is this a real number", and the skill tells them how to get that answer.
- C24 NDC 13 IoT numbers: mentioned in the reference, not validated. Device SIMs, not people; no ordinary user of a contact-number validator enters one.
- C32 1-705 paging, C33 1-255-XXX essential centres, C36 4-digit emergency and welfare codes, C37 151 / 153 number-attached services, C38 international access prefixes: rarely typed into forms or contact lists. The script reports them as invalid rather than mislabelling them; revisit if users report it.
- S3 consent for marketing SMS / WhatsApp (Communications Law s.30A): a messaging-compliance question, not a number-format one; route to the marketing and compliance skills.
- S7 prepaid-only block 055-91: no format consequence.
- Non-Israeli numbering plans beyond detecting "not Israeli", including the Palestinian +970 plan.
- Tariffs, billing rates and telecom licensing.
- Integrating message-sending APIs, beyond the number format.

## Authoritative sources
- MoC numbering plan, Feb 2023: https://www.gov.il/BlobFolder/policy/number_policy/en/The_numbering_plan-02-2023.pdf (Hebrew text despite the /en/ path)
- MoC allocations: https://data.gov.il/api/3/action/datastore_search?resource_id=caa80822-5880-4bbf-808a-06d7f53c4ae5&limit=5000
- MoC dialing plan / service numbers: https://data.gov.il/api/3/action/datastore_search?resource_id=f5e57cec-4af9-488e-94b5-53f948a3cec3&limit=5000
- libphonenumber IL metadata: https://raw.githubusercontent.com/google/libphonenumber/master/resources/PhoneNumberMetadata.xml
- WhatsApp Cloud API phone number formats: https://developers.facebook.com/docs/whatsapp/cloud-api/reference/phone-numbers/
