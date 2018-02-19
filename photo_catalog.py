# -*- coding: utf-8 -*-
import os, os.path
import re
import datetime
from stat import *
import hashlib
import exifread
import pickle
import copy

DB_FILE_NAME = "ph_index.pkl"
incl_masks=(r".jpg$", r".avi$", r".mkv$", 	r".mp4$", r".bmp$", r".png$", r".gif$", r".cr2$", r".vob$")
excl_masks = (
	r'.info$', 
	r'^Thumbs.db$', 
	r'.picasa\.ini$',
	#'\.cr2$',
	r'.thm$',
	r'.lnk$',
	r'.tmp$',
	r'.ini$',
	r'.nri$',
	r'.t$',
	r'.mta$',
	r'^ph_index.txt$'
)

class NoIndex(Exception):
	pass
class OldIndex(Exception):
	pass
class ArgError(Exception):
	pass

def md5sum(filename):
  with open(filename, mode='rb') as f:
    d = hashlib.md5()
    while True:
      buf = f.read(10*1024*1024) # 10 mb
      if not buf:
        break
      d.update(buf)
    return d.hexdigest()
	
class ph_image:
	def __init__(self, dir, fname):
		path = os.path.join(dir, fname)
		path = os.path.normcase(path)
		stat = os.stat(path)

		self.filename = fname
		self.size = stat[ST_SIZE]
		self.mtime = stat[ST_MTIME]
		self.timestamp = str(datetime.datetime.fromtimestamp(stat[ST_MTIME]))
		self.hash_value = md5sum(path)
		self.initExif(path)
	def initExif(self, path):
		f = open(path, 'rb')
		self.exif_info = exifread.process_file(f, details = False)

		# Удаляем элементы с Thumbnail
		try:
			del self.exif_info['JPEGThumbnail']
		except KeyError:
			pass
		k = []
		for i in self.exif_info.keys():
			k.append(i)
		for i in k:
			if i[0:9] == "Thumbnail":
				del self.exif_info[i]

		f.close
	def __repr__(self):
		s = "filename=%s\nsize=%i\ntimestamp=%s\nhash_value=%s" % (self.filename, self.size, self.timestamp, self.hash_value)
		for tag in sorted(self.exif_info):
			#if tag not in ('JPEGThumbnail', 'TIFFThumbnail', 'Filename', 'EXIF MakerNote'):
			s = s + "\n\t%s = %s" % (tag, self.exif_info[tag])
		return s
	def save(self, f):
		pickle.dump(self, f)

class ph_catalog:
	"""
	Каталог файлов. 
	"""
	def __init__(self, path = None):
		"""
		Инициирование-загрузка по абсолютному пути
		"""
		if not path is None: self.load(path)
	def load(self, path):
		"""
		Загрузка каталога. Подкаталоги загружаются из файловой системы. 
		Информация о файлах загрухается из БД, если она не старше каталога, иначе информация о файлах загружается из файловой системы
		"""
		self.mtime = 0
		self.db_mtime = 0
		self.files = []
		self.cats = []
		self.path = path
		self.mtime = os.stat(path)[ST_MTIME]
		db = os.path.join(self.path, DB_FILE_NAME)
		db = os.path.normcase(db)
		if not os.path.exists(db):
			raise NoIndex(self.path)
		self.db_mtime = (os.stat(db))[ST_MTIME]
		if self.db_mtime < self.mtime:
			raise OldIndex(self.path)
		self.__load_files_db()
		self.__load_cats()
	def __load_cats(self):
		"""
		Загрузка информации о подкаталогах из файловой системы
		"""
		self.cats = []
		for file in os.listdir(self.path):
			path = os.path.join(self.path, file)
			path = os.path.normcase(path)
			stat = os.stat(path)
			if S_ISDIR(stat[ST_MODE]): 
				cat = ph_catalog(path)
				self.cats.append(cat)
			else:
				continue
	def __load_files_db(self):
		"""
		Загрузка информации о файлах в каталоге из индекса
		"""
		self.files = []
		path = os.path.join(self.path, DB_FILE_NAME)
		path = os.path.normcase(path)
		f = open(path, "rb")
		self.files = pickle.load(f)
		f.close
	def __load_files_fs(self):
		"""
		Загрузка информации о файлах в каталоге из файловой системы
		"""
		self.files = []
		for file in os.listdir(self.path):
			path = os.path.join(self.path, file)
			path = os.path.normcase(path)
			stat = os.stat(path)
			if S_ISDIR(stat[ST_MODE]): 
				continue
			else:
				# Проверяем по маске имени файла
				for k in incl_masks:
					if re.search(k, file, re.IGNORECASE): break
				else:
					continue
				f = ph_image(self.path, file)
				self.files.append(f)
	def __save_db(self):
		path = os.path.join(self.path, DB_FILE_NAME)
		path = os.path.normcase(path)
		f = open(path, "wb")
		pickle.dump(self.files, f)
		f.close
		db = os.path.join(self.path, DB_FILE_NAME)
		db = os.path.normcase(db)
		self.db_mtime = os.stat(db)[ST_MTIME]
	def index(self, path, force = False):
		"""
		Обновление индекса каталога и вложенными подкаталогов
		force = True - создание нового индекса
		"""
		self.path = path
		self.mtime = os.stat(path)[ST_MTIME]
		db = os.path.join(self.path, DB_FILE_NAME)
		db = os.path.normcase(db)
		if force or not os.path.exists(db):
			print("Creating index for " + path)
			self.__load_files_fs()
			self.__save_db()
		else:
			self.db_mtime = (os.stat(db))[ST_MTIME]
			if self.db_mtime < self.mtime:
				print("Updating index for " + path)
				self.__load_files_fs()
				self.__save_db()
			else:
				print("Up to date " + path)
		for file in os.listdir(self.path):
			if S_ISDIR((os.stat(os.path.normcase(os.path.join(path, file))))[ST_MODE]):
				self.index(os.path.normcase(os.path.join(path, file)), force)
	def __repr__(self):
		s = "%s =>\n" % (self.path)
		for f in self.files:
			s = s + "\t%s\n" % (f.filename)
		for c in self.cats:
			s = s + "\t%s\n" % (c.path)
			s = s + str(c)
		return s
	def prep_hash(self):
		"""
		Подготавливает хэш с ключом по md5, элемент хэша - массив имён файлов (с полным путём)
		"""
		hdir = {}

		def add_files(h, d):
			for f in d.files:
				if not f.hash_value in h:
					h[f.hash_value] = []
				h[f.hash_value].append(os.path.normcase(os.path.join(d.path, f.filename)))
			for c in d.cats:
				add_files(h, c)

		add_files(hdir, self)
		return hdir
	def show_doubles(self):
		hdir = self.prep_hash()
		for i in hdir:
			if len(hdir[i]) > 1:
				for k in sorted(hdir[i]):
					print("%s\t" % k, end = "")
				print("")
				
	def compare(self, path4comp, path4mod, method=0):
		"""
		Сопоставление каталогов
		path4comp - каталог для проверки
		path4mod - эталонный каталог для сопоставления
		method:
			0 - показывать файлы из path4mod, отсутствующие в path4comp
			1 - показывать совпадающее
			2 - показывать файлы из path4comp, отсутствующие в path4mod
		"""
		if not method in (0,1,2):
			raise ArgError("Unknown method",method)

		a = []
		
		cat4comp = ph_catalog(path4comp)
		cat4mod = ph_catalog(path4mod)
		
		hdir4comp = cat4comp.prep_hash()
		hdir4mod = cat4mod.prep_hash()
		
		if method == 0:
			for i in hdir4mod:
				if not i in hdir4comp:
					for k in sorted(hdir4mod[i]):
						a.append("%s\t" % k)
		elif method == 1:
			for i in hdir4comp:
				if i in hdir4mod:
					for k in sorted(hdir4comp[i]):
						a.append("%s\t" % k)
		elif method == 2:
			for i in hdir4comp:
				if not i in hdir4mod:
					for k in sorted(hdir4comp[i]):
						a.append("%s\t" % k)

		for k in sorted(a):
			print(k)
			
	def print_tree(self, cat = None, lvl=0):
		"""
		Распечатывает информацию о каталоге
		"""
		if cat is None:
			cat = self
		for file in cat.files:
			print(os.path.join(cat.path, file.filename))
			for i in sorted(file.__dict__):
				if i != "exif_info":
					print('\t%s = %s' % (i, str(file.__dict__[i])))
			for i in sorted(file.exif_info):
				try:
					print('\t\t%s = %s' % (i, file.exif_info[i]))
				except Exception:
					pass
		for cat in cat.cats:
			self.print_tree(cat, lvl+1)

	def camera_stat(self, cat = None):
		"""
		Готовит информацию о камерах
		"""
		if cat is None:
			self.cameras = {}
			cat = self
		for file in cat.files:
			image_make  = str(file.exif_info.get('Image Make', '')) 
			image_model = str(file.exif_info.get('Image Model', '')) 
			body_sn = str(file.exif_info.get('EXIF BodySerialNumber', ''))
			isn = str(file.exif_info.get('MakerNote InternalSerialNumber ', ''))
			#s_isn = re.sub(b'\xff*$', b'', isn).decode()
			im = 'Model : ' + image_make + ' ' + image_model + ' sn : ' + body_sn + ' ' + isn
			self.cameras[im] = self.cameras.get(im, 0) + 1
			#self.cameras['a'] = self.cameras.get('a', 0) + 1
			#print("%s %s" % (im, self.cameras[im]))
			#if str(file.exif_info.get('Image Make', 'Unknown')) == 'Unknown':
			#	print(file.filename)
		for ct in cat.cats:
			self.camera_stat(ct)

	def print_camera_stat(self):
		for i in sorted(self.cameras):
			print('%s = %s' % (i, self.cameras[i]))

if __name__ == "__main__":
	# a = ph_image(r"e:\HomePhotoVideo\2004_05_01\PICT0001.JPG")
	# print(a)	

	d = ph_catalog()
	d.load("d:\yashkiny\2025_10_05")
	print(a)	
