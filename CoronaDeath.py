import streamlit as st
import plotly.graph_objects as go
import numpy as np
import pandas as pd
import copy
from datetime import date
from pathlib import Path

# jhu= pd.read_csv(\"https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv")
#
def read_markdown_file(markdown_file):
    return Path(markdown_file).read_text()

def main():
    '''Gathering data and Designing page layout.'''
    current_date= date.today()
    ecdc_link= "https://opendata.ecdc.europa.eu/covid19/casedistribution/csv"
    country_table_link= "https://raw.githubusercontent.com/quciet/NEPAD_covid19_mortality/master/ecdc%20country%20UN%20region%20concorded%2020200416.csv"
    #
    df_nday, df_region, today= fetch_ecdc(time= current_date,\
                link= ecdc_link, link_c= country_table_link)
    #
    af_list=[]
    for c in df_nday[df_nday.unregion.isin(["Africa"])].\
        countriesAndTerritories.drop_duplicates():
        if df_nday[df_nday.countriesAndTerritories.isin([c])].shape[0]>=10:
            af_list.append(c)
    # Title section
    intro_markdown = read_markdown_file("mdfeatures/MainPageIntro.md")
    st.markdown(intro_markdown, unsafe_allow_html=True)
    # Different graph themes
    graph_option= st.selectbox(label='Select a theme to display',
        options=['COVID-19 Daily deaths % Population- 7 Day Moving Average',
                'COVID-19 Total deaths'],
        index=0)
    #
    if st.button('Reset Countries and Territories'):
        if graph_option=='COVID-19 Daily deaths % Population- 7 Day Moving Average':
            nday_graph_af= line_deathpc_7ma_af(df_nday, df_region, reset=True)
        else:
            totd_graph_af= line_totdeath_af(df_nday, df_region, reset=True)
    #
    if graph_option=='COVID-19 Daily deaths % Population- 7 Day Moving Average':
        nday_graph_af= line_deathpc_7ma_af(df_nday, df_region)
        st.plotly_chart(nday_graph_af)
    else:
        totd_graph_af= line_totdeath_af(df_nday, df_region)
        st.plotly_chart(totd_graph_af)
    # Comparison plot for African countries
    st.markdown('---', unsafe_allow_html=True)
    af_compare_option= st.selectbox(
     label= 'Explore the most similar trend to the country and territory.',
     options= af_list)
    if st.checkbox("Show Trends"):
        c_similar, p_corr= trend_score(df_nday=df_nday, c_name=af_compare_option)
        st.markdown(f'Comparing at least 10 days of records.\
         Highest Pearson Correlation {"{:.2F}".format(p_corr)}, {c_similar}.', unsafe_allow_html=True)
        sim_graph= trend_score_fig(df_nday=df_nday, c_name=af_compare_option,\
            c_max=c_similar, t_max_actual= p_corr)
        st.plotly_chart(sim_graph)

# Grab data to current date, if date doesn't change, the function won't re-run
@st.cache
def fetch_ecdc(time, link, link_c):
    '''function to fetch the data from Europe CDC.'''
    try:
        df= pd.read_csv(link, na_values= "", encoding = "UTF-8")
        fetch_status=True
        print("European CDC Data Fetched")
    except:
        fetch_status=False
        print("European CDC Data Failed")
    #
    try:
        region_dt= pd.read_csv(link_c, encoding = "utf8")
        fetch_status_c=True
        print("Country Region Table Fetched")
    except:
        fetch_status_c=False
        print("Country Region Table Failed")
    #
    if fetch_status and fetch_status_c:
        df= df[df.year==2020]
        df.drop(columns=["month", "year", "day", "geoId", "countryterritoryCode"], inplace= True)
        df.dateRep= pd.to_datetime(df.dateRep, format='%d/%m/%Y')
        df["date"]= df["dateRep"].astype('str')
        df= pd.merge(left= df, right= region_dt, on=["countriesAndTerritories"], how="left")
        # deaths pct pop
        fn = lambda row: row.deaths/row.popData2018
        col = df.apply(fn, axis=1) # get column data with an index
        df = df.assign(death_per_capita=col.values) # assign values to new column
        df.sort_values(by=["countriesAndTerritories","dateRep"], inplace=True)
        df.reset_index(drop=True, inplace=True)
        df["total_deaths"]=df.groupby(["countriesAndTerritories"])["deaths"].cumsum()
        df["death_per_capita_7dayMA"]=df.groupby(["countriesAndTerritories"])["death_per_capita"].\
                            rolling(window=7,min_periods=1).mean().reset_index(drop=True)
        # convert date to number of days since first 3 daily deaths recorded
        country_list= list(region_dt.countriesAndTerritories)
        dt_start_date_dt= []
        for country in country_list:
            dt= df[df.countriesAndTerritories==country].copy(True)
            if dt[dt.deaths>=3].empty:
                continue
            first_3dailydeath= dt[dt.deaths>=3].index.values[0]
            dt= dt.loc[first_3dailydeath:,:]
            dt["number_of_days"]= range(1,1+dt.shape[0])
            dt_start_date_dt.append(dt)
        dt_start_date_dt= pd.concat(dt_start_date_dt)
        dt_start_date_dt.rename(columns={"popData2018": "population_2018",\
                            "deaths": "daily_deaths", "cases": "daily_cases"}, inplace=True)
        dt_start_date_dt['h_text']= dt_start_date_dt.apply(lambda x: \
        f'{x.date}<br>Daily deaths: {x.daily_deaths}<br>Total deaths: {x.total_deaths}<br>Dailydeaths per cap 7dayma: {"{:.2E}".format(x.death_per_capita_7dayMA)}<br>', axis=1)

        return dt_start_date_dt, region_dt, time
    #
    else:
        return None, None, time

@st.cache
def line_deathpc_7ma_af(df_nday, df_region, reset=False):
    '''Plotly trends on deaths pct pop 7 day moving avg, default with African countries.<br>
       Use visible='legendonly' to hide lines in Plotly.'''
    #
    fig = go.Figure()
    for c in df_region.countriesAndTerritories:
        dt_country= df_nday[df_nday.countriesAndTerritories==c].copy()
        if not dt_country.empty:
            if dt_country.unregion.values[0]=='Africa':
                fig.add_trace(go.Scatter(
                    x=dt_country['number_of_days'], y=dt_country['death_per_capita_7dayMA'],
                    mode='lines', name= c,
                    hovertemplate= dt_country['h_text']
                                        ))
            else:
                fig.add_trace(go.Scatter(
                    x=dt_country['number_of_days'], y=dt_country['death_per_capita_7dayMA'],
                    mode='lines', name= c,
                    hovertemplate= dt_country['h_text'],
                    visible='legendonly'
                                        ))
    fig.update_layout(
        width=900,
        height=500,
        margin=dict(l=20, r=20, t=35, b=0),
        #template= 'plotly_white',
        #title= 'COVID-19 Daily deaths % Population- 7 day moving avg',
        xaxis_title= "Number of Days- since 3 daily deaths recorded",
        yaxis_title= "Daily deaths per capita, 7 day moving average"
                    )
    print("Graph for daily deaths per capita 7dayMA generated.")
    return fig

@st.cache
def line_totdeath_af(df_nday, df_region, reset=False):
    '''Plotly trends on total deaths, default with African countries.<br>
       Use visible='legendonly' to hide lines in Plotly.'''
    #
    fig = go.Figure()
    for c in df_region.countriesAndTerritories:
        dt_country= df_nday[df_nday.countriesAndTerritories==c].copy()
        if not dt_country.empty:
            if dt_country.unregion.values[0]=='Africa':
                fig.add_trace(go.Scatter(
                    x=dt_country['number_of_days'], y=dt_country['total_deaths'],
                    mode='lines', name= c,
                    hovertemplate= dt_country['h_text']
                                        ))
            else:
                fig.add_trace(go.Scatter(
                    x=dt_country['number_of_days'], y=dt_country['total_deaths'],
                    mode='lines', name= c,
                    hovertemplate= dt_country['h_text'],
                    visible='legendonly'
                                        ))
    fig.update_layout(
        width=900,
        height=500,
        margin=dict(l=20, r=20, t=35, b=0),
        #template= 'plotly_white',
        #title= 'COVID-19 Daily deaths % Population- 7 day moving avg',
        xaxis_title= "Number of Days- since 3 daily deaths recorded",
        yaxis_title= "Cumulative deaths confirmed"
                    )
    print("Graph for total deaths generated.")
    return fig

@st.cache
def trend_score(df_nday, c_name):
    '''Use scatter plot & pearson correlation to calculate the trends that
    looks the most similar to the country or territory selected.'''
    dt_c1= df_nday[df_nday.countriesAndTerritories.isin([c_name])]\
    [["number_of_days", "death_per_capita_7dayMA"]].copy()
    country_list= list(df_nday.countriesAndTerritories.drop_duplicates())
    #print(country_list)
    t_max= 0
    t_max_actual= 0
    c_max= None
    for c2 in country_list:
        if c2!=c_name:
            dt_c2= df_nday[df_nday.countriesAndTerritories.isin([c2])]\
                [["number_of_days", "death_per_capita_7dayMA"]].copy()
            if dt_c2.shape[0]>=10:
                dt_trend= pd.merge(left=dt_c1, right=dt_c2, on=["number_of_days"], how='left')
                #dt_trend.dropna(inplace=True)
                t_score= dt_trend[["death_per_capita_7dayMA_x", "death_per_capita_7dayMA_y"]].corr()
                t_score= t_score['death_per_capita_7dayMA_x'].values[1]
                if abs(t_score)>t_max:
                    t_max= abs(t_score)
                    t_max_actual= t_score
                    c_max= c2
            #print(t_score)
    return c_max, t_max_actual

@st.cache
def trend_score_fig(df_nday, c_name, c_max, t_max_actual):
    '''Plot out the most similar trend.'''
    fig = go.Figure()
    for c in [c_name, c_max]:
        dt_country= df_nday[df_nday.countriesAndTerritories==c].copy()
        fig.add_trace(go.Scatter(
            x=dt_country['number_of_days'], y=dt_country['death_per_capita_7dayMA'],
            mode='lines', name= c,
            hovertemplate= dt_country['h_text']
                                ))
    fig.update_layout(
        width=800,
        height=400,
        margin=dict(l=20, r=20, t=35, b=0),
        #template= 'plotly_white',
        #title= 'COVID-19 Daily deaths % Population- 7 day moving avg',
        xaxis_title= "Number of Days- since 3 daily deaths recorded",
        yaxis_title= "Daily deaths per capita, 7 day moving average"
                    )
    return fig

#
if __name__ == "__main__":
    main()
