# src/routes/api_routes.py
from src.services.astro_service import process_question, process_question_with_context
from src.services.kundli import compute_kundli
from src.models.kundli_model import KundliResponse, KundliRequest
from src.models.astro_rag_model import AIRequests, AIResponses
from fastapi import Header, HTTPException, Security, Depends , APIRouter , Form, Body
from config import API_KEY

router = APIRouter()

async def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")


@router.post("/ask/", response_model=AIResponses)
async def astro_rag_endpoint(
    payload: AIRequests,
    x_api_key: str = Depends(verify_api_key)
) -> AIResponses:
    """
    Endpoint for Astro RAG (Retrieval-Augmented Generation) using ChromaDB and optionally MongoDB chat memory.

    This endpoint accepts a user question and optional context, then returns an AI-generated
    answer based on document retrieval and optionally prior chat history.

    ### Request Body:
    - **question** (str, required): The user's question.
    - **context** (str, optional): Any additional context to help answer the question.
    - **rag_with_context** (bool): If `True`, context is used for retrieval as well.
    - **religion** (str, optional): User's religion preference - one of: hindu, christian, muslim, buddhist, jain, sikh, secular. Defaults to "hindu".
   

    ### Behavior:
    - If `rag_with_context` is `True`, both the question and context are used for retrieval.


    ### Headers:
    - **x-api-key** (str, required): API key for authentication.

    ### Returns:
    - **category** (str): AI-inferred category of the question.
    - **answer** (str): AI-generated answer based on retrieved knowledge.
    - **remedy** (str): Suggested action/remedy based on the category.
    - **retrieved_sources** (List[Dict]): Sources used by AI to form the answer.

    ### Example Request:
    ```json
    {
      "question": "How does Mars influence career prospects?",
      "context": "Consider Mars' position in the 10th house and its aspects with Jupiter.",
      "rag_with_context": true,
      "religion": "hindu"
    }
    ```

    ### Example Response:
    ```json
    {
      "category": "Astrology",
      "answer": "Mars in the 10th house can indicate strong ambition and leadership in career.",
      "remedy": "Consider balancing Mars energy with meditation during Mars transits.",
      "retrieved_sources": [
        {"source": "astro_wiki", "page": "Mars_in_10th_house"},
        {"source": "vedic_texts", "verse": "BPHS-10.4"}
      ]
    }
    ```
    """
    try:
        if payload.rag_with_context:
            result = await process_question_with_context(
                question=payload.question,
                context=payload.context,
                religion=payload.religion,
                session_id=payload.session_id,
                use_history=payload.use_history,
            )
        else:
            result = await process_question(
                question=payload.question,
                context=payload.context,
                religion=payload.religion,
                session_id=payload.session_id,
                use_history=payload.use_history,
            )

        return AIResponses(**result)
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"ERROR in astro_rag_endpoint: {str(e)}")
        print(f"Traceback:\n{error_details}")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@router.post("/generate", response_model=KundliResponse)
async def generate_kundli(
   payload: KundliRequest = Body(...), x_api_key: str = Depends(verify_api_key)
):
    """
    Endpoint to generate a Vedic astrology Kundli (birth chart) using Swiss Ephemeris.

    Input Parameters (all sent as form-data):
    - name (str): Full name of the individual.
    - birth_date (str): Date of birth in ISO format (YYYY-MM-DD). Example: "1990-01-01".
    - birth_time (str): Time of birth in 24-hour format (HH:MM). Example: "14:30".
    - place (str): Place of birth (e.g., "Delhi", "Mumbai", or "Delhi, India").
    - gender (str): Gender identity (e.g., "Male", "Female", "Other").
    - x-api-key (header): API key for authorization.

    Processing Logic:
    - Uses `geopy` and `TimezoneFinder` to geolocate the place and determine timezone.
    - Parses the birth date and time into a timezone-aware datetime.
    - Converts to Julian date using Swiss Ephemeris (`swisseph`) for celestial calculations.
    - Calculates planetary positions, houses, ascendant (Lagna), and aspects.
    - Maps planets into zodiac signs and houses.
    - Detects Nakshatras and their respective Padas.

    Output:
    Returns a structured Kundli response containing:
    - Original user input (name, date, time, place, gender)
    - Planetary data (positions, signs, retrograde status, nakshatra, pada, house)
    - House positions with zodiac signs
    - Ascendant and MC (Midheaven)
    - Aspect relationships between planets
    - Julian day and timezone used

    Notes:
    - Accepts both "YYYY-MM-DD" and "DD-MM-YYYY" formats for birth_date.
    - Accepts "HH:MM" or "HH:MM:SS" for time.
    - Automatically retries geolocation if the request times out.
    - Ensure the place string is as accurate as possible for timezone and latitude/longitude lookup.

    Example Request (form-data):
    ----------------------------------
    {
    "name": "Vinay Kumar",
    "birth_date": "1985-05-10",
    "birth_time": "09:45",
    "place": "Bangalore, India",
    "gender": "Male"
        }


    Raises:
    - 400 Bad Request if input is invalid or geolocation fails.

    Security:
    - Requires a valid API key passed in the `x-api-key` header.
    """
    
    try:
        chart = compute_kundli(payload.birth_date, payload.birth_time, payload.place, payload.gender)
        return KundliResponse(
            name=payload.name,
            birth_date=payload.birth_date,
            birth_time=payload.birth_time,
            place=payload.place,
            gender=payload.gender,
            chart=chart
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


