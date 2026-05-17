"""Google Play app configuration for Ethiopian bank mobile apps."""

from dataclasses import dataclass


@dataclass(frozen=True)
class BankApp:
    bank: str
    app_id: str
    display_name: str


BANK_APPS: tuple[BankApp, ...] = (
    BankApp(
        bank="CBE",
        app_id="com.combanketh.mobilebanking",
        display_name="Commercial Bank of Ethiopia",
    ),
    BankApp(
        bank="BOA",
        app_id="com.boa.boaMobileBanking",
        display_name="BoA Mobile",
    ),
    BankApp(
        bank="Dashen",
        app_id="com.dashen.dashensuperapp",
        display_name="Dashen Bank",
    ),
)

MIN_REVIEWS_PER_BANK = 400
SOURCE_LABEL = "Google Play"
