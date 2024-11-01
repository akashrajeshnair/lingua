from fastapi import APIRouter
from app.models.prompt import Prompt
from app.services.llm_service import get_llm_response

router = APIRouter()

@router.post('/prompt')
async def send_prompt(prompt: Prompt):
    response = await get_llm_response(prompt.text)
    return {
        'response': response
    }