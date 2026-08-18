# Developer Tools Skills

AI agent skills for Israeli developer utilities, DevOps, and startup operations.

Part of [Skills IL](https://github.com/skills-il) — curated AI agent skills for Israeli developers.

## Skills

| Skill | Description | Scripts | References |
|-------|-------------|---------|------------|
| [cloudinary-assets](./cloudinary-assets/) | Cloudinary media management: upload, transform, optimize, deliver images and videos via REST API | `upload_asset.py` | `cloudinary-api.md`, `transformations.md` |
| [idf-date-converter](./idf-date-converter/) | Hebrew/Gregorian date conversion, Israeli holidays, dual-date formatting, business day calculation | `convert_date.py` | `hebrew-calendar.md` |
| [israeli-agritech-advisor](./israeli-agritech-advisor/) | Integrate CropX, Netafim GrowSphere, Taranis APIs. Irrigation optimization, crop monitoring, Israeli climate zones | -- | `agritech-apis.md` |
| [israeli-id-validator](./israeli-id-validator/) | Validate Israeli IDs: Teudat Zehut, company numbers, amuta, partnerships. Check digit algorithm and test ID generation | `validate_id.py` | `id-formats.md` |
| [israeli-marketplace-seller](./israeli-marketplace-seller/) | Manage online selling across Israeli marketplaces — Zap, KSP, Facebook Marketplace, and Instagram Shopping | -- | `marketplace-apis.md` |
| [israeli-phone-formatter](./israeli-phone-formatter/) | Validate, format, and convert Israeli phone numbers between local and international (+972) formats | `validate_phone.py` | `phone-prefixes.md` |
| [israeli-shipping-manager](./israeli-shipping-manager/) | Manage shipping across Israeli carriers — Israel Post, Cheetah, HFD, Baldar, Mahir Li, and BOX pickup points | `format_address.py` | `carrier-apis.md`, `pickup-points.md` |
| [israeli-startup-toolkit](./israeli-startup-toolkit/) | Israeli startup operations: company formation, IIA grants, SAFE/convertible notes, Option 102 ESOP, R&D tax benefits | -- | `iia-grants.md`, `option-102.md`, `company-formation.md` |
| [jfrog-devops](./jfrog-devops/) | JFrog Artifactory and Xray: repository management, Docker registry, build promotion, security scanning | `artifactory_client.py`, `xray_client.py` | `jfrog-api.md` |
| [skills-il-skill-creator](./skills-il-skill-creator/) | Interactive workflow for creating new skills for the skills-il organization — scaffolding, frontmatter generation, Hebrew companion, validation | `scaffold-skill.py` | `skill-spec.md` |

## Install

```bash
# Claude Code - install a specific skill
claude install github:skills-il/developer-tools/israeli-id-validator

# Or clone the full repo
git clone https://github.com/skills-il/developer-tools.git
```

## Contributing

See the org-level [Contributing Guide](https://github.com/skills-il/.github/blob/main/CONTRIBUTING.md).

## License

MIT

---

Built with care in Israel.
