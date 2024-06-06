# Somelite
Social media website made in the framework flask.
For the KU course DIS, Databases and Information Systems.

### Made by
- sdw128
- xqd627
- ngz419

### Requirements
- python3 & pip
- npm & tailwind (only for updating the styling)

### Building
```
git clone git@github.com:Skovrup1/somelite.git
cd somelite
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```
##### CSS (only for updating the styling)
```
npx tailwindcss -i ./src/static/css/input.css -o ./src/static/css/output.css --watch
```
### Running
```
flask --app src/app run
```
##### Debug
```
flask --debug --app src/app run
```
