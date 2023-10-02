# E-Voting Tool with Self Verification
Dissertation project for MSci in Computer Science at University of Liverpool.

# Directory
The `instance` folder is not found in this repositiory and will need to be created upon download. More information under installation.

```
C:.
├───LICENSE
├───README.md
├───requirements.txt
├───app_test.py
├───blockchain.py
│
├───databases_test
│   ├───voters.db
│   └───votes.db
├───instance
├───static
└───templates
```

# Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install the dependencies.

```
python -m pip install -r requirements.txt
```

Create the folder `instance` in the repository as indicated in the director. Create a file caled `config.py`. Copy and paste and save into it the below:

```python
SECRET_KEY = ''
encryption_key = ''
```

Add your own keys into the strings to run the programme.

# Usage

Run `app_test.py` to run the application on the chosen port in the `config.py` file and navigate to view. You can configure the port at the bottom of the `app_test.py`. For example:

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

# Contributing
Pull requests permitted.