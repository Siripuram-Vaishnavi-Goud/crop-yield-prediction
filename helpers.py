"""
utils/helpers.py — Shared data helpers
"""

import pandas as pd
import os
import streamlit as st

DATA_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "dataset", "crop_yield.csv"
)


@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].str.strip()
    df.dropna(inplace=True)
    df = df[df["Yield"] > 0]
    return df


def format_yield(value: float) -> str:
    """Format yield value with appropriate units."""
    if value >= 1000:
        return f"{value:,.1f} tonnes/ha"
    return f"{value:.3f} tonnes/ha"


def yield_category(value: float) -> tuple[str, str]:
    """Return (label, color) for a yield value."""
    if value < 0.5:
        return "Very Low", "#e74c3c"
    elif value < 1.5:
        return "Low", "#e67e22"
    elif value < 3.0:
        return "Moderate", "#f1c40f"
    elif value < 6.0:
        return "Good", "#2ecc71"
    else:
        return "Excellent", "#27ae60"


CROPS = [
    'Arecanut', 'Arhar/Tur', 'Bajra', 'Banana', 'Barley', 'Black pepper',
    'Cardamom', 'Cashewnut', 'Castor seed', 'Coconut', 'Coriander',
    'Cotton(lint)', 'Cowpea(Lobia)', 'Dry chillies', 'Garlic', 'Ginger',
    'Gram', 'Groundnut', 'Guar seed', 'Horse-gram', 'Jowar', 'Jute',
    'Khesari', 'Linseed', 'Maize', 'Masoor', 'Mesta', 'Moong(Green Gram)',
    'Moth', 'Niger seed', 'Oilseeds total', 'Onion', 'Other  Rabi pulses',
    'Other Cereals', 'Other Kharif pulses', 'Other Summer Pulses',
    'Peas & beans (Pulses)', 'Potato', 'Ragi', 'Rapeseed &Mustard', 'Rice',
    'Safflower', 'Sannhamp', 'Sesamum', 'Small millets', 'Soyabean',
    'Sugarcane', 'Sunflower', 'Sweet potato', 'Tapioca', 'Tobacco',
    'Turmeric', 'Urad', 'Wheat', 'other oilseeds'
]

SEASONS = ['Autumn', 'Kharif', 'Rabi', 'Summer', 'Whole Year', 'Winter']

STATES = [
    'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh',
    'Delhi', 'Goa', 'Gujarat', 'Haryana', 'Himachal Pradesh',
    'Jammu and Kashmir', 'Jharkhand', 'Karnataka', 'Kerala',
    'Madhya Pradesh', 'Maharashtra', 'Manipur', 'Meghalaya', 'Mizoram',
    'Nagaland', 'Odisha', 'Puducherry', 'Punjab', 'Sikkim', 'Tamil Nadu',
    'Telangana', 'Tripura', 'Uttar Pradesh', 'Uttarakhand', 'West Bengal'
]