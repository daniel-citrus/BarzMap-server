"""
Single configured Auth0 instance for creating protected FastAPI routes.
"""
from fastapi import FastAPI, Depends
from fastapi_plugin.fast_api_client import Auth0FastAPI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI()

# Initialize Auth0
auth0 = Auth0FastAPI(
    domain=os.environ.get("AUTH0_DOMAIN"),
    audience=os.environ.get("AUTH0_AUDIENCE")
)