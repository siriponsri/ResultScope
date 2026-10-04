# Product refresh v2 archive

This directory preserves exact source records from the one-time product-refresh
delivery contract. `LOCAL_CLOSEOUT.md` is the historical integration procedure;
it described the earlier c9236f5 package and must not be used as the current
workflow. The files under `scripts/` and `tests/` are historical source records,
not runnable commands at their relocated paths. Their root calculations and
original payload paths intentionally refer to the old repository layout.

For deliberate reproduction, inspect the historical Git revision recorded by the
corresponding report and use an isolated checkout. Current maintenance uses the
root `scripts/` commands and current documentation instead. The retained files
are not a second active cleanup or release contract.
