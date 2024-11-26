from pydantic import BaseModel
from typing import Optional, Any, Union, get_origin, get_args
from google.cloud import bigquery

class BengansProducts(BaseModel):
    product_name: str
    band_name: str
    discounted_price: Optional[float] = None
    original_price: Optional[float] = None
    current_price: float
    status: str
    media_format: str
    product_link: str

class BigQuerySchema:
    def __init__(self, model: BaseModel):
        """
        Initialize with a Pydantic model to convert to BigQuery schema.
        """
        self.model = model

    @staticmethod
    def pydantic_to_bq_type(field_type: Any) -> str:
        """
        Map Pydantic field types to BigQuery data types.
        """
        if field_type == int:
            return 'INTEGER'
        elif field_type == str:
            return 'STRING'
        elif field_type == bool:
            return 'BOOLEAN'
        elif field_type == float:
            return 'FLOAT'
        elif field_type == list:
            return 'REPEATED'
        else:
            raise ValueError(f"Unsupported type: {field_type}")
        
    @staticmethod
    def is_nullable(field_type: Any) -> bool:
        """
        Determine if a field is nullable by checking if its type is Optional.
        """
        return get_origin(field_type) is Union and type(None) in get_args(field_type)

    def generate_schema(self) -> list:
        """
        Generate the BigQuery schema from the provided Pydantic model.
        """
        schema = []
        for field_name, field in self.model.__fields__.items():
            field_type = field.annotation
            bq_type = self.pydantic_to_bq_type(get_args(field_type)[0] if self.is_nullable(field_type) else field_type)
            mode = 'NULLABLE' if self.is_nullable(field_type) else 'REQUIRED'
            
            schema.append(
                bigquery.SchemaField(
                    field_name,
                    bq_type,
                    mode=mode
                )
            )
        return schema