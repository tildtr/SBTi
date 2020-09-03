import matplotlib.pyplot as plt
import pandas as pd


def print_aggregations(aggregations):
    aggregations = aggregations.dict()
    for time_frame, time_frame_values in aggregations.items():
        if time_frame_values:
            for scope, scope_values in time_frame_values.items():
                if scope_values:
                    print("{} - {}: {t:.2f} degrees Celcius".format(time_frame, scope, t=scope_values["all"]["score"]))


def collect_company_contributions(aggregated_portfolio, amended_portfolio, analysis_parameters):
    timeframe, scope, grouping = analysis_parameters
    scope = str(scope[0])
    timeframe = str(timeframe[0]).lower()
    company_names = []
    relative_contributions = []
    temperature_scores = []
    for contribution in aggregated_portfolio[timeframe][scope]['all']['contributions']:
        company_names.append(contribution.company_name)
        relative_contributions.append(contribution.contribution_relative)
        temperature_scores.append(contribution.temperature_score)
    company_contributions = pd.DataFrame(data={'company_name': company_names, 'contribution': relative_contributions, 'temperature_score': temperature_scores})
    company_contributions = company_contributions.merge(right=amended_portfolio[['company_name', grouping, 'company_market_cap', 'investment_value']], how='left', on='company_name')
    company_contributions['portfolio_percentage'] = 100 * company_contributions['investment_value'] / company_contributions['investment_value'].sum()
    company_contributions['ownership_percentage'] = 100 * company_contributions['investment_value'] / company_contributions['company_market_cap']
    company_contributions = company_contributions.sort_values(by='contribution', ascending=False)
    return company_contributions


def plot_grouped_statistics(aggregated_portfolio, company_contributions, analysis_parameters):
    timeframe, scope, grouping = analysis_parameters
    scope = str(scope[0])
    timeframe = str(timeframe[0]).lower()

    sector_investments = company_contributions.groupby(grouping).investment_value.sum().values
    sector_contributions = company_contributions.groupby(grouping).contribution.sum().values
    sector_names = company_contributions.groupby(grouping).contribution.sum().keys()
    sector_temp_scores = [aggregation.score for aggregation in aggregated_portfolio[timeframe][scope]['grouped'].values()]

    sector_temp_scores, sector_names, sector_contributions, sector_investments = \
        zip(*sorted(zip(sector_temp_scores, sector_names, sector_contributions, sector_investments), reverse=True))

    fig = plt.figure(figsize=[10, 7.5])
    ax1 = fig.add_subplot(231)
    ax1.pie(sector_investments, autopct='%1.0f%%', pctdistance=1.25, labeldistance=2)
    ax1.set_title("Investments", pad=15)

    ax2 = fig.add_subplot(232)
    ax2.pie(sector_contributions, autopct='%1.0f%%', pctdistance=1.25, labeldistance=2)
    ax2.legend(labels=sector_names, bbox_to_anchor=(1.2, 1), loc='upper left')
    ax2.set_title("Contributions", pad=15)

    ax3 = fig.add_subplot(212)
    ax3.bar(sector_names, sector_temp_scores)
    ax3.set_title("Temperature scores per " + grouping)
    ax3.set_ylabel("Temperature score")
    for label in ax3.get_xticklabels():
        label.set_rotation(45)
        label.set_ha('right')
    ax3.axhline(y=1.5, linestyle='--', color='k')


def anonymize(portfolio, provider):
    portfolio_companies = portfolio['company_name'].unique()
    for index, company_name in enumerate(portfolio_companies):
        portfolio.loc[portfolio['company_name'] == company_name, 'company_id'] = 'C' + str(index + 1)
        portfolio.loc[portfolio['company_name'] == company_name, 'company_isin'] = 'C' + str(index + 1)
        provider.data['fundamental_data'].loc[provider.data['fundamental_data']['company_name'] == company_name, 'company_id'] = 'C' + str(index + 1)
        provider.data['fundamental_data'].loc[provider.data['fundamental_data']['company_name'] == company_name, 'company_isic'] = 'C' + str(index + 1)
        provider.data['target_data'].loc[provider.data['target_data']['company_name'] == company_name, 'company_id'] = 'C' + str(index + 1)
        portfolio.loc[portfolio['company_name'] == company_name, 'company_name'] = 'Company' + str(
            index + 1)
        provider.data['fundamental_data'].loc[provider.data['fundamental_data']['company_name'] == company_name, 'company_name'] = 'Company' + str(
            index + 1)
        provider.data['target_data'].loc[provider.data['target_data']['company_name'] == company_name, 'company_name'] = 'Company' + str(
            index + 1)
    for index, company_name in enumerate(provider.data['fundamental_data']['company_name'].unique()):
        if company_name not in portfolio['company_name'].unique():
            provider.data['fundamental_data'].loc[provider.data['fundamental_data']['company_name'] == company_name, 'company_id'] = '_' + str(index + 1)
            provider.data['fundamental_data'].loc[provider.data['fundamental_data']['company_name'] == company_name, 'company_name'] = 'Company_' + str(
                index + 1)
    return portfolio, provider