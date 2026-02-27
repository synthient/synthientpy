# synthientpy

A strongly typed Python client for [Synthient](https://synthient.com).
Supports asynchronous and synchronous requests to the Synthient API.

## Installation

MacOS/Linux
```bash
pip3 install synthientpy
```
Windows
```bat
pip install synthientpy
```

## Usage

Check synthientpy/models for the available fields in the response object.

Client and AsyncClient have the following methods:

```python
class Client:
    def __init__(
        self,
        api_key: str,
        default_timeout: int = DEFAULT_TIMEOUT,
        proxy: Optional[str] = None,
    ) -> None: ...
    def lookup_ip(self, ip_address: str) -> IPLookupResponse: ...
    def credits(self) -> Dict[str, Any]: ...
    def anonymizers(self, *, provider=None, type=None, last_observed=None, format=FeedFormat.CSV, country_code=None, full=False, order=SortOrder.DESC) -> bytes: ...
    def blacklist(self, *, provider=None, type=None, format=FeedFormat.CSV, order=SortOrder.DESC) -> bytes: ...
```

### Synchronous Usage

```python
import synthientpy as synthient

client = synthient.Client(api_key="sk_...")

ip_info = client.lookup_ip("8.8.8.8")
print(ip_info.ip_data.ip_risk)
print(ip_info.location)
print(ip_info.network)
```

### Asynchronous Usage

```python
import asyncio
import synthientpy as synthient

async def main():
    client = synthient.AsyncClient(api_key="sk_...")

    ip_info = await client.lookup_ip("8.8.8.8")
    print(ip_info.ip_data.ip_risk)

asyncio.run(main())
```

### Data Feeds

Bulk data is available for clients who want to perform large-scale analysis or integrate Synthient data into their own systems. Feeds are returned as raw bytes in JSONL, CSV, or TEXT format.

```python
import synthientpy as synthient

client = synthient.Client(api_key="sk_...")

anonymizers = client.anonymizers(
    provider="BIRDPROXIES",
    type="RESIDENTIAL_PROXY",
    last_observed="7D",
    format=synthient.FeedFormat.CSV,
    country_code="US",
)

blacklist = client.blacklist(
    provider="NORDVPN",
    type="COMMERCIAL_VPN",
    format=synthient.FeedFormat.CSV,
)
```

### Models

Full documentation of the fields and their types can be found in the [Synthient API documentation](https://docs.synthient.com). You can also find all the types in the `synthientpy.models` module.

### Issues

For any issues or feature requests, please open an issue on the [GitHub repository](https://github.com/synthient/synthientpy)
