#!/usr/bin/env python3
"""
CineplexxDB - Cinema Database Management System
Updated with new schema including Cinema, CHECK constraints, and business rules
Just run: python3 cineplex_admin.py
Then open: http://localhost:8080
"""
from flask import Flask, render_template_string, request, jsonify
import pyodbc
from datetime import date, time
from decimal import Decimal

app = Flask(__name__)

# ============================================
# DATABASE CONFIGURATION
# ============================================
DB_CONFIG = {
    'server': 'localhost,1433',
    'database': 'CineplexxDB',
    'username': 'sa',
    'password': 'YourStrongPassword123!'
}

def get_connection():
    conn_str = (
        f"DRIVER={{ODBC Driver 18 for SQL Server}};"
        f"SERVER={DB_CONFIG['server']};"
        f"DATABASE={DB_CONFIG['database']};"
        f"UID={DB_CONFIG['username']};"
        f"PWD={DB_CONFIG['password']};"
        f"TrustServerCertificate=yes;"
    )
    return pyodbc.connect(conn_str)

def serialize_row(row, columns):
    result = {}
    for i, col in enumerate(columns):
        value = row[i]
        if isinstance(value, (date, time)):
            result[col] = str(value)
        elif isinstance(value, Decimal):
            result[col] = float(value)
        else:
            result[col] = value
    return result

# ============================================
# UPDATED TABLE SCHEMAS (matching new SQL)
# ============================================
TABLES = {
    'Cinema': {
        'pk': ['cinema_id'],
        'columns': ['cinema_id', 'location', 'name'],
        'types': ['int', 'varchar(50)', 'varchar(50)'],
        'required': ['cinema_id', 'location', 'name'],
        'display_name': 'Cinemas',
        'icon': 'fa-building-columns'
    },
    'Hall': {
        'pk': ['hall_id'],
        'columns': ['hall_id', 'hall_name', 'capacity', 'cinema_id'],
        'types': ['int', 'varchar(50)', 'int', 'int'],
        'required': ['hall_id', 'hall_name', 'capacity', 'cinema_id'],
        'display_name': 'Halls',
        'icon': 'fa-door-open',
        'constraints': {'capacity': 'Must be greater than 0'}
    },
    'Seat': {
        'pk': ['hall_id', 'seat_number', 'seat_row'],
        'columns': ['hall_id', 'seat_number', 'seat_row', 'seat_type'],
        'types': ['int', 'int', 'varchar(5)', 'varchar(10)'],
        'required': ['hall_id', 'seat_number', 'seat_row', 'seat_type'],
        'display_name': 'Seats',
        'icon': 'fa-chair',
        'constraints': {'seat_type': 'Must be Regular or VIP'}
    },
    'Movie': {
        'pk': ['movie_id'],
        'columns': ['movie_id', 'title', 'duration', 'release_date', 'language', 'age_rating', 'adult_price', 'kids_price'],
        'types': ['int', 'varchar(100)', 'int', 'date', 'varchar(30)', 'int', 'decimal(8,2)', 'decimal(8,2)'],
        'required': ['movie_id', 'title', 'duration', 'release_date', 'language', 'age_rating', 'adult_price', 'kids_price'],
        'display_name': 'Movies',
        'icon': 'fa-film',
        'constraints': {'duration': 'Must be greater than 0', 'age_rating': 'Cannot be negative'}
    },
    'Genre': {
        'pk': ['genre_id'],
        'columns': ['genre_id', 'genre_name'],
        'types': ['int', 'varchar(30)'],
        'required': ['genre_id', 'genre_name'],
        'display_name': 'Genres',
        'icon': 'fa-tags'
    },
    'Movie_Genre': {
        'pk': ['movie_id', 'genre_id'],
        'columns': ['movie_id', 'genre_id'],
        'types': ['int', 'int'],
        'required': ['movie_id', 'genre_id'],
        'display_name': 'Movie Genres',
        'icon': 'fa-link'
    },
    'Showtime': {
        'pk': ['showtime_id'],
        'columns': ['showtime_id', 'movie_id', 'hall_id', 'show_date', 'start_time', 'end_time'],
        'types': ['int', 'int', 'int', 'date', 'time', 'time'],
        'required': ['showtime_id', 'movie_id', 'hall_id', 'show_date', 'start_time', 'end_time'],
        'display_name': 'Showtimes',
        'icon': 'fa-clock',
        'constraints': {'end_time': 'Must be after start_time', 'show_date': 'Cannot be in the past'}
    },
    'Customer': {
        'pk': ['customer_id'],
        'columns': ['customer_id', 'full_name', 'phone_number', 'email', 'date_of_birth', 'gender'],
        'types': ['int', 'varchar(100)', 'varchar(20)', 'varchar(100)', 'date', 'varchar(10)'],
        'required': ['customer_id', 'full_name', 'email', 'date_of_birth', 'gender'],
        'display_name': 'Customers',
        'icon': 'fa-users'
    },
    'Booking': {
        'pk': ['booking_id'],
        'columns': ['booking_id', 'customer_id', 'showtime_id', 'booking_date', 'adult_seat', 'child_seat'],
        'types': ['int', 'int', 'int', 'date', 'int', 'int'],
        'required': ['booking_id', 'customer_id', 'showtime_id', 'booking_date', 'adult_seat', 'child_seat'],
        'display_name': 'Bookings',
        'icon': 'fa-calendar-check',
        'constraints': {'adult_seat': 'Must be 0 or greater', 'child_seat': 'Must be 0 or greater'}
    },
    'Ticket': {
        'pk': ['ticket_id'],
        'columns': ['ticket_id', 'booking_id', 'showtime_id', 'hall_id', 'seat_number', 'seat_row', 'ticket_price'],
        'types': ['int', 'int', 'int', 'int', 'int', 'varchar(5)', 'decimal(8,2)'],
        'required': ['ticket_id', 'booking_id', 'showtime_id', 'hall_id', 'seat_number', 'seat_row', 'ticket_price'],
        'display_name': 'Tickets',
        'icon': 'fa-ticket',
        'constraints': {'ticket_price': 'Must be greater than 0'}
    },
    'Department': {
        'pk': ['department_id'],
        'columns': ['department_id', 'department_name'],
        'types': ['int', 'varchar(50)'],
        'required': ['department_id', 'department_name'],
        'display_name': 'Departments',
        'icon': 'fa-sitemap'
    },
    'Employee': {
        'pk': ['employee_id'],
        'columns': ['employee_id', 'full_name', 'role', 'phone_number', 'email', 'date_of_birth', 'department_id', 'cinema_id'],
        'types': ['int', 'varchar(100)', 'varchar(30)', 'varchar(20)', 'varchar(100)', 'date', 'int', 'int'],
        'required': ['employee_id', 'full_name', 'role', 'phone_number', 'email', 'date_of_birth', 'department_id', 'cinema_id'],
        'display_name': 'Employees',
        'icon': 'fa-id-badge'
    },
    'Manager': {
        'pk': ['employee_id'],
        'columns': ['employee_id', 'management_level', 'contract_type', 'hire_date'],
        'types': ['int', 'int', 'varchar(30)', 'date'],
        'required': ['employee_id', 'management_level', 'contract_type', 'hire_date'],
        'display_name': 'Managers',
        'icon': 'fa-user-tie'
    },
    'Cashier': {
        'pk': ['employee_id'],
        'columns': ['employee_id', 'shift_type', 'hire_date', 'employment_status'],
        'types': ['int', 'varchar(20)', 'date', 'varchar(10)'],
        'required': ['employee_id', 'shift_type', 'hire_date'],
        'display_name': 'Cashiers',
        'icon': 'fa-cash-register'
    },
    'Cleaner': {
        'pk': ['employee_id'],
        'columns': ['employee_id', 'shift_type'],
        'types': ['int', 'varchar(20)'],
        'required': ['employee_id', 'shift_type'],
        'display_name': 'Cleaners',
        'icon': 'fa-broom'
    },
    'Showtime_Supervisor': {
        'pk': ['employee_id'],
        'columns': ['employee_id', 'shift_type'],
        'types': ['int', 'varchar(20)'],
        'required': ['employee_id', 'shift_type'],
        'display_name': 'Supervisors',
        'icon': 'fa-user-shield'
    },
    'Food': {
        'pk': ['food_id'],
        'columns': ['food_id', 'food_name', 'price'],
        'types': ['int', 'varchar(50)', 'decimal(6,2)'],
        'required': ['food_id', 'food_name', 'price'],
        'display_name': 'Food Items',
        'icon': 'fa-utensils',
        'constraints': {'price': 'Must be greater than 0'}
    },
    'Order': {
        'pk': ['order_id'],
        'columns': ['order_id', 'customer_id', 'order_date', 'order_time', 'order_amount'],
        'types': ['int', 'int', 'date', 'time', 'decimal(8,2)'],
        'required': ['order_id', 'customer_id', 'order_date', 'order_time'],
        'display_name': 'Orders',
        'icon': 'fa-receipt',
        'constraints': {'order_amount': 'Must be greater than 0'}
    },
    'Order_Food': {
        'pk': ['order_id', 'food_id'],
        'columns': ['order_id', 'food_id', 'quantity'],
        'types': ['int', 'int', 'int'],
        'required': ['order_id', 'food_id', 'quantity'],
        'display_name': 'Order Items',
        'icon': 'fa-list',
        'constraints': {'quantity': 'Must be greater than 0'}
    },
    'Payment': {
        'pk': ['payment_id'],
        'columns': ['payment_id', 'booking_id', 'order_id', 'payment_date', 'payment_time', 'amount', 'status', 'payment_method'],
        'types': ['int', 'int', 'int', 'date', 'time', 'decimal(8,2)', 'varchar(15)', 'varchar(10)'],
        'required': ['payment_id', 'payment_date', 'payment_time', 'amount', 'status', 'payment_method'],
        'display_name': 'Payments',
        'icon': 'fa-credit-card',
        'constraints': {'amount': 'Must be greater than 0', 'status': 'Must be Completed or Failed', 'payment_method': 'Must be Cash or Card'}
    },
    'Cash_Payment': {
        'pk': ['payment_id'],
        'columns': ['payment_id', 'change_amount'],
        'types': ['int', 'decimal(6,2)'],
        'required': ['payment_id', 'change_amount'],
        'display_name': 'Cash Payments',
        'icon': 'fa-money-bill-wave',
        'constraints': {'change_amount': 'Cannot be negative'}
    },
    'Card_Payment': {
        'pk': ['payment_id'],
        'columns': ['payment_id', 'card_number', 'card_type', 'expiry_date', 'cardholder_name'],
        'types': ['int', 'varchar(20)', 'varchar(20)', 'date', 'varchar(100)'],
        'required': ['payment_id', 'card_number', 'card_type', 'expiry_date', 'cardholder_name'],
        'display_name': 'Card Payments',
        'icon': 'fa-credit-card'
    }
}

# ============================================
# HTML TEMPLATE - NETFLIX-INSPIRED CINEMA THEME
# ============================================
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CineplexxDB - Cinema Management</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {
            --primary: #e50914;
            --primary-dark: #b20710;
            --primary-light: #ff4d4d;
            --accent: #f5c518;
            --accent-dark: #d4a817;
            
            --bg-dark: #141414;
            --bg-card: #1f1f1f;
            --bg-hover: #2a2a2a;
            --bg-input: #333333;
            
            --text-white: #ffffff;
            --text-light: #e5e5e5;
            --text-gray: #808080;
            --text-dark: #b3b3b3;
            
            --success: #46d369;
            --warning: #f5c518;
            --danger: #e50914;
            --info: #0080ff;
            
            --border-color: #333333;
            --shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
            --sidebar-width: 280px;
            --header-height: 70px;
            --radius: 8px;
            --radius-lg: 16px;
        }
        
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Poppins', sans-serif;
            background-color: var(--bg-dark);
            color: var(--text-light);
            line-height: 1.6;
        }
        
        .app-container { display: flex; min-height: 100vh; }
        
        /* ===== SIDEBAR ===== */
        .sidebar {
            width: var(--sidebar-width);
            background: linear-gradient(180deg, #1a1a1a 0%, #0d0d0d 100%);
            border-right: 1px solid var(--border-color);
            position: fixed;
            height: 100vh;
            overflow-y: auto;
            z-index: 1000;
        }
        
        .sidebar::-webkit-scrollbar { width: 5px; }
        .sidebar::-webkit-scrollbar-thumb { background: var(--primary); border-radius: 5px; }
        .sidebar::-webkit-scrollbar-track { background: transparent; }
        
        .logo {
            padding: 25px 20px;
            display: flex;
            align-items: center;
            gap: 12px;
            border-bottom: 1px solid var(--border-color);
            background: linear-gradient(135deg, rgba(229, 9, 20, 0.1) 0%, transparent 100%);
        }
        
        .logo-icon {
            width: 45px;
            height: 45px;
            background: var(--primary);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.4rem;
            color: white;
            box-shadow: 0 4px 15px rgba(229, 9, 20, 0.4);
        }
        
        .logo-text {
            font-size: 1.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, var(--primary) 0%, var(--accent) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .nav-section { padding: 15px 0; }
        .nav-section-title {
            padding: 8px 25px;
            font-size: 0.65rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            color: var(--text-gray);
        }
        
        .nav-item {
            display: flex;
            align-items: center;
            gap: 14px;
            padding: 10px 25px;
            color: var(--text-dark);
            text-decoration: none;
            cursor: pointer;
            font-size: 0.85rem;
            font-weight: 500;
            transition: all 0.3s ease;
            border-left: 3px solid transparent;
            margin: 1px 0;
        }
        
        .nav-item:hover {
            background: linear-gradient(90deg, rgba(229, 9, 20, 0.15) 0%, transparent 100%);
            color: var(--text-white);
            border-left-color: var(--primary);
        }
        
        .nav-item.active {
            background: linear-gradient(90deg, rgba(229, 9, 20, 0.2) 0%, transparent 100%);
            color: var(--primary);
            border-left-color: var(--primary);
        }
        
        .nav-item i { width: 20px; text-align: center; font-size: 0.9rem; }
        
        /* ===== MAIN CONTENT ===== */
        .main-content {
            flex: 1;
            margin-left: var(--sidebar-width);
            min-height: 100vh;
            background: var(--bg-dark);
        }
        
        /* ===== HEADER ===== */
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0 35px;
            height: var(--header-height);
            background: rgba(20, 20, 20, 0.95);
            backdrop-filter: blur(10px);
            border-bottom: 1px solid var(--border-color);
            position: sticky;
            top: 0;
            z-index: 100;
        }
        
        .header h1 {
            font-size: 1.5rem;
            font-weight: 600;
            color: var(--text-white);
        }
        
        .header-right { display: flex; align-items: center; gap: 15px; }
        
        .search-box {
            display: flex;
            align-items: center;
            background: var(--bg-input);
            border: 1px solid var(--border-color);
            border-radius: 25px;
            padding: 10px 20px;
            gap: 12px;
            transition: all 0.3s ease;
        }
        
        .search-box:focus-within {
            border-color: var(--primary);
            box-shadow: 0 0 0 3px rgba(229, 9, 20, 0.2);
        }
        
        .search-box i { color: var(--text-gray); }
        .search-box input {
            background: none;
            border: none;
            color: var(--text-white);
            outline: none;
            width: 220px;
            font-size: 0.9rem;
            font-family: 'Poppins', sans-serif;
        }
        .search-box input::placeholder { color: var(--text-gray); }
        
        /* ===== BUTTONS ===== */
        .btn {
            display: inline-flex;
            align-items: center;
            gap: 10px;
            padding: 12px 24px;
            border: none;
            border-radius: 25px;
            font-size: 0.9rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            font-family: 'Poppins', sans-serif;
        }
        
        .btn-primary {
            background: var(--primary);
            color: white;
            box-shadow: 0 4px 15px rgba(229, 9, 20, 0.3);
        }
        .btn-primary:hover {
            background: var(--primary-dark);
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(229, 9, 20, 0.4);
        }
        
        .btn-secondary {
            background: var(--bg-input);
            color: var(--text-light);
            border: 1px solid var(--border-color);
        }
        .btn-secondary:hover { background: var(--bg-hover); }
        
        .btn-success { background: var(--success); color: var(--bg-dark); }
        .btn-danger { background: var(--danger); color: white; }
        
        .btn-sm { padding: 8px 14px; font-size: 0.8rem; }
        .btn-icon { padding: 10px; border-radius: 10px; min-width: 40px; justify-content: center; }
        
        .btn-edit { background: var(--info); color: white; }
        .btn-edit:hover { background: #0066cc; }
        .btn-delete { background: transparent; color: var(--danger); border: 1px solid var(--danger); }
        .btn-delete:hover { background: var(--danger); color: white; }
        
        /* ===== CONTENT AREA ===== */
        .content { padding: 35px; }
        
        /* ===== STATS GRID ===== */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }
        
        .stat-card {
            background: var(--bg-card);
            border-radius: var(--radius-lg);
            padding: 22px;
            display: flex;
            align-items: center;
            gap: 18px;
            border: 1px solid var(--border-color);
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        
        .stat-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 3px;
            background: linear-gradient(90deg, var(--primary), var(--accent));
        }
        
        .stat-card:hover {
            transform: translateY(-5px);
            box-shadow: var(--shadow);
            border-color: var(--primary);
        }
        
        .stat-icon {
            width: 55px;
            height: 55px;
            border-radius: 14px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.4rem;
        }
        
        .stat-icon.red { background: linear-gradient(135deg, #e50914, #ff4d4d); color: white; }
        .stat-icon.gold { background: linear-gradient(135deg, #f5c518, #ffd700); color: #1a1a1a; }
        .stat-icon.green { background: linear-gradient(135deg, #46d369, #2ecc71); color: white; }
        .stat-icon.blue { background: linear-gradient(135deg, #0080ff, #00bfff); color: white; }
        .stat-icon.purple { background: linear-gradient(135deg, #9b59b6, #8e44ad); color: white; }
        .stat-icon.orange { background: linear-gradient(135deg, #f39c12, #e67e22); color: white; }
        .stat-icon.teal { background: linear-gradient(135deg, #1abc9c, #16a085); color: white; }
        
        .stat-info { display: flex; flex-direction: column; }
        .stat-value { font-size: 1.8rem; font-weight: 700; color: var(--text-white); }
        .stat-label { color: var(--text-gray); font-size: 0.8rem; font-weight: 500; }
        
        /* ===== SECTION TITLES ===== */
        .section-title {
            font-size: 1.3rem;
            font-weight: 600;
            margin-bottom: 20px;
            color: var(--text-white);
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .section-title::before {
            content: '';
            width: 4px;
            height: 24px;
            background: var(--primary);
            border-radius: 2px;
        }
        
        /* ===== TABLES GRID ===== */
        .tables-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
            gap: 12px;
        }
        
        .table-card {
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: var(--radius);
            padding: 16px;
            display: flex;
            align-items: center;
            gap: 12px;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .table-card:hover {
            background: var(--bg-hover);
            border-color: var(--primary);
            transform: translateX(5px);
        }
        
        .table-card-icon {
            width: 40px;
            height: 40px;
            background: rgba(229, 9, 20, 0.1);
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: var(--primary);
            font-size: 1rem;
        }
        
        .table-card-info { flex: 1; }
        .table-card-name { font-weight: 600; color: var(--text-white); font-size: 0.9rem; }
        .table-card-count { font-size: 0.75rem; color: var(--text-gray); }
        
        .table-card-arrow { color: var(--text-gray); transition: all 0.3s ease; }
        .table-card:hover .table-card-arrow { color: var(--primary); transform: translateX(5px); }
        
        /* ===== DATA TABLE ===== */
        .table-container {
            background: var(--bg-card);
            border-radius: var(--radius-lg);
            border: 1px solid var(--border-color);
            overflow: hidden;
        }
        
        .table-header {
            padding: 20px 25px;
            border-bottom: 1px solid var(--border-color);
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: linear-gradient(90deg, rgba(229, 9, 20, 0.05) 0%, transparent 100%);
        }
        
        .table-header span { color: var(--text-gray); font-size: 0.9rem; }
        
        .table-wrapper { overflow-x: auto; }
        
        table { width: 100%; border-collapse: collapse; }
        
        th, td {
            padding: 14px 20px;
            text-align: left;
            border-bottom: 1px solid var(--border-color);
        }
        
        th {
            background: rgba(255, 255, 255, 0.03);
            font-weight: 600;
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: var(--text-gray);
            white-space: nowrap;
        }
        
        td { font-size: 0.85rem; color: var(--text-light); }
        
        tr:hover td { background: rgba(229, 9, 20, 0.03); }
        
        .actions-cell { display: flex; gap: 8px; }
        
        /* ===== MODAL ===== */
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.85);
            backdrop-filter: blur(5px);
            z-index: 2000;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        
        .modal.active { display: flex; }
        
        .modal-content {
            background: var(--bg-card);
            border-radius: var(--radius-lg);
            width: 100%;
            max-width: 550px;
            max-height: 90vh;
            overflow: hidden;
            border: 1px solid var(--border-color);
            box-shadow: 0 25px 50px rgba(0, 0, 0, 0.5);
        }
        
        .modal-small { max-width: 420px; }
        
        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 25px 30px;
            border-bottom: 1px solid var(--border-color);
            background: linear-gradient(90deg, rgba(229, 9, 20, 0.1) 0%, transparent 100%);
        }
        
        .modal-header h2 { font-size: 1.2rem; font-weight: 600; color: var(--text-white); }
        
        .close-btn {
            width: 35px;
            height: 35px;
            background: var(--bg-input);
            border: none;
            border-radius: 50%;
            color: var(--text-gray);
            font-size: 1.2rem;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .close-btn:hover { background: var(--danger); color: white; }
        
        .modal-body {
            padding: 30px;
            max-height: calc(90vh - 160px);
            overflow-y: auto;
        }
        
        .modal-footer {
            display: flex;
            justify-content: flex-end;
            gap: 12px;
            padding: 20px 30px;
            border-top: 1px solid var(--border-color);
            background: rgba(0, 0, 0, 0.2);
        }
        
        /* ===== FORM ===== */
        .form-group { margin-bottom: 20px; }
        
        .form-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: 500;
            font-size: 0.85rem;
            color: var(--text-light);
        }
        
        .form-group .required { color: var(--primary); margin-left: 3px; }
        .form-group .hint { color: var(--text-gray); font-size: 0.7rem; font-weight: 400; margin-left: 8px; }
        
        .form-group input, .form-group select {
            width: 100%;
            padding: 12px 16px;
            background: var(--bg-input);
            border: 1px solid var(--border-color);
            border-radius: var(--radius);
            color: var(--text-white);
            font-size: 0.9rem;
            font-family: 'Poppins', sans-serif;
            transition: all 0.3s ease;
        }
        
        .form-group input:focus, .form-group select:focus {
            outline: none;
            border-color: var(--primary);
            box-shadow: 0 0 0 3px rgba(229, 9, 20, 0.2);
        }
        
        .form-group input:disabled { opacity: 0.6; cursor: not-allowed; }
        
        /* ===== TOAST ===== */
        .toast {
            position: fixed;
            bottom: 30px;
            right: 30px;
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: var(--radius);
            padding: 18px 25px;
            display: flex;
            align-items: center;
            gap: 15px;
            transform: translateY(100px);
            opacity: 0;
            transition: all 0.4s ease;
            z-index: 3000;
            box-shadow: var(--shadow);
            max-width: 400px;
        }
        
        .toast.show { transform: translateY(0); opacity: 1; }
        .toast.success { border-left: 4px solid var(--success); }
        .toast.success .toast-icon { color: var(--success); }
        .toast.error { border-left: 4px solid var(--danger); }
        .toast.error .toast-icon { color: var(--danger); }
        .toast-icon { font-size: 1.3rem; }
        .toast-message { font-size: 0.85rem; color: var(--text-light); }
        
        /* ===== UTILITIES ===== */
        .loading { display: flex; justify-content: center; padding: 60px; }
        
        .spinner {
            width: 45px;
            height: 45px;
            border: 4px solid var(--border-color);
            border-top-color: var(--primary);
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
        }
        
        @keyframes spin { to { transform: rotate(360deg); } }
        
        .empty-state { text-align: center; padding: 60px; color: var(--text-gray); }
        .empty-state i { font-size: 4rem; margin-bottom: 20px; color: var(--border-color); }
        .empty-state p { font-size: 1.1rem; }
        
        .menu-toggle {
            display: none;
            background: none;
            border: none;
            color: var(--text-white);
            font-size: 1.3rem;
            cursor: pointer;
            margin-right: 20px;
        }
        
        /* ===== RESPONSIVE ===== */
        @media (max-width: 1024px) {
            .sidebar { transform: translateX(-100%); transition: transform 0.3s ease; }
            .sidebar.open { transform: translateX(0); }
            .main-content { margin-left: 0; }
            .menu-toggle { display: block; }
        }
        
        @media (max-width: 768px) {
            .header { padding: 0 20px; }
            .content { padding: 20px; }
            .stats-grid { grid-template-columns: 1fr 1fr; }
            .search-box input { width: 150px; }
        }
        
        @media (max-width: 480px) {
            .stats-grid { grid-template-columns: 1fr; }
            .search-box { display: none !important; }
            .btn span { display: none; }
        }
    </style>
</head>
<body>
    <div class="app-container">
        <!-- Sidebar -->
        <aside class="sidebar" id="sidebar">
            <div class="logo">
                <div class="logo-icon"><i class="fas fa-film"></i></div>
                <span class="logo-text">CineplexxDB</span>
            </div>
            
            <div class="nav-section">
                <div class="nav-section-title">Main Menu</div>
                <a href="#" class="nav-item active" data-view="dashboard">
                    <i class="fas fa-th-large"></i><span>Dashboard</span>
                </a>
            </div>
            
            <div class="nav-section">
                <div class="nav-section-title">Locations</div>
                <a href="#" class="nav-item" data-table="Cinema"><i class="fas fa-building-columns"></i><span>Cinemas</span></a>
                <a href="#" class="nav-item" data-table="Hall"><i class="fas fa-door-open"></i><span>Halls</span></a>
                <a href="#" class="nav-item" data-table="Seat"><i class="fas fa-chair"></i><span>Seats</span></a>
            </div>
            
            <div class="nav-section">
                <div class="nav-section-title">Movies & Shows</div>
                <a href="#" class="nav-item" data-table="Movie"><i class="fas fa-film"></i><span>Movies</span></a>
                <a href="#" class="nav-item" data-table="Genre"><i class="fas fa-tags"></i><span>Genres</span></a>
                <a href="#" class="nav-item" data-table="Movie_Genre"><i class="fas fa-link"></i><span>Movie Genres</span></a>
                <a href="#" class="nav-item" data-table="Showtime"><i class="fas fa-clock"></i><span>Showtimes</span></a>
            </div>
            
            <div class="nav-section">
                <div class="nav-section-title">Customers & Bookings</div>
                <a href="#" class="nav-item" data-table="Customer"><i class="fas fa-users"></i><span>Customers</span></a>
                <a href="#" class="nav-item" data-table="Booking"><i class="fas fa-calendar-check"></i><span>Bookings</span></a>
                <a href="#" class="nav-item" data-table="Ticket"><i class="fas fa-ticket"></i><span>Tickets</span></a>
            </div>
            
            <div class="nav-section">
                <div class="nav-section-title">Concessions</div>
                <a href="#" class="nav-item" data-table="Food"><i class="fas fa-utensils"></i><span>Food Menu</span></a>
                <a href="#" class="nav-item" data-table="Order"><i class="fas fa-receipt"></i><span>Orders</span></a>
                <a href="#" class="nav-item" data-table="Order_Food"><i class="fas fa-list"></i><span>Order Items</span></a>
            </div>
            
            <div class="nav-section">
                <div class="nav-section-title">Payments</div>
                <a href="#" class="nav-item" data-table="Payment"><i class="fas fa-credit-card"></i><span>All Payments</span></a>
                <a href="#" class="nav-item" data-table="Card_Payment"><i class="fas fa-credit-card"></i><span>Card Payments</span></a>
                <a href="#" class="nav-item" data-table="Cash_Payment"><i class="fas fa-money-bill-wave"></i><span>Cash Payments</span></a>
            </div>
            
            <div class="nav-section">
                <div class="nav-section-title">Staff Management</div>
                <a href="#" class="nav-item" data-table="Employee"><i class="fas fa-id-badge"></i><span>Employees</span></a>
                <a href="#" class="nav-item" data-table="Department"><i class="fas fa-sitemap"></i><span>Departments</span></a>
                <a href="#" class="nav-item" data-table="Manager"><i class="fas fa-user-tie"></i><span>Managers</span></a>
                <a href="#" class="nav-item" data-table="Cashier"><i class="fas fa-cash-register"></i><span>Cashiers</span></a>
                <a href="#" class="nav-item" data-table="Cleaner"><i class="fas fa-broom"></i><span>Cleaners</span></a>
                <a href="#" class="nav-item" data-table="Showtime_Supervisor"><i class="fas fa-user-shield"></i><span>Supervisors</span></a>
            </div>
        </aside>

        <!-- Main Content -->
        <main class="main-content">
            <header class="header">
                <div style="display: flex; align-items: center;">
                    <button class="menu-toggle" id="menuToggle"><i class="fas fa-bars"></i></button>
                    <h1 id="pageTitle">Dashboard</h1>
                </div>
                <div class="header-right">
                    <div class="search-box" id="searchBox" style="display: none;">
                        <i class="fas fa-search"></i>
                        <input type="text" id="searchInput" placeholder="Search records...">
                    </div>
                    <button class="btn btn-primary" id="addNewBtn" style="display: none;">
                        <i class="fas fa-plus"></i>
                        <span>Add New</span>
                    </button>
                </div>
            </header>

            <!-- Dashboard View -->
            <div class="content" id="dashboardView">
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-icon teal"><i class="fas fa-building-columns"></i></div>
                        <div class="stat-info">
                            <span class="stat-value" id="statCinemas">-</span>
                            <span class="stat-label">Cinemas</span>
                        </div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon red"><i class="fas fa-film"></i></div>
                        <div class="stat-info">
                            <span class="stat-value" id="statMovies">-</span>
                            <span class="stat-label">Movies</span>
                        </div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon gold"><i class="fas fa-users"></i></div>
                        <div class="stat-info">
                            <span class="stat-value" id="statCustomers">-</span>
                            <span class="stat-label">Customers</span>
                        </div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon green"><i class="fas fa-ticket"></i></div>
                        <div class="stat-info">
                            <span class="stat-value" id="statTickets">-</span>
                            <span class="stat-label">Tickets Sold</span>
                        </div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon blue"><i class="fas fa-calendar-check"></i></div>
                        <div class="stat-info">
                            <span class="stat-value" id="statBookings">-</span>
                            <span class="stat-label">Bookings</span>
                        </div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon purple"><i class="fas fa-credit-card"></i></div>
                        <div class="stat-info">
                            <span class="stat-value" id="statPayments">-</span>
                            <span class="stat-label">Payments</span>
                        </div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon orange"><i class="fas fa-id-badge"></i></div>
                        <div class="stat-info">
                            <span class="stat-value" id="statEmployees">-</span>
                            <span class="stat-label">Employees</span>
                        </div>
                    </div>
                </div>

                <h2 class="section-title">All Tables</h2>
                <div class="tables-grid" id="allTablesGrid"></div>
            </div>

            <!-- Table View -->
            <div class="content" id="tableView" style="display: none;">
                <div class="table-container">
                    <div class="table-header"><span id="recordCount">0 records</span></div>
                    <div class="table-wrapper">
                        <table id="dataTable">
                            <thead id="tableHead"></thead>
                            <tbody id="tableBody"></tbody>
                        </table>
                    </div>
                </div>
            </div>
        </main>
    </div>

    <!-- Record Modal -->
    <div class="modal" id="recordModal">
        <div class="modal-content">
            <div class="modal-header">
                <h2 id="modalTitle">Add New Record</h2>
                <button class="close-btn" id="closeModal"><i class="fas fa-times"></i></button>
            </div>
            <div class="modal-body"><form id="recordForm"></form></div>
            <div class="modal-footer">
                <button class="btn btn-secondary" id="cancelBtn">Cancel</button>
                <button class="btn btn-primary" id="saveBtn"><i class="fas fa-save"></i> Save</button>
            </div>
        </div>
    </div>

    <!-- Delete Modal -->
    <div class="modal" id="deleteModal">
        <div class="modal-content modal-small">
            <div class="modal-header">
                <h2>Confirm Delete</h2>
                <button class="close-btn" id="closeDeleteModal"><i class="fas fa-times"></i></button>
            </div>
            <div class="modal-body">
                <p style="text-align: center; font-size: 1rem;">
                    <i class="fas fa-exclamation-triangle" style="font-size: 3rem; color: var(--danger); display: block; margin-bottom: 15px;"></i>
                    Are you sure you want to delete this record?<br>
                    <span style="color: var(--text-gray); font-size: 0.85rem;">This action cannot be undone.</span>
                </p>
            </div>
            <div class="modal-footer">
                <button class="btn btn-secondary" id="cancelDeleteBtn">Cancel</button>
                <button class="btn btn-danger" id="confirmDeleteBtn"><i class="fas fa-trash"></i> Delete</button>
            </div>
        </div>
    </div>

    <!-- Toast -->
    <div class="toast" id="toast">
        <i class="toast-icon"></i>
        <span class="toast-message"></span>
    </div>

    <script>
        let currentTable = null;
        let currentTableData = [];
        let tableSchemas = {};
        let editingPK = null;

        document.addEventListener('DOMContentLoaded', async () => {
            await loadTableSchemas();
            await loadDashboardStats();
            setupEventListeners();
            buildAllTablesGrid();
        });

        async function loadTableSchemas() {
            const response = await fetch('/api/tables');
            tableSchemas = await response.json();
        }

        async function loadDashboardStats() {
            try {
                const response = await fetch('/api/stats');
                const stats = await response.json();
                if (!stats.error) {
                    document.getElementById('statCinemas').textContent = stats.Cinema || 0;
                    document.getElementById('statMovies').textContent = stats.Movie || 0;
                    document.getElementById('statCustomers').textContent = stats.Customer || 0;
                    document.getElementById('statTickets').textContent = stats.Ticket || 0;
                    document.getElementById('statBookings').textContent = stats.Booking || 0;
                    document.getElementById('statPayments').textContent = stats.Payment || 0;
                    document.getElementById('statEmployees').textContent = stats.Employee || 0;
                }
            } catch (error) { console.error('Stats error:', error); }
        }

        function buildAllTablesGrid() {
            const grid = document.getElementById('allTablesGrid');
            grid.innerHTML = '';
            for (const [tableName, schema] of Object.entries(tableSchemas)) {
                const card = document.createElement('div');
                card.className = 'table-card';
                card.innerHTML = `
                    <div class="table-card-icon"><i class="fas ${schema.icon || 'fa-table'}"></i></div>
                    <div class="table-card-info">
                        <div class="table-card-name">${schema.display_name}</div>
                        <div class="table-card-count">${schema.columns.length} columns</div>
                    </div>
                    <i class="fas fa-chevron-right table-card-arrow"></i>
                `;
                card.addEventListener('click', () => loadTable(tableName));
                grid.appendChild(card);
            }
        }

        function setupEventListeners() {
            document.querySelectorAll('.nav-item').forEach(item => {
                item.addEventListener('click', (e) => {
                    e.preventDefault();
                    document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
                    item.classList.add('active');
                    const table = item.dataset.table;
                    const view = item.dataset.view;
                    if (view === 'dashboard') showDashboard();
                    else if (table) loadTable(table);
                    document.getElementById('sidebar').classList.remove('open');
                });
            });
            
            document.getElementById('menuToggle').addEventListener('click', () => {
                document.getElementById('sidebar').classList.toggle('open');
            });
            document.getElementById('addNewBtn').addEventListener('click', () => openModal('add'));
            document.getElementById('closeModal').addEventListener('click', closeModal);
            document.getElementById('cancelBtn').addEventListener('click', closeModal);
            document.getElementById('closeDeleteModal').addEventListener('click', closeDeleteModal);
            document.getElementById('cancelDeleteBtn').addEventListener('click', closeDeleteModal);
            document.getElementById('saveBtn').addEventListener('click', saveRecord);
            document.getElementById('searchInput').addEventListener('input', debounce(handleSearch, 300));
            document.getElementById('recordModal').addEventListener('click', (e) => { if (e.target.id === 'recordModal') closeModal(); });
            document.getElementById('deleteModal').addEventListener('click', (e) => { if (e.target.id === 'deleteModal') closeDeleteModal(); });
        }

        function showDashboard() {
            currentTable = null;
            document.getElementById('pageTitle').textContent = 'Dashboard';
            document.getElementById('dashboardView').style.display = 'block';
            document.getElementById('tableView').style.display = 'none';
            document.getElementById('searchBox').style.display = 'none';
            document.getElementById('addNewBtn').style.display = 'none';
            loadDashboardStats();
        }

        async function loadTable(tableName) {
            currentTable = tableName;
            const schema = tableSchemas[tableName];
            document.getElementById('pageTitle').textContent = schema.display_name;
            document.getElementById('dashboardView').style.display = 'none';
            document.getElementById('tableView').style.display = 'block';
            document.getElementById('searchBox').style.display = 'flex';
            document.getElementById('addNewBtn').style.display = 'flex';
            document.getElementById('searchInput').value = '';
            
            document.getElementById('tableBody').innerHTML = '<tr><td colspan="100" class="loading"><div class="spinner"></div></td></tr>';
            
            try {
                const response = await fetch(`/api/${tableName}`);
                const result = await response.json();
                if (result.error) { showToast(result.error, 'error'); return; }
                currentTableData = result.data;
                renderTable(result.columns, result.data);
            } catch (error) { showToast('Failed to load data', 'error'); }
        }

        function renderTable(columns, data) {
            const schema = tableSchemas[currentTable];
            const thead = document.getElementById('tableHead');
            thead.innerHTML = `<tr>${columns.map(col => `<th>${formatColumnName(col)}</th>`).join('')}<th>Actions</th></tr>`;
            
            const tbody = document.getElementById('tableBody');
            if (data.length === 0) {
                tbody.innerHTML = `<tr><td colspan="${columns.length + 1}"><div class="empty-state"><i class="fas fa-inbox"></i><p>No records found</p></div></td></tr>`;
            } else {
                tbody.innerHTML = data.map(row => `
                    <tr>
                        ${columns.map(col => `<td>${formatValue(row[col])}</td>`).join('')}
                        <td class="actions-cell">
                            <button class="btn btn-sm btn-icon btn-edit" onclick="editRecord('${getPKValue(row, schema.pk)}')"><i class="fas fa-pen"></i></button>
                            <button class="btn btn-sm btn-icon btn-delete" onclick="confirmDelete('${getPKValue(row, schema.pk)}')"><i class="fas fa-trash"></i></button>
                        </td>
                    </tr>
                `).join('');
            }
            document.getElementById('recordCount').textContent = `${data.length} record${data.length !== 1 ? 's' : ''} found`;
        }

        function formatColumnName(name) { return name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()); }
        function formatValue(value) { return value === null || value === undefined ? '<span style="color: var(--text-gray)">—</span>' : escapeHtml(String(value)); }
        function escapeHtml(text) { const div = document.createElement('div'); div.textContent = text; return div.innerHTML; }
        function getPKValue(row, pkColumns) { return pkColumns.map(col => row[col]).join('/'); }

        function openModal(mode, pkValue = null) {
            const schema = tableSchemas[currentTable];
            editingPK = mode === 'edit' ? pkValue : null;
            document.getElementById('modalTitle').textContent = mode === 'edit' ? 'Edit Record' : 'Add New Record';
            
            const existingData = mode === 'edit' ? currentTableData.find(row => getPKValue(row, schema.pk) === pkValue) : null;
            let formHtml = '';
            
            schema.columns.forEach((col, index) => {
                const type = schema.types[index];
                const isRequired = schema.required.includes(col);
                const isPK = schema.pk.includes(col);
                const value = existingData ? existingData[col] : '';
                const constraint = schema.constraints && schema.constraints[col] ? schema.constraints[col] : null;
                const hint = constraint ? `<span class="hint">(${constraint})</span>` : '';
                formHtml += `<div class="form-group"><label>${formatColumnName(col)}${isRequired ? '<span class="required">*</span>' : ''}${hint}</label>${buildInputField(col, type, value, isPK && mode === 'edit')}</div>`;
            });
            
            document.getElementById('recordForm').innerHTML = formHtml;
            document.getElementById('recordModal').classList.add('active');
        }

        function buildInputField(name, type, value, disabled = false) {
            let inputType = 'text';
            let extraAttrs = disabled ? 'disabled' : '';
            
            if (type.includes('int') || type.includes('decimal')) { inputType = 'number'; if (type.includes('decimal')) extraAttrs += ' step="0.01"'; }
            else if (type.includes('date') && !type.includes('time')) { inputType = 'date'; }
            else if (type === 'time' || type.includes('time(')) { inputType = 'time'; if (value && value.includes('.')) value = value.split('.')[0]; }
            
            const selectFields = {
                'gender': ['Male', 'Female', 'Other'],
                'shift_type': ['Morning', 'Afternoon', 'Night'],
                'employment_status': ['Active', 'Inactive', 'On Leave'],
                'payment_method': ['Card', 'Cash'],
                'status': ['Completed', 'Failed'],
                'card_type': ['Visa', 'Mastercard', 'Amex', 'Discover'],
                'seat_type': ['Regular', 'VIP'],
                'contract_type': ['Full-time', 'Part-time', 'Contract']
            };
            
            if (selectFields[name]) {
                return `<select name="${name}" ${extraAttrs}><option value="">Select...</option>${selectFields[name].map(opt => `<option value="${opt}" ${value === opt ? 'selected' : ''}>${opt}</option>`).join('')}</select>`;
            }
            
            return `<input type="${inputType}" name="${name}" value="${value || ''}" ${extraAttrs} placeholder="Enter ${formatColumnName(name).toLowerCase()}">`;
        }

        function closeModal() { document.getElementById('recordModal').classList.remove('active'); editingPK = null; }
        function editRecord(pkValue) { openModal('edit', pkValue); }

        async function saveRecord() {
            const form = document.getElementById('recordForm');
            const data = {};
            form.querySelectorAll('input, select').forEach(input => { if (input.value !== '') data[input.name] = input.value; });
            form.querySelectorAll('input[disabled]').forEach(input => { if (input.value !== '') data[input.name] = input.value; });
            
            try {
                let response;
                if (editingPK) {
                    response = await fetch(`/api/${currentTable}/${editingPK}`, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
                } else {
                    response = await fetch(`/api/${currentTable}`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
                }
                const result = await response.json();
                if (result.error) { showToast(result.error, 'error'); }
                else { showToast(result.message, 'success'); closeModal(); loadTable(currentTable); }
            } catch (error) { showToast('Failed to save record', 'error'); }
        }

        let deletePK = null;
        function confirmDelete(pkValue) {
            deletePK = pkValue;
            document.getElementById('deleteModal').classList.add('active');
            document.getElementById('confirmDeleteBtn').onclick = async () => {
                try {
                    const response = await fetch(`/api/${currentTable}/${deletePK}`, { method: 'DELETE' });
                    const result = await response.json();
                    if (result.error) showToast(result.error, 'error');
                    else { showToast(result.message, 'success'); loadTable(currentTable); }
                } catch (error) { showToast('Failed to delete record', 'error'); }
                closeDeleteModal();
            };
        }
        function closeDeleteModal() { document.getElementById('deleteModal').classList.remove('active'); deletePK = null; }

        async function handleSearch(e) {
            const query = e.target.value;
            if (!query.trim()) { loadTable(currentTable); return; }
            try {
                const response = await fetch(`/api/search/${currentTable}?q=${encodeURIComponent(query)}`);
                const result = await response.json();
                if (result.error) { showToast(result.error, 'error'); return; }
                currentTableData = result.data;
                renderTable(result.columns, result.data);
            } catch (error) { showToast('Search failed', 'error'); }
        }

        function showToast(message, type = 'success') {
            const toast = document.getElementById('toast');
            toast.className = `toast ${type}`;
            toast.querySelector('.toast-icon').className = `toast-icon fas ${type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle'}`;
            toast.querySelector('.toast-message').textContent = message;
            toast.classList.add('show');
            setTimeout(() => { toast.classList.remove('show'); }, 4000);
        }

        function debounce(func, wait) {
            let timeout;
            return function(...args) {
                clearTimeout(timeout);
                timeout = setTimeout(() => func(...args), wait);
            };
        }
    </script>
</body>
</html>
'''

# ============================================
# API ROUTES
# ============================================

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/tables')
def get_tables():
    return jsonify(TABLES)

@app.route('/api/<table>', methods=['GET'])
def get_all_records(table):
    if table not in TABLES:
        return jsonify({'error': 'Table not found'}), 404
    try:
        conn = get_connection()
        cursor = conn.cursor()
        # Handle reserved word 'Order'
        table_name = f'[{table}]' if table == 'Order' else f'[{table}]'
        cursor.execute(f"SELECT * FROM {table_name}")
        columns = [column[0] for column in cursor.description]
        rows = [serialize_row(row, columns) for row in cursor.fetchall()]
        conn.close()
        return jsonify({'data': rows, 'columns': columns})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/<table>', methods=['POST'])
def create_record(table):
    if table not in TABLES:
        return jsonify({'error': 'Table not found'}), 404
    data = request.json
    columns = TABLES[table]['columns']
    insert_cols = [col for col in columns if col in data and data[col] not in [None, '']]
    values = [data[col] for col in insert_cols]
    try:
        conn = get_connection()
        cursor = conn.cursor()
        placeholders = ', '.join(['?' for _ in insert_cols])
        col_names = ', '.join([f'[{col}]' for col in insert_cols])
        table_name = f'[{table}]'
        cursor.execute(f"INSERT INTO {table_name} ({col_names}) VALUES ({placeholders})", values)
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Record created successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/<table>/<path:pk_values>', methods=['GET'])
def get_record(table, pk_values):
    if table not in TABLES:
        return jsonify({'error': 'Table not found'}), 404
    pk_cols = TABLES[table]['pk']
    pk_vals = pk_values.split('/')
    if len(pk_vals) != len(pk_cols):
        return jsonify({'error': 'Invalid primary key'}), 400
    try:
        conn = get_connection()
        cursor = conn.cursor()
        where_clause = ' AND '.join([f"[{col}] = ?" for col in pk_cols])
        table_name = f'[{table}]'
        cursor.execute(f"SELECT * FROM {table_name} WHERE {where_clause}", pk_vals)
        columns = [column[0] for column in cursor.description]
        row = cursor.fetchone()
        conn.close()
        if row:
            return jsonify(serialize_row(row, columns))
        return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/<table>/<path:pk_values>', methods=['PUT'])
def update_record(table, pk_values):
    if table not in TABLES:
        return jsonify({'error': 'Table not found'}), 404
    pk_cols = TABLES[table]['pk']
    pk_vals = pk_values.split('/')
    if len(pk_vals) != len(pk_cols):
        return jsonify({'error': 'Invalid primary key'}), 400
    data = request.json
    columns = TABLES[table]['columns']
    update_cols = [col for col in columns if col not in pk_cols and col in data]
    values = [data[col] if data[col] != '' else None for col in update_cols]
    try:
        conn = get_connection()
        cursor = conn.cursor()
        set_clause = ', '.join([f'[{col}] = ?' for col in update_cols])
        where_clause = ' AND '.join([f'[{col}] = ?' for col in pk_cols])
        table_name = f'[{table}]'
        cursor.execute(f"UPDATE {table_name} SET {set_clause} WHERE {where_clause}", values + pk_vals)
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Record updated successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/<table>/<path:pk_values>', methods=['DELETE'])
def delete_record(table, pk_values):
    if table not in TABLES:
        return jsonify({'error': 'Table not found'}), 404
    pk_cols = TABLES[table]['pk']
    pk_vals = pk_values.split('/')
    if len(pk_vals) != len(pk_cols):
        return jsonify({'error': 'Invalid primary key'}), 400
    try:
        conn = get_connection()
        cursor = conn.cursor()
        where_clause = ' AND '.join([f'[{col}] = ?' for col in pk_cols])
        table_name = f'[{table}]'
        cursor.execute(f"DELETE FROM {table_name} WHERE {where_clause}", pk_vals)
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Record deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats')
def get_stats():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        stats = {}
        for table in TABLES:
            table_name = f'[{table}]'
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            stats[table] = cursor.fetchone()[0]
        conn.close()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/search/<table>')
def search_table(table):
    if table not in TABLES:
        return jsonify({'error': 'Table not found'}), 404
    query = request.args.get('q', '')
    if not query:
        return get_all_records(table)
    columns = TABLES[table]['columns']
    types = TABLES[table]['types']
    search_cols = [col for col, typ in zip(columns, types) if 'varchar' in typ]
    if not search_cols:
        return get_all_records(table)
    try:
        conn = get_connection()
        cursor = conn.cursor()
        conditions = ' OR '.join([f"[{col}] LIKE ?" for col in search_cols])
        search_values = [f'%{query}%' for _ in search_cols]
        table_name = f'[{table}]'
        cursor.execute(f"SELECT * FROM {table_name} WHERE {conditions}", search_values)
        columns = [column[0] for column in cursor.description]
        rows = [serialize_row(row, columns) for row in cursor.fetchall()]
        conn.close()
        return jsonify({'data': rows, 'columns': columns})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================
# RUN THE APP
# ============================================
if __name__ == '__main__':
    print("")
    print("  ╔═══════════════════════════════════════════╗")
    print("  ║                                           ║")
    print("  ║      🎬  CineplexxDB  🎬                  ║")
    print("  ║      Cinema Management System             ║")
    print("  ║                                           ║")
    print("  ╠═══════════════════════════════════════════╣")
    print("  ║                                           ║")
    print("  ║   Server running at:                      ║")
    print("  ║   👉  http://localhost:8080               ║")
    print("  ║                                           ║")
    print("  ║   Press Ctrl+C to stop                    ║")
    print("  ║                                           ║")
    print("  ╚═══════════════════════════════════════════╝")
    print("")
    app.run(debug=True, host='0.0.0.0', port=8080)
