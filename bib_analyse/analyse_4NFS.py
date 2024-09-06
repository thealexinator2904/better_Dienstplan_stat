import pandas as pd


if __name__ == '__main__':
    df_data = pd.read_feather('data.feather')
    df_data[['Zeit_start', 'Zeit_end']] = df_data['Zeiten'].str.split('-', expand=True)
    
    df_data['datetime_start'] = pd.to_datetime(df_data['Datum'] + ' ' + df_data['Zeit_start'])
    df_data['datetime_end'] = pd.to_datetime(df_data['Datum'] + ' ' + df_data['Zeit_end'])

    # Add a day to the date if Zeit_end is smaller than Zeit_start
    df_data.loc[df_data['datetime_end'] < df_data['datetime_start'], 'datetime_end'] += pd.DateOffset(days=1)
    print(df_data)