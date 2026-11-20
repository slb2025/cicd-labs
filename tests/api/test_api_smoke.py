"""Tests d'API MiniShop — Parties A & B (Atelier 9)."""

from __future__ import annotations

import os

import httpx
import pytest

pytestmark = pytest.mark.api


def test_health(client) -> None:
    """Vérifie que l'endpoint /health répond 200 avec le statut ok."""
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_liste_produits(client) -> None:
    """Vérifie que GET /products retourne le catalogue complet des produits."""
    r = client.get("/products")
    assert r.status_code == 200
    assert {"mug", "tshirt"} <= {p["id"] for p in r.json()}


def test_produit_par_id_200(client) -> None:
    """Vérifie que GET /products/{id} retourne le détail d'un produit existant."""
    r = client.get("/products/mug")
    assert r.status_code == 200
    body = r.json()
    assert body["id"] == "mug"
    assert isinstance(body["name"], str)
    assert isinstance(body["price"], str)
    assert isinstance(body["stock"], int)


def test_produit_inconnu_404(client) -> None:
    """Vérifie que GET /products/{id} retourne 404 pour un identifiant inconnu."""
    r = client.get("/products/produit-inexistant")
    assert r.status_code == 404


def test_cart_quote_200_avec_coupon(client) -> None:
    """Vérifie le calcul de devis via POST /cart/quote avec application d'un coupon valide."""
    payload = {"items": [{"product_id": "mug", "qty": 2}], "coupon": "WELCOME10"}
    r = client.post("/cart/quote", json=payload)
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == "27.40"
    for field in ("subtotal", "discount", "shipping", "total"):
        assert isinstance(body[field], str)


def test_cart_quote_produit_inconnu_404(client) -> None:
    """Vérifie que POST /cart/quote retourne 404 si un produit du panier est inconnu."""
    payload = {"items": [{"product_id": "inconnu", "qty": 1}]}
    r = client.post("/cart/quote", json=payload)
    assert r.status_code == 404


@pytest.mark.parametrize(
    "payload",
    [
        pytest.param({"items": [{"product_id": "mug", "qty": 0}]}, id="qty-zero"),
        pytest.param({"items": [{"product_id": "mug", "qty": 100}]}, id="qty-100"),
        pytest.param({"items": [{"product_id": "mug", "qty": 1}], "coupon": "INVALID99"}, id="coupon-inconnu"),
        pytest.param({"items": "corps-invalide"}, id="corps-invalide"),
    ],
)
def test_cart_quote_erreurs_validation_422(client, payload: dict) -> None:
    """Vérifie que POST /cart/quote rejette les charges utiles invalides avec 422."""
    r = client.post("/cart/quote", json=payload)
    assert r.status_code == 422


def test_creation_et_lecture_commande_201_puis_200(client) -> None:
    """Vérifie la création d'une commande (201) puis sa consultation par identifiant (200)."""
    payload = {"items": [{"product_id": "mug", "qty": 2}], "coupon": "WELCOME10"}
    created = client.post("/orders", json=payload)
    assert created.status_code == 201
    order = created.json()
    assert "id" in order and isinstance(order["id"], str)
    assert order["total"] == "27.40"

    fetched = client.get(f"/orders/{order['id']}")
    assert fetched.status_code == 200
    assert fetched.json() == order


def test_commande_inconnue_404(client) -> None:
    """Vérifie que GET /orders/{id} retourne 404 pour une commande inexistante."""
    r = client.get("/orders/000000000000")
    assert r.status_code == 404


def test_creation_commande_panier_vide_422(client) -> None:
    """Vérifie que POST /orders refuse la création d'une commande sur panier vide (422)."""
    r = client.post("/orders", json={"items": []})
    assert r.status_code == 422


def test_metrics_expose_compteur_http(client) -> None:
    """Vérifie que l'endpoint /metrics expose les compteurs Prometheus des requêtes HTTP."""
    client.get("/health")
    r = client.get("/metrics")
    assert r.status_code == 200
    assert "minishop_http_requests_total" in r.text


def test_contrat_openapi_routes_et_types(client) -> None:
    """Vérifie la conformité des routes et schémas exposés dans /openapi.json."""
    spec = client.get("/openapi.json").json()
    paths = spec["paths"]

    expected_routes = {
        "/health": {"get"},
        "/products": {"get"},
        "/products/{product_id}": {"get"},
        "/cart/quote": {"post"},
        "/orders": {"post"},
        "/orders/{order_id}": {"get"},
    }
    for route, methods in expected_routes.items():
        assert route in paths, f"Route publique manquante dans OpenAPI : {route}"
        assert methods <= set(paths[route].keys()), f"Méthode manquante sur {route}"

    schemas = spec["components"]["schemas"]
    item_props = schemas["Item"]["properties"]
    assert item_props["product_id"]["type"] == "string"
    assert item_props["qty"]["type"] == "integer"

    product_body = client.get("/products/mug").json()
    expected_product_types = {"id": str, "name": str, "price": str, "stock": int}
    for key, expected_type in expected_product_types.items():
        assert key in product_body
        assert isinstance(product_body[key], expected_type)

    quote_body = client.post(
        "/cart/quote", json={"items": [{"product_id": "mug", "qty": 1}]}
    ).json()
    for key in ("subtotal", "discount", "shipping", "total"):
        assert key in quote_body
        assert isinstance(quote_body[key], str)


@pytest.mark.skipif(
    not os.getenv("LIVE_API_URL"),
    reason="Définir LIVE_API_URL=http://localhost:8000 pour exécuter la variante serveur réel",
)
def test_variante_serveur_reel_httpx() -> None:
    """Vérifie le fonctionnement de l'API contre une instance serveur réelle via HTTPX."""
    base_url = os.environ["LIVE_API_URL"]
    with httpx.Client(base_url=base_url, timeout=5.0) as live_client:
        r = live_client.post(
            "/cart/quote",
            json={"items": [{"product_id": "mug", "qty": 2}], "coupon": "WELCOME10"},
        )
        assert r.status_code == 200
        assert r.json()["total"] == "27.40"
