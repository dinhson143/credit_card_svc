from dependency_injector import providers
from dependency_injector.containers import DeclarativeContainer
from src.services.credit_card_service import CreditCardService


class Container(DeclarativeContainer):
    config = providers.Configuration()

    credit_card_service = providers.Singleton(
            CreditCardService
    )


container = Container()
