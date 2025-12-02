from flask import Flask, render_template, request
from pymysql import connections
import boto3
import os
import random
import argparse

app = Flask(__name__)

# Environment variables
DBHOST = os.environ.get("MYSQL_HOST") or "localhost"
DBUSER = os.environ.get("MYSQL_USER") or "root"
DBPWD = os.environ.get("MYSQL_PASSWORD") or "password"
DATABASE = os.environ.get("MYSQL_DB") or "employees"
DBPORT = int(os.environ.get("MYSQL_PORT") or 3306)

BG_IMAGE_URL = os.environ.get("BG_IMAGE_URL")  
HEADER_NAME = os.environ.get("HEADER_NAME") or "Employee Portal"

region = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")
s3 = boto3.client("s3", region_name=region)

# MySQL connection
db_conn = connections.Connection(
    host=DBHOST,
    port=DBPORT,
    user=DBUSER,
    password=DBPWD,
    db=DATABASE
)

# UI color selection (keep original logic)
color_codes = {
    "red": "#e74c3c",
    "green": "#16a085",
    "blue": "#89CFF0",
    "blue2": "#30336b",
    "pink": "#f4c2c2",
    "darkblue": "#130f40",
    "lime": "#C1FF9C",
}
COLOR = random.choice(list(color_codes.keys()))

# Download S3 background image
def fetch_background():
    if not BG_IMAGE_URL:
        print("No BG_IMAGE_URL set — using default theme")
        return

    if not BG_IMAGE_URL.startswith("s3://"):
        print("BG_IMAGE_URL format invalid")
        return

    try:
        parts = BG_IMAGE_URL.replace("s3://", "").split("/", 1)
        bucket = parts[0]
        key = parts[1]

        print(f"Downloading background from S3: {bucket}/{key}")

        s3 = boto3.client("s3")
        os.makedirs("static", exist_ok=True)
        local_path = "static/bg.png"

        s3.download_file(bucket, key, local_path)
        print("Background downloaded successfully.")

    except Exception as e:
        print(f"Error downloading background: {e}")


# Fetch background on startup
fetch_background()


@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('addemp.html',
                           color=color_codes[COLOR],
                           header_name=HEADER_NAME)

@app.route("/about", methods=['GET', 'POST'])
def about():
    return render_template('about.html',
                           color=color_codes[COLOR],
                           header_name=HEADER_NAME)

@app.route("/addemp", methods=['POST'])
def AddEmp():
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    primary_skill = request.form['primary_skill']
    location = request.form['location']

    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    try:
        cursor.execute(insert_sql, (emp_id, first_name, last_name, primary_skill, location))
        db_conn.commit()
        emp_name = first_name + " " + last_name
    finally:
        cursor.close()

    return render_template('addempoutput.html',
                           name=emp_name,
                           color=color_codes[COLOR],
                           header_name=HEADER_NAME)

@app.route("/getemp", methods=['GET', 'POST'])
def GetEmp():
    return render_template("getemp.html",
                           color=color_codes[COLOR],
                           header_name=HEADER_NAME)

@app.route("/fetchdata", methods=['GET','POST'])
def FetchData():
    emp_id = request.form['emp_id']
    select_sql = "SELECT emp_id, first_name, last_name, primary_skill, location FROM employee WHERE emp_id=%s"
    cursor = db_conn.cursor()

    try:
        cursor.execute(select_sql, (emp_id,))
        result = cursor.fetchone()
        if not result:
            return "Employee Not Found"
        data = {
            "emp_id": result[0],
            "first_name": result[1],
            "last_name": result[2],
            "primary_skill": result[3],
            "location": result[4],
        }
    finally:
        cursor.close()

    return render_template(
        "getempoutput.html",
        id=data["emp_id"],
        fname=data["first_name"],
        lname=data["last_name"],
        interest=data["primary_skill"],
        location=data["location"],
        color=color_codes[COLOR],
        header_name=HEADER_NAME
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=81, debug=True)
