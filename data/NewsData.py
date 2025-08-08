import requests

class NewsData:
    def __init__(self, apiKey, baseUrl):
        self.apiKey = apiKey
        self.baseUrl = baseUrl

    def getNews(self, symbol, startDate=None, endDate=None, pageSize=100):
        params = {
            "token": self.apiKey,
            "symbols": symbol,
            "pageSize": pageSize,
        }
        if startDate:
            params["published_since"] = startDate
        if endDate:
            params["published_before"] = endDate

        response = requests.get(self.baseUrl, params=params)
        if not response.ok:
            raise Exception(f"Benzinga API error {response.status_code}: {response.text}")

        return response.json()
