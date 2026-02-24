# Developer Tools Skills

AI agent skills for Israeli developer utilities, DevOps, and startup operations.

Part of [Skills IL](https://github.com/skills-il) — curated AI agent skills for Israeli developers.

## Skills

| Skill | Description | Scripts | References |
|-------|-------------|---------|------------|
| [israeli-id-validator](./israeli-id-validator/) | Validate Israeli IDs: Teudat Zehut, company numbers, amuta, partnerships. Check digit algorithm and test ID generation. | `validate_id.py` | 1 |
| [idf-date-converter](./idf-date-converter/) | Hebrew/Gregorian date conversion, Israeli holidays, dual-date formatting, business day calculation. | `convert_date.py` | 1 |
| [israeli-agritech-advisor](./israeli-agritech-advisor/) | Integrate CropX, Netafim GrowSphere, Taranis APIs. Irrigation optimization, crop monitoring, Israeli climate zones. | -- | 1 |
| [jfrog-devops](./jfrog-devops/) | JFrog Artifactory and Xray: repository management, Docker registry, build promotion, security scanning. | `artifactory_client.py`, `xray_client.py` | 1 |
| [cloudinary-assets](./cloudinary-assets/) | Cloudinary media management: upload, transform, optimize, deliver images and videos via REST API. | `upload_asset.py` | 2 |
| [israeli-startup-toolkit](./israeli-startup-toolkit/) | Israeli startup operations: company formation, IIA grants, SAFE/convertible notes, Option 102 ESOP, R&D tax benefits. | -- | 3 |

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
