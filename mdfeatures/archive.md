---
Use the following function to explore the most similar trends between countries and territories.


#intro_markdown = read_markdown_file("mdfeatures/MainPageIntro.md")
st.markdown('## COVID-19 Mortality Monitoring', unsafe_allow_html=True)
st.markdown('Data source: [European CDC](https://www.ecdc.europa.eu/en/covid-19-pandemic)', unsafe_allow_html=True)
st.markdown('- <font size="2"> Default highlighted regions are African countries and territories. </font>', unsafe_allow_html=True)
st.markdown('- <font size="2"> Use the panel on right side of Plotly graph to add or hide certain countries or territories. </font>', unsafe_allow_html=True)
st.markdown('---', unsafe_allow_html=True)


#
# deaths pct pop
#fn = lambda row: row.deaths/row.popData2018
#col = df.apply(fn, axis=1) # get column data with an index
#df = df.assign(death_per_capita=col.values) # assign values to new column

df["total_deaths_per_capita"]=df.groupby(["countriesAndTerritories"])["death_per_capita"].\
                    rolling(window=7,min_periods=1).mean().reset_index(drop=True)


                    if graph_option=='COVID-19 Total deaths per million population':
                        totpc_graph_af= line_totdeath_pc_af(df_nday, df_region,)
                        st.plotly_chart(totpc_graph_af)
                    elif graph_option=='COVID-19 Total deaths':
                        totd_graph_af= line_totdeath_af(df_nday, df_region)
                        st.plotly_chart(totd_graph_af)
                    else:
                        daily_graph_af= line_daydeath_af(df_nday, df_region)

Using percent change, highest Pearson correlation is {"{:.3F}".format(pearson_max)},


###
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
    return fig

@st.cache
def line_daydeath_af(df_nday, df_region, ,reset=False):
    '''Plotly trends on total deaths, default with African countries.<br>
       Use visible='legendonly' to hide lines in Plotly.'''
    #
    fig = go.Figure()
    for c in df_region.countriesAndTerritories:
        dt_country= df_nday[df_nday.countriesAndTerritories==c].copy()
        if not dt_country.empty:
            if dt_country.unregion.values[0]=='Africa':
                fig.add_trace(go.Scatter(
                    x=dt_country['number_of_days'], y=dt_country['daily_deaths'],
                    mode='lines', name= c,
                    hovertemplate= dt_country['h_text']
                                        ))
            else:
                fig.add_trace(go.Scatter(
                    x=dt_country['number_of_days'], y=dt_country['daily_deaths'],
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
        yaxis_title= "Daily deaths confirmed"
                    )
    return fig


    if graph_option=='COVID-19 Total deaths per million population':
        out_put_graph= line_totdeath_pc_af(df_nday, df_region)
    elif graph_option=='COVID-19 Total deaths':
        out_put_graph= line_totdeath_af(df_nday, df_region)
    else:
        out_put_graph= line_daydeath_af(df_nday, df_region)
