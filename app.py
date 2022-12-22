from flask import Flask, render_template
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from bs4 import BeautifulSoup 
import requests

#don't change this
matplotlib.use('Agg')
app = Flask(__name__) #do not change this

#insert the scrapping here
url_get = requests.get('https://www.exchange-rates.org/history/IDR/USD/T')
soup = BeautifulSoup(url_get.content,"html.parser")

#find your right key here
table = soup.find('table', attrs={'class' : 'table'})
tr = table.find_all('tr')

row_length = len(tr)

temp = [] #initiating a list 

for i in range(1, row_length):
#insert the scrapping process here
    #scrapping process
    row = table.find_all('tr')[i]
    #use the key to take information here
    #name_of_object = row.find_all(...)[0].text
        
    #get tanggal
    tanggal = row.find_all('td')[0].text
    tanggal = tanggal.strip() #for removing the excess whitespace
        
    #get harga_harian
    harga_harian = row.find_all('td')[2].text
    harga_harian = harga_harian.strip() #for removing the excess whitespace

    temp.append((tanggal,harga_harian)) 

temp = temp[::-1]

#change into dataframe
data = pd.DataFrame(temp, columns = ('Tanggal', 'Harga_Harian'))

#insert data wrangling here

# cek tipe data
data.dtypes

# hapus ',' , '.', dan 'IDR'

data['Harga_Harian'] = data['Harga_Harian'].apply(lambda x: x.replace('IDR', ''))
data['Harga_Harian'] = data['Harga_Harian'].apply(lambda x: x.replace(',', ''))
data['Harga_Harian'] = data['Harga_Harian'].apply(lambda x: x.replace('.', ''))

# ubah tipe data
data['Harga_Harian'] = data['Harga_Harian'].astype('int64')
data['Tanggal'] = pd.to_datetime(data['Tanggal'])

# buat dua angka dibelakang koma
data['Harga_Harian'] = round((data['Harga_Harian'] * 0.00001), 2)
data['Harga_Harian']

# buat kolom baru period
data['Period'] = data['Tanggal'].dt.to_period('M')
data.head()

# visualisasi
data[['Period','Harga_Harian']].groupby(by=['Period']).mean().round(2).plot()

#end of data wranggling 

@app.route("/")
def index(): 
	
	card_data = f'{data["Harga_Harian"].mean().round(2)}' #be careful with the " and ' 

	# generate plot
	ax = data[['Period','Harga_Harian']].groupby(by=['Period']).mean().round(2).plot(figsize = (12,9)) 
	
	# Rendering plot
	# Do not change this
	figfile = BytesIO()
	plt.savefig(figfile, format='png', transparent=True)
	figfile.seek(0)
	figdata_png = base64.b64encode(figfile.getvalue())
	plot_result = str(figdata_png)[2:-1]

	# render to html
	return render_template('index.html',
		card_data = card_data, 
		plot_result=plot_result
		)


if __name__ == "__main__": 
    app.run(debug=True)