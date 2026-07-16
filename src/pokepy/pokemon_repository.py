import boto3
from botocore.config import Config

class Pokemon:
    def __init__(self, name: str, image_bytes: bytes):
        self.name = name
        self.image_bytes = image_bytes

class PokemonRepository:
    def __init__(self):
        self.db_unavailable = False

        # DynamoDB emulated by LocalStack. LocalStack needs to be running in Docker (command:localstack start)      
        self.db = boto3.client(
            "dynamodb",
            endpoint_url = "http://localhost:4566",
            aws_access_key_id = "test",
            aws_secret_access_key = "test",
            region_name = "eu-west-2",
            config = Config(
                connect_timeout=1,
                read_timeout=1,
                retries={"max_attempts": 1,},
            )
        )

        # Create the Pokemon table if it doesn't exist. This is just because we are using LocalStack
        # which drops everything when it shuts down.
        self._create_table() 

    def _create_table(self):
        try:
            table_exists: bool = "pokemon" in self.db.list_tables()["TableNames"]

            if not table_exists:
                self.db.create_table(
                    TableName="pokemon",
                    KeySchema=[
                        {"AttributeName": "name", "KeyType": "HASH"}
                    ],
                    AttributeDefinitions=[{"AttributeName": "name", "AttributeType": "S"}],
                    ProvisionedThroughput={"ReadCapacityUnits": 1, "WriteCapacityUnits": 1}
                )             
        except Exception as e:
            print(f"DynamoDB (LocalStack) not available. Running without it.", e)
            self.db_unavailable = True
            return

    def create_pokemon(self, name: str, image_bytes: bytes) -> Pokemon | None:
        if self.db_unavailable:
            return None

        self.db.put_item(
            TableName="pokemon",
            Item={
                "name": {"S": name},
                "image_bytes": {"B": image_bytes}
            }
        )

        pokemon = Pokemon(name, image_bytes)
        return pokemon

    def get_pokemon(self, name: str) -> Pokemon | None:
        if self.db_unavailable:
            return None

        response = self.db.get_item(
            TableName="pokemon",
            Key={"name": {"S": name}}
        )

        if "Item" not in response:
            return None

        pokemon = Pokemon(
            name=response["Item"]["name"]["S"],
            image_bytes=response["Item"]["image_bytes"]["B"]
        )

        return pokemon