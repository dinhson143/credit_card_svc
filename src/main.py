from fastapi import FastAPI

from src.apis import credit_card_router
from src.utils.dependencies import container

container.wire(modules=['src.apis.credit_card_router'])

app = FastAPI()
app.include_router(credit_card_router.router)
