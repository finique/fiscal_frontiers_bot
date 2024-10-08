import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import matplotlib.colors as mcolors
from fmp_api import get_yield, get_commodity, get_segmentation, get_economics
from datetime import datetime, timedelta


def graph_peers_multiple(multiples_series, multiple):
    multiples_series = multiples_series.loc['{}'.format(multiple)]
    # Convert Series to DataFrame
    Multiple_df = multiples_series.to_frame().reset_index()
    Multiple_df.columns = ['Company', 'debtEquityRatio']

    # Calculate the average ratio
    Average_ratio = multiples_series.mean()

    # Sorting the DataFrame
    Multiple_df = Multiple_df.sort_values(by='debtEquityRatio', ascending=True)

    # Plotting
    plt.figure(figsize=(10, 8))
    barplot = sns.barplot(x='Company', y='debtEquityRatio', data=Multiple_df,
                          hue='Company', dodge=False, palette='viridis')
    plt.legend([], [], frameon=False)  # Suppress the legend

    # Average line and text
    plt.axhline(Average_ratio, color='r', linewidth=2, linestyle='--')
    # Position the average text in the center of the plot
    plt.text(len(Multiple_df) / 2 - 0.5, Average_ratio, f'Average: {Average_ratio:.2f}',
             color='red', ha="center", va="bottom")

    # Adding text labels on bars
    for bar in barplot.patches:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2., height, f'{height:.2f}',
                 ha='center', va='bottom', color='black')

    # Final touches on the plot
    plt.title('Comparison Among Peers - {}'.format(multiple))
    plt.ylabel('{}'.format(multiple))
    plt.xlabel('Company')
    plt.xticks(rotation=45)  # Rotate company names for better readability
    plt.tight_layout()

    plt.show()  # Display the plot

    # Return None to avoid outputting the last expression result
    return None




def graph_peers_multiple_by_type(multiple, ax, multiples_series):
    # Transpose and reset index
    transposed_df = multiples_series.T.reset_index()

    transposed_df.columns = ['Company'] + list(multiples_series.index)

    # Select the appropriate data for the given multiple
    Multiple_df = transposed_df[['Company', multiple]]
    Average_ratio = Multiple_df[multiple].mean()
    Multiple_df = Multiple_df.sort_values(by=multiple, ascending=True)

    # Plotting using the passed Axes object (ax)
    sns.barplot(x='Company', y=multiple, data=Multiple_df,
                hue='Company', dodge=False, palette='viridis', ax=ax)
    ax.legend([], [], frameon=False)  # Suppress the legend
    ax.axhline(Average_ratio, color='r', linewidth=1, linestyle='--')
    # ax.text(len(Multiple_df) / 2 - 0.5, Average_ratio, f'Average: {Average_ratio:.2f}',
    #         color='red', ha="center", va="bottom", fontsize=6)  # Adjust fontsize here for average ratio text

    for bar in ax.patches:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2., height, f'{height:.1f}',
                ha='center', va='bottom', color='black', fontsize=6)  # Adjust fontsize here for bar labels

    ax.set_title('{}'.format(multiple), fontsize=8)  # Adjust fontsize for graph title
    ax.set_ylabel('')
    ax.set_xlabel('')
    #ax.set_ylabel('{}'.format(multiple), fontsize=0)  # Adjust fontsize for y-label
    #ax.set_xlabel('Company', fontsize=6)  # Adjust fontsize for x-label
    ax.tick_params(axis='y', labelsize=6)  # Adjust fontsize for ylabel numbers
    # Set x-tick labels with corresponding locations
    ax.set_xticks(range(len(Multiple_df['Company'])))
    ax.set_xticklabels(Multiple_df['Company'], rotation=45, fontsize=6)  # Adjust fontsize for ticker names






def graph_yield(df=get_yield(offset = 3), show = 0):
    # Assuming yield_curve is already defined within df
    yield_curve = df[::15]
    
    # Define your custom colormap starting from a light blue to a darker blue
    # The example uses hex color codes, but you can adjust these colors as needed
    start_color = '#003366' # Very light blue, almost white-blue
    end_color =  '#e0f7fa'  # Deep navy blue

    colormap = mcolors.LinearSegmentedColormap.from_list("my_colormap", [start_color, end_color])
    
    # Normalize date index for color mapping
    num_dates = len(yield_curve.index)
    date_norm = mcolors.Normalize(vmin=0, vmax=num_dates - 1)
    
    plt.figure(figsize=(10, 6))
    
    for i, date in enumerate(yield_curve.index):
        color = colormap(date_norm(i))
        plt.plot(yield_curve.columns, yield_curve.loc[date], label=date.strftime('%Y-%m-%d'), color=color, linewidth=2, marker='o')
    
    plt.title('Yield Curves')
    plt.xlabel('Maturity')
    plt.ylabel('Yield (%)')
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()
    plt.legend(title='Date', loc='upper right')

    if show ==1:
        plt.show()
    
    else:
        pass


# Example call to the function would now require a pre-defined DataFrame 'df'
# df = get_yield(offset=3)
# graph_yield(df=df)

def graph_datatable(ax, df, title):
    ax.axis('tight')
    ax.axis('off')
    table = ax.table(cellText=df.values, colLabels=df.columns, loc='center', cellLoc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(5)
    ax.set_title(title)


import io  # For BytesIO

# Modified graph_tech_optimized function from before
def graph_tech_optimized(df, ticker='Ticker'):
    df['date'] = pd.to_datetime(df['date'])
    current_date = datetime.today()
    periods = {
        'All time': pd.Timestamp.min,
        '1 year': current_date - timedelta(days=365),
        '6 months': current_date - timedelta(days=180),
        '3 months': current_date - timedelta(days=90),
    }
    fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(10, 8))
    axes = axes.flatten()
    for ax, (period, start_date) in zip(axes, periods.items()):
        temp_df = df[df['date'] >= start_date] if period != 'All time' else df
        for column in temp_df.columns[1:]:
            if '+2StDev' in column:
                ax.fill_between(temp_df['date'], temp_df[column], temp_df[temp_df.columns[temp_df.columns.get_loc(column)+1]], color='lightblue', alpha=0.5, label='+/-2 StDev')
            elif 'close' in column:
                ax.plot(temp_df['date'], temp_df[column], label=column, color='black')
            elif '-2StDev' in column:
                continue
            else:
                ax.plot(temp_df['date'], temp_df[column], label=column, linewidth=0.6)
        ax.set_title(f'Technicals for {ticker} ({period})', fontsize=8)
        ax.legend(fontsize=7)
        ax.tick_params(axis='y', labelsize=7)
        ax.tick_params(axis='x', labelsize=7)
        ax.xaxis.set_major_locator(plt.MaxNLocator(5))
        ax.grid(True)

    plt.tight_layout()
    plt.subplots_adjust(wspace=0.25, hspace=0.25)
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight', dpi=300)
    buffer.seek(0)
    plt.close()
    return buffer



######################!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!#########################


def graph_comm_returns(asset, metric='close'):
    # Define dynamic start dates for each selected period based on today's date
    today = datetime.now()
    dates = {
        '1 week': today - timedelta(days=7),
        '3 months': today - timedelta(days=90),
        '6 months': today - timedelta(days=180),
        '1 year': today - timedelta(days=365)
    }

    # Fetch and preprocess commodity data
    preped_df = get_commodity(asset, metric)  # Assume this function is defined elsewhere
    preped_df['date'] = pd.to_datetime(preped_df['date'])
    preped_df.sort_values('date', inplace=True)  # Ensure data is sorted by date

    # Fill missing data
    preped_df.fillna(method='ffill', inplace=True)  # Forward fill to carry last observation forward
    preped_df.fillna(method='bfill', inplace=True)  # Backward fill to handle any initial NaNs

    # Setting up subplots grid
    fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(12, 10))
    axes = axes.flatten()

    for ax, (period, start_date) in zip(axes, dates.items()):
        # Filter data for the relevant date range
        temp_df = preped_df[(preped_df['date'] >= start_date) & (preped_df['date'] <= today)].copy()

        # Calculate base returns for each commodity
        base_prices = temp_df.iloc[0][1:]  # Base prices from the first row after filtering by date
        for commodity in temp_df.columns[1:]:
            temp_df[f'returns_{commodity}'] = (temp_df[commodity] / base_prices[commodity] - 1) * 100
            ax.plot(temp_df['date'], temp_df[f'returns_{commodity}'], label=commodity, linewidth=1.2)

        ax.set_title(f'Simple Returns for ({period})', fontsize=8)
        ax.legend(fontsize=8)
        ax.tick_params(axis='both', which='major', labelsize=7)

        # Set major locator for x-axis to improve readability
        ax.xaxis.set_major_locator(plt.MaxNLocator(5))
        ax.grid(True)

    plt.tight_layout()
    plt.subplots_adjust(wspace=0.25, hspace=0.2)  # Adjust spacing to avoid label overlap
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight', dpi=300)
    buffer.seek(0)
    plt.close()
    return buffer




def graph_segmentation(ticker):
    product_df, geo_df = get_segmentation(ticker)
    # Filter data for the last period in each dataset
    latest_product_date = product_df['Date'].max()
    latest_product_data = product_df[product_df['Date'] == latest_product_date]

    latest_geo_date = geo_df['Date'].max()
    latest_geo_data = geo_df[geo_df['Date'] == latest_geo_date]

    # Plotting
    fig, ax = plt.subplots(1, 2, figsize=(14, 7))

    ax[0].pie(latest_product_data['Revenue'], labels=latest_product_data['Product'], autopct='%1.1f%%')
    ax[0].set_title(f'Product Segmentation \n{ticker} on {latest_product_date}')

    ax[1].pie(latest_geo_data['Revenue'], labels=latest_geo_data['Segment'], autopct='%1.1f%%')
    ax[1].set_title(f'Geographic Segmentation \n{ticker} on {latest_geo_date}')

    plt.tight_layout()
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight', dpi=300)
    buffer.seek(0)
    plt.close()

    return buffer


def calculate_subplot_grid_size(num_indicators):
    if num_indicators <= 2:
        return 1, num_indicators
    elif num_indicators == 3:
        return 2, 2
    else:  # For 4 indicators
        return 2, 2


def graph_economic_indicators(indicators):
    num_indicators = len(indicators)
    nrows, ncols = calculate_subplot_grid_size(num_indicators)
    fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(10, 8))
    axes = axes.flatten()  # Flatten the 2D array of axes for easy iteration
    
    # Plot each indicator on its subplot
    for i, indicator in enumerate(indicators):
        if i < len(axes):  # Check to avoid index error if fewer indicators than subplots
            data = get_economics(indicator)
            ax = axes[i]
            ax.plot(data.index, data[indicator], label=indicator)
            ax.set_title(f'{indicator}', fontsize=8)
            ax.legend(fontsize=7)
            ax.tick_params(axis='y', labelsize=7)
            ax.tick_params(axis='x', labelsize=7)
            ax.xaxis.set_major_locator(plt.MaxNLocator(5))
            ax.grid(True)
    
    # Hide unused subplots if indicators are fewer than subplots
    for j in range(i + 1, len(axes)):
        axes[j].axis('off')
    
    plt.tight_layout()
    plt.subplots_adjust(wspace=0.25, hspace=0.25)
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight', dpi=300)
    buffer.seek(0)
    plt.close()

    return buffer




#########


def graph_calendar_table(calendar_data):
    """Plot the economic calendar data as a table using Matplotlib."""
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.axis('tight')
    ax.axis('off')
    table = ax.table(cellText=calendar_data.values,
                     colLabels=calendar_data.columns,
                     cellLoc='center',
                     loc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(8)  # Adjust the font size as desired

    # Adjusting alignment of the last column (assuming it's the rightmost column)
    last_col_idx = len(calendar_data.columns) - 1
    for key, cell in table._cells.items():
        if key[0] != 0 and key[1] == last_col_idx:
            cell.set_text_props(ha='left', ma='left')  # Align text to the left
            cell._text.set_position((100, 0))  # Indent the text slightly from the very left

    ax.set_title('High Impact Events - US (Week ahead)')
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight', dpi=300)
    buffer.seek(0)
    plt.close()

    return buffer