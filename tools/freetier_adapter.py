"""Free-tier adapter for remote execution fallback.

This module provides a lightweight promotion scraper, a local cache, and
fallback free-tier options for environments where local execution is not
practical.
"""

from __future__ import annotations

import json
import socket
import time
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Optional

CACHE_PATH = Path(__file__).resolve().parent / "freetier_promotions_cache.json"

SCRAPE_TARGETS = [
    {
        "provider": "AWS",
        "url": "https://aws.amazon.com/free/",
        "description": "AWS Free Tier page",
        "marker": "always free",
    },
    {
        "provider": "Google Cloud",
        "url": "https://cloud.google.com/free",
        "description": "Google Cloud Free Tier page",
        "marker": "free tier",
    },
    {
        "provider": "Oracle Cloud",
        "url": "https://www.oracle.com/cloud/free/",
        "description": "Oracle Cloud Free Tier page",
        "marker": "always free cloud services",
    },
]


@dataclass
class FreeTierPromotion:
    name: str
    provider: str
    resources: str
    validity: str
    url: str
    notes: str
    scraped: bool = False
    fetched_at: str = ""

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)

    @staticmethod
    def from_dict(data: Dict[str, object]) -> "FreeTierPromotion":
        return FreeTierPromotion(
            name=str(data.get("name", "")),
            provider=str(data.get("provider", "")),
            resources=str(data.get("resources", "")),
            validity=str(data.get("validity", "")),
            url=str(data.get("url", "")),
            notes=str(data.get("notes", "")),
            scraped=bool(data.get("scraped", False)),
            fetched_at=str(data.get("fetched_at", "")),
        )


def _fetch_page_text(url: str, timeout: int = 10) -> Optional[str]:
    try:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (compatible; FreeTierAdapter/1.0)"
            },
        )
        with urllib.request.urlopen(req, timeout=timeout) as response:
            payload = response.read()
            return payload.decode("utf-8", errors="ignore")
    except (urllib.error.URLError, socket.timeout, ValueError):
        return None


def static_free_tier_promotions() -> List[FreeTierPromotion]:
    return [
        FreeTierPromotion(
            name="AWS Free Tier",
            provider="AWS",
            resources="1 vCPU / 1 GiB RAM / 750h EC2 t4g.nano + always-free services",
            validity="ongoing",
            url="https://aws.amazon.com/free/",
            notes="Use a separate AWS account or free tier host for heavy analysis jobs.",
        ),
        FreeTierPromotion(
            name="Google Cloud Free Tier",
            provider="Google Cloud",
            resources="1 vCPU / 0.6 GiB RAM always-free + $300 credit for 90 days",
            validity="ongoing",
            url="https://cloud.google.com/free",
            notes="Google Cloud pode suportar análise em VM remota sem impactar seu PC local.",
        ),
        FreeTierPromotion(
            name="Oracle Cloud Free Tier",
            provider="Oracle Cloud",
            resources="2 VMs com 1 OCPU / 1 GiB RAM cada + 2 block volumes",
            validity="ongoing",
            url="https://www.oracle.com/cloud/free/",
            notes="Oracle oferece sempre-free com recursos razoáveis para carga leve a moderada.",
        ),
        FreeTierPromotion(
            name="Fly.io Free Plan",
            provider="Fly.io",
            resources="256 MiB RAM / 1 shared CPU grátis em apps pequenos",
            validity="ongoing",
            url="https://fly.io/docs/about/pricing/",
            notes="Útil para jobs pequenos ou testes de infraestrutura remota.",
        ),
        FreeTierPromotion(
            name="Railway Free Tier",
            provider="Railway",
            resources="500 MiB RAM / 1 vCPU + créditos gratuitos de boas-vindas",
            validity="ongoing",
            url="https://railway.app/pricing",
            notes="Serviço simples para provas de conceito remotas.",
        ),
    ]


def load_cached_promotions(path: Path = CACHE_PATH) -> List[FreeTierPromotion]:
    if not path.exists():
        return []
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        return [FreeTierPromotion.from_dict(item) for item in raw if isinstance(item, dict)]
    except Exception:
        return []


def save_promotions(promotions: List[FreeTierPromotion], path: Path = CACHE_PATH) -> None:
    payload = [promotion.to_dict() for promotion in promotions]
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def get_cached_promotions(path: Path = CACHE_PATH) -> List[FreeTierPromotion]:
    promotions = load_cached_promotions(path)
    return promotions if promotions else static_free_tier_promotions()


def is_local_host_insufficient(total_memory_bytes: int, cpu_count: int) -> bool:
    """Return True when the local host is unlikely to handle heavy analysis."""
    if total_memory_bytes <= 0 or cpu_count <= 0:
        return True
    if total_memory_bytes < 8 * 1024 ** 3:
        return True
    if cpu_count < 4:
        return True
    return False


def recommend_remote_fallback(
    total_memory_bytes: int,
    cpu_count: int,
    prefer_low_impact: bool = True,
) -> List[FreeTierPromotion]:
    if is_local_host_insufficient(total_memory_bytes, cpu_count):
        return get_cached_promotions()
    if prefer_low_impact and total_memory_bytes < 12 * 1024 ** 3:
        return get_cached_promotions()
    return []


def scrape_free_tier_promotions(timeout: int = 10) -> List[FreeTierPromotion]:
    scraped: List[FreeTierPromotion] = []
    for entry in SCRAPE_TARGETS:
        html = _fetch_page_text(entry["url"], timeout=timeout)
        if html and entry["marker"] in html.lower():
            scraped.append(
                FreeTierPromotion(
                    name=f"{entry['provider']} Free Tier",
                    provider=entry["provider"],
                    resources="Ver site oficial para limites atuais",
                    validity="verificar no site",
                    url=entry["url"],
                    notes=f"Encontrado via scraping de {entry['description']}.",
                    scraped=True,
                    fetched_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                )
            )
    return scraped


def refresh_free_tier_promotions(path: Path = CACHE_PATH, timeout: int = 10) -> List[FreeTierPromotion]:
    promotions = static_free_tier_promotions()
    scraped = scrape_free_tier_promotions(timeout=timeout)
    if scraped:
        promotions = scraped + promotions
    promotions = sorted(
        {p.url: p for p in promotions}.values(), key=lambda item: (item.provider, item.name)
    )
    save_promotions(promotions, path=path)
    return promotions


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="List or refresh free-tier promotion fallback options."
    )
    parser.add_argument("--list", action="store_true", help="List cached free-tier promotions")
    parser.add_argument("--refresh", action="store_true", help="Refresh the promotion cache by scraping official pages")
    parser.add_argument("--cache", type=Path, default=CACHE_PATH, help="Cache file path")
    parser.add_argument("--timeout", type=int, default=10, help="Timeout seconds for scraping")
    args = parser.parse_args()

    if args.refresh:
        promos = refresh_free_tier_promotions(path=args.cache, timeout=args.timeout)
        print(f"Refreshed {len(promos)} free-tier promotions into {args.cache}")
        for promo in promos:
            print(f"- {promo.provider}: {promo.name} ({promo.resources}) -> {promo.url}")
        raise SystemExit(0)

    if args.list:
        promos = get_cached_promotions(path=args.cache)
        print(f"Loaded {len(promos)} free-tier promotions from {args.cache}")
        for promo in promos:
            print(f"- {promo.provider}: {promo.name}")
            print(f"  resources: {promo.resources}")
            print(f"  validity: {promo.validity}")
            print(f"  url: {promo.url}")
            print(f"  notes: {promo.notes}\n")
        raise SystemExit(0)

    print("Use --list ou --refresh")
