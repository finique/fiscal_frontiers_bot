import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import matplotlib.colors as mcolors
from fmp_api import get_yield
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




import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
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
                ax.fill_between(temp_df['date'], temp_df[column], temp_df[temp_df.columns[temp_df.columns.get_loc(column)+1]], color='lightblue', alpha=0.5, label='StDev Band')
            elif 'close' in column:
                ax.plot(temp_df['date'], temp_df[column], label=column, color='black')
            elif '-2StDev' in column:
                continue
            else:
                ax.plot(temp_df['date'], temp_df[column], label=column, linewidth=0.6)
        ax.set_title(f'Technicals for {ticker} for {period}', fontsize=8)
        ax.legend(fontsize=6)
        ax.tick_params(axis='y', labelsize=6)
        ax.tick_params(axis='x', labelsize=6)
        ax.xaxis.set_major_locator(plt.MaxNLocator(5))
    plt.tight_layout()
    plt.subplots_adjust(wspace=0.25, hspace=0.25)
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight', dpi=300)
    buffer.seek(0)
    plt.close()
    return buffer

