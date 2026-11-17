"""Tests unitaires des règles de prix."""

from decimal import Decimal

import pytest

from minishop.pricing import coupon_discount, line_total, money, quote, shipping_cost

pytestmark = pytest.mark.unit


# --- 1. Arrondi commercial et détection du bug injectable ---


@pytest.mark.parametrize(
    "valeur, attendu",
    [
        ("0.125", Decimal("0.13")),   # Échoue si MINISHOP_BUG=rounding (ROUND_HALF_EVEN -> 0.12)
        ("0.124", Decimal("0.12")),
        (Decimal("19.995"), Decimal("20.00")),
        (10, Decimal("10.00")),
    ],
)
def test_money_arrondi_commercial(valeur, attendu):
    assert money(valeur) == attendu


# --- 2. Calcul de ligne et remise volume (9 vs 10 unités) ---


def test_line_total_sans_remise():
    assert line_total(Decimal("12.50"), 2) == Decimal("25.00")


@pytest.mark.parametrize(
    "unit_price, qty, attendu",
    [
        (Decimal("10.00"), 1, Decimal("10.00")),
        (Decimal("10.00"), 9, Decimal("90.00")),    # Juste sous le seuil : pas de remise
        (Decimal("10.00"), 10, Decimal("95.00")),   # Seuil exact : -5 %
        (Decimal("2.45"), 10, Decimal("23.28")),    # 24.50 * 0.95 = 23.275 -> arrondi 23.28
        (Decimal("10.00"), 99, Decimal("940.50")),  # Quantité max autorisée : -5 %
    ],
)
def test_line_total_remise_volume_limites(unit_price, qty, attendu):
    assert line_total(unit_price, qty) == attendu


@pytest.mark.parametrize("qty", [0, -1, 100, "2", True, False, 1.5, None])
def test_line_total_quantite_invalide(qty):
    with pytest.raises(ValueError):
        line_total(Decimal("10.00"), qty)


# --- 3. Coupons (WELCOME10, FIXED5, FREESHIP, casse, inconnu) ---


@pytest.mark.parametrize(
    "subtotal, coupon, remise_attendue",
    [
        (Decimal("19.99"), "WELCOME10", Decimal("0.00")),   # Juste sous 20 €
        (Decimal("20.00"), "WELCOME10", Decimal("2.00")),   # Seuil 20 € inclus
        (Decimal("25.50"), " welcome10 ", Decimal("2.55")), # Tolérance casse et espaces
        (Decimal("29.99"), "FIXED5", Decimal("0.00")),      # Juste sous 30 €
        (Decimal("30.00"), "FIXED5", Decimal("5.00")),      # Seuil 30 € inclus
        (Decimal("40.00"), "freeship", Decimal("0.00")),    # Remise monétaire nulle (agit sur port)
        (Decimal("40.00"), None, Decimal("0.00")),
        (Decimal("40.00"), "", Decimal("0.00")),
        (Decimal("20.00"), "STUDENT15", Decimal("3.00")),
    ],
)
def test_coupon_discount_valide(subtotal, coupon, remise_attendue):
    assert coupon_discount(subtotal, coupon) == remise_attendue


@pytest.mark.parametrize("coupon_invalide", ["PROMO50", "WELCOME20", "123"])
def test_coupon_inconnu_leve_value_error(coupon_invalide):
    with pytest.raises(ValueError, match="Coupon inconnu"):
        coupon_discount(Decimal("50.00"), coupon_invalide)


# --- 4. Frais de livraison (49,99 € vs 50,00 € après remise) ---


@pytest.mark.parametrize(
    "amount_after_discount, coupon, empty, port_attendu",
    [
        (Decimal("0.00"), None, True, Decimal("0.00")),           # Panier vide
        (Decimal("49.99"), None, False, Decimal("4.90")),         # Juste sous 50 €
        (Decimal("50.00"), None, False, Decimal("0.00")),         # Seuil 50 € atteint
        (Decimal("15.00"), "FREESHIP", False, Decimal("0.00")),   # Livraison offerte par coupon
    ],
)
def test_shipping_cost_limites(amount_after_discount, coupon, empty, port_attendu):
    assert shipping_cost(amount_after_discount, coupon, empty) == port_attendu


# --- 5. Devis complet (quote) avec les produits réels de catalog.py ---


def test_quote_panier_vide():
    q = quote([])
    assert q.total == Decimal("0.00")
    assert q.shipping == Decimal("0.00")


def test_quote_produit_inconnu():
    with pytest.raises(KeyError):
        quote([{"product_id": "inexistant", "qty": 1}])


def test_quote_seuil_fixed5_sur_book():
    # book coûte 29.99 € : juste sous les 30 € requis pour FIXED5
    q = quote([{"product_id": "book", "qty": 1}], coupon="FIXED5")
    assert q.subtotal == Decimal("29.99")
    assert q.discount == Decimal("0.00")
    assert q.shipping == Decimal("4.90")
    assert q.total == Decimal("34.89")


def test_quote_livraison_facturee_si_total_passe_sous_50_apres_remise():
    # 4 mugs = 50.00 € (livraison offerte sans coupon), mais -10 % WELCOME10 ramène à 45.00 € (< 50 €)
    q = quote([{"product_id": "mug", "qty": 4}], coupon="WELCOME10")
    assert q.subtotal == Decimal("50.00")
    assert q.discount == Decimal("5.00")
    assert q.shipping == Decimal("4.90")
    assert q.total == Decimal("49.90")
    assert q.as_dict()["coupon"] == "WELCOME10"

# --- 6. Coupon STUDENT15 (TDD) ---

def test_student15_sans_minimum_et_sans_remise_volume():
    # 1 mug = 12.50 € (< 20 €, mais STUDENT15 n'a pas de minimum) -> remise 1.88 €
    q = quote([{"product_id": "mug", "qty": 1}], coupon="STUDENT15")
    assert q.discount == Decimal("1.88")


def test_student15_non_cumulable_si_remise_volume():
    # 10 stickers ont déjà -5 % de remise volume -> STUDENT15 ne s'applique pas
    q = quote([{"product_id": "sticker", "qty": 10}], coupon="STUDENT15")
    assert q.discount == Decimal("0.00")


def test_student15_panier_mixte_applique_uniquement_lignes_sans_volume():
    # 2 mugs (25.00 €, éligible STUDENT15 -> 3.75 €) + 10 stickers (remise volume -> exclu)
    q = quote(
        [
            {"product_id": "mug", "qty": 2},
            {"product_id": "sticker", "qty": 10},
        ],
        coupon="STUDENT15",
    )
    assert q.discount == Decimal("3.75")