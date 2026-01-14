import aiohttp
import os
import asyncio
from dotenv import load_dotenv
from typing import Optional


class ControllerClient:
    def __init__(self):
        load_dotenv()
        self.BASE_URL = os.getenv("BASE_URL")

    async def get_request_id(self, question: str, answer: str) -> str:
        url = f"{self.BASE_URL}/check"
        payload = {"question": question, "answer": answer}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as resp:
                data = await resp.json()
                if "request_id" not in data:
                    raise ValueError("Не получен request_id. Ответ:", data)
                return data["request_id"]

    async def get_result(self, request_id: str) -> Optional[dict]:
        url = f"{self.BASE_URL}/result/{request_id}"
        print(f"Wait 2.3s before first attempt: {url}")
        await asyncio.sleep(2)

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print("Response from /result:", request_id, data)
                    return data
                elif resp.status == 404:
                    print(f"[{request_id}] Not ready (404). Waiting 3 more seconds...")
                    await asyncio.sleep(3.0)
                    # Повторный запрос
                    async with session.get(url) as retry_resp:
                        if retry_resp.status == 200:
                            data = await retry_resp.json()
                            print("Response from /result (retry):", request_id, data)
                            return data
                        elif retry_resp.status == 404:
                            print(f"[{request_id}] Still not found after retry.")
                            return None  # или raise ValueError("Result not found after retry")
                        else:
                            text = await retry_resp.text()
                            raise RuntimeError(f"Unexpected status {retry_resp.status}: {text}")
                else:
                    text = await resp.text()
                    raise RuntimeError(f"Unexpected status {resp.status}: {text}")
