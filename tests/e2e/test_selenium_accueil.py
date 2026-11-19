"""Test UI comparatif avec Selenium WebDriver (Atelier 8 — Partie B)."""

from __future__ import annotations

import os

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

pytestmark = pytest.mark.e2e


def test_selenium_titre_et_ajout_produit() -> None:
    base_url = os.getenv("BASE_URL", "http://127.0.0.1:8000")
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)
    try:
        driver.get(base_url)
        assert "MiniShop" in driver.title

        wait = WebDriverWait(driver, 10)
        add_btn = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid=\"add-mug\"]"))
        )
        add_btn.click()

        cart_item = wait.until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "[data-testid=\"cart-mug\"]"))
        )
        assert "1" in cart_item.text
    finally:
        driver.quit()
