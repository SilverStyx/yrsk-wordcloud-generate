# -*- coding:utf-8 -*-
# ◂Ⓘ▸ ヨルシカ/n-buna词云生成器
import requests
import re
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import jieba
from PIL import Image
import numpy as np
from lxml import etree

headers = {
		'Referer'	:'http://music.163.com',
		'Host'	 	:'music.163.com',
		'Accept' 	:'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
		'User-Agent':'Chrome/10'
	}

# 得到某一首歌的歌词
def get_song_lyric(headers, lyric_url):
	res = requests.request('GET', lyric_url, headers=headers)
	if 'lrc' in res.json():
		lyric = res.json()['lrc']['lyric']
		new_lyric = re.sub(r'[\d:.[\]]','',lyric)
		return new_lyric
	else:
		return ''
		print(res.json())

# 过滤假名,仅保留汉字
def extract_unicode_block(string):
	hiragana_full = r'[ぁ-ゟ]'
	katakana_full = r'[゠-ヿ]'
	kanji = r'[㐀-䶵一-鿋豈-頻]'
	return re.findall(kanji, string)


# 停用词
def remove_stop_words(f):
	stop_words = ['n-buna', '作词', '作曲', '编曲', 'Arranger', '录音', '混音', '人声']
	for stop_word in stop_words:
		f = f.replace(stop_word, '')
	f = extract_unicode_block(f)
	# 过滤后重新拼接字符串
	str = ''
	for i in f:
		str += i + ' '

	return str

# 生成夜鹿词云
def create_word_cloud(f):
	print('开始生成夜鹿词云')
	f = remove_stop_words(f)
	cut_text = " ".join(jieba.cut(f,cut_all=False, HMM=True))
	# 背景图片path，按自己选择的配置
	img = Image.open(r"./yrsk.jpg")
	img_array = np.array(img)
	wc = WordCloud(
		background_color='white',
		mask=img_array,
		# 字体可以自行更换
		font_path="./fot.ttf",
		max_words=50,
		max_font_size=300,
		width=800,
		height=800,
		mode='RGBA',
		#random_state='30#',
    )
	print(cut_text)
	wordcloud = wc.generate(cut_text)
	# 写图片
	wordcloud.to_file("wordcloud.png")
	# 显示文件
	plt.imshow(wordcloud)
	plt.axis("off")
	plt.show()


def get_songs(artist_id):
	page_url = 'https://music.163.com/artist?id=' + artist_id
	res = requests.request('GET', page_url, headers=headers)
	html = etree.HTML(res.text)
	href_xpath = "//*[@id='hotsong-list']//a/@href"
	name_xpath = "//*[@id='hotsong-list']//a/text()"
	hrefs = html.xpath(href_xpath)
	names = html.xpath(name_xpath)
	song_ids = []
	song_names = []
	for href, name in zip(hrefs, names):
		song_ids.append(href[9:])
		song_names.append(name)
		print(href, '  ', name)
	return song_ids, song_names


artist_id = '981185'
music_id = '1870469768'
[song_ids, song_names] = get_songs(artist_id)

# 所有歌词
all_word = ''

# 获取每首歌歌词
if artist_id != '':
	for (song_id, song_name) in zip(song_ids, song_names):
		# 歌词API URL
		lyric_url = 'http://music.163.com/api/song/lyric?os=pc&id=' + song_id + '&lv=-1&kv=-1&tv=-1'
		lyric = get_song_lyric(headers, lyric_url)
		all_word = all_word + ' ' + lyric
		print(song_name)
else:
	# 获取单首歌的歌词
	lyric_url = 'http://music.163.com/api/song/lyric?os=pc&id=' + music_id + '&lv=-1&kv=-1&tv=-1'
	lyric = get_song_lyric(headers, lyric_url)
	all_word = all_word + ' ' + lyric
	print(music_id)

#根据词频 生成词云
create_word_cloud(all_word)
