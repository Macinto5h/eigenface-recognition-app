"""
eigenface.py

Version 0.1

By: M.J. Camara

Implements the Eigenface algorithm in its own class with functions
"""

# import opencv
import cv2
import os
import sys
import numpy as np
from mergesort import MergeSort

"""
Eigenface class that contains all of its functions, fields, etc.
"""
class Eigenface:

	"""
	Loads images from a given directory, and returns them as an array
	"""
	def getImages(self, directory):
		image_array = []
		# Load each image from the directory
		for file in os.listdir(directory):
			image = cv2.imread("{}{}".format(directory,file), 0)
			# Removes null cases
			if image is not None:
				image_array.append(image)
		return image_array

	"""
	Initializer
	"""
	def __init__(self, test_dir, user_dir, eigenface_dir, avg_dir, image_dim):
		# "Constants"
		self.FACE_NUMBER = 25
		self.TEST_DIR = test_dir
		self.USER_DIR = user_dir
		self.EIGENFACE_DIR = eigenface_dir
		self.AVG_DIR = avg_dir
		self.IMAGE_DIM = image_dim

		# Fields
		self.images = self.getImages(self.TEST_DIR) if os.listdir(self.TEST_DIR) else []
		self.users = self.getImages(self.USER_DIR) if os.listdir(self.USER_DIR) else []
		# self.avg_face = (self.getImages(self.AVG_DIR))[0] if os.listdir(self.AVG_DIR) else np.zeros((self.IMAGE_DIM[0], self.IMAGE_DIM[1]))
		self.eigenfaces = np.zeros((self.FACE_NUMBER, self.IMAGE_DIM[0] * self.IMAGE_DIM[1]))

	"""
	Builds/Rebuilds eigenfaces when called
	"""
	def build(self):
		# convert all of the loaded images into a matrix for the Eigenface algorithm to use
		# Create the image matrix where the image data can be manipulated
		image_matrix = np.zeros((len(self.images) + len(self.users), self.IMAGE_DIM[0] * self.IMAGE_DIM[1]))
		# Add flattened image data into the image matrix
		im_index = 0
		for i in range(0, len(self.images)):
			image_matrix[im_index,:] = self.images[i].flatten()
			im_index += 1
		for i in range(0, len(self.users)):
			image_matrix[im_index,:] = self.images[i].flatten()
			im_index += 1
		# Calculate the mean image with the image matrix
		matrix_sum = image_matrix[0,:]
		for i in range(1, len(image_matrix)):
			matrix_sum = matrix_sum + image_matrix[i,:]
		mean = matrix_sum * (1 / len(image_matrix)) 
		# Create the average face
		mean = mean.astype(np.uint8)
		self.avg_face = mean.reshape(self.IMAGE_DIM)
		cv2.imwrite("{}avg_face.jpg".format(self.AVG_DIR), self.avg_face)
		# Subtract the mean from all of the original images
		for i in range(0, len(image_matrix)):
			image_matrix[i,:] = image_matrix[i,:] - mean
		# Create a matrix with equivalent eigenvectors with the covariance
		square_matrix = image_matrix.dot(np.transpose(image_matrix))
		# retrieve the vectors and the values
		eigenvalues, eigenvectors = np.linalg.eig(square_matrix)
		start_index = 2
		end_index = self.FACE_NUMBER + 2
		eigenface_index = 0
		for i in range(start_index, end_index):
			eigenface = eigenvectors[i,0] * image_matrix[i,:]
			for j in range(start_index + 1, end_index):
				eigenface += eigenvectors[i,j] * image_matrix[j,:]
			self.eigenfaces[eigenface_index,:] = eigenface
			eigenface_index += 1
		for i in range(len(self.eigenfaces)):
			cv2.imwrite('{}{}.jpg'.format(self.EIGENFACE_DIR, i), self.eigenfaces[i,:].reshape(self.IMAGE_DIM))
	"""
	Returns the distances of a given input image
	"""
	def getDistances(self, input_image):
		# read_image = cv2.imread(input_image, 0)
		read_image = input_image
		weight_vectors = self.getWeightVectors(read_image)

		fc_dist = sys.maxsize
		matrix_len = len(weight_vectors)

		for i in range(len(self.users)):
			face_class = self.getWeightVectors(self.users[i])
			distance = np.linalg.norm(weight_vectors - face_class)

			if (distance < fc_dist):
				fc_dist = distance
		image_dif = (read_image - self.avg_face).flatten()
		face_space_var = np.zeros(len(image_dif))
		for i in range(self.FACE_NUMBER):
			face_space_var += (weight_vectors[i] * self.eigenfaces[i])
		fs_dist = np.linalg.norm(image_dif - face_space_var)
		return fc_dist, fs_dist

	"""
	Returns the weight vectors of a given image
	"""
	def getWeightVectors(self, input_image):
		# Initialize local weight vector
		weight_vectors = np.zeros(len(self.eigenfaces))
		# Add entries into weight vector
		for i in range(len(self.eigenfaces)):
			vector = self.eigenfaces[i]
			img_dif = (input_image - self.avg_face).flatten()
			w_vector = (np.transpose(vector)).dot(img_dif)
			weight_vectors[i] = w_vector
		return weight_vectors
if __name__ == '__main__':
	# Initialize class
	eigenface = Eigenface("../eigenface-training-images/", "./users/", "./eigenfaces/", "./avg_face/", (218, 178))
	eigenface.build()
	# window_name = 'Loading average face'
	# cv2.namedWindow(window_name)
	# output = cv2.resize(eigenface.avg_face, (0,0), fx = 2, fy = 2)
	# cv2.imshow(window_name, output)
	# cv2.waitKey(0)
	# cv2.destroyAllWindows()
	photo = cv2.imread("../eigenface-training-images/mdark-01.jpg",0)
	fc_dist, fs_dist = eigenface.getDistances(photo)
	print("This is fc dist: {:.2e}, this is fs dist: {:.2e}".format(fc_dist, fs_dist))