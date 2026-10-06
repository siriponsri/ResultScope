# Legacy rulebook status

The deterministic rulebook belongs to the retained local v1 API. It is not the v2 conversation controller. Current code uses only conservative comparisons against a confirmed report interval in services/lab_fields_v2.py; no hardcoded clinical thresholds drive answers. See engineering/ARCHITECTURE.md. The original rulebook is preserved under archive/pre-llm-v2/.
