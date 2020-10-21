from datetime import datetime
import sys

actions = [{'date': '1992/07/14 11:12:30', 'action': 'BUY', 'price': '12.3', 'ticker': 'AAPL', 'shares': '500'}, {'date': '1992/07/14 11:12:30', 'action': 'BUY', 'price': '100', 'ticker': 'TEST', 'shares': '500'}, {'date': '1992/09/13 11:15:20', 'action': 'SELL', 'price': '15.3', 'ticker': 'AAPL', 'shares': '100'}, {'date': '1992/10/14 15:14:20', 'action': 'BUY', 'price': '20', 'ticker': 'MSFT', 'shares': '300'}, {'date': '1992/10/17 16:14:30', 'action': 'SELL', 'price': '20.2', 'ticker': 'MSFT', 'shares': '200'}, {'date': '1992/10/19 15:14:20', 'action': 'BUY', 'price': '21', 'ticker': 'MSFT', 'shares': '500'}, {'date': '1992/10/23 16:14:30', 'action': 'SELL', 'price': '18.2', 'ticker': 'MSFT', 'shares': '600'}, {'date': '1992/10/25 10:15:20', 'action': 'SELL', 'price': '20.3', 'ticker': 'AAPL', 'shares': '300'}, {'date': '1992/10/25 16:12:10', 'action': 'BUY', 'price': '18.3', 'ticker': 'MSFT', 'shares': '500'}]
stock_actions = [{'date': '1992/08/14', 'dividend': '0.10', 'split': '', 'stock': 'AAPL'}, {'date': '1992/09/01', 'dividend': '', 'split': '3', 'stock': 'AAPL'}, {'date': '1992/10/15', 'dividend': '0.20', 'split': '', 'stock': 'MSFT'},{'date': '1992/10/16', 'dividend': '0.20', 'split': '', 'stock': 'ABC'}]


##### Preprocessing Two Input Lists ####

# label the action type in the two lists given
# converting all entries like 'shares', 'price', 'dividend', 'split' from string to float for easier calculation later
# make 'date' in consistent form "1111/11/11 11:11:11" for stcok_actions (assuming stock_actions happen at the beginning of every day 00:00:00)
for dic in actions:
  dic['label'] = 'action'
  dic['shares'] = float(dic['shares'])
  dic['price'] = float(dic['price'])


for dic in stock_actions:
  dic['label'] = 'stock_action'

  if dic['split'] == '':
    dic['split'] = float(0)
    dic['dividend'] = float(dic['dividend'])
  
  if dic['dividend'] == '':
    dic['dividend'] = float(0)
    dic['split'] = float(dic['split'])

  dic['dividend'] = float(dic['dividend'])
  dic['split'] = float(dic['split'])

  # 'date' formatting
  dic['date'] += " 00:00:00"

##### Merging two lists ######

# This list will store dictionaries from both actions[] and stock_actions[] in from the earliest to the latest
actions_master = []

# combine two lists into one based on their timestamps actions[0]['date'] <- get date
i = 0 # i tracks actions index
j = 0 # j tracks stock_actions index

while i< len(actions) and j< len(stock_actions):
  print('i:' + str(i) + '   j:' + str(j))
  # In case one list's elements are all inserted, then focus on inserting elements in the other list only
  if i==(len(actions)-1):
    actions_master.append(stock_actions[j])
    j+=1
    print('No more actions! Appending rest of stock_actions...')
    continue
  elif j==(len(stock_actions)-1):
    actions_master.append(actions[i])
    i+=1
    continue

  action_date = datetime.strptime(actions[i]['date'], "%Y/%m/%d %H:%M:%S")
  stock_action_date = datetime.strptime(stock_actions[j]['date'], "%Y/%m/%d %H:%M:%S")
  # Append the element that has the earlier date the increment that index
  if action_date >= stock_action_date:
    # i.e. stock_action happens earlier (prioritize the stock actions since we assumed they happen at the beginning of the time before any actions)
    actions_master.append(stock_actions[j])
    j+=1
  else:
    actions_master.append(actions[i])
    i+=1


##### Making the statement data structure #####

# statement = { 'date1' : [portfolio{ticker1 : {},ticker2 : {},..., dividend_income}, transcation[]], 'date2' : [portfolio{ }, transcation[]], ...}
statement = {} # a dic (date as key) with a list of portfolio{} and transaction[] as snapshots
portfolio = {} # a dic (tickers and dividend_income as key) of dics
portfolio['dividend_income'] = 0
transaction = [] # a list of disc (transactions) (transaction type as key: 'buy', 'sold', 'dividend', 'split')


for i in range(len(actions_master)):
  
  action = actions_master[i]

  # update portfolio{} & transaction[] based on the label(action/stock_action) and actions types(buy/sell or split/dividend)
  if action['label'] == 'action':
    if action['action'] == 'BUY':
      # update portfolio{} if the ticker exists, else create new ticker -> dictionary {'shares': ,'price': }
      ticker_name = action['ticker']
      if ticker_name in portfolio:
        portfolio[ticker_name]['shares'] += action['shares'] # update the share number
        portfolio[ticker_name]['price'] = action['price'] # update the share price
      else:
        # new ticker
        portfolio[ticker_name] = {}
        portfolio[ticker_name]['shares'] = action['shares']
        portfolio[ticker_name]['price'] = action['price']
      
      # update transaction[] by creating a new 
      transaction.append({'type': 'BUY', 'amount': action['shares'], 'price': action['price'], 'ticker': ticker_name})
    elif action['action'] == 'SELL':
      ticker_name = action['ticker']
      if ticker_name in portfolio:
        portfolio[ticker_name]['shares'] -= action['shares'] # update the share number
        portfolio[ticker_name]['price'] = action['price'] # update the share price
      else:
        # new ticker
        portfolio[ticker_name] = {'shares': action['shares'], 'price': action['price'], 'ticker': ticker_name}
    
      # update transaction[] by creating a new 
      transaction.append({'type': 'SELL', 'amount': action['shares'], 'price': action['price']})
  elif action['label'] == 'stcok_action':
    if action['split'] != 0:
      # it's a split stock_action (split must happens on an existing stock)
      ticker_name = action['stock']
      # update the portfolio{} and transaction[]
      portfolio[ticker_name]['shares'] *= action['split'] # update the share number
      portfolio[ticker_name]['price'] /= action['split'] # update the share price
      transaction.append({'type': 'SPLIT', 'amount': action['split'], 'shares': portfolio[ticker_name]['shares'], 'ticker': ticker_name})
    elif action['dividends'] != 0:
      # it's dividens payout
      ticker_name = action['stock']
      # update the portfolio{} and transaction[]
      portfolio['dividend_income'] += action['dividends'] * portfolio[ticker_name]['shares']
      transaction.append({'type': 'DIV', 'amount': action['dividens'], 'shares': portfolio[ticker_name]['shares'], 'ticker': ticker_name})
      
  # Check if it's the end of the day. If yes insert the snapshots of portfolio{} & transaction{} into statement{} with date as key
  try:
    today = datetime.strptime(actions_master[i]['date'], "%Y/%m/%d %H:%M:%S")
    nextDay = datetime.strptime(actions_master[i+1]['date'], "%Y/%m/%d %H:%M:%S")
    if today.date() != nextDay.date():
      print("item " + str(i) +" in actions_master")
      print("today is: " + str(today.date()) + "  tmr is: " + str(nextDay.date()))
      today_str = today.date().strftime("%Y/%m/%d")
      statement[today_str] = [portfolio, transaction]
      # reset transaction history for the new day
      transaction = []
  except IndexError:
    # out of range meaning end of the statement
    today = datetime.strptime(actions_master[i]['date'], "%Y/%m/%d %H:%M:%S")
    today_str = today.date().strftime("%Y/%m/%d")
    statement[today_str] = [portfolio, transaction]

# display the statement{} <- Note The statment is not constructed correctly except timestamps are right
print(statement)

# Recall: statement = { 'date1' : [portfolio{ticker1,ticker2,..., dividend_income}, transcation{}], 'date2' : [portfolio{ }, transcation{ }], ...}
# statment = { 'date1': [ {portfolio}, [transaction] ], 'date2': [], ...}
# Code for printing out statement{} (output)
for date in statement:
  print("On " + date + ", you have:\n  print out portfolio{} & transaction[] snapshot ...")

