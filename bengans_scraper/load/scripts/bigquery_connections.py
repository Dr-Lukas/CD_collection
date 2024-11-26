import time
from google.cloud import bigquery
from google.api_core.exceptions import NotFound
from config import BengansScraper, load_config
from bengans_scraper.models import data_model_schema


class BigQueryTable:
    def __init__(self, config: BengansScraper, data_model: list[data_model_schema.BengansProducts]):
        self.bq_schema_generator = data_model_schema.BigQuerySchema(data_model)
        self.schema = self.bq_schema_generator.generate_schema()
        self.project = config.BigQuery.project_id
        self.client = bigquery.Client(project=config.BigQuery.project_id)
        self.dataset_ref = self.client.dataset(config.BigQuery.dataset_id)
        self.table_ref = self.dataset_ref.table(config.BigQuery.table_id)
        if self.table_exists():
            self.table = self.client.get_table(self.table_ref)

    def table_exists(self) -> bool:
        try:
            self.client.get_table(self.table_ref)
            return True  
        except NotFound:
            return False  

    def create_table(self):
        table = bigquery.Table(self.table_ref, schema=self.schema)

        self.client.create_table(table)
        while not self.table_exists():
            time.sleep(1)

        print(f"Table {table.table_id} created.")

    def upload_data(self, data: list[data_model_schema.BengansProducts]):
        products_as_dicts = [product.dict() for product in data]
        errors = self.client.insert_rows(
            self.table, products_as_dicts, selected_fields=self.table.schema
        )

        if not errors:
            print("Data chunk uploaded successfully.")
        else:
            print(f"Errors while uploading data chuck: {errors}, retrying...")
            for _ in range(3):
                errors = self.client.insert_rows(
                    self.table, data, selected_fields=self.table.schema
                )
                if not errors:
                    print("Data chunk uploaded successfully.")
                    break
                else:
                    print(f"Errors while uploading data chuck: {errors}")
                    time.sleep(1)
    
if __name__ == "__main__":

    config = load_config("config/config.yaml")
    my_table = BigQueryTable(
        config, data_model_schema.BengansProducts
    )
    my_table.create_table()