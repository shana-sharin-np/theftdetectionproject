# USAGE
# python recognize_faces_image.py --encodings encodings.pickle --image examples/example_01.png

# import the necessary packages
import face_recognition
import argparse
import pickle
import cv2


def rec_face_image(imagepath):

	detected_name=[]
	try:
		idddss=imagepath.split('/')
		ap = argparse.ArgumentParser()
		data = pickle.loads(open(r'C:\Users\shana\Desktop\theft detection\Theft_Detection\faces.pickles', "rb").read())
		# load the input image and convert it from BGR to RGB
		image = cv2.imread(imagepath)
		#print(image)
		h,w,ch=image.shape
		rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
		# detect the (x, y)-coordinates of the bounding boxes corresponding
		# to each face in the input image, then compute the facial embeddings
		# for each face

		boxes = face_recognition.face_locations(rgb,
			model='hog',)
		encodings = face_recognition.face_encodings(rgb, boxes)

		# initialize the list of names for each face detected
		names = []

		# loop over the facial embeddings
		for encoding in encodings:
			# attempt to match each face in the input image to our known
			# encodings
			matches = face_recognition.compare_faces(data["encodings"],
				encoding,tolerance=0.5)
			name = "Unknown"
			print (matches)

			# check to see if we have found a match
			if True in matches:
				# find the indexes of all matched faces then initialize a
				# dictionary to count the total number of times each face
				# was matched
				matchedIdxs = [i for (i, b) in enumerate(matches) if b]
				counts = {}

				# loop over the matched indexes and maintain a count for
				# each recognized face face
				for i in matchedIdxs:

					name = data["names"][i]
					counts[name] = counts.get(name, 0) + 1
					print(name,"================")
					if name not in detected_name:
						detected_name.append(name)
				print(counts, " rount ")
				# determine the recognized face with the largest number of
				# votes (note: in the event of an unlikely tie Python will
				# select first entry in the dictionary)

				name = max(counts, key=counts.get)
				print("result1111111", name)
	except:
		pass
	return detected_name


def rec_face_image1(image):
	detected_name=[]

	data = pickle.loads(open(r'C:\Users\shana\Desktop\theft detection\Theft_Detection\faces.pickles', "rb").read())
	# load the input image and convert it from BGR to RGB

	#print(image)
	h,w,ch=image.shape
	rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
	# detect the (x, y)-coordinates of the bounding boxes corresponding
	# to each face in the input image, then compute the facial embeddings
	# for each face

	boxes = face_recognition.face_locations(rgb,
		model='hog',)
	encodings = face_recognition.face_encodings(rgb, boxes)

	# initialize the list of names for each face detected
	names = []

	# loop over the facial embeddings
	for encoding in encodings:
		# attempt to match each face in the input image to our known
		# encodings
		matches = face_recognition.compare_faces(data["encodings"],
			encoding,tolerance=0.5)
		name = "Unknown"
		print (matches)

		# check to see if we have found a match
		if True in matches:
			# find the indexes of all matched faces then initialize a
			# dictionary to count the total number of times each face
			# was matched
			matchedIdxs = [i for (i, b) in enumerate(matches) if b]
			counts = {}

			# loop over the matched indexes and maintain a count for
			# each recognized face face
			for i in matchedIdxs:

				name = data["names"][i]
				counts[name] = counts.get(name, 0) + 1
				print(name,"================")
				if name not in detected_name:
					detected_name.append(name)
			print(counts, " rount ")
			# determine the recognized face with the largest number of
			# votes (note: in the event of an unlikely tie Python will
			# select first entry in the dictionary)

			name = max(counts, key=counts.get)
			print("result1111111", name)
	return detected_name

# print(rec_face_image(r"C:\Users\krish\PycharmProjects\OSN_TheftDetection\media\chatbot.png"))
