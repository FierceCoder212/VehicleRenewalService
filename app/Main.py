from fastapi import FastAPI, HTTPException
from Models.QueryPriceRequest import QueryPriceRequest
from Models.CompleteTransactionRequest import CompleteTransactionRequest
from Services.RenewalService import RenewalService
import os
app = FastAPI()
renewal_service_url = os.getenv("RENEWAL_SERVICE_URL")


@app.post('/query/price/tennessee')
async def query_price(request: QueryPriceRequest):
    try:
        renewal_service = RenewalService(request)

        renewal_service.driver.get(renewal_service_url)

        alert_text = renewal_service.search_plate_number()

        if renewal_service.driver.current_url == renewal_service_url:
            raise HTTPException(status_code=400, detail=f"{alert_text}")

        current_page = renewal_service.check_current_page()

        if current_page == "form_page":
            renewal_service.fill_form_page()
            renewal_service.county_selection_element()
        elif current_page == "street_number_page":
            renewal_service.fill_street_number_page()

        fee_summary = renewal_service.collect_form_data()
        if fee_summary:
            return fee_summary
        raise HTTPException(status_code=500, detail="Unable to retrieve fee summary")
    except HTTPException as ex:
        raise HTTPException(status_code=500, detail=ex.detail)
    except Exception as ex:
        raise HTTPException(status_code=500, detail=ex)


@app.post('/complete/tennessee')
async def complete_transaction(request: CompleteTransactionRequest):
    try:
        renewal_service = RenewalService(request)

        renewal_service.driver.get(renewal_service_url)
        alert_text = renewal_service.search_plate_number()

        if renewal_service.driver.current_url == renewal_service_url:
            raise HTTPException(status_code=400, detail=f"{alert_text}")

        current_page = renewal_service.check_current_page()

        if current_page == "form_page":
            renewal_service.fill_form_page()
            renewal_service.county_selection_element()
        elif current_page == "street_number_page":
            renewal_service.fill_street_number_page()
        payment_process = renewal_service.handle_payment_processing()
        if not payment_process:
            raise HTTPException(status_code=400, detail=f"Payment processing failed")
        return payment_process
    except HTTPException as ex:
        raise HTTPException(status_code=400, detail=ex.detail)
    except Exception as ex:
        raise HTTPException(status_code=400, detail=ex)
