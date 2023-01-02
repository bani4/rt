# RESONANZ TECHNOLOGIES
## Development task
### Input
- A path to a utf-8 encoded .csv file with two columns Name,Address.
- A path to a directory where output file should be saved.
### Output
- A text document saved at the specified location. Each line is a commaseparated list of names of the people living at the same address. The
names in a line should be sorted alphabetically. The lines of the file should
also be sorted alphabetically. 
### Additional requirements
- Observe good coding practices
- Include a short readme file documenting the solution.
- There are no library usage restrictions.
## Solution
### Idea
- Data from the input file is transfered to a dataframe in pandas.
- Normalizing the address in a new column, needed because of the specifics of the chosen geocoder.
- Second new column associated with the normalized address returning location
- Grouping by the location
- Based on Nominatim geocoder in geopy library.
### PROs:
- Without api keys. 
- Checks for input file and folder
- Easy to use
### CONs:
- Slow on big data.
- Normalization of the given addresses.
- Undetailed map (openstreetmap.org). Merged different street numbers on same street can appear in the output.
### Instalations
- copy the repo
- create venv in folder
```bash
python -m venv venv
```
Use the requirements.txt to install the libraries needed
```bash
python -m pip install -r requirements.txt
```
### Running
Activate the venv
```bash
venv\Scripts\activate.bat
```

Run the file
```bash
python task1.py
```
