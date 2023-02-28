import streamlit as st
import yaml
import altair as alt
import pandas as pd


def configuration():
    global date_column, actual_column, predict_column, account_column, target_column,best_column,worse_column,scenarios
    
    with open("config.yml", "r") as ymlfile:
        cfg = yaml.safe_load(ymlfile)
    
    date_column = cfg['date_column']
    actual_column = cfg['actual_column']
    predict_column = cfg['predict_column']
    account_column = cfg['account_column']
    target_column = cfg['target_column']
    best_column = cfg['best_column']
    worse_column = cfg['worse_column']
    scenarios = {'Most likely scenario': predict_column,'Best case scenario':best_column,'Wost case scenatio':worse_column, 'Show boundries': None}
   
    return 0

def load_data():
    df = pd.read_csv('Data.csv')
    df = pd.read_csv('Data.csv',parse_dates=[date_column])
    df[date_column] = pd.to_datetime(df[date_column]).dt.date
    
    return df

    
def get_chart(df):    
    
    #define line chart for prediction      
        viz_columns = scenarios[viz_]                    
            
        line_chart = alt.Chart(df).mark_line().encode(
            alt.X(f"{date_column}:T",axis=alt.Axis(title='Date')),
            alt.Y(f"{viz_columns}:Q",axis=alt.Axis(format='$.2f',title='Total sales actual/prediction')),
            color = alt.value('blue')
        ).properties(
            width = 600*1.5,
            height = 400*1.5
        )
        
        bound_chart = alt.Chart(df).mark_area(opacity= 0.2).encode(
                    x='time:T',
                    y=f"{best_column}:Q",
                    y2=f"{worse_column}:Q",
                    color = alt.value('blue')
                        ).properties(
                            width = 600*1.5,
                            height = 400*1.5
                        )
        #define area chart for actual
        if viz_type=='Area':
            
            area_chart = alt.Chart(df).mark_area(opacity = area_opacity,line=True,color="lightblue").encode(
                alt.X(f"{date_column}:T"),
                alt.Y(f"{actual_column}:Q",axis=alt.Axis(format='$.2f',title='Total sales actual/prediction'))
                )
        else:
            area_chart = alt.Chart(df).mark_bar(size = bar_size, opacity= area_opacity).encode(
                alt.X(f"{date_column}:T"),
                alt.Y(f"{actual_column}:Q",axis=alt.Axis(format='$.2f',title='Total sales actual/prediction'))
                )
        
        #define hover
        hover = alt.selection_single(
                fields=["time"],
                nearest=True,
                on="mouseover",
                empty="none",
                clear="mouseout",
            )
        
        points = line_chart.transform_filter(hover).mark_circle(size=65)
        #define tooltips
        tooltips = (
                alt.Chart(df)
                .mark_rule(strokeWidth=2,  color="orange")
                .encode(
                    x = date_column,
                    y = predict_column,
                    opacity=alt.condition(hover, alt.value(0.3), alt.value(0)),
                    tooltip=[
                        alt.Tooltip(date_column, title="Date"),
                        alt.Tooltip(predict_column, title="Prediction",format='$.2f'),
                        alt.Tooltip(best_column, title="best case scenario",format='$.2f'),
                        alt.Tooltip(worse_column, title="worst case scenario",format='$.2f'),
                        alt.Tooltip(actual_column, title="Actual",format='$.2f'),
                    ],
                )
                .add_selection(hover)
            )
        
        #define target line        
        target_chart = alt.Chart(pd.DataFrame({'y': [df[target_column].max()],'color': ['red']})).mark_rule(strokeWidth=2).encode(y='y',color=alt.Color('color:N', scale=None))
        recent_time = alt.Chart(pd.DataFrame({
          'Date': [df[df[actual_column].notnull()][date_column].max()],
          'color': ['black']
        })).mark_rule(strokeWidth=2).encode(
          x='Date:T',
          color=alt.Color('color:N', scale=None)
          )

        #Combine the two charts using layering
        if viz_columns is None:
            chart = alt.layer(bound_chart, area_chart,target_chart,recent_time, points).resolve_scale(
                y='shared'
            )
        else:
            
            chart = alt.layer(line_chart, area_chart,target_chart,recent_time, points).resolve_scale(
                y='shared'
                )
        
        # Add chart title and axis labels
        
        account= df[account_column].drop_duplicates().tolist()[0]
        
        chart = chart.properties(
            title=f"{viz_} sales growth forecasting for the {account} account",
        ).configure_axis(
            labelFontSize=14,
            titleFontSize=16,
        )                    
                    
        return (chart + tooltips).interactive()



def filter_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    global viz_, viz_type, bar_size, area_opacity
    modification_container = st.container()
   
    st.sidebar.title("Vizulization Configuration")

    with modification_container:         
                st.title("Sales Growth Insight Dashboard")
                st.write("""Please select the account and date range to get growth forecasting""")
                account_input  = st.selectbox("Select Account: ", df[account_column].drop_duplicates())
                date_input = st.slider('Select Date Range', min_value=df.time.min(), value=df.head(15).time.max() ,max_value=df.time.max())                    
                viz_  = st.sidebar.radio("Select forecasting scenario you want to visualize: ", list(scenarios.keys()))
                viz_type  = st.sidebar.radio("Select visualization type to plot actual values: ", ('Area', 'Bar'))
                bar_size = st.sidebar.slider('Select bar size in the case of bar type visualization:',5,50,20)
                area_opacity = st.sidebar.slider('Select area opacity:',0.0,1.0,0.5)
                df = df[(df.time<date_input) & (df.Account==account_input)]
            
    return df

def main():
        
    configuration()    
    data = load_data()       
    chart = get_chart(filter_dataframe(data))
        
    st.altair_chart((chart).interactive(), use_container_width=True)



if __name__ == "__main__":
    main()
