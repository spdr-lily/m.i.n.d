from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
import pandas as pd


class AggregationService:
    def __init__(self, session: Session):
        self.session = session

    def query(self, sql: str, params: Optional[Dict] = None) -> pd.DataFrame:
        return pd.read_sql_query(text(sql), self.session.bind, params=params or {})
