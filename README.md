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
##### CSS
Only needed if you change the css styling
```
npx tailwindcss -i ./src/static/css/input.css -o ./src/static/css/output.css --watch
```
### Running
```
flask --app src/server run
```
##### Debug
```
flask --debug --app src/server run
```
