from flask import Flask, request, jsonify, render_template, redirect, url_for, session
import pymysql


from datetime import datetime, date, time,timedelta

import json

app = Flask(__name__)

# MySQL Workbench connection config
db = pymysql.connect(
    host='localhost',
    user='root',
    password='admin@123',
    database='yatrisimplified',
    cursorclass=pymysql.cursors.DictCursor
)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/show_routes', methods=['POST'])
def show_routes():
    source = request.form['source']
    destination = request.form['destination']
    travel_date = request.form['travel_date']

    # Manually create a JSON-like dict
    data = {
        'source': source,
        'destination': destination,
        'travel_date': travel_date
    }

    # Simulate a request to get_multimodal_route
    with app.test_request_context(json=data):
        response = get_multimodal_route()
        if isinstance(response, tuple):
            response, status_code = response
            if status_code != 200:
                return render_template('show_routes.html', options=[], error=response.get_json().get("message"))
        options = response.get_json().get("options", [])

    return render_template('show_routes.html', options=options)


@app.route('/confirm_route', methods=['POST'])
def confirm_route():
    route_json = request.form.get('route_data')
    print("Raw JSON from form:", route_json)  # Debug print
    route = json.loads(route_json)  # Should now work!
    return render_template('confirm_booking.html', route=route)


@app.route('/api/register', methods=['POST'])
def register_user():
    data = request.get_json()

    try:
        with db.cursor() as cursor:
            sql = """
                INSERT INTO users (
                    name, email, phone_number, age, password
                ) VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                data['name'],
                data['email'],
                data['phone_number'],
                data['age'],
                data['password']
            ))
            db.commit()
            return jsonify({'message': 'Registration successful'}), 201

    except Exception as e:
        print("Error:", e)
        return jsonify({'error': 'Registration failed'}), 500

@app.route('/api/update-profile/<int:user_id>', methods=['PUT'])
def update_profile(user_id):
    data = request.get_json()

    try:
        with db.cursor() as cursor:
            sql = """
                UPDATE users
                SET nationality=%s, adhar_number=%s, passport_number=%s, document=%s, wallet_balance=%s
                WHERE user_id = %s
            """
            cursor.execute(sql, (
                data.get('nationality'),
                data.get('adhar_number'),
                data.get('passport_number'),
                data.get('document'),
                data.get('wallet_balance'),
                user_id
            ))
            db.commit()
            return jsonify({'message': 'Profile updated successfully'}), 200

    except Exception as e:
        print("Error:", e)
        return jsonify({'error': 'Profile update failed'}), 500


import base64

@app.template_filter('b64encode')
def b64encode_filter(s):
    return base64.b64encode(s.encode('utf-8')).decode('utf-8')


@app.route('/add_train', methods=['POST'])
def add_train():
    try:
        data = request.get_json()

        train_number = data['train_number']
        train_name = data['train_name']
        train_type = data.get('train_type', '')
        operator = data.get('operator', '')

        # Create cursor inside the function
        with db.cursor() as cursor:
            sql = """
                INSERT INTO trains (train_number, train_name, train_type, operator)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(sql, (train_number, train_name, train_type, operator))
            db.commit()

        return jsonify({'message': 'Train added successfully'}), 201

    except pymysql.MySQLError as e:
        return jsonify({'error': str(e)}), 400
@app.route('/api/add_flight', methods=['POST'])
def add_flight():
    data = request.get_json()
    cursor = db.cursor()
    sql = '''
    INSERT INTO flights (
        flight_id, flight_number, source, destination,
        airline, departure_time, arrival_time, contact_number,
        price, distance, password
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    '''
    values = (
        data['flight_id'], data['flight_number'], data['source'], data['destination'],
        data['airline'], data['departure_time'], data['arrival_time'],
        data['contact_number'], data['price'], data['distance'], data['password']
    )
    cursor.execute(sql, values)
    db.commit()
    return jsonify({'message': 'Flight added successfully!'}), 201

@app.route('/api/add_flight_route', methods=['POST'])
def add_flight_route():
    data = request.get_json()
    cursor = db.cursor()
    sql = '''
    INSERT INTO flight_routes (
        flight_id, airport_name, arrival_time, departure_time
    ) VALUES (%s, %s, %s, %s)
    '''
    values = (
        data['flight_id'],
        data['airport_name'],
        data['arrival_time'],
        data['departure_time']
    )
    cursor.execute(sql, values)
    db.commit()
    return jsonify({'message': 'Flight route added successfully!'}), 201


@app.route('/add_train_route', methods=['POST'])
def add_route():
    try:
        data = request.get_json()

        train_id = data['train_id']
        station_name = data['station_name']
        station_code = data.get('station_code', '')
        stop_number = data['stop_number']
        arrival_time = data.get('arrival_time')     # "HH:MM:SS" format
        departure_time = data.get('departure_time') # "HH:MM:SS" format
        halt_time = data.get('halt_time', 0)
        distance_from_start = data.get('distance_from_start', 0)

        with db.cursor() as cursor:
            # Step 1: Insert current station
            insert_sql = """
                INSERT INTO train_routes 
                (train_id, station_name, station_code, stop_number, arrival_time, departure_time, halt_time, distance_from_start)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_sql, (
                train_id, station_name, station_code, stop_number,
                arrival_time, departure_time, halt_time, distance_from_start
            ))

            # Step 2: Update previous stop's `arrived_time` with this stop's `arrival_time`
            if stop_number > 1 and arrival_time:
                update_sql = """
                    UPDATE train_routes
                    SET arrived_time = %s
                    WHERE train_id = %s AND stop_number = %s
                """
                cursor.execute(update_sql, (
                    arrival_time,
                    train_id,
                    stop_number - 1
                ))

            db.commit()

        return jsonify({'message': 'Train route added successfully'}), 201

    except pymysql.MySQLError as e:
        return jsonify({'error': str(e)}), 400


@app.route('/add_train_fare', methods=['POST'])
def add_fare():
    try:
        data = request.get_json()

        train_id = data['train_id']
        from_station = data['from_station']
        to_station = data['to_station']
        travel_class = data['travel_class']
        fare = data['fare']

        with db.cursor() as cursor:
            sql = """
                INSERT INTO fares (train_id, from_station, to_station, travel_class, fare)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (train_id, from_station, to_station, travel_class, fare))
            db.commit()

        return jsonify({'message': 'Fare added successfully'}), 201

    except pymysql.MySQLError as e:
        return jsonify({'error': str(e)}), 400

@app.route('/generate_fares/<int:train_id>', methods=['POST'])
def generate_fares(train_id):
    try:
        with db.cursor() as cursor:
            # Step 1: Get all stations for the train
            cursor.execute("""
                SELECT station_name, distance_from_start
                FROM train_routes
                WHERE train_id = %s
                ORDER BY stop_number
            """, (train_id,))
            stations = cursor.fetchall()

            # Fare rates
            fare_rates = {
                'Sleeper': 0.6,
                'AC': 1.2
            }

            # Step 2: Loop through combinations
            for i in range(len(stations)):
                for j in range(i + 1, len(stations)):
                    from_station = stations[i]['station_name']
                    to_station = stations[j]['station_name']
                    distance = stations[j]['distance_from_start'] - stations[i]['distance_from_start']

                    for travel_class, rate in fare_rates.items():
                        fare = round(distance * rate, 2)

                        # Insert fare
                        insert_sql = """
                            INSERT INTO fares (train_id, from_station, to_station, travel_class, fare)
                            VALUES (%s, %s, %s, %s, %s)
                        """
                        cursor.execute(insert_sql, (train_id, from_station, to_station, travel_class, fare))

            db.commit()
            return jsonify({'message': 'Fares generated successfully'}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/fare', methods=['GET'])
def get_fare():
    train_id = request.args.get('train_id')
    from_station = request.args.get('from_station')
    to_station = request.args.get('to_station')
    travel_class = request.args.get('class')

    if not all([train_id, from_station, to_station, travel_class]):
        return jsonify({"error": "Missing required query parameters"}), 400

    try:
        with db.cursor() as cursor:
            query = """
                SELECT fare FROM fares
                WHERE train_id = %s AND from_station = %s AND to_station = %s AND travel_class = %s
            """
            cursor.execute(query, (train_id, from_station, to_station, travel_class))
            result = cursor.fetchone()

            print(result)
            if result:
                return jsonify({
                    "train_id": int(train_id),
                    "from_station": from_station,
                    "to_station": to_station,
                    "class": travel_class,
                    "fare": float(result['fare'])
                })
            else:
                return jsonify({"message": "Fare not found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500

FARE_PER_KM_TRAIN = {
    "Sleeper": 0.75,
    "AC": 1.5,
    "General": 0.5
}

@app.route('/train/calculate_fare', methods=['POST'])
def calculate_train_fare():
    data = request.get_json()
    train_id = data.get('train_id')
    from_station = data.get('from_station')
    to_station = data.get('to_station')
    travel_class = data.get('travel_class', 'General')

    if not all([train_id, from_station, to_station]):
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        with db.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("""
                SELECT distance_from_start FROM train_routes
                WHERE train_id = %s AND station_name = %s
            """, (train_id, from_station))
            from_result = cursor.fetchone()

            cursor.execute("""
                SELECT distance_from_start FROM train_routes
                WHERE train_id = %s AND station_name = %s
            """, (train_id, to_station))
            to_result = cursor.fetchone()

            if not from_result or not to_result:
                return jsonify({'error': 'Invalid station names for this train'}), 404

            distance = abs(to_result['distance_from_start'] - from_result['distance_from_start'])

            if distance == 0:
                return jsonify({'error': 'Source and destination are the same or invalid'}), 400

            rate = FARE_PER_KM_TRAIN.get(travel_class, FARE_PER_KM_TRAIN["General"])
            fare = round(distance * rate, 2)

            return jsonify({
                "train_id": train_id,
                "from_station": from_station,
                "to_station": to_station,
                "travel_class": travel_class,
                "distance_km": distance,
                "calculated_fare": fare
            }), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/add_bus', methods=['POST'])
def add_bus():
    data = request.get_json()

    required_fields = ['bus_number', 'bus_name', 'bus_type', 'operator']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        with db.cursor() as cursor:
            sql = """
                INSERT INTO buses (bus_number, bus_name, bus_type, operator)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(sql, (
                data['bus_number'],
                data['bus_name'],
                data['bus_type'],
                data['operator']
            ))
            db.commit()

        return jsonify({'message': 'Bus added successfully'}), 201

    except pymysql.err.IntegrityError as e:
        return jsonify({'error': 'Bus number must be unique'}), 409
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/add_bus_route', methods=['POST'])
def add_bus_route():
    data = request.get_json()

    required_fields = [
        'bus_id', 'station_name', 'station_code', 'stop_number',
        'arrival_time', 'departure_time', 'halt_time', 'distance_from_start'
    ]

    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        with db.cursor() as cursor:
            # Step 1: Insert the new stop
            insert_sql = """
                INSERT INTO bus_routes (
                    bus_id, station_name, station_code, stop_number,
                    arrival_time, departure_time, halt_time, distance_from_start
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_sql, (
                data['bus_id'],
                data['station_name'],
                data['station_code'],
                data['stop_number'],
                data['arrival_time'],
                data['departure_time'],
                data['halt_time'],
                data['distance_from_start']
            ))

            # Step 2: Update the previous stop's `arrived_time` with this stop's arrival_time
            if data['stop_number'] > 1:  # only update if this is not the first stop
                update_sql = """
                    UPDATE bus_routes
                    SET arrived_time = %s
                    WHERE bus_id = %s AND stop_number = %s
                """
                cursor.execute(update_sql, (
                    data['arrival_time'],
                    data['bus_id'],
                    data['stop_number'] - 1
                ))

            db.commit()

        return jsonify({'message': 'Bus route added successfully'}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500



FARE_PER_KM = {
    "General": 0.8,
    "Sleeper": 1.2,
    "AC": 1.8
}

@app.route('/bus/calculate_fare', methods=['POST'])
def calculate_bus_fare():
    data = request.get_json()
    bus_id = data.get('bus_id')
    from_station = data.get('from_station')
    to_station = data.get('to_station')
    travel_class = data.get('travel_class', 'General')

    if not all([bus_id, from_station, to_station]):
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        with db.cursor() as cursor:
            # Fetch distance_from_start for from_station
            cursor.execute("""
                SELECT distance_from_start FROM bus_routes
                WHERE bus_id = %s AND station_name = %s
            """, (bus_id, from_station))
            from_result = cursor.fetchone()

            # Fetch distance_from_start for to_station
            cursor.execute("""
                SELECT distance_from_start FROM bus_routes
                WHERE bus_id = %s AND station_name = %s
            """, (bus_id, to_station))
            to_result = cursor.fetchone()
            print("From distance:", from_result)
            print("To distance:", to_result)

            if not from_result or not to_result:
                return jsonify({'error': 'Invalid station names for this bus'}), 404

            distance = abs(to_result['distance_from_start'] - from_result['distance_from_start'])
            rate = FARE_PER_KM.get(travel_class, FARE_PER_KM["General"])
            fare = round(distance * rate, 2)

            return jsonify({
                "bus_id": bus_id,
                "from_station": from_station,
                "to_station": to_station,
                "travel_class": travel_class,
                "distance_km": distance,
                "calculated_fare": fare
            }), 200


    except Exception as e:

        import traceback

        traceback.print_exc()  # This will show the error in terminal

        return jsonify({'error': str(e)}), 500

BUS_FARE_PER_KM = {
    'AC': 1.5,
    'Non-AC': 1.0
}
TRAIN_FARE_PER_KM = {
    'Sleeper': 0.8,
    'General': 0.5
}

from datetime import datetime, timedelta

from datetime import datetime, timedelta

from flask import request, jsonify
from datetime import datetime, timedelta


def parse_time(t):
    return datetime.strptime(str(t), "%H:%M:%S").time()

from flask import request, jsonify
from datetime import datetime, timedelta, time


def ensure_time(value):
    if isinstance(value, time):
        return value
    elif isinstance(value, timedelta):
        total_seconds = int(value.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return time(hour=hours, minute=minutes, second=seconds)
    else:
        raise ValueError("Unsupported time value type")


from flask import request, jsonify
from datetime import datetime, timedelta

from flask import request, jsonify
from datetime import datetime, timedelta, date


@app.route('/multi_mode_route', methods=['POST'])
def get_multimodal_route():
    data = request.get_json()
    source_name = data.get('source')
    destination_name = data.get('destination')
    travel_date_str = data.get('travel_date')  # Format: 'YYYY-MM-DD'

    try:
        travel_date = datetime.strptime(travel_date_str, "%Y-%m-%d").date() if travel_date_str else datetime.today().date()
    except ValueError:
        return jsonify({'message': 'Invalid travel_date format. Use YYYY-MM-DD.'}), 400

    cursor = db.cursor(pymysql.cursors.DictCursor)

    # Fetch unified location entries
    cursor.execute("SELECT * FROM unified_locations WHERE location_name = %s", (source_name,))
    source = cursor.fetchone()
    cursor.execute("SELECT * FROM unified_locations WHERE location_name = %s", (destination_name,))
    destination = cursor.fetchone()

    if not source or not destination:
        return jsonify({'message': 'Source or destination not found'}), 404

    options = []

    # --------- Option 1: Direct Bus Route ---------
    cursor.execute("""
        SELECT br1.*, br2.*, b.*
        FROM bus_routes br1
        JOIN bus_routes br2 ON br1.bus_id = br2.bus_id
        JOIN buses b ON br1.bus_id = b.bus_id
        WHERE br1.station_code = %s AND br2.station_code = %s AND br1.stop_number < br2.stop_number
    """, (source['bus_station_code'], destination['bus_station_code']))
    bus_direct_routes = cursor.fetchall()

    for route in bus_direct_routes:
        dep_time = ensure_time(route['departure_time'])
        arr_time = ensure_time(route['arrival_time'])
        arrived_time = ensure_time(route.get('arrived_time'))

        dep_datetime = datetime.combine(travel_date, dep_time)
        arr_datetime = datetime.combine(travel_date, arrived_time)

        option = {
            'message': 'Direct bus route found',
            'via': None,
            'travel_date': str(travel_date),
            'total_fare': None,
            'transfer_wait_time_minutes': 0,
            'bus_leg': {
                'bus_number': route['bus_number'],
                'bus_name': route['bus_name'],
                'from': {
                    'station_code': source['bus_station_code'],
                    'station_name': source['location_name']
                },
                'to': {
                    'station_code': destination['bus_station_code'],
                    'station_name': destination['location_name']
                },
                'departure_from_source': dep_datetime.isoformat(),
                'arrival_at_source': datetime.combine(travel_date, arr_time).isoformat(),
                'arrived_time': arr_datetime.isoformat()
            },
            'final_arrival_at_destination': arr_datetime.isoformat()
        }

        cursor.execute("""
            SELECT fare FROM fares 
            WHERE mode = 'bus' AND from_station_code = %s AND to_station_code = %s
        """, (source['bus_station_code'], destination['bus_station_code']))
        fare = cursor.fetchone()
        if fare:
            option['bus_leg']['fare'] = f"{float(fare['fare']):.2f}"
            option['total_fare'] = f"{float(fare['fare']):.2f}"
        else:
            option['bus_leg']['fare'] = "0.00"
            option['total_fare'] = "0.00"

        options.append(option)

    # --------- Option 2: Multimodal (Bus + Train via Hubs) ---------
    cursor.execute("SELECT * FROM unified_locations")
    all_locations = cursor.fetchall()

    for hub in all_locations:
        if hub['location_name'] in [source_name, destination_name]:
            continue

        # Get bus leg
        cursor.execute("""
            SELECT br1.*, br2.*, b.*
            FROM bus_routes br1
            JOIN bus_routes br2 ON br1.bus_id = br2.bus_id
            JOIN buses b ON br1.bus_id = b.bus_id
            WHERE br1.station_code = %s AND br2.station_code = %s AND br1.stop_number < br2.stop_number
        """, (source['bus_station_code'], hub['bus_station_code']))
        bus_leg = cursor.fetchone()

        # Get train leg
        cursor.execute("""
            SELECT tr1.*, tr2.*, t.*
            FROM train_routes tr1
            JOIN train_routes tr2 ON tr1.train_id = tr2.train_id
            JOIN trains t ON tr1.train_id = t.train_id
            WHERE tr1.station_code = %s AND tr2.station_code = %s AND tr1.stop_number < tr2.stop_number
        """, (hub['train_station_code'], destination['train_station_code']))
        train_leg = cursor.fetchone()

        if not bus_leg or not train_leg:
            continue

        bus_arrival = ensure_time(bus_leg['arrival_time'])
        bus_departure = ensure_time(bus_leg['departure_time'])
        train_arrival = ensure_time(train_leg['arrival_time'])
        train_departure = ensure_time(train_leg['departure_time'])

        bus_arrival_dt = datetime.combine(travel_date, bus_arrival)
        train_departure_dt = datetime.combine(travel_date, train_departure)

        if train_departure_dt <= bus_arrival_dt:
            continue

        transfer_wait_minutes = int((train_departure_dt - bus_arrival_dt).total_seconds() / 60)

        # Fares
        cursor.execute("""
            SELECT fare FROM fares 
            WHERE mode = 'bus' AND from_station_code = %s AND to_station_code = %s
        """, (source['bus_station_code'], hub['bus_station_code']))
        bus_fare_row = cursor.fetchone()
        bus_fare = float(bus_fare_row['fare']) if bus_fare_row else 0.0

        cursor.execute("""
            SELECT fare FROM fares 
            WHERE mode = 'train' AND from_station_code = %s AND to_station_code = %s
        """, (hub['train_station_code'], destination['train_station_code']))
        train_fare_row = cursor.fetchone()
        train_fare = float(train_fare_row['fare']) if train_fare_row else 0.0

        total_fare = bus_fare + train_fare
        final_arrived_time = ensure_time(train_leg.get('arrived_time'))
        final_arrival_dt = datetime.combine(travel_date, final_arrived_time)

        option = {
            'message': 'Multimodal route found',
            'via': hub['location_name'],
            'travel_date': str(travel_date),
            'transfer_wait_time_minutes': transfer_wait_minutes,
            'total_fare': f"{total_fare:.2f}",
            'bus_leg': {
                'bus_number': bus_leg['bus_number'],
                'bus_name': bus_leg['bus_name'],
                'from': {
                    'station_code': source['bus_station_code'],
                    'station_name': source['location_name']
                },
                'to': {
                    'station_code': hub['bus_station_code'],
                    'station_name': hub['location_name']
                },
                'departure_from_source': datetime.combine(travel_date, bus_departure).isoformat(),
                'arrival_at_source': datetime.combine(travel_date, bus_arrival).isoformat(),
                'arrived_time': datetime.combine(travel_date, ensure_time(bus_leg.get('arrived_time'))).isoformat(),
                'fare': f"{bus_fare:.2f}"
            },
            'train_leg': {
                'train_number': train_leg['train_number'],
                'train_name': train_leg['train_name'],
                'from': {
                    'station_code': hub['train_station_code'],
                    'station_name': hub['location_name']
                },
                'to': {
                    'station_code': destination['train_station_code'],
                    'station_name': destination['location_name']
                },
                'departure_from_source': train_departure_dt.isoformat(),
                'arrival_at_source': datetime.combine(travel_date, train_arrival).isoformat(),
                'arrived_time': final_arrival_dt.isoformat(),
                'fare': f"{train_fare:.2f}"
            },
            'final_arrival_at_destination': final_arrival_dt.isoformat()
        }

        options.append(option)

    if not options:
        return jsonify({'message': 'No route found'}), 404

    # ----- Tag fastest and affordable -----
    min_transfer_wait = min(opt['transfer_wait_time_minutes'] for opt in options)
    min_total_fare = min(float(opt['total_fare']) for opt in options)

    for opt in options:
        opt['type'] = []
        if opt['transfer_wait_time_minutes'] == min_transfer_wait:
            opt['type'].append('fastest')
        if float(opt['total_fare']) == min_total_fare:
            opt['type'].append('affordable')

    return jsonify({'options': options})



@app.route("/api/cab", methods=["POST"])
def add_cab():
    data = request.json
    try:
        with db.cursor() as cursor:
            sql = """INSERT INTO cabs (cab_id, cab_number, driver_name, cab_type, seater, email, phone_number, region, password)
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            cursor.execute(sql, (
                data["cab_id"], data["cab_number"], data["driver_name"], data["cab_type"],
                data["seater"], data["email"], data["phone_number"], data["region"], data["password"]
            ))
            db.commit()
            return jsonify({"message": "Cab added successfully"})
    except Exception as e:
        return jsonify({"error": str(e)})


@app.route("/api/book-passenger", methods=["POST"])
def book_passenger():
    data = request.json
    try:
        with db.cursor() as cursor:
            # Step 1: Check wallet balance
            cursor.execute("SELECT wallet_balance FROM users WHERE user_id = %s", (data["user_id"],))
            wallet = cursor.fetchone()

            if wallet is None:
                return jsonify({"error": "User not found"}), 404

            if data.get("deduct_from_wallet"):
                if wallet["wallet_balance"] < data["price"]:
                    return jsonify({"error": "Insufficient wallet balance"}), 400

            # Step 2: Insert passenger booking
            sql = """
                INSERT INTO passengers (
                    user_id, mode, name, age, gender,
                    journey_date, source, destination, price
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            cursor.execute(sql, (
                data["user_id"],
                data["mode"],
                data["name"],
                data["age"],
                data["gender"],
                data["journey_date"],
                data["source"],
                data["destination"],
                data["price"]
            ))

            # Get the auto-incremented booking_id
            booking_id = cursor.lastrowid

            # Step 3: Deduct wallet balance (if requested)
            if data.get("deduct_from_wallet"):
                cursor.execute(
                    "UPDATE users SET wallet_balance = wallet_balance - %s WHERE user_id = %s",
                    (data["price"], data["user_id"])
                )

            db.commit()
            return jsonify({"message": "Passenger booked successfully", "booking_id": booking_id}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/journey-segment", methods=["POST"])
def add_segment():
    data = request.json
    try:
        with db.cursor() as cursor:
            sql = """INSERT INTO journey_segments (
                        booking_id, transport_type, transport_id, segment_source, segment_destination,
                        departure_time, arrival_time, price, is_paid)
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            cursor.execute(sql, (
                data["booking_id"], data["transport_type"], data["transport_id"], data["segment_source"],
                data["segment_destination"], data["departure_time"], data["arrival_time"],
                data["price"], data.get("is_paid", False)
            ))
            db.commit()
            return jsonify({"message": "Journey segment added successfully"})
    except Exception as e:
        return jsonify({"error": str(e)})


@app.route('/api/add-payment', methods=['POST'])
def add_payment():
    data = request.get_json()

    try:
        db = pymysql.connect(host='localhost', user='root', password='admin@123', db='yatrisimplified')
        cursor = db.cursor()

        sql = """
            INSERT INTO payment (user_id, booking_id, service_type, transport_id, amount, 
                                 payment_method, payment_status)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        values = (
            data['user_id'],
            data['booking_id'],
            data['service_type'],
            data['transport_id'],
            data['amount'],
            data['payment_method'],
            data['payment_status']
        )

        cursor.execute(sql, values)
        db.commit()

        return jsonify({"message": "Payment added successfully!"}), 201

    except Exception as e:
        print("Error:", e)
        return jsonify({"error": str(e)}), 500

    finally:
        # Ensure the DB is closed safely
        try:
            cursor.close()
            db.close()
        except:
            pass


if __name__ == '__main__':
    app.run(debug=True)
