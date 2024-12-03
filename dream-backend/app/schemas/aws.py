from typing import Optional, List
from pydantic import BaseModel, Field

from app.schemas.schema import *

class ResultInput(BaseModel):
    file_url : str = Field("")

