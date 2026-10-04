# Open-access guidelines supplement

Added in response to the owner's instruction to use openly available guidelines with clear references. These are genuine WHO guidelines, not generated sources or a synthetic hospital policy. Access and reuse are subject to the stated **non-commercial** license; they are not unrestricted commercial open data.

## Sources

1. World Health Organization. *Guideline on haemoglobin cutoffs to define anaemia in individuals and populations*. Geneva: WHO; 2024. Published 5 March 2024. ISBN 978-92-4-008854-2. https://www.who.int/publications/i/item/9789240088542
2. World Health Organization. *WHO guideline on use of ferritin concentrations to assess iron status in individuals and populations*. Geneva: WHO; 2020. Published 21 April 2020. ISBN 978-92-4-000012-4. https://www.who.int/publications/i/item/9789240000124

Both original PDFs state **CC BY-NC-SA 3.0 IGO**. The license text is on PDF page 3 for haemoglobin and page 4 for ferritin. https://creativecommons.org/licenses/by-nc-sa/3.0/igo/

## What was indexed

Three brief Thai educational adaptations: haemoglobin context, ferritin context/inflammation, and limits of interpreting high ferritin. Each has original title, year, section, PDF page, printed page, hash and source URL in `data/guidelines/notes.json`. The referenced pages are haemoglobin PDF 30 / printed 9 and ferritin PDF 37 / printed 19. Those pages were read as text and visually checked. Other parts of the full guidelines have not been converted into rules or reviewed in full.

The separate tree is guideline corpus → document → educational summary. `GuidelineCorpus.search` retrieves these summaries by exact known aliases. The preview includes them when no hospital/sex filter is selected. The main application must still apply its scope, citation and output checks. `EvidenceCorpus.context_packet` covers numeric manual records only; use a distinct guideline evidence adapter preserving this supplement's metadata when wiring summaries into an LLM.

No numeric diagnostic threshold, prescription, supplement dose, patient classification, reference interval override or automated guideline applicability rule was added. Neither a PDF download nor a hash establishes clinical approval. Only the selected notes are searchable; do not imply the complete guidelines have been indexed. The editions are identified explicitly; no claim of an exhaustive latest-guideline review is made.

## Adaptation notice and license

The Thai summaries in `data/guidelines/notes.json` are ResultScope coursework adaptations, licensed under CC BY-NC-SA 3.0 IGO. This license statement applies to those adaptations and the separately licensed WHO materials, not to unrelated application source code. Changes: selection, short paraphrase into Thai, source metadata and retrieval structure. WHO has not endorsed ResultScope and its logo is not used as product branding.

This translation was not created by the World Health Organization (WHO). WHO is not responsible for the content or accuracy of this translation. The original English edition shall be the binding and authentic edition.

Use these materials for the local non-commercial coursework/review purpose. Before a commercial product catalog release that reproduces guideline content or PDFs, resolve the license/permission requirements; do not remove the NC restriction or assume that a paid product may use the bundled adaptations unchanged. No commercial permission is claimed here.

Guidelines supplement clinical educational knowledge. They do not supply the selected business's approved service catalog, fees, contacts or policies, and do not close G1-data.
