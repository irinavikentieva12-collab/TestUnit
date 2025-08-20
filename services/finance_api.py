import aiohttp
import json
from typing import Dict, List, Optional, Any
from config import settings


class FinanceAPIService:
    def __init__(self):
        self.coingecko_session = None
        self.alpha_vantage_session = None
    
    async def _get_coingecko_session(self) -> aiohttp.ClientSession:
        if self.coingecko_session is None or self.coingecko_session.closed:
            self.coingecko_session = aiohttp.ClientSession()
        return self.coingecko_session
    
    async def _get_alpha_vantage_session(self) -> aiohttp.ClientSession:
        """Получение сессии для Alpha Vantage API"""
        if self.alpha_vantage_session is None or self.alpha_vantage_session.closed:
            self.alpha_vantage_session = aiohttp.ClientSession()
        return self.alpha_vantage_session
    
    async def close_sessions(self):
        """Закрытие всех сессий"""
        if self.coingecko_session and not self.coingecko_session.closed:
            await self.coingecko_session.close()
        if self.alpha_vantage_session and not self.alpha_vantage_session.closed:
            await self.alpha_vantage_session.close()
    
    async def get_crypto_price(self, coin_id: str, currency: str = "usd") -> Optional[Dict[str, Any]]:
        try:
            session = await self._get_coingecko_session()
            url = f"{settings.coingecko_api_url}/simple/price"
            params = {
                "ids": coin_id,
                "vs_currencies": currency,
                "include_24hr_change": "true",
                "include_market_cap": "true"
            }
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if coin_id in data:
                        coin_data = data[coin_id]
                        return {
                            "symbol": coin_id.upper(),
                            "price": coin_data.get(currency, 0),
                            "change_24h": coin_data.get(f"{currency}_24h_change", 0),
                            "market_cap": coin_data.get(f"{currency}_market_cap", 0),
                            "currency": currency.upper()
                        }
                return None
        except Exception as e:
            print(f"Error getting crypto price: {e}")
            return None
    
    async def get_crypto_info(self, coin_id: str) -> Optional[Dict[str, Any]]:
        """Получение информации о криптовалюте"""
        try:
            session = await self._get_coingecko_session()
            url = f"{settings.coingecko_api_url}/coins/{coin_id}"
            params = {
                "localization": "false",
                "tickers": "false",
                "market_data": "true",
                "community_data": "false",
                "developer_data": "false"
            }
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "id": data.get("id"),
                        "name": data.get("name"),
                        "symbol": data.get("symbol", "").upper(),
                        "current_price": data.get("market_data", {}).get("current_price", {}).get("usd", 0),
                        "market_cap": data.get("market_data", {}).get("market_cap", {}).get("usd", 0),
                        "volume_24h": data.get("market_data", {}).get("total_volume", {}).get("usd", 0),
                        "price_change_24h": data.get("market_data", {}).get("price_change_24h", 0),
                        "price_change_percentage_24h": data.get("market_data", {}).get("price_change_percentage_24h", 0),
                        "description": data.get("description", {}).get("en", "")[:500] + "..." if data.get("description", {}).get("en") else "Описание недоступно"
                    }
                return None
        except Exception as e:
            print(f"Error getting crypto info: {e}")
            return None
    
    async def get_trending_cryptos(self) -> List[Dict[str, Any]]:
        """Получение трендовых криптовалют"""
        try:
            session = await self._get_coingecko_session()
            url = f"{settings.coingecko_api_url}/search/trending"
            
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    trending = []
                    for coin in data.get("coins", [])[:10]:
                        coin_data = coin.get("item", {})
                        trending.append({
                            "id": coin_data.get("id"),
                            "name": coin_data.get("name"),
                            "symbol": coin_data.get("symbol", "").upper(),
                            "market_cap_rank": coin_data.get("market_cap_rank"),
                            "price_btc": coin_data.get("price_btc", 0)
                        })
                    return trending
                return []
        except Exception as e:
            print(f"Error getting trending cryptos: {e}")
            return []
    
    async def get_stock_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Получение цены акции через Alpha Vantage API"""
        if not settings.alpha_vantage_api_key:
            return None
        
        try:
            session = await self._get_alpha_vantage_session()
            url = settings.alpha_vantage_api_url
            params = {
                "function": "GLOBAL_QUOTE",
                "symbol": symbol.upper(),
                "apikey": settings.alpha_vantage_api_key
            }
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    quote = data.get("Global Quote", {})
                    if quote:
                        return {
                            "symbol": quote.get("01. symbol"),
                            "price": float(quote.get("05. price", 0)),
                            "change": float(quote.get("09. change", 0)),
                            "change_percent": quote.get("10. change percent", "0%"),
                            "volume": quote.get("06. volume", "0"),
                            "market_cap": quote.get("07. market cap", "0")
                        }
                return None
        except Exception as e:
            print(f"Error getting stock price: {e}")
            return None
    
    async def search_crypto(self, query: str) -> List[Dict[str, Any]]:
        """Поиск криптовалюты по названию"""
        try:
            session = await self._get_coingecko_session()
            url = f"{settings.coingecko_api_url}/search"
            params = {"query": query}
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    coins = []
                    for coin in data.get("coins", [])[:5]:
                        coins.append({
                            "id": coin.get("id"),
                            "name": coin.get("name"),
                            "symbol": coin.get("symbol", "").upper(),
                            "market_cap_rank": coin.get("market_cap_rank")
                        })
                    return coins
                return []
        except Exception as e:
            print(f"Error searching crypto: {e}")
            return []
    
    async def get_market_summary(self) -> Dict[str, Any]:
        """Получение сводки рынка"""
        try:
            session = await self._get_coingecko_session()
            url = f"{settings.coingecko_api_url}/global"
            
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    global_data = data.get("data", {})
                    return {
                        "total_market_cap": global_data.get("total_market_cap", {}).get("usd", 0),
                        "total_volume": global_data.get("total_volume", {}).get("usd", 0),
                        "market_cap_percentage": global_data.get("market_cap_percentage", {}),
                        "active_cryptocurrencies": global_data.get("active_cryptocurrencies", 0),
                        "market_cap_change_24h": global_data.get("market_cap_change_percentage_24h_usd", 0)
                    }
                return {}
        except Exception as e:
            print(f"Error getting market summary: {e}")
            return {}


# Глобальный экземпляр сервиса
finance_api = FinanceAPIService()
