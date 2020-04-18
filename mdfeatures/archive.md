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
