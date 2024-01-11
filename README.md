# Internet Electronic Voting Tool with Biometric and Text Identification and Self Verification

This repository contains code for an internet electronic voting tool that uses a biometric and text identification system and a secret word self verification system. It is a prototype design for a potential voting model that could be used in UK government elections.

This project is for MSci in Computer Science at University of Liverpool.

Author: Cheylea Hopkinson

## Python Version
This project requires Python 3.9.12.

# Directory
The `instance` and `idphoto` folders may not be found in this repositiory and will need to be created upon download. More information under installation.

```
C:.
├───__init__.py
├───app_test.py
├───app.py
├───blockchain.py
├───identification.py
├───LICENSE
├───README.md
├───requirements.txt
├───databases_test
│   ├───voters.db
│   └───votes.db
├───idphoto
├───instance
├───static
├───templates
└───test
    ├───results
    ├───test_images
    ├───blockchain_test.py
    └───identification_test.py
```

# Installation

## Step One
Use the package manager [pip](https://pip.pypa.io/en/stable/) to install the dependencies.

```
python -m pip install -r requirements.txt
```
You will also need to download and install [Tesseract](https://github.com/UB-Mannheim/tesseract/wiki).

## Step Two
Create the folder `instance` if required in the repository as indicated in the directory. Create a file caled `config.py`. Copy and paste and save into it the below:

```python
SECRET_KEY = ''
encryption_key = ''
```
Add your own keys into the strings to run the programme.

## Step Three
Create the folder `idphoto` if required in the repository as indicated in the directory. Leave empty.


# Usage

There are two versions of this tool in the repository. The "test" version `app_test.py` that skips the biometric identification and the version that is the complete tool `app.py`.

## Step One
Run either `app.py` or `app_test.py` to run the application. You can configure the port at the bottom of the `app_test.py`. For example:

```python
# Before
if __name__ == '__main__':
    main()
    # If statement to prevent run when hosting in PythonAnywhere
    if 'liveconsole' not in gethostname():
        app.run()

# After
if __name__ == '__main__':
    main()
    # If statement to prevent run when hosting in PythonAnywhere
    if 'liveconsole' not in gethostname():
        app.run(debug=True, port = 8000)
```

Then, if port is set to `8000`, navigate to http://127.0.0.1:8000 to view and click through the application to use it.

## Step Two - app.py only
`app.py` will require at least one test credential which is set up in the app.py script:

```python
from testdetails import myname, myaddress, mypostcode

...

# Insert test voters
insert_table_voters = """ INSERT INTO voters (id, pollstation, pollnumber, name, address, postcode, iseligible)
                          VALUES
                            (1, 'ABC', 1, 'Charlie Voter (Test)', '1 Example Street', 'ZZ01 000', 1),
                            (2, 'ABC', 2, 'Sam Voter (Test)', '2 Example Street', 'ZZ01 000', 1),
                            (3, 'ABC', 3, 'Bailey Voter (Test)', '3 Example Street', 'ZZ01 000', 1),
                            (4, 'ABC', 4, '""" + myname + """', '""" + myaddress + """', '""" + mypostcode + """', 1);
```

Create a file in the root called `testdetails.py` and paste your test details to compare to a real or generated id:

``` python

# My Address
myname = 'John Smith' # full name
myaddress = '1 Test Street' # address without postcode
mypostcode = 'AA00 0AA' # postcode

```

## Step Three - app.py only
You may get an error if your tesseract install is not located at `r"C:\Program Files\Tesseract-OCR\tesseract.exe"`. Ensure you have downloaded and installed [Tesseract](https://github.com/UB-Mannheim/) as mentioned in installed. Then you may need to correct the script in `identification.py` to the correct directory:

``` python
# Use Tesseract to extract text from the image
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
text = pytesseract.image_to_string(image)
```

# Testing

## Identification
`identification_test.py` is a file for looping through the text and face recognition tools to check their results from a provided folder of images. Load your images into the text_images folder.
Open the folder in file explorer and right click to open terminal. Type in the following

``` bash
dir /b > filenames.txt
```

This will create a file in the images folder that is used in the test module to load in the file path for the images. To prevent any images uploading to git, add these file names to your `.gitignore` file.

There are example results provided in the folder `test/results` which can be used to calculate the results by running the `identification_test.py` file. To refresh the results, uncomment where indicated.

## Blockchain
`blockchain_test.py` is a file for looping through test blockchains with added interference. This is to test the chain valid function and to ensure altered blocks would be identified.
There are example results provided in the folder `test/results` which can be used to calculate the results by running the `blockchain_test.py` file. To refresh the results, uncomment where indicated.

# Contributing
Pull requests permitted.