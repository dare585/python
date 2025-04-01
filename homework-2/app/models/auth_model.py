from enum import Enum
from pydantic import BaseModel, Field, field_validator


# Enum for AWS Regions
class AWSRegionEnum(str, Enum):
    us_east_1 = "us-east-1" # N. Virginia
    us_east_2 = "us-east-2" # Ohio
    us_west_1 = "us-west-1" # N. California
    us_west_2 = "us-west-2" # Oregon
    eu_west_1 = "eu-west-1" # Ireland
    eu_west_2 = "eu-west-2" # London
    eu_west_3 = "eu-west-3" # Paris
    eu_north_1 = "eu-north-1" # Stockholm
    eu_central_1 = "eu-central-1" # Frankfurt
    ca_central_1 = "ca-central-1" # Central
    ap_south_1 = "ap-south-1" # Mumbai
    ap_northeast_1 = "ap-northeast-1" # Tokyo
    ap_northeast_2 = "ap-northeast-2" # Seoul
    ap_northeast_3 = "ap-northeast-3" # Osaka
    ap_southeast_1 = "ap-southeast-1" # Singapore
    ap_southeast_2 = "ap-southeast-2" # Sydney
    sa_east_1 = "sa-east-1" # São Paulo

    # Add more regions here if needed


# Define the Pydantic model for request validation
class AuthRequestModel(BaseModel):
    aws_access_key_id: str = Field(..., title="AWS Access Key ID")
    aws_secret_access_key: str = Field(..., title="AWS Secret Access Key")
    aws_region: AWSRegionEnum = Field(..., title="AWS Region")  # Use the Enum for validation


    # Validator to ensure that aws_access_key_id is not an empty string
    @field_validator('aws_access_key_id')
    @classmethod
    def check_aws_access_key_id(cls, value):
        if not value.strip():  # Checks if it's an empty string or only spaces
            raise ValueError('AWS Access Key ID cannot be empty')
        return value


     # Validator to ensure that aws_secret_access_key is not an empty string
    @field_validator('aws_secret_access_key')
    @classmethod
    def check_aws_secret_access_key(cls, value):
        if not value.strip():  # Checks if it's an empty string or only spaces
            raise ValueError('AWS Secret Access Key cannot be empty')
        return value