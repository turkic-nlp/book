# Chapter 4 corpus inventory

## data/

| File | Content |
|---|---|
| `hplt_v3_turkic.csv` | HPLT v3.0: one row per Turkic language and script variant checked (38 rows: 24 languages, script variants, rus/eng as reference). Manifest fields plus a rough word estimate and the share of bytes in quality bins 8–10. |
| `hplt_v3_turkic_quality_bins.csv` | HPLT v3.0: compressed bytes per Web Docs Scorer bin (5–10) for the 11 Turkic subsets. |
| `hplt_v3_SOURCE.md` | Provenance: manifest URL, SHA-256, access date, extraction method, caveats. |

## First observations (HPLT v3.0, labelled sizes, not audited)

- **Present:** 11 Turkic subsets — tur, azj, azb, tuk, kaz, kir, tat, bak, crh, uzn (Latin only), uig (Arabic only).
- **Absent:** Gagauz, Karakalpak, Nogai, Kumyk, Karachay-Balkar, Sakha, Altai, Tuvan, Khakas, Chuvash, Khalaj, Ottoman and Old Turkic, and the Cyrillic Uzbek, Latin Kazakh, Latin/Cyrillic Uyghur and Cyrillic Crimean Tatar script variants.
- **Sizes span more than three orders of magnitude**, measured in characters:
  - Turkish: 513 billion;
  - North Azerbaijani: 41 billion;
  - Kazakh: 17 billion;
  - Crimean Tatar: 0.3 billion;
  - South Azerbaijani: 0.3 billion.
- **Characters per Gemma 3 token are lowest for the non-Latin scripts:** Uyghur 1.80, Bashkir 2.04, South Azerbaijani 2.20. Latin-script languages are higher: Uzbek 2.79, Turkish 3.42. English is 4.44. This is consistent with the fertility results in §6.1 (@tbl-fertility), here at corpus scale.
- **Uyghur is an outlier in the quality bins.** Only 1.2% of its bytes are in bins 8–10, against 48–72% for every other Turkic subset. Either the Web Docs Scorer is poorly calibrated for Arabic-script Uyghur, or the Uyghur subset really is lower quality. A manual audit would be needed before drawing any conclusion.
