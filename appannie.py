import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import os
import datetime
from datetime import date
import time
import random
import string


def crawling(date, product_id, type_, product_name, proxy=None):

	start_time = time.time()

	headers = {
		'authority': 'www.appannie.com',
		'accept': 'text/plain, */*; q=0.01',
		'x-requested-with': 'XMLHttpRequest',
		'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
		'sec-gpc': '1',
		'sec-fetch-site': 'same-origin',
		'sec-fetch-mode': 'cors',
		'sec-fetch-dest': 'empty',
		'referer': 'https://www.appannie.com/headless/udw/apps/ios/app/'+product_id+'/app-ranking/?app_slug='+product_id+'&market_slug=ios&headless=yes&device=iphone&type='+type_+'&date='+date,
		'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
		'cookie': 'csrftoken=hNALzrkY3vEHLWksJBEIBjgXgMmSNMHq; aa_language=en; django_language=en; sessionId=".eJxVjb9Lw0AYQGNaU4n4q-isoy7BxlrTtZ1UXIoHtx1f7r62R-Mll-9OqSA4if6HgrN_hJspguL2ePB4z-GTXTvme0EQEBLp0lRYkyaHxr3yrUYL8G4uPGEttLr6ej8M2EYBZuZhhiyUhu_8tQIN5AWq65C3GwukFT9qoAfDocrOBlPsXfRlhtkgzVSWnk_TFBX2kW26koSvFDhUNnzj3f_jHOQCjeKnjX7AHAwUS6clJSBl6Y1LxkB4aQgNaafv8aZUWIx-IrYLBdZOyDnKhXD6DuVqs4L4F2yLxZ3Pzna034oOPmS1dI-xYLfj2LZPJnb9ZWIjn3wD8alh3A:1m3YFX:31ZUhwxGxIT6onl0fujeE9Lu_wg";',	
	}

	params = (
		('type', type_),
		('device', 'iphone'),
		('date', date),
	)

	response = requests.get('https://www.appannie.com/apps/ios/app/'+product_name+'/ranking_table/', headers=headers, params=params, proxies={'http':proxy, 'https':proxy})

	if response.status_code != 200:
		print('Error')
		return None

	print(proxy, response, date, 'Success!', round(time.time()-start_time, 2))

	return response.content

def format_0(titles, stores, ranks, date):

	store_names = []
	store_nums = []

	for i, store in enumerate(stores):
		if i < 6:
			store_names.append(store.text)
		else:
			ls = store.text.split()
			to_add = []
			for i, val in enumerate(ls):
				if '▼' in val:
					to_add.append(int('-' + val[1:]))
				elif '▲' in val:
					to_add.append(int(val[1:]))
				elif val == '=':
					to_add.append(0)
				elif val == '0':
					try:
						to_add.append(int(val))
						if '▼' in ls[i+1] or '▲' in ls[i+1] or '=' in ls[i+1]:
							pass
						else:
							to_add.append(0)
					except:
						to_add.append(0)
				else:
					try:
						to_add.append(int(val))
					except:
						to_add.append(float('NaN'))
						
			store_nums.append(to_add)

	store_titles = []
	for title in titles:
		store_titles.append(title.text)

	store_nums = [dict(zip(store_titles, [nums[i:i+2] for i in range(0, len(nums), 2)])) for nums in store_nums]
	stores_ls = list(zip(store_names, store_nums))

	rank_names = []
	rank_nums = []
	for i, rank in enumerate(ranks):
		if len(rank.find_all('a')) > 0:
			rank_names.append(rank.text.strip())
		else:
			ls = rank.text.split()
			to_add = []
			for i, val in enumerate(ls):
				if '▼' in val:
					to_add.append(int('-' + val[1:]))
				elif '▲' in val:
					to_add.append(int(val[1:]))
				elif val == '=':
					to_add.append(0)
				elif val == '-':
					to_add.append(float('NaN'))
					to_add.append(float('NaN'))
				else:
					try:
						to_add.append(int(val))
					except:
						to_add.append(float('NaN'))
						
			rank_nums.append(to_add)

	rank_nums = [dict(zip(store_titles, [nums[i:i+2] for i in range(0, len(nums), 2)])) for nums in rank_nums]

	ranks_ls = list(zip(rank_names, rank_nums))

	final_ls = stores_ls + ranks_ls 
	
	final_d = {date.strftime('%Y-%m-%d') : final_ls}
	final_df = pd.DataFrame(final_d)

	return final_df

def add():

	df = pd.DataFrame()

	product_id = input("product ID: ")
	product_name = input("product name: ")
	desired_name = input("desired name: ")
	type_ = input("ranks/grossing-ranks: ")

	today = (date.today() - datetime.timedelta(days=2)).strftime('%Y-%m-%d')

	line = product_id + " " + product_name + " " + desired_name + " " + type_

	with open('id_name.txt') as f:
		
		lines = f.read().splitlines()
		if line in lines:
			print("File already exists")
			return None

	start = date.today() - datetime.timedelta(days=89)
	end = date.today() - datetime.timedelta(days=2)
	print(f"from {start} to {end}")

	date_interval = pd.date_range(start = start, end = end, freq="d")

	for date_ in date_interval:
		
		start_time = time.time()
		
		content = crawling(date_.strftime('%Y-%m-%d'), product_id, type_, product_name)

		if content == None:
			print("Please go to check the box to prove that you are a human...")
			break

		soup = BeautifulSoup(content, 'html.parser')
		titles = soup.find_all('th', class_='rank')
		stores = soup.find_all('tr', class_='stores')
		ranks = soup.find_all('tr', class_='ranks')

		final_df = format_0(titles, stores, ranks, date_)
		
		df = pd.concat([df, final_df], axis=1)

	print('Done!')

	df.to_csv(f'data pool/{desired_name}_{type_}.csv')

	with open('id_name.txt') as f:
		
		lines = f.read().splitlines()

	with open('id_name.txt', 'a') as f:

		if line not in lines:

			f.write(line + '\n')

def check_update():

	path = 'data pool'

	for file in os.listdir(path):

		if '.csv' in file:

			df = pd.read_csv(path+'/'+file)

			dates = df.columns.to_list()

			yield (path+'/'+file, dates[-1])

def update():

	today = date.today()
	required = date.today() - datetime.timedelta(days=2)

	need_updates = []

	for file in check_update():
		
		if file[-1] != required.strftime('%Y-%m-%d'):
			print(file[0], file[-1], 'NOT up to date')

			start = datetime.datetime.strptime(file[1], '%Y-%m-%d') + datetime.timedelta(days=1)

			need_updates.append([file[0], start.strftime('%Y-%m-%d'), required.strftime('%Y-%m-%d')])

		elif file[-1] == required.strftime('%Y-%m-%d'):
			print(file[0], file[-1], 'up to date')

	print()
	print(f'There are {len(need_updates)} apps need to be updated')

	if len(need_updates) != 0:

		print()
		print("Today is", today, "last update should be", required)
		command = input('Do you want to update? (y/other keys to leave) ')

		if command == 'y':

			for i, file in enumerate(need_updates):

				df = pd.read_csv(file[0], index_col=0)

				start = file[1]
				end = file[-1]

				date_interval = pd.date_range(start = start, end = end, freq="d")

				with open('id_name.txt') as f:
			
						lines = f.read().splitlines()

				lines = dict([(line.split()[-2], [line.split()[0], line.split()[1]]) for line in lines if line != ""])

				product = file[0].replace('data pool/', '')
				product = product.replace('.csv', '')
				desired_name = product.split('_')[0]
				type_ = product.split('_')[1]
				product_id = lines[desired_name][0]
				product_name = lines[desired_name][1]

				print(f'updating {desired_name}...')

				for date_ in date_interval:
	
					content = crawling(date_.strftime('%Y-%m-%d'), product_id, type_, product_name)

					if content == None:
						print("Please go to check the box to prove that you are a human...")
						break

					soup = BeautifulSoup(content, 'html.parser')
					titles = soup.find_all('th', class_='rank')
					stores = soup.find_all('tr', class_='stores')
					ranks = soup.find_all('tr', class_='ranks')
					
					final_df = format_0(titles, stores, ranks, date_)
					
					df = pd.concat([df, final_df], axis=1)

				print('Done!')

				df.to_csv(f'data pool/{desired_name}_{type_}.csv')

def report():

	path = 'data pool'

	for file in os.listdir(path):

		if '.csv' in file:

			df = pd.read_csv(path+'/'+file, index_col=0)

			dates = df.columns.to_list()

			print(file)
			print('		From:', dates[0], 'Last Update:', dates[-1])

def extract():

	path = 'data pool'

	for file in os.listdir(path):

		if '.csv' in file:

			df = pd.read_csv(path+'/'+file, index_col=0)
			
			s = 0
			start = df.columns[0]

			
			e = len(df.columns) - 1
			end = df.columns[-1]

			ds = dict()

			for i, col in enumerate(df):  

				if i >= s and i <= e:
					for info in df[col]:

						nan = float('NaN')

						try:
							info = eval(info)
							region = info[0]

							for key in info[1]:
								if key not in ds:
									ds[key] = dict()

							vs = dict()

							for key, val in info[1].items():
								vs[key] = val

							
							for key, val in ds.items():
								try:
									ds[key][region].append(vs[key][0])
								except:
									try:
										ds[key][region] = [float('NaN')]*i + [vs[key][0]]
									except:
										ds[key][region].append(float('NaN'))
						except:
							pass

				for key, val in ds.items():
					for k, v in val.items():
						if len(v) < (i+1):
							v.append(float('NaN'))

			for key, val in ds.items():
				ds[key] = pd.DataFrame(ds[key])
				ds[key].index = pd.date_range(start = start, end = end, freq="d").strftime('%Y-%m-%d') 

			required = ['# of countries - rank 1 reached', 
					'# of countries - rank 5 reached', 
					'# of countries - rank 10 reached', 
					'# of countries - rank 100 reached',
					'# of countries - rank 500 reached', 
					'# of countries - rank 1000 reached', 
					'China', 
					'Hong Kong',
					'Taiwan',
					'Spain',
					'Russia',
					'Brazil', 
					'India', 
					'South Korea',
					'Saudi Arabia', 
					'Turkey', 
					'Singapore', 
					'United States',
					'Germany',
					'Japan', 
					'France',
					'United Kingdom', 
					'Mexico', 
					'Argentina', 
					'Indonesia', 
					'Thailand', 
					'Malaysia', 
					'Philippines', 
					'Vietnam', 
					'Israel', 
					'Iran', 
					'Egypt', 
					'United Arab Emirates', 
					'Iraq',
					'Qatar',
					'Nigeria']

			for key, val in ds.items():

				to_remove = []
				output = pd.DataFrame()
				for region in required:
					try:
						output[region] = val[region]
						to_remove.append(region)
					except:
						output[region] = [float('NaN')]*(e-s+1)

				output = pd.concat([output, val.drop(to_remove, axis=1)], axis=1)
				file = file.split('.')[0]
				output.to_excel('lab/'+file+'_'+key+'.xlsx')



if __name__ == '__main__':

	command = input('What can I help you? \'menu\' to check all the commands ')
	print()

	while command != 'exit':
		
		if command == 'add':
			add()

		elif command == 'report':
			report()

		elif command == 'update':
			update()

		elif command == 'extract':
			extract()

		elif command == 'menu':
			print('add -- add new app data to data pool')
			print('update -- update all the app data in the data pool')
			print('report -- report all the app data situation in the data pool')
			print('extract -- extract the excel file you want')
			print('exit -- leave the survice')

		print()
		command = input('What can I help you? ')
		print()
