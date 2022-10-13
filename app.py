import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px

DATA_URI = "Motor_Vehicle_Collisions_-_Crashes.csv"


st.title("https://drive.google.com/file/d/10600OXn6VJOPUWpWFevB1ahzVX4LZNHH/view?usp=sharing")
st.markdown("This Application is  Streamlit Dashboard ")


@st.cache(persist=True)
def load_data(nrows):
    data = pd.read_csv(DATA_URI, nrows=nrows, parse_dates=[['CRASH_DATE', 'CRASH_TIME']])
    data.dropna(subset=['LATITUDE', 'LONGITUDE'], inplace=True)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis='columns', inplace=True)
    data.rename(columns={"crash_date_crash_time": 'date/time'}, inplace=True)
    return data


data = load_data(10000)
original_data=data
# a=max(data[injured_persons])
st.header("Where are the most people injured in NYC?")
injured_people = st.slider("Number of Persons injured in vehicle collision", 0, 29)
st.map(data.query("injured_persons >= @injured_people")[['latitude', "longitude"]].dropna(how='any'))

st.header("How many collisions occur during a time of day?")
hour = st.slider("24 hour Time Table", 0, 29)
data = data[data['date/time'].dt.hour == hour]

st.markdown("Vehicle Collisions Between %i:00 and %i:00" % (hour, (hour + 1)))
midpoint = (np.average(data['latitude']), np.average(data['longitude']))

st.write(pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state={
        "latitude": midpoint[0],
        'longitude': midpoint[1],
        "zoom": 11,
        "pitch": 50,
    },
    layers=[
        pdk.Layer(
            "HexagonLayer",
            data=data[['date/time', 'latitude', 'longitude']],
            get_position=['longitude', 'latitude'],
            radius=100,
            pickable=True,
            elevation_scale=4,
            elevation_range=[0, 1000],
        ),
    ],
))

st.subheader("Breakdown by minite %i:00 and %i:00" % (hour, (hour +1)))
filtered=data[
    (data['date/time'].dt.hour >= hour) & (data['date/time'].dt.hour < (hour+1))
]
hist=np.histogram(filtered['date/time'].dt.minute,bins=60,range=(0,60))[0]
char_data=pd.DataFrame({'minute': range(60), 'crashes':hist})
fig=px.bar(char_data,x='minute',y='crashes',hover_data=['minute','crashes'],height=400)
st.write(fig)

st.header('Top 5 dangerous streets by affected type')
select=st.selectbox('Affected type of people',['Pedestrians','Cyclist','Motorists'])

if select=='Pedestrians':
    st.write(original_data.query("injured_pedestrians >=1")[['on_street_name', 'injured_pedestrians']]
             .sort_values(by=['injured_pedestrians'], ascending=False).dropna(how='any')[:5])
elif select=='Cyclist':
    st.write(original_data.query("injured_cyclists >=1")[['on_street_name', 'injured_cyclists']]
             .sort_values(by=['injured_cyclists'], ascending=False).dropna(how='any')[:5])
elif select=='Motorists':
    st.write(original_data.query("injured_motorists >=1")[['on_street_name', 'injured_motorists']]
             .sort_values(by=['injured_motorists'], ascending=False).dropna(how='any')[:5])




if st.checkbox("Show Row Data", False):
    st.subheader('Raw Data')
    st.write(data)