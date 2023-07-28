from flask import Flask, request, render_template, redirect, url_for
import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX
import plotly.graph_objs as go



app = Flask(__name__)

@app.route('/')
@app.route('/login')
def login():
    return '''
        <!DOCTYPE html>
<html>
<head>
    <title>Login Page</title>
    <style>

     body {
  background-color:#ffffe6;
  background-size: cover;
  background-repeat: no-repeat;
  background-attachment: fixed;
  font-family: "Open Sans", sans-serif;
  color: #333333;

}
.loginbutton
        {
          margin-left: 90px;
          margin-bottom: 12px;
          margin-top:29px;
          border: none;
          background-color:#282A35;
          padding-top: 12px;
          padding-bottom: 12px;
          padding-left: 30px;
          padding-right: 30px;
          border-radius: 23px;
          color: white;
          font-weight:bold;
          box-shadow:0 1px 5px  rgba(0, 0,0, 0.25);
          border-color: white;
          cursor: pointer;
          font-family:Times new Roman;
        }
       .input2{
          margin-left: 30px;
          margin-bottom: 12px;
          border: none;
          padding-top: 10px;
          padding-bottom: 10px;
          padding-left: 30px;
          padding-right: 30px;
          border-radius: 4px;
          color: black;
          box-shadow:0 1px 5px  rgba(0, 0,0, 0.25);
          border-color: black;
          cursor: pointer;
    }
        .input1{
        margin-left: 30px;
          margin-bottom: 12px;
          border: none;
          padding-top: 10px;
          padding-bottom: 10px;
          padding-left: 30px;
          padding-right: 30px;
          border-radius: 4px;
          color: black;
          box-shadow:0 1px 5px  rgba(0, 0,0, 0.25);
          border-color: black;
          cursor: pointer;
    }
         .all{
border-radius: 23px;
          border-color:white;
          border-width: 2px;
          display: inline-block;
          box-shadow:0 1px 5px  rgba(0, 0,0, 0.25);
          object-fit: cover;
          margin-left: 490px;
          margin-top:50px;
          padding-left:60px;
          padding-right:90px;
          padding-top:80px;
          padding-bottom:80px;
          background-color:#04AA6D;
    }

    h1{
    margin-left: 580px;
    color:#204060;
    font-size:40px;
    font-family:Times new Roman;

    }
    p{
    font-family:Times new Roman;
    font-weight:bold;
    margin-left:30px;
    }

    </style>
</head>
<body>
<div>
<h1>Login Page</h1>
<form action="/login" method="post" class="all">

  <div>
    <p>Username:</p>
    <input class="input1" type="text"  name="username">

      <p>Password:</p>
    <input class="input2" type="password"  name="password" >
  </div>
  <button class="loginbutton" type="submit" value="Login">Login</button>
</form>
</div>
</body>
</html>
    '''

@app.route('/login', methods=['POST'])
def do_login():
    username = request.form['username']
    password = request.form['password']

    if username == 'logu' and password == 'logu':
        return redirect(url_for('sarima'))
    else:
        return 'Invalid username/password combination'


@app.route('/sarima', methods=['GET', 'POST'])
def sarima():
    if request.method == 'POST':
        # Read the CSV file and preprocess the data for SARIMA model
        data = pd.read_csv(request.files['file'], parse_dates=['Month'], index_col='Month')

        # Get interval type and value from form
        interval_type = request.form['interval_type']
        interval_value = int(request.form['interval_value'])

        # Resample data to desired interval
        resampled_data = data.resample(interval_type).sum()

        # Fit SARIMA model
        model = SARIMAX(resampled_data['Sales'], order=(1, 1, 1), seasonal_order=(1, 1, 1, 12))
        results = model.fit()

        # Make future predictions
        future_dates = pd.date_range(start=resampled_data.index[-1], periods=interval_value, freq=interval_type)
        forecast = results.predict(start=len(resampled_data), end=len(resampled_data)+interval_value-1, dynamic=False, typ='levels')

        # Visualize time series and forecast
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=resampled_data.index, y=resampled_data['Sales'], name='Observed'))
        fig.add_trace(go.Scatter(x=future_dates, y=forecast, name='Future prediction'))
        fig.update_layout(title=' Sales Prediction',
                          xaxis_title='Month',
                          yaxis_title='Sales')

        # fig.write_image('E:/myplot.png')
        # Render template with forecasted values and plot
        return render_template('sarima.html', forecast=forecast.tolist(), plot=fig.to_html(full_html=False))
    return render_template('sarima.html')


if __name__ == '__main__':
    app.run(debug=True)