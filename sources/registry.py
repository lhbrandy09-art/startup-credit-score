from sources.yc_source import load as load_yc
from sources.techstars_source import load as load_techstars
from sources.product_hunt_source import load as load_product_hunt
from sources.external_csv_source import load as load_external

SOURCE_REGISTRY = [
    {
        "name": "YC",
        "loader": load_yc,
        "enabled": True
    },
    {
        "name": "Techstars",
        "loader": load_techstars,
        "enabled": True
    },
    {
        "name": "Product Hunt",
        "loader": load_product_hunt,
        "enabled": True
    },
    {
        "name": "External CSVs",
        "loader": load_external,
        "enabled": True
    }
]
