# from flask import Flask
# app = Flask(__name__)

# @app.route("/")
# def hello():
#     return "Hello World!"

# # -*- coding:utf-8 -*-

import json

from flask import Flask, request, render_template
app = Flask(__name__)

app.debug = True

class BaseDataTables:
    
    def __init__(self, request, columns, collection):
        
        self.columns = columns

        self.collection = collection
         
        # values specified by the datatable for filtering, sorting, paging
        self.request_values = request.values
         
 
        # results from the db
        self.result_data = None
         
        # total in the table after filtering
        self.cardinality_filtered = 0
 
        # total in the table unfiltered
        self.cadinality = 0
 
        self.run_queries()
    
    def output_result(self):
        
        output = {}
        aaData_rows = []
        
        for row in self.result_data:
            aaData_row = []
            for i in range(len(self.columns)):
                print row, self.columns, self.columns[i]
                aaData_row.append(str(row[ self.columns[i] ]).replace('"','\\"'))
            aaData_rows.append(aaData_row)

        # By default DataTables will look for the property 'aaData'
        # when obtaining data from an Ajax source or for server-side
        # processing.
        output['aaData'] = aaData_rows
        
        return output
    
    def run_queries(self):
        
         self.result_data = self.collection
         self.cardinality_filtered = len(self.result_data)
         self.cardinality = len(self.result_data)

columns = [ 'column_1', 'column_2', 'column_3', 'column_4']

@app.route('/')
def index():
    return render_template('index.html', columns=columns)


@app.route('/_server_data')
def get_server_data():

    img = "<img src='https://www.datatables.net/media/images/nav-dt.png' style='height:30px; width:30px'>"
    check = "<img src='/static/img/green_check.png' style='height:25px'>"
    x = "<img src='/static/img/red_x.png' style='height:15px'>"
    bar = "<img src='/static/img/blue_box.png' style='height:15px; width:100px'>"
    bar2 = "<img src='/static/img/blue_box.png' style='height:15px; width:200px'>"
    collection = [dict(zip(columns, [1,bar2,3,4])), dict(zip(columns, [bar2,bar,x,check]))]
    
    results = BaseDataTables(request, columns, collection).output_result()
    
    # return the results as a string for the datatable
    return json.dumps(results)

if __name__ == '__main__':
    app.run()
