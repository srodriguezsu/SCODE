import logging
import httpx
from api.config import DATA_API_BASE_URL

logger = logging.getLogger(__name__)

async def fetch_project(project_id: int, auth_header: str) -> dict:
    url = f"{DATA_API_BASE_URL}/projects/{project_id}"
    logger.info(f"Fetching project details from {url}")
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers={"Authorization": auth_header})
        response.raise_for_status()
        return response.json()

async def fetch_employees(auth_header: str) -> list:
    url = f"{DATA_API_BASE_URL}/employees/"
    logger.info(f"Fetching employees from {url}")
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers={"Authorization": auth_header})
        response.raise_for_status()
        return response.json()

async def fetch_skills_factors(skill_id: int, auth_header: str) -> list:
    url = f"{DATA_API_BASE_URL}/skills/{skill_id}/factors"
    logger.info(f"Fetching factors for skill {skill_id} from {url}")
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers={"Authorization": auth_header})
        response.raise_for_status()
        return response.json()

async def create_team(project_id: int, predicted_cohesion_index: float, employee_ids: list, auth_header: str) -> dict:
    url = f"{DATA_API_BASE_URL}/teams/"
    logger.info(f"Posting new team recommendation to {url}")
    async with httpx.AsyncClient() as client:
        response = await client.post(
            url,
            json={
                "project_id": project_id,
                "predicted_cohesion_index": predicted_cohesion_index,
                "employee_ids": employee_ids
            },
            headers={"Authorization": auth_header}
        )
        if response.status_code >= 400:
            try:
                err_data = response.json()
                detail = err_data.get("detail", response.text)
            except Exception:
                detail = response.text
            logger.error(f"Failed to post team to {url}. Status: {response.status_code}, Detail: {detail}")
            raise httpx.HTTPStatusError(
                f"Client error '{response.status_code} {response.reason_phrase}' for url '{url}'. Message: {detail}",
                request=response.request,
                response=response
            )
        return response.json()
