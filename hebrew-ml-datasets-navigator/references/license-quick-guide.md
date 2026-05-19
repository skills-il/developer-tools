# License Quick Guide for Hebrew ML Resources

Plain-English summary of the most common licenses in the Hebrew ML ecosystem and what they allow for commercial use. Not legal advice.

## Commercial-friendly licenses

### CC-BY-4.0 (Creative Commons Attribution 4.0)

- **Commercial use:** Yes
- **Modification:** Yes
- **Distribution:** Yes
- **Requirements:** Attribute the original creator, indicate if changes were made, link to the license
- **Common uses:** Many Hebrew NLP datasets and academic releases (always check the live dataset card for the exact license string before relying on it)
- **What to do:** Credit the creator in your product documentation or model card

### MIT License

- **Commercial use:** Yes
- **Modification:** Yes
- **Distribution:** Yes
- **Requirements:** Include the original copyright and license text
- **Common uses:** Many open-source code repositories and some datasets
- **What to do:** Keep the LICENSE file with your distribution

### Apache License 2.0

- **Commercial use:** Yes
- **Modification:** Yes
- **Distribution:** Yes
- **Requirements:** Include the license, state changes, preserve notices, grants patent rights
- **Common uses:** Many HuggingFace models and some datasets
- **What to do:** Include a NOTICE file if the upstream distribution has one

### ivrit.ai permissive license

- **Commercial use:** Yes (explicitly, by design)
- **Modification:** Yes
- **Distribution:** Yes (check specific dataset for any restrictions)
- **Requirements:** Check the specific dataset card for attribution and use-case restrictions
- **Common uses:** ivrit.ai Hebrew speech datasets
- **What to do:** Read the dataset card carefully; ivrit.ai explicitly wants commercial use but each dataset may have attribution requirements

## Restricted licenses (not commercial-friendly)

### CC-BY-NC (Creative Commons Attribution-NonCommercial)

- **Commercial use:** NO
- **Modification:** Yes
- **Distribution:** Non-commercial only
- **What to do:** Do NOT use for commercial products. Use only for research or internal non-commercial tooling.

### CC-BY-ND (Attribution-NoDerivatives)

- **Commercial use:** Yes (without modification)
- **Modification:** No
- **Distribution:** Yes (unmodified only)
- **What to do:** Cannot fine-tune or derive modified datasets. Can use the original as-is in commercial products.

### CC-BY-NC-ND (Non-Commercial, No Derivatives)

- **Commercial use:** NO
- **Modification:** NO
- **What to do:** Do NOT use commercially. Do NOT fine-tune.

### GPL v2 / v3

- **Commercial use:** Yes, but your derivative work must also be GPL
- **Modification:** Yes, but strong copyleft
- **What to do:** Avoid unless your product is also GPL-licensed. "Infection" risk for closed-source products.

### AGPL v3

- **Commercial use:** Yes, but stronger than GPL (covers network-based services)
- **What to do:** Even more infectious than GPL for SaaS. Consult legal before use.

### Research-only licenses (often called "Academic Use Only", "Non-Commercial Research", etc.)

- **Commercial use:** NO
- **What to do:** Research and publications only. Some allow internal prototyping; most do not. Read the specific terms.

## Model-specific licenses

### Mistral license (applies to DictaLM-3.0-24B derivatives)

- **Commercial use:** Varies by specific Mistral license variant. DictaLM-3.0-24B adapts Mistral-Small-3.1; check both Mistral's and Dicta's terms.
- **What to do:** Read Mistral AI's current license and Dicta's DictaLM terms together.

### NVIDIA Nemotron license (applies to DictaLM-3.0-Nemotron-12B derivatives)

- **Commercial use:** Check NVIDIA's terms. Nemotron models typically allow commercial use but may have specific conditions.
- **What to do:** Verify both NVIDIA's and Dicta's distributions.

### Qwen license (applies to DictaLM-3.0-1.7B derivatives)

- **Commercial use:** Qwen models generally allow commercial use under Qwen's own license.
- **What to do:** Check Qwen license terms in the model card.

### Anthropic, OpenAI, Google API terms

- These are API services, not open-source models. Commercial use is governed by each provider's terms of service.
- **What to do:** Read the provider's terms of service and any rate limits or usage restrictions before integrating.

## Quick decision tree

1. **Is this for commercial product distribution?**
   - Yes → Only use: CC-BY-4.0, MIT, Apache 2.0, ivrit.ai, permissive Dicta variants (check each)
   - No → Any license that permits your intended use

2. **Am I fine-tuning or modifying?**
   - Yes → Avoid CC-BY-ND or anything with "NoDerivatives"
   - No → ND is acceptable if other terms match

3. **Will my product be closed-source?**
   - Yes → Avoid GPL and AGPL
   - No (GPL product) → GPL is acceptable

4. **Am I using a managed LLM API (OpenAI, Anthropic, etc)?**
   - Yes → Terms of service apply. License concepts above may not apply directly.
   - No (local model) → Open-source license terms apply directly

## When in doubt

- Email the dataset or model owner (HuggingFace has a "Community" tab on most artifacts)
- Consult your legal team for production decisions
- Err on the side of more-restrictive interpretation
- Keep a compliance log: dataset/model ID, license version at time of use, where you obtained it, attribution planned

## Attribution templates

For CC-BY datasets, include attribution in your model card or product docs. Verify the exact license string on the dataset card itself — the HebArabNlpProject/HebrewSentiment card, for example, has shifted between license labels and currently reads "other"; treat the templates below as a structure, not a guarantee of the live license:

```
This product uses the {DatasetName} dataset by {Author}, licensed under {LicenseFromTheDatasetCard}. {DatasetURL}
```

For ivrit.ai, cite the Interspeech 2025 paper:

```
Marmor et al., "Building an Accurate Open-Source Hebrew ASR System through Crowdsourcing",
Proc. Interspeech 2025, pp. 723-727.
```
