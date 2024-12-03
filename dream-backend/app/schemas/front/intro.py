
from typing import Optional, List
from pydantic import BaseModel, Field


class AgreementInput(BaseModel):
    mode: str = Field("")
    partner_name: str = Field("")