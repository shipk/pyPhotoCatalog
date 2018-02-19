import photo_catalog
import pickle

if __name__ == "__main__":
	#a = photo_catalog.ph_image(r"e:\HomePhotoVideo\2004_05_01\PICT0001.JPG")
	#print(a)

	s = photo_catalog.ph_catalog()

	#d.index(r"e:\Shipkovy")
	#s.load(r"e:\Shipkovy")
	#d.load(r"e:\HomePhotoVideo")
	#d.show_doubles()
	#d.print_tree()
	
	#h = photo_catalog.ph_catalog()
	#d.index(r"e:\HomePhotoVideo")
	#h.load(r"e:\HomePhotoVideo")
	#d.show_doubles()
	
	#s.index(r"g:\shipkovy", False)
	#s.index(r"g:\ФОТО скан. альбомы и пленки Шипковы", False)

	s.index(r"e:\shipkovy", False)
	s.load(r"e:\shipkovy")
	s.show_doubles()

	#s.compare(r"g:\Shipkovy", r"e:\shipkovy", 0)
	#s.index(r"e:\HomePhotoVideo")
	
	#s.index(r"g:\HomePhotoVideo", False)
	#s.load(r"g:\HomePhotoVideo")
	#s.print_tree()
	#s.camera_stat()
	#s.print_camera_stat()
	
	#s.print_camera_stat()
	#d.show_doubles()
	#print(d)	
	#d.compare()

	#d.compare(r"e:\HomePhotoVideo", r"f:\HomePhotoVideo", 2)