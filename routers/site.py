"""Public website pages (server-rendered Jinja, progressively enhanced by JavaScript).

Pages read the same canonical catalog/branches/policies used by the API and the LLM
planner, so prices and package IDs never diverge between surfaces.
"""
from __future__ import annotations

import json
from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from services import business_ops as ops
from services import business_store as db
from services.conversation_transport import ConversationError

ROOT = Path(__file__).resolve().parents[1]
templates = Jinja2Templates(directory=ROOT / "templates")
router = APIRouter()

SEGMENTS = [
    {"id": "core", "label": "Core health checks", "query": "segment=individual&review=excluded",
     "blurb": "Annual-style packages you can book directly after staff confirmation."},
    {"id": "follow", "label": "Follow-up tests", "query": "segment=individual&review=only",
     "blurb": "Targeted tests that our team reviews with you before booking."},
    {"id": "org", "label": "For organizations", "query": "segment=organization",
     "blurb": "Per-person pricing for teams of 20 or more, at a center or onsite."},
    {"id": "budget", "label": "Under ฿1,000", "query": "max_price=1000&sort=price_asc",
     "blurb": "Smaller checks and single follow-up tests."},
]


def _business() -> dict:
    # Without a transaction, configuration() falls back to the seed files on a hosted
    # runtime that has no database yet, so public pages never fail with a storage error.
    return {"catalog": db.catalog(), "branches": db.branches(), "policies": db.policies()}


def page(request: Request, name: str, title: str, description: str, status: int = 200, **context) -> HTMLResponse:
    return templates.TemplateResponse(request, name, {"title": title, "description": description, "path": request.url.path, **context}, status_code=status)


def _package_json(data) -> str:
    # Embedded as non-executable JSON for progressive enhancement; escape closing tags.
    return json.dumps(data, ensure_ascii=False).replace("</", "<\\/")


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    from services import business_dots
    data = _business()
    packages = [p for p in data["catalog"]["packages"] if p.get("active", True)]
    groups = {
        "core": [p for p in packages if p["segment"] == "individual" and not p.get("staff_review_required")],
        "follow": [p for p in packages if p["segment"] == "individual" and p.get("staff_review_required")],
        "org": [p for p in packages if p["segment"] == "organization"],
        "budget": sorted([p for p in packages if p["price_thb"] < 1000], key=lambda p: p["price_thb"]),
    }
    counts = {k: len(v) for k, v in groups.items()}
    featured = next((p for p in groups["core"] if p["id"] == "P02"), groups["core"][0] if groups["core"] else None)
    return page(request, "site/home.html", "ResultScope | Health checks, explained and booked",
                "Compare health-check packages, ask questions in your own language and request an appointment. Coursework simulation.",
                groups=groups, segments=SEGMENTS, counts=counts, featured=featured, branches=data["branches"]["branches"],
                policies=data["policies"], catalog_version=data["catalog"]["version"], dots=business_dots.public_roster(),
                total=len(packages), source_count=len(json.loads((ROOT / "knowledge/evidence/catalog.json").read_text(encoding="utf-8"))["records"]))


@router.get("/packages", response_class=HTMLResponse)
async def packages(request: Request, q: str = "", segment: str = "", branch_id: str = "", max_price: int | None = None,
                   min_price: int | None = None, review: str = "", sort: str = "featured"):
    if segment not in ("", "individual", "organization"):
        segment = ""
    if review not in ("", "excluded", "only"):
        review = ""
    result = ops.catalog_search(None, q, segment, branch_id, max_price, min_price, review, sort)
    branches = db.branches()["branches"]
    return page(request, "site/packages.html", "Health checks | ResultScope",
                "Search, filter, sort and compare simulated health-check packages.",
                result=result, branches=branches, page_json=_package_json({"result": result, "branches": branches}))


@router.get("/packages/{package_id}", response_class=HTMLResponse)
async def package_detail(request: Request, package_id: str):
    try:
        detail = ops.package_detail(None, package_id)
        related = [p for p in db.catalog()["packages"] if p.get("active", True) and p["id"] != package_id
                   and p["segment"] == detail["package"]["segment"]][:3]
    except ConversationError:
        return page(request, "site/not_found.html", "Health check not found | ResultScope",
                    "This health check is unavailable.", status=404, what="health check")
    return page(request, "site/package_detail.html", f"{detail['package']['name']} | ResultScope",
                f"What {detail['package']['name']} includes, its simulated price and how to request it.",
                detail=detail, p=detail["package"], related=related)


@router.get("/compare", response_class=HTMLResponse)
async def compare(request: Request, ids: str = ""):
    error = ""
    comparison = None
    try:
        comparison = ops.compare(None, [i.strip() for i in ids.split(",")])
    except ConversationError as exc:
        error = exc.message
    return page(request, "site/compare.html", "Compare health checks | ResultScope",
                "Side-by-side comparison of included tests and simulated prices.", comparison=comparison, error=error, ids=ids)


@router.get("/centers", response_class=HTMLResponse)
async def centers(request: Request):
    data = _business()
    import os
    return page(request, "site/centers.html", "Our centers | ResultScope",
                "Three simulated service centers with hours and booking capacity.",
                branches=data["branches"]["branches"], policies=data["policies"], maps_key=bool(os.getenv("GOOGLE_MAPS_EMBED_KEY")))


@router.get("/organizations", response_class=HTMLResponse)
async def organizations(request: Request):
    data = _business()
    org = [p for p in data["catalog"]["packages"] if p["segment"] == "organization" and p.get("active", True)]
    return page(request, "site/organizations.html", "Health checks for organizations | ResultScope",
                "Request a quotation for team health checks at a center or onsite.",
                packages=org, branches=data["branches"]["branches"], policies=data["policies"])


@router.get("/help", response_class=HTMLResponse)
async def help_page(request: Request):
    data = _business()
    return page(request, "site/help.html", "Help and policies | ResultScope",
                "How booking, payments, reports and the assistant work in this coursework simulation.",
                policies=data["policies"], branches=data["branches"]["branches"])


@router.get("/privacy", response_class=HTMLResponse)
async def privacy(request: Request):
    return page(request, "site/privacy.html", "Privacy | ResultScope", "How this coursework simulation handles data.",
                policies=_business()["policies"])


@router.get("/sources", response_class=HTMLResponse)
async def sources(request: Request):
    evidence = json.loads((ROOT / "knowledge/evidence/catalog.json").read_text(encoding="utf-8"))
    records = sorted(evidence["records"], key=lambda r: (r.get("publisher", ""), r.get("title", "")))
    publishers: dict[str, int] = {}
    for r in records:
        publishers[r.get("publisher", "")] = publishers.get(r.get("publisher", ""), 0) + 1
    return page(request, "site/sources.html", "Medical sources | ResultScope",
                "Public references the assistant may cite, with review dates.", records=records, publishers=publishers,
                version=evidence.get("version", ""))


@router.get("/pay/sim/{txn_id}", response_class=HTMLResponse)
async def pay_simulator(request: Request, txn_id: str):
    # Data loads client-side with the session cookie; the page itself holds no transaction data.
    return page(request, "site/pay_sim.html", "Test payment simulator | ResultScope",
                "Simulated payment page. No real money can be paid here.", txn_id=txn_id)
