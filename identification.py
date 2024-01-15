#!/usr/bin/python3
# Python program to create Blockchain

# Imports
import cv2
import face_recognition
import datetime as dt
import pytesseract
from PIL import Image
from difflib import SequenceMatcher

"""
Class containing functions for the biometric and text identification check.
Functions accept an image path to use for identification.
Sources:
https://realpython.com/face-recognition-with-python/
https://medium.com/@pawan329/ocr-extract-text-from-image-in-8-easy-steps-3113a1141c34
"""

class Identification:

    # Set up text recognition for the ID
    def check_identification_text(self, imagepath, name, address):
        """Scan an image to identify any text and compare it to a name and address
        Designed to work only with a provisional or full UK driving licence.

        Function will return a list with two numbers eg. [1,1] with the first being the
        text similarity percentage to the name and second to the address.
        If [-1,-1] is returned then an error has occured.

        Key arguments
        imagepath -- path for the image of the provisional or full UK driving licence eg. idphoto/image.png
        name -- name for the person to be id checked
        address -- address for the person to be id checked
        """

        # Open the image to use
        image = Image.open(imagepath)

        # Use Tesseract to extract text from the image
        pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        text = pytesseract.image_to_string(image)

        # Provisional or full UK driving licence take up multiple lines
        # Split the text string of new lines into sections
        text_split = text.splitlines()

        # Try to extract full name
        try:
            # First name should be on the third line and last name on the second line
            id_name = text_split[3] + text_split[2] # Concatenate name
        except:
            # If an error has occured then usually an image without text is being used
            name_similarity_ratio = -1 # set to -1 to record it as an error
            address_similarity_ratio = -1 # set to -1 to record it as an error
            return name_similarity_ratio, address_similarity_ratio

        # Clean up the name found on the ID licence to improve similarity check
        id_name = id_name.replace(" ","").replace(",","").upper() # Remove spaces, commas and capitalise
        id_name = id_name.replace("MR","").replace("MRS","").replace("MISS","").replace("DR","").replace("REV","").replace("MX","") # Strip titles

        # Clean up the comparison name given to the function to improve similarity check
        name = name.replace(" ","").replace(",","").upper() # Remove spaces, commas and capitalise

        # Try to extract address
        try:
            # Address should begin on the 12th line of the id text
            id_address = text_split[12]
        except:
            # If an error has occured then usually an image without text is being used
            name_similarity_ratio = -1 # set to -1 to record it as an error
            address_similarity_ratio = -1 # set to -1 to record it as an error
            return name_similarity_ratio, address_similarity_ratio

        # Some addresses go over more than one line, this is indicated by a comma
        # Check if there is a comma at the end and concatenate the next two or three lines
        # if so
        if id_address.endswith(",") or id_address.endswith("."): # Add next line if over 2 lines
            id_address = id_address + text_split[13]
            if id_address.endswith(",") or id_address.endswith("."): # Add next line if over 3 lines
                id_address = id_address + text_split[14]

        # Clean up the address found on the ID licence to improve similarity check
        id_address = id_address.replace(" ","").replace(",","").upper() # Remove spaces, commas and capitalise

        # Clean up the comparison address given to the function to improve similarity check
        address = address.replace(" ","").replace(",","").upper() # Remove spaces, commas and capitalise

        # Run the SequenceMatcher to calculate the similarity ratios for name and address
        name_similarity_ratio = SequenceMatcher(None, id_name, name).ratio()
        address_similarity_ratio = SequenceMatcher(None, id_address, address).ratio()

        # Return the similarities as a list eg. [1,1]
        return name_similarity_ratio, address_similarity_ratio

    def check_identification_face(self, image_path):
        """Scan an image to identify a single face and compare it to a live face in the webcam.
        Can work with any image.

        Function will return a "true" or "false" result to indicate if the face in each image
        matches each other.

        Key arguments
        image_path -- path for the image eg. idphoto/image.png
        """

        # Try to recognise a face in the provided image
        try:
            # Load the image file
            face = face_recognition.load_image_file(image_path)
            # Encode image for comparison
            known_encoding = face_recognition.face_encodings(face)[0]
        except:
            # If error, this means a face has not been found
            matched = "error, face not found"
            return matched

        # Once a face has been recognised in the provided image, the webcam
        # is opened to live check the user.
        # Open the webcam
        video_capture = cv2.VideoCapture(0)
        # Calculate the start time for future time out if a face cannot be found
        # This is to give a period of time for the person to adjust themselves
        # if they were unprepared for the webcame
        starttime = dt.datetime.now()

        # Loop through captures until a face and match is found or time out after
        # two minutes

        while True:
            # Capture each frame
            ret, frame = video_capture.read()

            # Find all face locations and encodings in the current frame
            face_locations = face_recognition.face_locations(frame)
            face_encodings = face_recognition.face_encodings(frame, face_locations)

            # Check if captured face matches the provided image
            for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                # Add results to matches variable
                matches = face_recognition.compare_faces([known_encoding], face_encoding)
                print("no match yet")
                # If a true match is found
                if True in matches:
                    # Set to true
                    matched = "true"
                    # Close webcam
                    video_capture.release()
                    # Return result
                    return matched


            # Stop trying after 2 minutes
            # Set 2 minute change
            time_change = dt.timedelta(minutes=0.4)
            # Set the stop time to start time plus 2 minutes

            stop_time = starttime + time_change
            # If time exceeded the stop time, the result is returned as false
            if stop_time < dt.datetime.now():
                # Set to false
                matched = "false"
                # Close webcam
                video_capture.release()
                print("time expired")
                # Return result
                return matched