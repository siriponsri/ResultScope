from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


DEFAULT_SYSTEM_PROMPT = """You are ResultScope, a laboratory-results education assistant.

MISSION
Help people understand laboratory results in clear language. You may converse in any language the user chooses; preserve the user's language unless they ask for another one. You are not a general-purpose assistant and you are not a clinician.

SCOPE
- Discuss laboratory tests, laboratory panels, specimen-related results, trends, and questions to ask a clinician.
- You may explain common relationships among values when the user provides enough context.
- Do not answer unrelated questions. The application has a deterministic scope gate before this prompt, but still stay within laboratory-result education.

SAFETY AND EVIDENCE DISCIPLINE
- Never diagnose a disease from laboratory values alone.
- Never prescribe, dose, stop, or change medication.
- Treat the laboratory's supplied reference range as authoritative for flagging high/low when provided.
- If a reference range, unit, age, sex, pregnancy status, specimen type, fasting status, or clinical context is needed, say what is missing instead of inventing it.
- Separate observations from possible interpretations. Use cautious language such as 'this pattern may be consistent with...' rather than definitive diagnosis.
- If a result may be urgent or the user reports severe symptoms, tell them to seek prompt professional medical assessment. Do not invent numeric emergency thresholds unless the user supplied a reference/critical range.
- Do not claim that a value is normal merely because it is familiar; use the provided reference range when available.

RESPONSE SHAPE
For multi-value results, prefer this structure:
1. ## Snapshot — one-sentence overview.
2. ## What stands out — concise bullets anchored to the user's exact values.
3. ## How the values connect — relationships/patterns, with uncertainty stated.
4. ## Missing context — only information that materially changes interpretation.
5. ## Questions to take forward — useful questions for a clinician or laboratory.

For a single-test educational question, answer directly and briefly, then mention what context changes interpretation.

STYLE
- Calm, precise, non-alarmist, no hype.
- Do not use emojis unless the user does.
- Prefer short paragraphs and compact bullets.
- Quote the user's values when making a claim so the explanation stays grounded.
- End with a brief reminder that the explanation is educational and not a diagnosis when interpreting personal results.
"""


class Settings(BaseSettings):
    # App / brand
    APP_NAME: str = "ResultScope Laboratory Assistant"
    APP_TAGLINE: str = "Laboratory results, in context."
    OWNER_NAME: str = "Your Name"
    APP_ENV: str = "development"
    # Same-origin UI needs no CORS. Set an explicit comma-separated allowlist
    # only when a separate trusted frontend must call this API.
    CORS_ALLOWED_ORIGINS: str = ""

    # LLM: OpenAI-compatible provider (Typhoon by default)
    LLM_BASE_URL: str = "https://api.opentyphoon.ai/v1"
    LLM_API_KEY: str = ""
    LLM_MODEL: str = "typhoon-v2.5-30b-a3b-instruct"
    LLM_TIMEOUT_SECONDS: float = 60.0
    SYSTEM_PROMPT: str = DEFAULT_SYSTEM_PROMPT

    # Session storage
    # auto = Upstash if credentials exist; otherwise SQLite locally; memory on Vercel.
    STORAGE_BACKEND: str = "auto"
    SQLITE_PATH: str = "data/resultscope.db"
    SESSION_TTL_SECONDS: int = 60 * 60 * 24
    UPSTASH_REDIS_REST_URL: str = ""
    UPSTASH_REDIS_REST_TOKEN: str = ""

    # Product behavior
    MAX_MESSAGE_CHARS: int = 12000
    MAX_HISTORY_MESSAGES: int = 20
    MAX_HISTORY_CHARS: int = 24000
    MAX_HISTORY_MESSAGE_CHARS: int = 4000
    MAX_PROVIDER_OUTPUT_CHARS: int = 5000
    CHAT_RATE_LIMIT_REQUESTS: int = 120
    CHAT_RATE_LIMIT_WINDOW_SECONDS: int = 60
    KNOWLEDGE_MODE: str = "release"
    PUBLIC_REFERENCE_ENABLED: bool = False
    PUBLIC_REFERENCE_ROOT: str = "vendor/resultscope_evidence_v1"
    SESSION_SIGNING_KEY: str = ""

    # Admin Settings is deliberately opt-in and local-demo-only. A cloud
    # deployment must use its platform secret store instead of this file path.
    LOCAL_DEMO_MODE: bool = False
    ADMIN_SETTINGS_PATH: str = "data/admin_settings.json"
    ADMIN_PASSWORD_HASH: str = ""
    ADMIN_SESSION_TTL_SECONDS: int = 1800
    ADMIN_LOGIN_RATE_LIMIT_REQUESTS: int = 5
    ADMIN_LOGIN_RATE_LIMIT_WINDOW_SECONDS: int = 60
    ADMIN_TEST_RATE_LIMIT_REQUESTS: int = 3
    ADMIN_TEST_RATE_LIMIT_WINDOW_SECONDS: int = 300
    ADMIN_SECRET_STORAGE_KEY: str = ""
    SYSTEMONE_SHADOW_ENABLED: bool = False

    # Provider calls are deny-by-default until an owner explicitly enables a
    # persisted attempt cycle. The ledger is local-only in this remediation.
    PROVIDER_NETWORK_ENABLED: bool = False
    PROVIDER_BUDGET_PATH: str = "data/provider_budget.sqlite3"
    PROVIDER_BUDGET_CYCLE_ID: str = ""
    PROVIDER_BUDGET_LLM_LIMIT: int = 5
    PROVIDER_BUDGET_OCR_LIMIT: int = 5
    PROVIDER_BUDGET_SYSTEMONE_LIMIT: int = 5

    # Vision/OCR is opt-in. A text-capable model is never assumed to support images.
    VISION_ENABLED: bool = False
    VISION_BASE_URL: str = "https://api.opentyphoon.ai/v1"
    VISION_API_KEY: str = ""
    VISION_MODEL: str = "typhoon-ocr"
    VISION_TIMEOUT_SECONDS: float = 60.0
    IMAGE_MAX_BYTES: int = 3 * 1024 * 1024
    IMAGE_MAX_PIXELS: int = 12 * 1000 * 1000
    MAX_EXTRACTION_FIELDS: int = 30
    EXTRACTION_TTL_SECONDS: int = 60 * 60 * 24

    # Conversation v2: model-led decisions, bounded tools and guarded answers.
    GUARD_BASE_URL: str = "https://openrouter.ai/api/v1"
    GUARD_API_KEY: str = ""
    GUARD_MODEL: str = "meta-llama/llama-guard-4-12b"
    GUARD_SERVICE_URL: str = ""
    GUARD_SERVICE_TOKEN: str = ""
    GUARD_TIMEOUT_SECONDS: float = 20.0
    # All categories are blocked, including specialized medical advice (S6).
    DEMO_ACCESS_CODE: str = ""
    CONTEXT_TTL_SECONDS: int = 3600
    CLOUD_CALL_LIMIT: int = 200
    LIGHTRAG_URL: str = ""
    LIGHTRAG_API_KEY: str = ""
    LIGHTRAG_ENABLED: bool = False
    # External retrieval may rank only records in our verified local manifest.
    RETRIEVAL_TIMEOUT_SECONDS: float = 12.0
    # MongoDB Atlas Vector Search (Render + Atlas RAG pattern). Atlas ranks record IDs;
    # evidence text still comes from the local verified catalog. Off by default.
    VECTOR_SEARCH_ENABLED: bool = False
    MONGODB_URI: str = ""
    MONGODB_DB: str = "resultscope"
    MONGODB_COLLECTION: str = "evidence_vectors"
    MONGODB_VECTOR_INDEX: str = "evidence_vector_index"
    EMBEDDING_BASE_URL: str = "https://api.openai.com/v1"
    EMBEDDING_API_KEY: str = ""
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    EMBEDDING_DIMENSIONS: int = 1536

    # Project-total THB cost ledger (owner decision 2026-10-06: 300 THB total until
    # coursework submission, not monthly). Fail-closed: unknown prior spend or an
    # unpriced model blocks paid calls. Prices are THB per one million tokens.
    COST_LEDGER_ENABLED: bool = True
    PROJECT_BUDGET_THB: float = 300.0
    PROJECT_BUDGET_PRIOR_SPEND_THB: str = ""
    MODEL_PRICES_THB: str = ""
    COST_IMAGE_TOKEN_ESTIMATE: int = 1500

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
