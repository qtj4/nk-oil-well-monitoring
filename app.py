import pandas as pd
import plotly.express as px
import streamlit as st

from nk_oil.config import paths

st.set_page_config(page_title='NK Well Monitoring', layout='wide')
st.title('NK Well Monitoring · historical data')
target = paths()
if not (target / 'long.parquet').exists():
    st.info('Run: python -m nk_oil.cli prepare --phase1')
    st.stop()
df = pd.read_parquet(target / 'long.parquet')
st.caption('Verified source slice · historical sensor readings · no failure labels')
well = st.selectbox('Well', sorted(df.well_id.unique()))
selected = df[df.well_id == well]
parameter = st.selectbox('Parameter', sorted(selected.parameter.unique()))
selected = selected[selected.parameter == parameter]
st.plotly_chart(px.line(selected, x='timestamp', y='value', title=f'{well}: {parameter} ({selected.unit.iloc[0]})'))
st.dataframe(selected[['timestamp', 'value', 'flag', 'n_obs']])
