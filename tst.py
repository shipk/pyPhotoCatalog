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
	
	#s.load(r"e:\Shipkovy")
	#s.compare(r"e:\Shipkovy", r"e:\HomePhotoVideo", 1)
	#s.index(r"e:\HomePhotoVideo")
	
	#s.index(r"e:\HomePhotoVideo", True)
	s.load(r"e:\HomePhotoVideo")
	s.print_tree()
	s.camera_stat()
	s.print_camera_stat()
	
	#s.print_camera_stat()
	#d.show_doubles()
	#print(d)	
	#d.compare()

	#d.compare(r"e:\HomePhotoVideo", r"f:\HomePhotoVideo", 2)