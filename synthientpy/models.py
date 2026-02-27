from enum import Enum
from typing import List, Optional

from pydantic import BaseModel


class FeedFormat(str, Enum):
    """Format options for data feed exports.
    JSONL - JSON Lines format.
    CSV - Comma-separated values.
    TEXT - Plain text, one IP per line with provider annotation.
    """

    JSONL = "JSONL"
    CSV = "CSV"
    TEXT = "TEXT"


class SortOrder(str, Enum):
    """Sort order for feed results.
    ASC - Ascending order.
    DESC - Descending order.
    """

    ASC = "asc"
    DESC = "desc"


class Network(BaseModel):
    """Network information for an IP address.

    asn (int): Autonomous System Number.
    org (Optional[str]): Organization owning the ASN.
    isp (str): Internet Service Provider.
    type (str): Type of network (e.g., RESIDENTIAL, BUSINESS).
    abuse_email (Optional[str]): Abuse contact email.
    abuse_phone (Optional[str]): Abuse contact phone number.
    domain (Optional[str]): Domain associated with the network.
    """

    asn: int
    org: Optional[str] = None
    isp: str
    type: str
    abuse_email: Optional[str] = None
    abuse_phone: Optional[str] = None
    domain: Optional[str] = None


class Location(BaseModel):
    """Geographical location details of an IP address.

    geo_hash (Optional[str]): Geohash representing the location.
    country (str): Two-letter country code (ISO 3166-1 alpha-2).
    state (Optional[str]): State or region within the country.
    city (str): City of the location.
    timezone (str): Timezone of the location (e.g., Africa/Lagos).
    longitude (float): Longitude coordinate.
    latitude (float): Latitude coordinate.
    """

    geo_hash: Optional[str] = None
    country: str
    state: Optional[str] = None
    city: str
    timezone: str
    longitude: float
    latitude: float


class Device(BaseModel):
    """Device associated with an IP address.

    os (str): Operating system of the device.
    version (str): OS version.
    """

    os: str
    version: str


class EnrichedEntry(BaseModel):
    """Enriched data from a third-party provider.

    provider (str): Name of the enrichment provider.
    type (str): Type of service identified by the provider.
    last_seen (str): Date when the provider last saw this IP as this type.
    """

    provider: str
    type: str
    last_seen: str


class IPData(BaseModel):
    """Detailed data and risk assessment for an IP address.

    device_count (int): Number of devices associated with the IP.
    devices (List[Device]): List of devices associated with the IP.
    behavior (List[str]): Observed behaviors (e.g., VPN_USER, ACTIVE_CRAWLER).
    categories (List[str]): Categories the IP falls into (e.g., TOR_NODE, FREE_VPN).
    enriched (Optional[List[EnrichedEntry]]): Enriched data from various providers.
    ip_risk (int): Numeric risk score from 0 (none) to 100 (highest).
    """

    device_count: int
    devices: List[Device]
    behavior: List[str]
    categories: List[str]
    enriched: Optional[List[EnrichedEntry]] = None
    ip_risk: int


class IPLookupResponse(BaseModel):
    """Response model for the IP lookup endpoint.

    ip (str): The IP address that was looked up.
    network (Optional[Network]): Details about the network the IP belongs to.
    location (Optional[Location]): Geographical location details.
    ip_data (IPData): Detailed data and risk assessment.
    """

    ip: str
    network: Optional[Network] = None
    location: Optional[Location] = None
    ip_data: IPData


class ProxyEvent(BaseModel):
    """Event model for the Redis Pub/Sub firehose feed.
    Channel name: proxy_feed

    ip (str): The IP address observed.
    provider (str): The provider that observed the IP.
    timestamp (str): Timestamp of the observation.
    """

    ip: str
    provider: str
    timestamp: str
