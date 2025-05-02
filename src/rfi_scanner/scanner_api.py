from flask import Flask, jsonify
import sqlite3
import io
import numpy as np

app = Flask(__name__)
DB_FILE = './config/scanner.db'


def bytes_to_array(byte_data):
    buffer = io.BytesIO(byte_data)
    array = np.load(buffer)
    return array

def get_data(limit=10):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT timestamp, data, state FROM sensor_data ORDER BY id DESC LIMIT ?', (limit,))
    rows = cursor.fetchall()
    conn.close()
    return rows[::-1]  # Return newest last

def load_last_array_from_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT timestamp, data, flag FROM sensor_data ORDER BY id DESC LIMIT 1')
    row = cursor.fetchone()
    conn.close()

    if row:
        timestamp, binary_data, flag = row

        array = bytes_to_array(binary_data)
        if array is not None:
            return timestamp, array, flag
        else:
            print("Error: Unable to convert binary data to array.")
            return None
    return None

def stats():
    """Calculate statistics for the scan array."""
    pass


@app.route('/api/data', methods=['GET'])
def data():
    try:
        data = get_data()
        if not data:
            return jsonify({'error': 'No data found'}), 404
        
        json = []
        for t, d, s in data:
            if d is not None:
                array = bytes_to_array(d)
                if array is not None:
                    # Perform any necessary processing on the array
                    
                    json.append({
                        'timestamp': t,
                        #'array': array.tolist(),  # To large to actually send like this
                        'state': s
                    })
                    pass
                else:
                    return jsonify({'error': 'Invalid data format'}), 400
        
        return jsonify(json)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)  # Accessible on local network