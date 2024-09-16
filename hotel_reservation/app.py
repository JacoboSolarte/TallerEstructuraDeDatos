from flask import Flask, render_template, request, redirect, url_for
from collections import deque

app = Flask(__name__)

# In-memory data structures
# Array (en Python, esto se usa como una lista)
rooms = [
    {'room_number': 101, 'room_type': 'Single', 'status': 'Available'},
    {'room_number': 102, 'room_type': 'Double', 'status': 'Available'},
    {'room_number': 103, 'room_type': 'Suite', 'status': 'Available'},
    {'room_number': 201, 'room_type': 'Single', 'status': 'Available'},
    {'room_number': 202, 'room_type': 'Double', 'status': 'Available'},
    {'room_number': 203, 'room_type': 'Suite', 'status': 'Available'},
    {'room_number': 301, 'room_type': 'Single', 'status': 'Available'},
    {'room_number': 302, 'room_type': 'Double', 'status': 'Available'},
    {'room_number': 303, 'room_type': 'Suite', 'status': 'Available'},
    {'room_number': 401, 'room_type': 'Single', 'status': 'Available'}
]

# Lista para almacenar reservas
reservations = []  # Lista
# Cola para deshacer la última acción
undo_queue = deque()  # Cola
# Pila para rehacer reservas
redo_stack = deque()  # Pila

class Reservation:
    def __init__(self, hotel, room, customer_name, identification, phone, reservation_date, time_slot):
        self.hotel = hotel
        self.room = room
        self.customer_name = customer_name
        self.identification = identification
        self.phone = phone
        self.reservation_date = reservation_date
        self.time_slot = time_slot

@app.route('/')
def index():
    return render_template('index.html', rooms=rooms)

@app.route('/reserve/<int:room_number>', methods=['POST'])
def reserve(room_number):
    room = next((r for r in rooms if r['room_number'] == room_number), None)
    if room and room['status'] == 'Available':
        hotel = request.form['hotel']
        customer_name = request.form['customer_name']
        identification = request.form['identification']
        phone = request.form['phone']
        reservation_date = request.form['reservation_date']
        time_slot = request.form['time_slot']

        # Crear una nueva reserva
        reservation = Reservation(hotel, room, customer_name, identification, phone, reservation_date, time_slot)
        reservations.append(reservation)  # Añadir a la lista de reservas
        undo_queue.append(reservation)     # Añadir a la cola de deshacer
        redo_stack.clear()  # Limpiar la pila de rehacer al hacer una nueva acción

        room['status'] = 'Reserved'
    return redirect(url_for('index'))

@app.route('/reservations')
def view_reservations():
    return render_template('reservations.html', reservations=reservations)

@app.route('/undo', methods=['POST'])
def undo_reservation():
    if undo_queue:
        last_reservation = undo_queue.popleft()  # Obtener y eliminar de la cola de deshacer
        for room in rooms:
            if room['room_number'] == last_reservation.room['room_number']:
                room['status'] = 'Available'
                reservations.remove(last_reservation)  # Eliminar de la lista de reservas
                redo_stack.append(last_reservation)  # Añadir a la pila de rehacer
                break
    return redirect(url_for('view_reservations'))

@app.route('/redo', methods=['POST'])
def redo_reservation():
    if redo_stack:
        reservation_to_redo = redo_stack.pop()  # Obtener y eliminar de la pila de rehacer
        room = next((r for r in rooms if r['room_number'] == reservation_to_redo.room['room_number']), None)
        if room and room['status'] == 'Available':
            reservations.append(reservation_to_redo)  # Añadir a la lista de reservas
            undo_queue.append(reservation_to_redo)  # Añadir a la cola de deshacer
            room['status'] = 'Reserved'
    return redirect(url_for('view_reservations'))

if __name__ == '__main__':
    app.run(debug=True)
