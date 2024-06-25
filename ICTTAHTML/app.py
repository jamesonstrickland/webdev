from flask import Flask, request, jsonify, render_template

import pyodbc

app = Flask(__name__)

db_config = {
    'server': 'USABQM0TEST',
    'database': 'ICTTA',
    'username': 'username',
    'password': 'password',
    'port': '1433'
}

def get_segment(request):

    try:
        segment = request.path.split('/')[-1]
        if segment == '':
            segment = 'index'
        return segment
    except:
        return None


def get_db_connection():
    connection_string = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={db_config['server']};"
        f"DATABASE={db_config['database']};"
        f"UID={db_config['username']};"
        f"PWD={db_config['password']}"
    )
    return pyodbc.connect(connection_string)

@app.route("/")
def home():
    return render_template('index.html')

@app.route("/warehouse-dashboard")
def warehouse_dashboard():
    return render_template('warehouse-dashboard.html')

@app.route("/fidelitone-dashboard")
def fidelitone_dashboard():
    return render_template('fidelitone-dashboard.html')

@app.route('/new-request')
def new_request():
    return render_template('NewRequestNew.html')

@app.route('/request-status')
def request_status():
    return render_template('request-status.html')

@app.route('/api/get-material-ids', methods=['GET'])
def get_material_ids():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT MaterialID FROM Materials")
        material_ids = cursor.fetchall()
        conn.close()
        if not material_ids:
            print("No material IDs found in the database.")
            return jsonify("DB Empty?")
        return jsonify([row[0] for row in material_ids])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/get-requestIds', methods=['GET'])
def get_request_ids():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT RequestID, Status, Priority, MaterialID, Quantity, Timestamp FROM Requests")
    request_ids = cursor.fetchall()
    conn.close()

    requests_data = []   
    for request in request_ids:
        request_data = {
            'RequestID': request[0],
            'Status': request[1],
            'Priority': request[2],
            'MaterialID': request[3],
            'Quantity': request[4],
            'Timestamp': request[5].strftime('%Y-%m-%d %H:%M:%S')
            }
        requests_data.append(request_data)
    return jsonify(requests_data)

@app.route('/submit-request', methods=['POST'])
def submit_request():
    try:
        data = request.json
        request_id = data['requestId']
        status = data['status']
        priority = data['priority']
        material_id = data['materialId']
        quantity = data['quantity']
    
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Requests (RequestID, Status, Priority, MaterialID, Quantity) VALUES (?, ?, ?, ?, ?)",
            (request_id, status, priority, material_id, quantity)
        )
        conn.commit()
        conn.close()
    
        return jsonify({'message': 'Request submitted successfully!'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/edit-status-page/<request_id>')
def edit_status_page(request_id):
    return render_template('edit-status.html', request_id=request_id)

@app.route('/edit-status/<request_id>')
def edit_status(request_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT requestID, status, priority, materialId, quantity FROM requests WHERE requestID = ?", (request_id,))
    request_data = cursor.fetchone()
    conn.close()

    if request_data:
        data = {
            "requestID": request_data.requestID,
            "status": request_data.status,
            "priority": request_data.priority,
            "materialId": request_data.materialId,
            "quantity": request_data.quantity
        }
        return jsonify(data)
    else:
        return jsonify({"error": "Request not found"}), 404
    
@app.route('/submit-status-update/<request_id>', methods=['POST'])
def submit_status_update(request_id):
    try:
        new_status = request.form['status']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE requests SET status = ? WHERE requestID = ?", (new_status, request_id))
        conn.commit()
        conn.close()
    
        return jsonify({'message': 'Request submitted successfully!', 'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

@app.route('/check-db-connection', methods=['GET'])
def check_db_connection():
    try:
        conn = get_db_connection()
        conn.close()
        return jsonify({'message': 'Database connection successful!'})
    except Exception as e:
        return jsonify({'message': f'Database connection failed: {str(e)}'}), 500
    

if __name__ == '__main__':
    app.run(debug=True)
