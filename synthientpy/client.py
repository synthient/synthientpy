"""Main module."""

from typing import Any, Dict, Optional

import aiohttp
import requests
import urllib3

from synthientpy.constants import API_URL, DEFAULT_TIMEOUT, FEEDS_URL
from synthientpy.exceptions import ErrorResponse, InternalServerError
from synthientpy.models import FeedFormat, IPLookupResponse, SortOrder

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def _build_feed_params(
    format: FeedFormat,
    order: SortOrder,
    full: Optional[bool] = None,
    **kwargs: Optional[str],
) -> Dict[str, str]:
    """Build query parameters for feed endpoints, filtering out None values.

    Args:
        format (FeedFormat): The output format for the feed.
        order (SortOrder): The sort order for results.
        full (Optional[bool]): Whether to return all records.
        **kwargs: Additional optional string parameters.

    Returns:
        Dict[str, str]: The constructed query parameters.
    """
    params: Dict[str, str] = {"format": format.value, "order": order.value}
    if full is not None:
        params["full"] = str(full).lower()
    for key, value in kwargs.items():
        if value is not None:
            params[key] = value
    return params


class Client:
    """Synchronous client for interacting with the Synthient API."""

    def __init__(
        self,
        api_key: str,
        default_timeout: int = DEFAULT_TIMEOUT,
        proxy: Optional[str] = None,
    ):
        self._http = requests.Session()
        self._http.headers = {"Authorization": api_key}
        if proxy:
            self._http.proxies = {"http": proxy, "https": proxy}
            self._http.verify = False
        self.default_timeout: int = default_timeout

    def lookup_ip(self, ip_address: str) -> IPLookupResponse:
        """Query the risk, geo, and behavioral information of an IP address.

        Args:
            ip_address (str): The IP address to look up.

        Raises:
            ErrorResponse: If the server returns a 401, 404, or 422.
            InternalServerError: If the server returns an unexpected error.

        Returns:
            IPLookupResponse: The IP data. See docs.synthient.com for more information.
        """
        resp = self._http.get(
            f"{API_URL}lookup/ip/{ip_address}", timeout=self.default_timeout
        )
        if resp.status_code == 200:
            return IPLookupResponse(**resp.json())
        elif resp.status_code in (400, 401, 404, 422):
            json = resp.json()
            raise ErrorResponse(json["error"])
        else:
            raise InternalServerError("Server failed to lookup IP address.")

    def credits(self) -> Dict[str, Any]:
        """Retrieve credit balance for the authenticated account.

        Raises:
            ErrorResponse: If the server returns a 401.
            InternalServerError: If the server returns an unexpected error.

        Returns:
            Dict[str, Any]: The credit information.
        """
        resp = self._http.get(f"{API_URL}credits", timeout=self.default_timeout)
        if resp.status_code == 200:
            return resp.json()
        elif resp.status_code == 401:
            json = resp.json()
            raise ErrorResponse(json["error"])
        else:
            raise InternalServerError("Server failed to retrieve credits.")

    def anonymizers(
        self,
        *,
        provider: Optional[str] = None,
        type: Optional[str] = None,
        last_observed: Optional[str] = None,
        format: FeedFormat = FeedFormat.CSV,
        country_code: Optional[str] = None,
        full: bool = False,
        order: SortOrder = SortOrder.DESC,
    ) -> bytes:
        """Fetch the anonymizers feed containing historical proxy data.

        Args:
            provider (Optional[str]): Filter by provider name.
            type (Optional[str]): Filter by anonymization service type.
            last_observed (Optional[str]): Filter by recency (e.g., 24H, 7D, 1M).
            format (FeedFormat): Output format. Defaults to CSV.
            country_code (Optional[str]): Filter by country code (e.g., US, DE).
            full (bool): If True, returns all records. Defaults to False.
            order (SortOrder): Sort order. Defaults to DESC.

        Raises:
            ErrorResponse: If the server returns a 401.
            InternalServerError: If the server returns an unexpected error.

        Returns:
            bytes: The raw feed data in the requested format.
        """
        params = _build_feed_params(
            format=format,
            order=order,
            full=full,
            provider=provider,
            type=type,
            last_observed=last_observed,
            country_code=country_code,
        )
        resp = self._http.get(f"{FEEDS_URL}feeds/anonymizers", params=params)
        if resp.status_code == 200:
            return resp.content
        elif resp.status_code == 401:
            raise ErrorResponse(resp.json()["error"])
        else:
            raise InternalServerError("Server failed to fetch anonymizers feed.")

    def blacklist(
        self,
        *,
        provider: Optional[str] = None,
        type: Optional[str] = None,
        format: FeedFormat = FeedFormat.CSV,
        order: SortOrder = SortOrder.DESC,
    ) -> bytes:
        """Fetch the blacklist feed containing IP addresses and subnets
        belonging to proxy providers, VPNs, and TOR nodes.

        Args:
            provider (Optional[str]): Filter by provider name.
            type (Optional[str]): Filter by anonymization service type.
            format (FeedFormat): Output format. Defaults to CSV.
            order (SortOrder): Sort order. Defaults to DESC.

        Raises:
            ErrorResponse: If the server returns a 401.
            InternalServerError: If the server returns an unexpected error.

        Returns:
            bytes: The raw feed data in the requested format.
        """
        params = _build_feed_params(
            format=format,
            order=order,
            provider=provider,
            type=type,
        )
        resp = self._http.get(f"{FEEDS_URL}feeds/blacklist", params=params)
        if resp.status_code == 200:
            return resp.content
        elif resp.status_code == 401:
            raise ErrorResponse(resp.json()["error"])
        else:
            raise InternalServerError("Server failed to fetch blacklist feed.")


class AsyncClient:
    """Asynchronous client for interacting with the Synthient API."""

    def __init__(
        self,
        api_key: str,
        default_timeout: int = DEFAULT_TIMEOUT,
        proxy: Optional[str] = None,
    ):
        self.api_key: str = api_key
        self.proxy: Optional[str] = proxy
        self.default_timeout: int = default_timeout

    async def lookup_ip(self, ip_address: str) -> IPLookupResponse:
        """Query the risk, geo, and behavioral information of an IP address.

        Args:
            ip_address (str): The IP address to look up.

        Raises:
            ErrorResponse: If the server returns a 401, 404, or 422.
            InternalServerError: If the server returns an unexpected error.

        Returns:
            IPLookupResponse: The IP data. See docs.synthient.com for more information.
        """
        async with aiohttp.ClientSession(
            headers={"Authorization": self.api_key}
        ).get(
            f"{API_URL}lookup/ip/{ip_address}",
            timeout=self.default_timeout,
            proxy=self.proxy,
        ) as resp:
            if resp.status == 200:
                return IPLookupResponse(**await resp.json())
            elif resp.status in (400, 401, 404, 422):
                json = await resp.json()
                raise ErrorResponse(json["error"])
            else:
                raise InternalServerError("Server failed to lookup IP address.")

    async def credits(self) -> Dict[str, Any]:
        """Retrieve credit balance for the authenticated account.

        Raises:
            ErrorResponse: If the server returns a 401.
            InternalServerError: If the server returns an unexpected error.

        Returns:
            Dict[str, Any]: The credit information.
        """
        async with aiohttp.ClientSession(
            headers={"Authorization": self.api_key}
        ).get(
            f"{API_URL}credits",
            timeout=self.default_timeout,
            proxy=self.proxy,
        ) as resp:
            if resp.status == 200:
                return await resp.json()
            elif resp.status == 401:
                json = await resp.json()
                raise ErrorResponse(json["error"])
            else:
                raise InternalServerError("Server failed to retrieve credits.")

    async def anonymizers(
        self,
        *,
        provider: Optional[str] = None,
        type: Optional[str] = None,
        last_observed: Optional[str] = None,
        format: FeedFormat = FeedFormat.CSV,
        country_code: Optional[str] = None,
        full: bool = False,
        order: SortOrder = SortOrder.DESC,
    ) -> bytes:
        """Fetch the anonymizers feed containing historical proxy data.

        Args:
            provider (Optional[str]): Filter by provider name.
            type (Optional[str]): Filter by anonymization service type.
            last_observed (Optional[str]): Filter by recency (e.g., 24H, 7D, 1M).
            format (FeedFormat): Output format. Defaults to CSV.
            country_code (Optional[str]): Filter by country code (e.g., US, DE).
            full (bool): If True, returns all records. Defaults to False.
            order (SortOrder): Sort order. Defaults to DESC.

        Raises:
            ErrorResponse: If the server returns a 401.
            InternalServerError: If the server returns an unexpected error.

        Returns:
            bytes: The raw feed data in the requested format.
        """
        params = _build_feed_params(
            format=format,
            order=order,
            full=full,
            provider=provider,
            type=type,
            last_observed=last_observed,
            country_code=country_code,
        )
        async with aiohttp.ClientSession(
            headers={"Authorization": self.api_key}
        ).get(
            f"{FEEDS_URL}feeds/anonymizers",
            params=params,
            proxy=self.proxy,
        ) as resp:
            if resp.status == 200:
                return await resp.read()
            elif resp.status == 401:
                json = await resp.json()
                raise ErrorResponse(json["error"])
            else:
                raise InternalServerError("Server failed to fetch anonymizers feed.")

    async def blacklist(
        self,
        *,
        provider: Optional[str] = None,
        type: Optional[str] = None,
        format: FeedFormat = FeedFormat.CSV,
        order: SortOrder = SortOrder.DESC,
    ) -> bytes:
        """Fetch the blacklist feed containing IP addresses and subnets
        belonging to proxy providers, VPNs, and TOR nodes.

        Args:
            provider (Optional[str]): Filter by provider name.
            type (Optional[str]): Filter by anonymization service type.
            format (FeedFormat): Output format. Defaults to CSV.
            order (SortOrder): Sort order. Defaults to DESC.

        Raises:
            ErrorResponse: If the server returns a 401.
            InternalServerError: If the server returns an unexpected error.

        Returns:
            bytes: The raw feed data in the requested format.
        """
        params = _build_feed_params(
            format=format,
            order=order,
            provider=provider,
            type=type,
        )
        async with aiohttp.ClientSession(
            headers={"Authorization": self.api_key}
        ).get(
            f"{FEEDS_URL}feeds/blacklist",
            params=params,
            proxy=self.proxy,
        ) as resp:
            if resp.status == 200:
                return await resp.read()
            elif resp.status == 401:
                json = await resp.json()
                raise ErrorResponse(json["error"])
            else:
                raise InternalServerError("Server failed to fetch blacklist feed.")
