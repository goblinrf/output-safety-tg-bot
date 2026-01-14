from controller_clients.ControllerClient import ControllerClient

class ProcessingService:
    def __init__(self):
        self.client = ControllerClient()

    async def getMascedAnswer(self, question: str, answer: str) -> str:
        request_id = await self.client.get_request_id(question, answer)
        result = await self.client.get_result(request_id)
        return result["masked_answer"]
