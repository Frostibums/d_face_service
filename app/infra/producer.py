import json

from aiokafka import AIOKafkaProducer


class KafkaProducer:
    def __init__(self, bootstrap_servers: str):
        self._producer = AIOKafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )
        self._service_name = "face-recognition"

    async def start(self):
        await self._producer.start()

    async def stop(self):
        await self._producer.stop()

    async def publish_student_recognized(self, event_id: str, student_id: str):
        message = {
            "event_id": event_id,
            "student_id": student_id,
            # "service_name": self._service_name,
        }
        await self._producer.send_and_wait("student-recognized", message)
