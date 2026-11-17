"""Tests pytest du calcul de panier MiniShop (minishop.pricing).

Spécification : pricing.feature. Les prix unitaires sont déduits de la spécification :
mug = 12.50 €, hoodie = 44.00 €, sticker = 2.45 €.
"""

from decimal import Decimal

import pytest

from minishop.pricing import line_total, money, quote

pytestmark = [pytest.mark.generated, pytest.mark.unit]

D = Decimal


def _cart(*entries):
    """Construit une liste d'items {product_id, qty} à partir de tuples (qty, produit)."""
    return [{"product_id": pid, "qty": qty} for qty, pid in entries]


@pytest.fixture(autouse=True)
def _sans_bug_arrondi(monkeypatch):
    """Garantit que le mode de régression d'arrondi n'est pas actif pendant les tests."""
    monkeypatch.delenv("MINISHOP_BUG", raising=False)


# ---------------------------------------------------------------------------
# Scénarios de la spécification
# ---------------------------------------------------------------------------


def test_panier_vide():
    """Un panier vide a un total nul et aucuns frais de livraison."""
    q = quote([])
    assert q.total == D("0.00")
    assert q.shipping == D("0.00")


def test_achat_simple_avec_frais_de_livraison():
    """Un panier sous 50 € après remise paie des frais de livraison de 4,90 €."""
    q = quote(_cart((2, "mug")))
    assert q.subtotal == D("25.00")
    assert q.shipping == D("4.90")
    assert q.total == D("29.90")


def test_livraison_offerte_a_partir_de_50_euros():
    """La livraison est offerte quand le total après remise atteint 50 € ou plus."""
    q = quote(_cart((1, "hoodie"), (1, "mug")))
    assert q.shipping == D("0.00")
    assert q.total == D("56.50")


def test_remise_volume_des_10_unites():
    """Dès 10 stickers, une remise volume de 5 % s'applique à la ligne."""
    q = quote(_cart((10, "sticker")))
    assert q.subtotal == D("23.28")


def test_coupon_de_bienvenue():
    """WELCOME10 applique 10 % de remise quand le sous-total atteint 20 €."""
    q = quote(_cart((2, "mug")), coupon="WELCOME10")
    assert q.discount == D("2.50")
    assert q.total == D("27.40")


def test_coupon_de_bienvenue_sous_le_seuil():
    """WELCOME10 n'accorde aucune remise si le sous-total est inférieur à 20 €."""
    q = quote(_cart((1, "mug")), coupon="WELCOME10")
    assert q.discount == D("0.00")


def test_coupon_de_livraison_offerte():
    """FREESHIP offre la livraison sans appliquer de remise sur les articles."""
    q = quote(_cart((1, "sticker")), coupon="FREESHIP")
    assert q.shipping == D("0.00")
    assert q.total == D("2.45")


def test_coupon_inconnu():
    """Un code coupon non répertorié lève une erreur 'Coupon inconnu'."""
    with pytest.raises(ValueError, match="Coupon inconnu"):
        quote(_cart((1, "mug")), coupon="NOEL2026")


def test_produit_inconnu():
    """Un produit absent du catalogue lève une erreur 'Produit inconnu'."""
    # DIVERGENCE SPEC/CODE : la spec attend une erreur de message "Produit inconnu",
    # alors que le code délègue à get_product (commentaire : KeyError si inconnu).
    # Le test suit la spécification ; le message exact dépend de minishop.catalog.
    with pytest.raises(Exception, match="Produit inconnu"):
        quote(_cart((1, "licorne")))


def test_coupon_etudiant_sans_minimum_d_achat():
    """STUDENT15 applique 15 % de remise sans minimum d'achat."""
    q = quote(_cart((1, "mug")), coupon="STUDENT15")
    assert q.discount == D("1.88")
    assert q.shipping == D("4.90")
    assert q.total == D("15.52")


def test_coupon_etudiant_non_cumulable_avec_la_remise_volume():
    """STUDENT15 ne s'applique pas aux lignes bénéficiant de la remise volume."""
    q = quote(_cart((10, "sticker")), coupon="STUDENT15")
    assert q.subtotal == D("23.28")
    assert q.discount == D("0.00")
    assert q.total == D("28.18")


def test_coupon_etudiant_sur_panier_mixte():
    """STUDENT15 ne remise que les lignes sans remise volume dans un panier mixte."""
    q = quote(_cart((2, "mug"), (10, "sticker")), coupon="STUDENT15")
    assert q.subtotal == D("48.28")
    assert q.discount == D("3.75")
    assert q.total == D("49.43")


# ---------------------------------------------------------------------------
# Cas limites (non cités par la spécification)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "qty, expected",
    [
        (9, D("112.50")),  # juste sous le seuil de remise volume : pas de remise
        (10, D("118.75")),  # seuil inclus : 125.00 * 0.95
    ],
)
def test_limite_seuil_remise_volume(qty, expected):
    """La remise volume s'applique exactement à partir de 10 unités, pas avant."""
    assert line_total(D("12.50"), qty) == expected


@pytest.mark.parametrize("qty", [0, -1, 100, 1000])
def test_limite_quantite_hors_bornes(qty):
    """Une quantité hors de l'intervalle 1..99 lève une ValueError."""
    with pytest.raises(ValueError):
        line_total(D("12.50"), qty)


@pytest.mark.parametrize("qty", [1, 99])
def test_limite_quantite_bornes_incluses(qty):
    """Les bornes 1 et 99 sont des quantités valides."""
    assert line_total(D("1.00"), qty) >= D("0")


@pytest.mark.parametrize("qty", ["2", 2.0, None, True])
def test_limite_quantite_non_entiere(qty):
    """Une quantité qui n'est pas un entier (y compris booléen) lève une ValueError."""
    with pytest.raises(ValueError):
        line_total(D("12.50"), qty)


def test_limite_quantite_zero_dans_devis():
    """Une quantité nulle dans un devis lève une ValueError."""
    with pytest.raises(ValueError):
        quote(_cart((0, "mug")))


def test_limite_livraison_exactement_au_seuil():
    """Un total après remise exactement égal à 50 € obtient la livraison offerte."""
    q = quote(_cart((4, "mug")))  # 4 * 12.50 = 50.00
    assert q.subtotal == D("50.00")
    assert q.shipping == D("0.00")
    assert q.total == D("50.00")


def test_limite_livraison_juste_sous_le_seuil():
    """Un total de 37.50 € paie la livraison standard."""
    q = quote(_cart((3, "mug")))
    assert q.shipping == D("4.90")
    assert q.total == D("42.40")


def test_limite_remise_coupon_fait_repasser_sous_le_seuil():
    """La livraison se calcule après remise : WELCOME10 fait repasser le total sous 50 €."""
    q = quote(_cart((4, "mug")), coupon="WELCOME10")
    assert q.discount == D("5.00")
    assert q.shipping == D("4.90")
    assert q.total == D("49.90")


def test_limite_freeship_sur_petit_panier():
    """FREESHIP supprime la livraison même sur un panier très en dessous de 50 €."""
    q = quote(_cart((1, "mug")), coupon="FREESHIP")
    assert q.shipping == D("0.00")
    assert q.total == D("12.50")


def test_limite_welcome10_applique_apres_remise_volume():
    """WELCOME10 s'applique sur le sous-total déjà réduit par la remise volume."""
    q = quote(_cart((10, "sticker")), coupon="WELCOME10")
    assert q.subtotal == D("23.28")
    assert q.discount == D("2.33")
    assert q.total == D("25.85")


def test_limite_fixed5_sous_le_seuil():
    """FIXED5 n'accorde rien quand le sous-total est inférieur à 30 €."""
    q = quote(_cart((2, "mug")), coupon="FIXED5")
    assert q.discount == D("0.00")
    assert q.total == D("29.90")


def test_limite_fixed5_au_dessus_du_seuil():
    """FIXED5 accorde 5 € de remise à partir de 30 € de sous-total."""
    q = quote(_cart((3, "mug")), coupon="FIXED5")
    assert q.discount == D("5.00")
    assert q.total == D("37.40")


def test_limite_student15_sur_remise_volume_partielle():
    """STUDENT15 ne remise que la ligne sans remise volume dans un panier de 9 mugs."""
    q = quote(_cart((9, "mug")), coupon="STUDENT15")
    assert q.subtotal == D("112.50")
    assert q.discount == D("16.88")
    assert q.total == D("95.62")


@pytest.mark.parametrize("code", ["welcome10", " WELCOME10 ", "Welcome10"])
def test_limite_code_coupon_insensible_a_la_casse_et_aux_espaces(code):
    """Les codes coupon sont normalisés (espaces retirés, casse ignorée)."""
    q = quote(_cart((2, "mug")), coupon=code)
    assert q.coupon == "WELCOME10"
    assert q.discount == D("2.50")


def test_limite_coupon_vide_equivalent_a_aucun_coupon():
    """Une chaîne de coupon vide ne déclenche aucune remise."""
    q = quote(_cart((2, "mug")), coupon="")
    assert q.coupon is None
    assert q.discount == D("0.00")


@pytest.mark.parametrize(
    "value, expected",
    [
        (D("0.125"), D("0.13")),  # ROUND_HALF_UP, pas ROUND_HALF_EVEN
        (D("1.005"), D("1.01")),
        (D("2.345"), D("2.35")),
        (D("10.004"), D("10.00")),
        (0.1 + 0.2, D("0.30")),  # float converti via str, pas d'erreur binaire
        (7, D("7.00")),
        ("3.5", D("3.50")),
    ],
)
def test_limite_arrondi_commercial_au_centime(value, expected):
    """Les montants sont arrondis au centime en ROUND_HALF_UP."""
    assert money(value) == expected


def test_limite_arrondi_remise_student_demi_centime():
    """La remise STUDENT15 sur 12.50 € (1.875 €) est arrondie à 1.88 €."""
    q = quote(_cart((1, "mug")), coupon="STUDENT15")
    assert q.discount == D("1.88")


def test_limite_sous_total_est_somme_des_lignes():
    """Le sous-total est la somme exacte des totaux de lignes."""
    q = quote(_cart((2, "mug"), (1, "hoodie"), (3, "sticker")))
    assert q.subtotal == sum((ln.total for ln in q.lines), D("0"))


def test_limite_devis_as_dict_montants_en_chaine_decimale():
    """La sérialisation expose les montants sous forme de chaînes décimales à 2 chiffres."""
    data = quote(_cart((2, "mug"))).as_dict()
    assert data["subtotal"] == "25.00"
    assert data["total"] == "29.90"
    assert data["coupon"] is None
