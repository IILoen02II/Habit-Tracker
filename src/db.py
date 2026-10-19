import os

import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()


def _get_url() -> str:
    """Busca la cadena de conexión en st.secrets (Streamlit) o en .env."""
    try:
        return st.secrets["DATABASE_URL"]
    except (FileNotFoundError, KeyError):
        url = os.getenv("DATABASE_URL")
        if not url:
            raise RuntimeError(
                "Falta DATABASE_URL: defínela en .env o en .streamlit/secrets.toml"
            )
        return url


@st.cache_resource
def get_engine():
    # pool_pre_ping reconecta si Neon "durmió" la base
    return create_engine(_get_url(), pool_pre_ping=True)
