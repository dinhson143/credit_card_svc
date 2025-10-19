from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, HTTPException, Depends
from src.schemas.credit_card_request import CreditCardRequest
from src.services.credit_card_service import CreditCardService
from src.utils.dependencies import Container
from src.utils.logging import logger, mask_card
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/credit-card", tags=["Credit Card Service"])


@router.post("/validate")
@inject
async def validate_card(request: CreditCardRequest, service: CreditCardService = Depends(Provide[Container.credit_card_service])):

    try:
        response = service.validate(request.number)
        return response

    except HTTPException as http_ex:
        logger.warning(f"[CreditCardRouter] - {http_ex.detail}")
        raise http_ex

    except Exception as ex:
        masked = mask_card(request.number)
        logger.error(f"[CreditCardRouter] - [CARD_NUMBER: {masked}] - FAILED: {ex}")
        return JSONResponse(status_code=500, content={"message": "Internal server error"})


@router.get("/health")
async def health():
    return {"status": "ok"}
