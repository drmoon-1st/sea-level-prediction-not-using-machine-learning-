import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
import requests
import seaborn as sns

import warnings
warnings.filterwarnings('ignore')

'''web scrapping'''
db = [] # all data
db2 = [] # elevation
db3 = [] # country name

main_url = requests.get("https://ko.wikipedia.org/wiki/%EC%B5%9C%EA%B3%A0_%EA%B3%A0%EB%8F%84%EC%88%9C_%EB%82%98%EB%9D%BC_%EB%AA%A9%EB%A1%9D")

main_soup = BeautifulSoup(main_url.text, "html.parser")

allinfo = main_soup.find("div", {"class": "mw-parser-output"}).find("table").find_all("tr")

for section in allinfo:
  a = section.find_all("td")
  for i in a:
    db.append(i.text)

'''elevation, country name'''
for i in db:
  if "\n" in i:
    v = i[:-3]
    if "," in v:
      v = v.replace(",", "")
      try:
        v = float(v)
      except:
        v = float(v[-4:])
    db2.append(v)
  
for i in db:
  if "\n" not in i:
    try:
      i = float(i)
    except:
      db3.append(i)
for i in range(0, len(db3)):
  if i % 2 != 0:
    db3[i] = 0
for i in reversed(db3):
  if i == 0:
    db3.remove(i)

##################
'''world co2 emission'''
world_data = pd.read_csv('world_data.csv', header=0)
####
'''Index(['CountryName', 'CountryCode', 'IndicatorName', 'IndicatorCode', 'Year',
       'Value'],
      dtype='object')'''
####
world_data = world_data.drop(columns=['CountryName','CountryCode','IndicatorName'])
print("null\n", world_data.isnull().sum())
CO2emission = world_data[world_data.IndicatorCode == 'EN.ATM.CO2E.KT'] # EN.ATM.CO2E.KT -> CO2 emission code
group_CO2 = CO2emission.groupby('Year')

_,axe = plt.subplots()
axe.plot(group_CO2.sum())
axe.set_xlabel("year")
axe.set_ylabel("CO2 emission")

##################
world_data2 = world_data[world_data['IndicatorCode'] == 'EN.ATM.CO2E.KT']
print("null\n", world_data2.isnull().sum())
x = sns.barplot(data=world_data2, x='Year', y='Value')
fig = x.figure
fig.set_size_inches(12,8)
plt.xticks(rotation=90)

##################
'''world temp'''
temp_data = pd.read_csv('/content/drive/MyDrive/temp.csv', header=0)
temp_data = temp_data[temp_data['Source'] == 'GISTEMP']
temp_data.drop(columns=['Source'], inplace=True)
print("null\n", temp_data.isnull().sum())

_,axe = plt.subplots()
axe.plot(temp_data['Year'], temp_data['Mean'])
axe.set_xlabel("year")
axe.set_ylabel("temp deviation")
plt.show()

##################
'''temp rate of change'''
lst = []
for i in range(100, len(temp_data['Mean'])-1):
  w = (temp_data['Mean'].iloc[i+1] - temp_data['Mean'].iloc[i]) / 1 # year[i] - year[i-1] = 1
  lst.append(w)

x = sns.barplot(x=temp_data['Year'].iloc[:36], y=lst)
fig = x.figure
fig.set_size_inches(12,8)
plt.xticks(rotation=90)

plus = []
minus = []
for i in lst:
  if i >= 0:
    plus.append(i)
  else:
    minus.append(i)
print("sum of temp by sign : ", sum(plus), "/", sum(minus))

##################
'''sea level'''
sea_data = pd.read_csv('/content/drive/MyDrive/sea.csv',header=0)
print("null\n", sea_data.isnull().sum())
sea_data.drop(columns=['오차범위(상한)', '오차범위(하한)', 'Unnamed: 4'], inplace=True)
sea_data.dropna(inplace=True)
sea_data = sea_data.astype("float64")

_,axe = plt.subplots()
axe.plot(sea_data.iloc[:, 0].astype("int64"),sea_data.iloc[:, 1])
axe.set_xlabel("year")
axe.set_ylabel("sea level")
plt.show()

##################
f, ax = plt.subplots(figsize=(10, 6))
ax.plot(group_CO2.sum()/10**8, label='CO2 emission')

ax.plot(temp_data['Year'][:57], temp_data['Mean'][:57], label='temp deviation')

ax.plot(sea_data.iloc[:, 0].astype("int64")[80:],sea_data.iloc[:, 1][80:]/200, label='sea level')
ax.set_xlabel('Year')
ax.set_ylabel('Trends')
ax.legend()
plt.show()

##################
'''corelation'''
cor_data = pd.DataFrame(index=np.arange(0,54),columns=['CO2em', 'temp', 'sealevel'])
cor_data['CO2em'] = group_CO2.sum()[3:].to_numpy().squeeze()
cor_data['temp'] = temp_data['Mean'][:54].to_numpy()[::-1]
cor_data['sealevel'] = sea_data.iloc[80:, 1].to_numpy()
cor = sns.heatmap(cor_data.corr(),annot=True)
fig = cor.figure
fig.set_size_inches(12,8)
plt.show()

##################
year = 2050 # year
year_train = np.arange(1960, 2014)
x_train = group_CO2.sum().to_numpy().squeeze()[:-3]
y_train = sea_data.iloc[80:, 1].to_numpy()

'''co2'''
p1 = x_train/year_train
W1 = 0
for i in p1:
  W1 += i
W1 = W1/len(p1)
b1 = x_train[-1]-(W1*year_train[-1])
CO2em = W1*year+b1 # CO2 emission
'''co2 & sea level'''
p2 = y_train/x_train
W2 = 0
for i in p2:
  W2 += i
W2 = W2/len(p2)
b2 = y_train[-1]-(W2*x_train[-1])
height = W2*CO2em+b2 # sea level

disappear = []
for idx,val in enumerate(db2):
  if float(val) <= height-y_train[-1]: # height-y_train[-1] -> sea level amount of change
    disappear.append(db3[idx])
print(f"submerged country in {year} :",disappear)