# Python Programme to test Identification class
import os
import inspect
import sys
cdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(cdir)
sys.path.insert(0, parentdir)

# Setup for Identification
from identification import Identification
id = Identification()

# Add test credentials
from testdetails import myname, myaddress, mypostcode

# Create list of image paths
with open("test/test_images/filenames.txt","r") as image_filenames:
    images = image_filenames.readlines()
    images.pop(0)

    my_image_paths = []
    for i in images:
        image = "test/test_images/" + i[:-1]
        my_image_paths.append(image)


# T E X T   R E C O G N I T I O N   T E S T S

# Testing Expected Passes
def text_positive(image_paths, name, address):
    """Tests the results of the text checks
    and writes to a positive results file

    Key arguments
    image_paths -- list of image urls for images to be checked
    name -- correct name to match id
    address -- correct address to match id
    """
    print("Starting test...")
    text_positive_results = []

    # For each image in the list of files, run the text check
    for img in image_paths:
        text_result = id.check_identification_text(img, name, address)
        if (text_result[0] > 0.5 and text_result[1] > 0.5) or text_result[0] > 0.75:
            # If it passes as expected in the tool, return this result
            result = "pass"
        else:
            # else fail
            result = "fail"
        final_result = [img, result, text_result[0], text_result[1]]
        text_positive_results.append(final_result)
        with open("test/results/text_positive_results.txt","a") as p_results:
            p_results.write("%s\n" % final_result)
        print("Image " + str(len(text_positive_results)) + " complete.")
                
    print("Test complete.")
    return text_positive_results

# Testing Expected Failures
def text_negative(image_paths, name, address):
    """Tests the results of the text checks
    and writes to a negative results file

    Key arguments
    image_paths -- list of image urls for images to be checked
    name -- incorrect name to match id
    address -- incorrect address to match id
    """
    print("Starting test...")
    text_negative_results = []
    for img in image_paths:
        text_result = id.check_identification_text(img, name, address)
        if (text_result[0] > 0.5 and text_result[1] > 0.5) or text_result[0] > 0.75:
            result = "pass"
        else:
            result = "fail"
        final_result = [img, result, text_result[0], text_result[1]]
        text_negative_results.append(final_result)
        with open("test/results/text_negative_results.txt","a") as p_results:
            p_results.write("%s\n" % final_result)
        print("Image " + str(len(text_negative_results)) + " complete.")

    print("Test complete.")
    return text_negative_results

# U N C O M M E N T   T O   R E F R E S H   R E S U L T S
# Positive results (expecting a match)
with open("test/results/text_positive_results.txt","w") as text_positive_file:
    text_positive(my_image_paths, myname, myaddress + mypostcode)
    text_positive_file.close()
# Negative results (expecting a no match)
#with open("test/results/text_negative_results.txt","w") as text_negative_file:
    #text_negative(my_image_paths, "John Smith", myaddress.replace("9","8") + mypostcode)
    #text_negative_file.close()


# Read positive and negative results from the file
text_positive_results = []
text_negative_results = []
with open("test/results/text_positive_results.txt","r") as p_results:
    for line in p_results:
        result = line[:-1] # Remove new line character
        result = result.strip('][').split(', ')
        text_positive_results.append(result)

with open("test/results/text_negative_results.txt","r") as n_results:
    for line in n_results:
        result = line[:-1] # Remove new line character
        result = result.strip('][').split(', ')
        text_negative_results.append(result)

# Create empty list to store results
text_results = []

# All results
# Get the count of True Positives, False Positives, True Negatives and False Negatives
text_true_positives = sum(1 for r in text_positive_results if r[1] == "'pass'")
text_false_positives = sum(1 for r in text_positive_results if r[1] == "'fail'")

text_true_negatives = sum(1 for r in text_negative_results if r[1] == "'fail'")
text_false_negatives = sum(1 for r in text_negative_results if r[1] == "'pass'")

# Use the counts to calculate the sensitivity, specificity and accuracy
text_sensitivity = text_true_positives / (text_true_positives + text_false_negatives) * 100
text_specificity = text_true_negatives / (text_false_positives + text_true_negatives) * 100
text_accuracy = (text_true_positives + text_true_negatives) / (text_true_positives + text_false_positives + text_true_negatives + text_false_negatives) * 100

# Add result to list of results
text_results.append(["All Results        ", text_sensitivity, text_specificity, text_accuracy, text_true_positives, text_false_positives, text_true_negatives, text_false_negatives])

# Good Webcam Only
# Filter to only the 'good webcam' images
gw_text_positive_results = [x for x in text_positive_results if "IMG_" in x[0]]
gw_text_negative_results = [x for x in text_negative_results if "IMG_" in x[0]]

# Get the count of True Positives, False Positives, True Negatives and False Negatives
gw_text_true_positives = sum(1 for r in gw_text_positive_results if r[1] == "'pass'")
gw_text_false_positives = sum(1 for r in gw_text_positive_results if r[1] == "'fail'")

gw_text_true_negatives = sum(1 for r in gw_text_negative_results if r[1] == "'fail'")
gw_text_false_negatives = sum(1 for r in gw_text_negative_results if r[1] == "'pass'")

# Use the counts to calculate the sensitivity, specificity and accuracy
gw_text_sensitivity = gw_text_true_positives / (gw_text_true_positives + gw_text_false_negatives) * 100
gw_text_specificity = gw_text_true_negatives / (gw_text_false_positives + gw_text_true_negatives) * 100
gw_text_accuracy = (gw_text_true_positives + gw_text_true_negatives) / (gw_text_true_positives + gw_text_false_positives + gw_text_true_negatives + gw_text_false_negatives) * 100

# Add result to list of results
text_results.append(["Good Webcam Results", gw_text_sensitivity, gw_text_specificity, gw_text_accuracy, gw_text_true_positives, gw_text_false_positives, gw_text_true_negatives, gw_text_false_negatives])

# Bad Webcam Only
# Filter to only the 'bad webcam' images
bw_text_positive_results = [x for x in text_positive_results if "WIN_" in x[0]]
bw_text_negative_results = [x for x in text_negative_results if "WIN_" in x[0]]

# Get the count of True Positives, False Positives, True Negatives and False Negatives
bw_text_true_positives = sum(1 for r in bw_text_positive_results if r[1] == "'pass'")
bw_text_false_positives = sum(1 for r in bw_text_positive_results if r[1] == "'fail'")

bw_text_true_negatives = sum(1 for r in bw_text_negative_results if r[1] == "'fail'")
bw_text_false_negatives = sum(1 for r in bw_text_negative_results if r[1] == "'pass'")

# Use the counts to calculate the sensitivity, specificity and accuracy
bw_text_sensitivity = bw_text_true_positives / (bw_text_true_positives + bw_text_false_negatives) * 100
bw_text_specificity = bw_text_true_negatives / (bw_text_false_positives + bw_text_true_negatives) * 100
bw_text_accuracy = (bw_text_true_positives + bw_text_true_negatives) / (bw_text_true_positives + bw_text_false_positives + bw_text_true_negatives + bw_text_false_negatives) * 100

# Add result to list of results
text_results.append(["Bad Webcam Results ", bw_text_sensitivity, bw_text_specificity, bw_text_accuracy, bw_text_true_positives, bw_text_false_positives, bw_text_true_negatives, bw_text_false_negatives])

# Print text results
for r in text_results:
    print(r)


# F A C E   R E C O G N I T I O N   T E S T S

# Testing Face Positive Recognition
def face_positive(image_paths):
    """Opens the webcam and tests against
    provided images where an expected result
    is pass. Writes to positive results file.

    Key arguments
    image_paths -- list of image urls for images to be checked
    """
    print("Starting test...")
    face_positive_results = []
    for img in image_paths:
        face_result = id.check_identification_face(img)
        if face_result == "true":
            result = "pass"
        else:
            result = "fail"
        face_positive_results.append(result)
        final_result = [img, result]
        with open("test/results/face_positive_results.txt","a") as p_results:
            p_results.write("%s\n" % final_result)
        print("Image " + str(len(face_positive_results)) + " complete.")
    
    print("Test complete.")
    return face_positive_results

# Testing Negative Recognition
def face_negative(image_paths):
    """Opens the webcam and tests against
    provided images where an expected result
    is fail. Writes to negative results file.

    Key arguments
    image_paths -- list of image urls for images to be checked
    """
    print("Starting test...")
    face_negative_results = []
    for img in image_paths:
        face_result = id.check_identification_face(img)
        if face_result == "true":
            result = "pass"
        else:
            result = "fail"
        face_negative_results.append(result)
        final_result = [img, result]
        with open("test/results/face_negative_results.txt","a") as n_results:
            n_results.write("%s\n" % final_result)
        print("Image " + str(len(face_negative_results)) + " complete.")
    
    print("Test complete.")
    return face_negative_results

# U N C O M M E N T   T O   R E F R E S H   R E S U L T S
# Positive results (expecting a match)
#with open("test/face_positive_results.txt","w") as face_positive:
    #face_positive(my_image_paths)
    #face_positive.close()
# Negative results (expecting a no match)
#with open("test/face_negative_results.txt","w") as face_negative:
    #face_negative(my_image_paths)
    #face_negative.close()

# Read positive and negative results from the file
face_positive_results = []
face_negative_results = []
with open("test/results/face_positive_results.txt","r") as p_results:
    for line in p_results:
        result = line[:-1] # Remove new line character
        result = result.strip('][').split(', ')
        face_positive_results.append(result)

with open("test/results/face_negative_results.txt","r") as n_results:
    for line in n_results:
        result = line[:-1] # Remove new line character
        result = result.strip('][').split(', ')
        face_negative_results.append(result)

# Create empty list to store results
face_results = []

# All results
# Get the count of True Positives, False Positives, True Negatives and False Negatives
face_true_positives = sum(1 for r in face_positive_results if r[1] == "'pass'")
face_false_positives = sum(1 for r in face_positive_results if r[1] == "'fail'")

face_true_negatives = sum(1 for r in face_negative_results if r[1] == "'fail'")
face_false_negatives = sum(1 for r in face_negative_results if r[1] == "'pass'")

# Use the counts to calculate the sensitivity, specificity and accuracy
face_sensitivity = face_true_positives / (face_true_positives + face_false_negatives) * 100
face_specificity = face_true_negatives / (face_false_positives + face_true_negatives) * 100
face_accuracy = (face_true_positives + face_true_negatives) / (face_true_positives + face_false_positives + face_true_negatives + face_false_negatives) * 100

# Add result to list of results
face_results.append(["All Results        ", face_sensitivity, face_specificity, face_accuracy, face_true_positives, face_false_positives, face_true_negatives, face_false_negatives])

# Good Webcam Only
# Filter to only the 'good webcam' images
gw_face_positive_results = [x for x in face_positive_results if "IMG_" in x[0]]
gw_face_negative_results = [x for x in face_negative_results if "IMG_" in x[0]]

# Get the count of True Positives, False Positives, True Negatives and False Negatives
gw_face_true_positives = sum(1 for r in gw_face_positive_results if r[1] == "'pass'")
gw_face_false_positives = sum(1 for r in gw_face_positive_results if r[1] == "'fail'")

gw_face_true_negatives = sum(1 for r in gw_face_negative_results if r[1] == "'fail'")
gw_face_false_negatives = sum(1 for r in gw_face_negative_results if r[1] == "'pass'")

# Use the counts to calculate the sensitivity, specificity and accuracy
gw_face_sensitivity = gw_face_true_positives / (gw_face_true_positives + gw_face_false_negatives) * 100
gw_face_specificity = gw_face_true_negatives / (gw_face_false_positives + gw_face_true_negatives) * 100
gw_face_accuracy = (gw_face_true_positives + gw_face_true_negatives) / (gw_face_true_positives + gw_face_false_positives + gw_face_true_negatives + gw_face_false_negatives) * 100

# Add result to list of results
face_results.append(["Good Webcam Results", gw_face_sensitivity, gw_face_specificity, gw_face_accuracy, gw_face_true_positives, gw_face_false_positives, gw_face_true_negatives, gw_face_false_negatives])

# Bad Webcam Only
# Filter to only the 'good webcam' images
bw_face_positive_results = [x for x in face_positive_results if "WIN_" in x[0]]
bw_face_negative_results = [x for x in face_negative_results if "WIN_" in x[0]]

# Get the count of True Positives, False Positives, True Negatives and False Negatives
bw_face_true_positives = sum(1 for r in bw_face_positive_results if r[1] == "'pass'")
bw_face_false_positives = sum(1 for r in bw_face_positive_results if r[1] == "'fail'")

bw_face_true_negatives = sum(1 for r in bw_face_negative_results if r[1] == "'fail'")
bw_face_false_negatives = sum(1 for r in bw_face_negative_results if r[1] == "'pass'")

# Use the counts to calculate the sensitivity, specificity and accuracy
bw_face_sensitivity = bw_face_true_positives / (bw_face_true_positives + bw_face_false_negatives) * 100
bw_face_specificity = bw_face_true_negatives / (bw_face_false_positives + bw_face_true_negatives) * 100
bw_face_accuracy = (bw_face_true_positives + bw_face_true_negatives) / (bw_face_true_positives + bw_face_false_positives + bw_face_true_negatives + bw_face_false_negatives) * 100

# Add result to list of results
face_results.append(["Bad Webcam Results ", bw_face_sensitivity, bw_face_specificity, bw_face_accuracy, bw_face_true_positives, bw_face_false_positives, bw_face_true_negatives, bw_face_false_negatives])

# Print text results
for r in face_results:
    print(r)
