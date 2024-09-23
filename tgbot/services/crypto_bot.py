import aiohttp
import asyncio


class CryptoBot:
    def __init__(self, api_token: str):
        self.token = api_token
        self.base_url = "https://pay.crypt.bot/api"
        self.timeout = aiohttp.ClientTimeout(total=360)
        loop = asyncio.get_event_loop()
        loop.create_task(self.check())

    async def get_me(self):
        async with aiohttp.ClientSession(
            headers={ "Crypto-Pay-API-Token": self.token}, timeout=self.timeout
        ) as session:
            resp = await session.get(f"{self.base_url}/getMe")

            await session.close()
            return await resp.json()

    async def get_balance(self):
        async with aiohttp.ClientSession(
            headers={ "Crypto-Pay-API-Token": self.token }, timeout=self.timeout
        ) as session:
            resp = await session.get(f"{self.base_url}/getBalance")
            await session.close()
            return await resp.json()

    async def check(self):
        result = await self.get_me()

        if not result['ok']:
            raise ConnectionError("Неверный токен [CryptoBot]")

    async def create_bill(self, amount, asset):
        async with aiohttp.ClientSession(
                headers={"Crypto-Pay-API-Token": self.token}, timeout=self.timeout
        ) as session:

            currencies = await session.get(f"{self.base_url}/getExchangeRates")
            cur = await currencies.json()
            await session.close()
            c = cur['result']
            rate = (next((item for item in c if item["source"] == asset and item["target"] == "RUB"), None))['rate']
            amount_crypto = amount / float(rate)

        async with aiohttp.ClientSession(
                headers={"Crypto-Pay-API-Token": self.token}, timeout=self.timeout
        ) as session:

            data = {
                "amount": amount_crypto,
                "asset": asset
            }
            resp = await session.post(f'{self.base_url}/createinvoice', data=data)
            await session.close()
            return await resp.json()

    async def check_bill(self, bill_id):
        async with aiohttp.ClientSession(headers={"Crypto-Pay-API-Token": self.token}, timeout=self.timeout) as session:
            data = {
                "invoice_ids": bill_id,
                "count": 1
            }

            resp = await session.get(f"{self.base_url}/getInvoices", data=data)
            await session.close()
            r = await resp.json()
            if r['result']['items'][0]['status'] == "paid":
                return True
            return False