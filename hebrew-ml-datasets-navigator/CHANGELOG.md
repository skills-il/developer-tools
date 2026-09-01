# Changelog

## 1.1.0 - 2026-09-02

Licence and gating corrections, verified against the HuggingFace Hub API rather than inferred.

- **Corrected the HebArabNlpProject licence guidance, which was wrong in the permissive direction.** The skill said "generally permissive with CC-BY-4.0 or similar, most are commercial-friendly". The API says `HebrewSentiment` and `HebNLI` declare `license: other` with no name, and `HebSummaries` and `biunlp/HeSum` declare no licence at all. The skill now states the rule plainly: an undeclared or unnamed licence is not a grant, treat it as all rights reserved and ask the depositor. `references/license-quick-guide.md` already said this; the body contradicted its own reference file.
- **Added gating throughout.** Every ivrit.ai dataset is gated (auto-approval) while the models are not, so the model half of a build downloads and the dataset half returns 401 on a machine whose token has not accepted the gate. Acceptance is per HuggingFace account. CulturaX is gated too. None of this was mentioned anywhere.
- **Removed the unverifiable CulturaX "Apache 2.0" claim.** The card is behind the gate and the API declares no licence.
- **Replaced the OSCAR-2301 "access suspended pending legal clarification" claim** with what is observable: gated with manual approval, unmodified since 2025-08-06, approval latency reported as long. The suspension claim had no evidence entry.
- **Stated the actual DictaLM 3.0 licences** instead of sending readers to hunt upstream terms: the 24B and 1.7B families declare `apache-2.0`, only the Nemotron-12B family declares `nvidia-open-model-license`, and all `dictabert*` are `cc-by-4.0`.
- **Fixed two dead IDs.** `pig4431/HeQ_v1` (404) was the primary recommendation in five places including the executable script; replaced with `Etelis/HeQ_v1`. `ivrit-ai/whisper-v2-d3-e3` (404) removed from the model catalog.
- Noted the ODC-BY attribution obligation on FineWeb-2 and MADLAD-400.
- New: `ivrit-ai/VoxKnesset`, and a section distinguishing the two Knesset resources, since ivrit.ai's audio (bespoke licence, gated) and `HaifaCLGroup/KnessetCorpus` (cc-by-sa-4.0, ShareAlike, not gated) carry materially different obligations.
- New Step 6 on Hebrew-specific data hygiene: niqqud, sofit forms, geresh and gershayim, maqaf, subword fertility, and the invisible bidi control characters that silently defeat the de-duplication this skill recommends.
- Corrected the model catalog, which named a CTranslate2 artefact as a fine-tuning starting point. CT2 and GGML are inference-only formats.
- Script: the docstring advertised an `--interactive` mode that does not exist; it still carried the 22,000-hour figure a previous cycle claimed to correct to 20,000; and `--commercial` silently dropped datasets. It now prints the reason for each exclusion and surfaces the gating requirement.
- Added this changelog, which the skill did not have.
- Second review round, all from an independent verification pass: the statement that *every* ivrit.ai dataset is gated was a false universal generalised from one card (4 of 28 are not gated, and the same paragraph already said one of them was ungated); the OSCAR "access suspended" and CulturaX "grants are being processed" claims survived in the English Gotchas after Step 2 was corrected; and the three reference files plus the script were still carrying the pre-correction licence posture, so the reader consulting the file the skill points them at got the old answer. All corrected, and the licence and gating facts now agree across all six surfaces.
- ParaShoot is no longer shown as a loadable HuggingFace id. There is no public repo at `omrikeren/ParaShoot`; the source is GitHub and the loadable mirror is `imvladikon/parashoot`, which declares no licence.
- Corrected the script's unsourced "mostly permissive" for `Helsinki-NLP/opus-100` to the declared `unknown`.
- Extended the undeclared-licence rule to `ivrit-ai/whisper-large-v3-turbo-onnx` and `yi-whisper-large-v3-ct2`, which declare no licence despite the org being permissive by design. An organisation's posture is not a licence on a specific repo.

