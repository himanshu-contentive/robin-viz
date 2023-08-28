from flask import Flask, render_template, request, jsonify
import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots

app = Flask(__name__)

uploaded_file = None
column_names = None
df = None

@app.route('/', methods=['GET', 'POST'])
def index():
    global uploaded_file, column_names, df
    if request.method == 'POST':
        if 'file' not in request.files:
            return "No file part"
        
        file = request.files['file']
        if file.filename == '':
            return "No selected file"
        
        if file and allowed_file(file.filename):
            uploaded_file = file.filename
            df = pd.read_excel(file)
            column_names = df.columns.tolist()

            # Get unique values for Filter 3 (Job Seniority) and Filter 4 (Company Turnover)
            filter_3_values = df['Job seniority'].unique().tolist()
            filter_4_values = df['Company turnover'].unique().tolist()

            # Display the top 4 rows
            top_rows = df.head(4).to_html(classes="table table-striped")
            return render_template('index.html', column_names=column_names, uploaded_file=uploaded_file, top_rows=top_rows,
                                   filter_3_values=filter_3_values, filter_4_values=filter_4_values)
    
    # If it's a GET request or no file is uploaded, clear the columns and top_rows
    uploaded_file = None
    column_names = None
    top_rows = None
    return render_template('index.html', column_names=column_names, uploaded_file=uploaded_file, top_rows=top_rows)

@app.route('/pie_chart', methods=['POST'])
def create_pie_chart():
    global df
    filter_column = request.form.get('filter_column')
    if filter_column:
        # Count occurrences of values in the selected filter column
        data_counts = df[filter_column].value_counts()
        labels = data_counts.index.tolist()
        values = data_counts.values.tolist()

        # Create a pie chart using Plotly
        fig = make_subplots(1, 1)
        fig.add_trace(go.Pie(labels=labels, values=values, hole=0.4))

        # Configure layout settings for the chart
        fig.update_layout(title_text=f"Pie Chart based on '{filter_column}'", showlegend=True)

        # Convert the plot to JSON format
        pie_chart = fig.to_json()
    else:
        pie_chart = None

    return jsonify(pie_chart)

@app.route('/bar_chart', methods=['POST'])
def create_bar_chart():
    global df
    filter_column = request.form.get('filter_column')
    if filter_column:
        # Count occurrences of values in the selected filter column
        data_counts = df[filter_column].value_counts()

        # Create a bar chart using Plotly
        fig = go.Figure()
        fig.add_trace(go.Bar(x=data_counts.index.tolist(), y=data_counts.values.tolist()))

        # Configure layout settings for the chart
        fig.update_layout(title_text=f"Bar Chart based on '{filter_column}'", xaxis_title=filter_column, yaxis_title="Count")

        # Convert the plot to JSON format
        bar_chart = fig.to_json()
    else:
        bar_chart = None

    return jsonify(bar_chart)

@app.route('/pie_chart_filter3', methods=['POST'])
def create_pie_chart_filter3():
    global df
    filter_values = request.form.getlist('filter3[]')
    if filter_values:
        # Filter the DataFrame based on selected values from Filter 3 (Job Seniority)
        filtered_df = df[df['Job seniority'].isin(filter_values)]

        # Count occurrences of values in the selected filter column
        data_counts = filtered_df['Job seniority'].value_counts()
        labels = data_counts.index.tolist()
        values = data_counts.values.tolist()

        # Create a pie chart using Plotly
        fig = make_subplots(1, 1)
        fig.add_trace(go.Pie(labels=labels, values=values, hole=0.4))

        # Configure layout settings for the chart
        fig.update_layout(title_text=f"Pie Chart based on selected values from 'Job Seniority'", showlegend=True)

        # Convert the plot to JSON format
        pie_chart = fig.to_json()
    else:
        pie_chart = None

    return jsonify(pie_chart)

@app.route('/bar_chart_filter4', methods=['POST'])
def create_bar_chart_filter4():
    global df
    filter_values = request.form.getlist('filter4[]')
    if filter_values:
        # Filter the DataFrame based on selected values from Filter 4 (Company Turnover)
        filtered_df = df[df['Company turnover'].isin(filter_values)]

        # Count occurrences of values in the selected filter column
        data_counts = filtered_df['Company turnover'].value_counts()

        # Create a bar chart using Plotly
        fig = go.Figure()
        fig.add_trace(go.Bar(x=data_counts.index.tolist(), y=data_counts.values.tolist()))

        # Configure layout settings for the chart
        fig.update_layout(title_text=f"Bar Chart based on selected values from 'Company Turnover'",
                          xaxis_title="Company Turnover", yaxis_title="Count")

        # Convert the plot to JSON format
        bar_chart = fig.to_json()
    else:
        bar_chart = None

    return jsonify(bar_chart)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'xls', 'xlsx'}

if __name__ == '__main__':
    app.run(debug=True, port=5006)