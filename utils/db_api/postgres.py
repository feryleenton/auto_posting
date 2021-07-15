import asyncpg as asyncpg
import asyncio
from data.config import PGUSER, PGPASSWORD, IP


class Database:
    def __init__(self, loop: asyncio.AbstractEventLoop):
        self.pool: asyncio.pool.Pool = loop.run_until_complete(
            asyncpg.create_pool(
                user=PGUSER,
                password=PGPASSWORD,
                host=IP,
            )
        )

    async def get_time_slots_by_schedule(self, schedule):
        sql = "SELECT * FROM time_slot WHERE schedule_id = $1"
        return await self.pool.fetch(sql, schedule)

    async def get_time_slots_by_id(self, id):
        sql = "SELECT * FROM time_slot WHERE id = $1"
        return await self.pool.fetch(sql, id)


db = Database(loop=asyncio.get_event_loop())
