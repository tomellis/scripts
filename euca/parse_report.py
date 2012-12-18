#!/usr/bin/python
import csv
reader = csv.reader(open("report.csv", "rb"))
for row in reader:
    print row
