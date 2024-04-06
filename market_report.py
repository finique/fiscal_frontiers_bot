import pandas as pd
import numpy as np
from datetime import datetime
from dateutil.relativedelta import relativedelta
from fmp_api import get_yield

def round_up_to_2_decimals(series):
    return np.ceil(series * 100) / 100

def how_is_curve(df = get_yield(offset = 3)):
    results = []
    p1 = relativedelta(days=1)
    p2 = relativedelta(weeks=1)
    p3 = relativedelta(months=1)
    periods = {
        "1 Day": p1,
        "1 Week": p2,
        "1 Month": p3
    }

    for period_name, delta in periods.items():
        end_date = df.index.max() - delta
        nearest_date = df.index[df.index <= end_date].max()
        latest_date = df.index.max()

        # Calculate changes between the two dates
        latest_data = df.loc[latest_date]
        earlier_data = df.loc[nearest_date]
        change_in_yields = latest_data - earlier_data

        # Define term segments
        short_term = ["month1", "month2", "month3", "month6"]
        medium_term = ["year1", "year2", "year3", "year5"]
        long_term = ["year7", "year10", "year20", "year30"]

        # Calculate average changes
        avg_short_term_change = change_in_yields[short_term].mean()
        avg_medium_term_change = change_in_yields[medium_term].mean()
        avg_long_term_change = change_in_yields[long_term].mean()

        # Step 1: Determine basic curve behaviour
        if avg_short_term_change < avg_medium_term_change and avg_medium_term_change < avg_long_term_change:
            curve_behaviour = "Steepening: ΔS < ΔL"
        elif avg_short_term_change > avg_medium_term_change and avg_medium_term_change > avg_long_term_change:
            curve_behaviour = "Flattening: ΔS > ΔM > ΔL"
        elif avg_short_term_change < avg_long_term_change and avg_medium_term_change > avg_long_term_change:
            curve_behaviour = "Bull Steepening"
        elif avg_short_term_change > avg_long_term_change and avg_medium_term_change < avg_short_term_change:
            curve_behaviour = "Bear Flattening"
        elif avg_long_term_change > avg_short_term_change and avg_medium_term_change < avg_long_term_change:
            curve_behaviour = "Bear Steepening"
        elif avg_long_term_change < avg_short_term_change and avg_medium_term_change < avg_long_term_change:
            curve_behaviour = "Bull Flattening"
        else:
            curve_behaviour = "Complex Behavior"  # For patterns that do not match the above

#ΔS < ΔL, ΔM > ΔL
#ΔS > ΔL, ΔM < ΔS
#ΔL > ΔS, ΔM < ΔL
#ΔL < ΔS, ΔM < ΔL

        # Step 2: Independently check for parallel shifts
        if all(x > 0 for x in [avg_short_term_change, avg_medium_term_change, avg_long_term_change]):
            if curve_behaviour != "Complex Behavior":  # Append to existing behaviour if not complex
                curve_behaviour += "\nParallel Shift Up"
            else:
                pass  # Set as the behaviour if previously complex

        elif all(x < 0 for x in [avg_short_term_change, avg_medium_term_change, avg_long_term_change]):
            if curve_behaviour != "Complex Behavior":  # Append to existing behaviour if not complex
                curve_behaviour += "\nParallel Shift Down"
            else:
                pass  # Set as the behaviour if previously complex
        

        results.append({
        "Change since (p.p.)": period_name,
        "Curve behaviour": curve_behaviour,
        "S-T change": avg_short_term_change,
        "M-T change": avg_medium_term_change,
        "L-T change": avg_long_term_change
        })

    results_df = pd.DataFrame(results)

    results_df.iloc[:, -3:] = results_df.iloc[:, -3:].apply(round_up_to_2_decimals)
    results_df.set_index('Change since (p.p.)', inplace = True)

    return results_df



def how_is_twist(df = get_yield(offset = 3), threshold=0.05):
    changes = df.diff().dropna()  # Calculates day-to-day changes
    
    short_term = ["month1", "month2", "month3", "month6"]
    long_term = ["year10", "year20", "year30"]
    
    short_term_changes = changes[short_term].mean(axis=1)
    long_term_changes = changes[long_term].mean(axis=1)
    
    # Calculate the absolute difference and check against threshold
    diff_changes = abs(short_term_changes - long_term_changes)
    twist_criteria = (diff_changes > threshold) & (short_term_changes * long_term_changes < 0)
    
    # Determine the direction of the twist
    twist_direction = np.where(short_term_changes > long_term_changes, "Flattening Twist", "Steepening Twist")
    
    # Apply twist criteria to filter dates and directions
    twist_dates = twist_criteria[twist_criteria].index.strftime('%Y-%m-%d').tolist()
    twist_directions = twist_direction[twist_criteria]
    
    results_df = pd.DataFrame({"Date": twist_dates, "Twist & Direction": twist_directions})
    results_df.set_index('Date', inplace = True)
    
    return results_df if not results_df.empty else pd.DataFrame({"Date": [], "Detected": [], "Direction": []})





def how_is_acceleration(df = get_yield(offset = 3)):
    changes = df.diff().dropna()  # Daily changes
    acceleration = changes.diff().dropna()  # Daily acceleration

    # Define term segments
    short_term = ["month1", "month2", "month3", "month6"]
    medium_term = ["year1", "year2", "year3", "year5"]
    long_term = ["year7", "year10", "year20", "year30"]

    # Calculate the average acceleration for each term segment
    s_t_acceleration = acceleration[short_term].mean(axis=1)
    m_t_acceleration = acceleration[medium_term].mean(axis=1)
    l_t_acceleration = acceleration[long_term].mean(axis=1)

    # Group by month and summarize the trend
    monthly_s_t_summary = s_t_acceleration.resample('ME').mean().apply(lambda x: "↑" if x > 0 else "↓")
    monthly_m_t_summary = m_t_acceleration.resample('ME').mean().apply(lambda x: "↑" if x > 0 else "↓")
    monthly_l_t_summary = l_t_acceleration.resample('ME').mean().apply(lambda x: "↑" if x > 0 else "↓")

    # Combine into a single DataFrame
    results_df = pd.DataFrame({
        "1-6M": monthly_s_t_summary,
        "1-5Y": monthly_m_t_summary,
        "7-30Y": monthly_l_t_summary
    })
    results_df.index = results_df.index.strftime('%Y-%m')  # Format the index to show only year-month
    results_df = results_df.sort_index(ascending=False)
    

    return results_df


