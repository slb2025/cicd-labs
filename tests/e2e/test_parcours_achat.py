"""Tests fonctionnels UI de bout en bout Playwright (Atelier 8)."""

from __future__ import annotations

import re

import pytest
from playwright.sync_api import Locator, Page, expect

pytestmark = pytest.mark.e2e


class ShopPage:
    """Page Object représentant l'interface boutique MiniShop."""

    def __init__(self, page: Page, base_url: str) -> None:
        self.page = page
        self.base_url = base_url

    def open(self) -> ShopPage:
        self.page.goto(self.base_url)
        expect(self.page.get_by_test_id("add-mug")).to_be_visible()
        return self

    def add(self, product_id: str, count: int = 1) -> ShopPage:
        button = self.page.get_by_test_id(f"add-{product_id}")
        for _ in range(count):
            button.click()
        return self

    def apply_coupon(self, code: str) -> ShopPage:
        self.page.get_by_test_id("coupon").fill(code)
        self.page.get_by_role("button", name="Calculer le total").click()
        return self

    def total(self) -> Locator:
        return self.page.get_by_test_id("total")

    def error_alert(self) -> Locator:
        return self.page.get_by_role("alert")

    def order_button(self) -> Locator:
        return self.page.get_by_test_id("order-btn")

    def confirmation(self) -> Locator:
        return self.page.get_by_test_id("confirmation")

    def order(self) -> Locator:
        self.order_button().click()
        return self.confirmation()


@pytest.fixture
def shop(page: Page, app_url: str) -> ShopPage:
    return ShopPage(page, app_url).open()


def test_page_accueil(shop: ShopPage) -> None:
    """Vérifie l'affichage du titre et du catalogue de produits sur la page d'accueil."""
    expect(shop.page).to_have_title(re.compile("MiniShop"))
    expect(shop.page.get_by_test_id("products").locator("li")).to_have_count(5)


def test_parcours_achat_avec_coupon_et_commande(shop: ShopPage) -> None:
    """Vérifie le parcours E2E complet d'ajout au panier, coupon et validation de commande."""
    shop.add("mug", count=2).apply_coupon("WELCOME10")
    expect(shop.total()).to_have_text(re.compile(r"^27\.40?$"))
    shop.order()
    expect(shop.confirmation()).to_be_visible()
    expect(shop.confirmation()).to_have_text(re.compile(r"^Commande .+ confirmée$"))


def test_coupon_invalide_affiche_alerte(shop: ShopPage) -> None:
    """Vérifie l'affichage d'un message d'alerte lors de la saisie d'un coupon invalide."""
    shop.add("mug", count=1).apply_coupon("CODE_INVALIDE")
    expect(shop.error_alert()).to_be_visible()
    expect(shop.error_alert()).not_to_be_empty()


def test_bouton_commander_desactive_si_panier_vide(shop: ShopPage) -> None:
    """Vérifie que le bouton Commander reste désactivé tant que le panier est vide."""
    expect(shop.page.get_by_test_id("cart")).to_contain_text("Votre panier est vide")
    expect(shop.order_button()).to_be_disabled()
