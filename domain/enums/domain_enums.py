from enum import Enum


class DomainSourceType(Enum):
    AUCTIONS_GO_DADDY = "auctions_go_daddy"
    EXPIRED_DOMAINS = "expired_domains"


class FilterType(Enum):
    PRICE = "FILTER BY PRICE"
    TIME = "FILTER BY TIME"
