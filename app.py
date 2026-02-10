#!/usr/bin/env python3
"""
CineplexxDB - Cinema Database Management System
Render Deployment Version (PostgreSQL) - Auto-loads sample data
"""
from flask import Flask, render_template_string, request, jsonify
import psycopg
import os
from datetime import date, time
from decimal import Decimal

app = Flask(__name__)

# ============================================
# DATABASE CONFIGURATION (PostgreSQL)
# ============================================
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://localhost/cineplexxdb')

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

def get_connection():
    return psycopg.connect(DATABASE_URL)

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
# TABLE SCHEMAS
# ============================================
TABLES = {
    'cinema': {
        'pk': ['cinema_id'],
        'columns': ['cinema_id', 'location', 'name'],
        'types': ['int', 'varchar(50)', 'varchar(50)'],
        'required': ['cinema_id', 'location', 'name'],
        'display_name': 'Cinemas',
        'icon': 'fa-building-columns'
    },
    'hall': {
        'pk': ['hall_id'],
        'columns': ['hall_id', 'hall_name', 'capacity', 'cinema_id'],
        'types': ['int', 'varchar(50)', 'int', 'int'],
        'required': ['hall_id', 'hall_name', 'capacity', 'cinema_id'],
        'display_name': 'Halls',
        'icon': 'fa-door-open'
    },
    'seat': {
        'pk': ['hall_id', 'seat_number', 'seat_row'],
        'columns': ['hall_id', 'seat_number', 'seat_row', 'seat_type'],
        'types': ['int', 'int', 'varchar(5)', 'varchar(10)'],
        'required': ['hall_id', 'seat_number', 'seat_row', 'seat_type'],
        'display_name': 'Seats',
        'icon': 'fa-chair'
    },
    'movie': {
        'pk': ['movie_id'],
        'columns': ['movie_id', 'title', 'duration', 'release_date', 'language', 'age_rating', 'adult_price', 'kids_price'],
        'types': ['int', 'varchar(100)', 'int', 'date', 'varchar(30)', 'int', 'decimal(8,2)', 'decimal(8,2)'],
        'required': ['movie_id', 'title', 'duration', 'release_date', 'language', 'age_rating', 'adult_price', 'kids_price'],
        'display_name': 'Movies',
        'icon': 'fa-film'
    },
    'genre': {
        'pk': ['genre_id'],
        'columns': ['genre_id', 'genre_name'],
        'types': ['int', 'varchar(30)'],
        'required': ['genre_id', 'genre_name'],
        'display_name': 'Genres',
        'icon': 'fa-tags'
    },
    'movie_genre': {
        'pk': ['movie_id', 'genre_id'],
        'columns': ['movie_id', 'genre_id'],
        'types': ['int', 'int'],
        'required': ['movie_id', 'genre_id'],
        'display_name': 'Movie Genres',
        'icon': 'fa-link'
    },
    'showtime': {
        'pk': ['showtime_id'],
        'columns': ['showtime_id', 'movie_id', 'hall_id', 'show_date', 'start_time', 'end_time'],
        'types': ['int', 'int', 'int', 'date', 'time', 'time'],
        'required': ['showtime_id', 'movie_id', 'hall_id', 'show_date', 'start_time', 'end_time'],
        'display_name': 'Showtimes',
        'icon': 'fa-clock'
    },
    'customer': {
        'pk': ['customer_id'],
        'columns': ['customer_id', 'full_name', 'phone_number', 'email', 'date_of_birth', 'gender'],
        'types': ['int', 'varchar(100)', 'varchar(20)', 'varchar(100)', 'date', 'varchar(10)'],
        'required': ['customer_id', 'full_name', 'email', 'date_of_birth', 'gender'],
        'display_name': 'Customers',
        'icon': 'fa-users'
    },
    'booking': {
        'pk': ['booking_id'],
        'columns': ['booking_id', 'customer_id', 'showtime_id', 'booking_date', 'adult_seat', 'child_seat'],
        'types': ['int', 'int', 'int', 'date', 'int', 'int'],
        'required': ['booking_id', 'customer_id', 'showtime_id', 'booking_date', 'adult_seat', 'child_seat'],
        'display_name': 'Bookings',
        'icon': 'fa-calendar-check'
    },
    'ticket': {
        'pk': ['ticket_id'],
        'columns': ['ticket_id', 'booking_id', 'showtime_id', 'hall_id', 'seat_number', 'seat_row', 'ticket_price'],
        'types': ['int', 'int', 'int', 'int', 'int', 'varchar(5)', 'decimal(8,2)'],
        'required': ['ticket_id', 'booking_id', 'showtime_id', 'hall_id', 'seat_number', 'seat_row', 'ticket_price'],
        'display_name': 'Tickets',
        'icon': 'fa-ticket'
    },
    'department': {
        'pk': ['department_id'],
        'columns': ['department_id', 'department_name'],
        'types': ['int', 'varchar(50)'],
        'required': ['department_id', 'department_name'],
        'display_name': 'Departments',
        'icon': 'fa-sitemap'
    },
    'employee': {
        'pk': ['employee_id'],
        'columns': ['employee_id', 'full_name', 'role', 'phone_number', 'email', 'date_of_birth', 'department_id', 'cinema_id'],
        'types': ['int', 'varchar(100)', 'varchar(30)', 'varchar(20)', 'varchar(100)', 'date', 'int', 'int'],
        'required': ['employee_id', 'full_name', 'role', 'phone_number', 'email', 'date_of_birth', 'department_id', 'cinema_id'],
        'display_name': 'Employees',
        'icon': 'fa-id-badge'
    },
    'manager': {
        'pk': ['employee_id'],
        'columns': ['employee_id', 'management_level', 'contract_type', 'hire_date'],
        'types': ['int', 'int', 'varchar(30)', 'date'],
        'required': ['employee_id', 'management_level', 'contract_type', 'hire_date'],
        'display_name': 'Managers',
        'icon': 'fa-user-tie'
    },
    'cashier': {
        'pk': ['employee_id'],
        'columns': ['employee_id', 'shift_type', 'hire_date', 'employment_status'],
        'types': ['int', 'varchar(20)', 'date', 'varchar(10)'],
        'required': ['employee_id', 'shift_type', 'hire_date'],
        'display_name': 'Cashiers',
        'icon': 'fa-cash-register'
    },
    'cleaner': {
        'pk': ['employee_id'],
        'columns': ['employee_id', 'shift_type'],
        'types': ['int', 'varchar(20)'],
        'required': ['employee_id', 'shift_type'],
        'display_name': 'Cleaners',
        'icon': 'fa-broom'
    },
    'showtime_supervisor': {
        'pk': ['employee_id'],
        'columns': ['employee_id', 'shift_type'],
        'types': ['int', 'varchar(20)'],
        'required': ['employee_id', 'shift_type'],
        'display_name': 'Supervisors',
        'icon': 'fa-user-shield'
    },
    'food': {
        'pk': ['food_id'],
        'columns': ['food_id', 'food_name', 'price'],
        'types': ['int', 'varchar(50)', 'decimal(6,2)'],
        'required': ['food_id', 'food_name', 'price'],
        'display_name': 'Food Items',
        'icon': 'fa-utensils'
    },
    'food_order': {
        'pk': ['order_id'],
        'columns': ['order_id', 'customer_id', 'order_date', 'order_time', 'order_amount'],
        'types': ['int', 'int', 'date', 'time', 'decimal(8,2)'],
        'required': ['order_id', 'customer_id', 'order_date', 'order_time'],
        'display_name': 'Orders',
        'icon': 'fa-receipt'
    },
    'order_food': {
        'pk': ['order_id', 'food_id'],
        'columns': ['order_id', 'food_id', 'quantity'],
        'types': ['int', 'int', 'int'],
        'required': ['order_id', 'food_id', 'quantity'],
        'display_name': 'Order Items',
        'icon': 'fa-list'
    },
    'payment': {
        'pk': ['payment_id'],
        'columns': ['payment_id', 'booking_id', 'order_id', 'payment_date', 'payment_time', 'amount', 'status', 'payment_method'],
        'types': ['int', 'int', 'int', 'date', 'time', 'decimal(8,2)', 'varchar(15)', 'varchar(10)'],
        'required': ['payment_id', 'payment_date', 'payment_time', 'amount', 'status', 'payment_method'],
        'display_name': 'Payments',
        'icon': 'fa-credit-card'
    },
    'cash_payment': {
        'pk': ['payment_id'],
        'columns': ['payment_id', 'change_amount'],
        'types': ['int', 'decimal(6,2)'],
        'required': ['payment_id', 'change_amount'],
        'display_name': 'Cash Payments',
        'icon': 'fa-money-bill-wave'
    },
    'card_payment': {
        'pk': ['payment_id'],
        'columns': ['payment_id', 'card_number', 'card_type', 'expiry_date', 'cardholder_name'],
        'types': ['int', 'varchar(20)', 'varchar(20)', 'date', 'varchar(100)'],
        'required': ['payment_id', 'card_number', 'card_type', 'expiry_date', 'cardholder_name'],
        'display_name': 'Card Payments',
        'icon': 'fa-credit-card'
    }
}

# ============================================
# HTML TEMPLATE
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
            --accent: #f5c518;
            --bg-dark: #141414;
            --bg-card: #1f1f1f;
            --bg-hover: #2a2a2a;
            --bg-input: #333333;
            --text-white: #ffffff;
            --text-light: #e5e5e5;
            --text-gray: #808080;
            --text-dark: #b3b3b3;
            --success: #46d369;
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
        body { font-family: 'Poppins', sans-serif; background-color: var(--bg-dark); color: var(--text-light); line-height: 1.6; }
        .app-container { display: flex; min-height: 100vh; }
        
        .sidebar { width: var(--sidebar-width); background: linear-gradient(180deg, #1a1a1a 0%, #0d0d0d 100%); border-right: 1px solid var(--border-color); position: fixed; height: 100vh; overflow-y: auto; z-index: 1000; }
        .sidebar::-webkit-scrollbar { width: 5px; }
        .sidebar::-webkit-scrollbar-thumb { background: var(--primary); border-radius: 5px; }
        
        .logo { padding: 25px 20px; display: flex; align-items: center; gap: 12px; border-bottom: 1px solid var(--border-color); background: linear-gradient(135deg, rgba(229, 9, 20, 0.1) 0%, transparent 100%); }
        .logo-icon { width: 45px; height: 45px; background: var(--primary); border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 1.4rem; color: white; box-shadow: 0 4px 15px rgba(229, 9, 20, 0.4); }
        .logo-text { font-size: 1.5rem; font-weight: 700; background: linear-gradient(135deg, var(--primary) 0%, var(--accent) 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
        
        .nav-section { padding: 15px 0; }
        .nav-section-title { padding: 8px 25px; font-size: 0.65rem; font-weight: 600; text-transform: uppercase; letter-spacing: 1.5px; color: var(--text-gray); }
        .nav-item { display: flex; align-items: center; gap: 14px; padding: 10px 25px; color: var(--text-dark); text-decoration: none; cursor: pointer; font-size: 0.85rem; font-weight: 500; transition: all 0.3s ease; border-left: 3px solid transparent; }
        .nav-item:hover { background: linear-gradient(90deg, rgba(229, 9, 20, 0.15) 0%, transparent 100%); color: var(--text-white); border-left-color: var(--primary); }
        .nav-item.active { background: linear-gradient(90deg, rgba(229, 9, 20, 0.2) 0%, transparent 100%); color: var(--primary); border-left-color: var(--primary); }
        .nav-item i { width: 20px; text-align: center; font-size: 0.9rem; }
        
        .main-content { flex: 1; margin-left: var(--sidebar-width); min-height: 100vh; background: var(--bg-dark); }
        
        .header { display: flex; justify-content: space-between; align-items: center; padding: 0 35px; height: var(--header-height); background: rgba(20, 20, 20, 0.95); backdrop-filter: blur(10px); border-bottom: 1px solid var(--border-color); position: sticky; top: 0; z-index: 100; }
        .header h1 { font-size: 1.5rem; font-weight: 600; color: var(--text-white); }
        .header-right { display: flex; align-items: center; gap: 15px; }
        
        .search-box { display: flex; align-items: center; background: var(--bg-input); border: 1px solid var(--border-color); border-radius: 25px; padding: 10px 20px; gap: 12px; transition: all 0.3s ease; }
        .search-box:focus-within { border-color: var(--primary); box-shadow: 0 0 0 3px rgba(229, 9, 20, 0.2); }
        .search-box i { color: var(--text-gray); }
        .search-box input { background: none; border: none; color: var(--text-white); outline: none; width: 220px; font-size: 0.9rem; font-family: 'Poppins', sans-serif; }
        .search-box input::placeholder { color: var(--text-gray); }
        
        .btn { display: inline-flex; align-items: center; gap: 10px; padding: 12px 24px; border: none; border-radius: 25px; font-size: 0.9rem; font-weight: 600; cursor: pointer; transition: all 0.3s ease; font-family: 'Poppins', sans-serif; }
        .btn-primary { background: var(--primary); color: white; box-shadow: 0 4px 15px rgba(229, 9, 20, 0.3); }
        .btn-primary:hover { background: var(--primary-dark); transform: translateY(-2px); }
        .btn-secondary { background: var(--bg-input); color: var(--text-light); border: 1px solid var(--border-color); }
        .btn-secondary:hover { background: var(--bg-hover); }
        .btn-danger { background: var(--danger); color: white; }
        .btn-sm { padding: 8px 14px; font-size: 0.8rem; }
        .btn-icon { padding: 10px; border-radius: 10px; min-width: 40px; justify-content: center; }
        .btn-edit { background: var(--info); color: white; }
        .btn-delete { background: transparent; color: var(--danger); border: 1px solid var(--danger); }
        .btn-delete:hover { background: var(--danger); color: white; }
        
        .content { padding: 35px; }
        
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 40px; }
        .stat-card { background: var(--bg-card); border-radius: var(--radius-lg); padding: 22px; display: flex; align-items: center; gap: 18px; border: 1px solid var(--border-color); transition: all 0.3s ease; position: relative; overflow: hidden; }
        .stat-card::before { content: ''; position: absolute; top: 0; left: 0; width: 100%; height: 3px; background: linear-gradient(90deg, var(--primary), var(--accent)); }
        .stat-card:hover { transform: translateY(-5px); box-shadow: var(--shadow); border-color: var(--primary); }
        .stat-icon { width: 55px; height: 55px; border-radius: 14px; display: flex; align-items: center; justify-content: center; font-size: 1.4rem; }
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
        
        .section-title { font-size: 1.3rem; font-weight: 600; margin-bottom: 20px; color: var(--text-white); display: flex; align-items: center; gap: 10px; }
        .section-title::before { content: ''; width: 4px; height: 24px; background: var(--primary); border-radius: 2px; }
        
        .tables-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 12px; }
        .table-card { background: var(--bg-card); border: 1px solid var(--border-color); border-radius: var(--radius); padding: 16px; display: flex; align-items: center; gap: 12px; cursor: pointer; transition: all 0.3s ease; }
        .table-card:hover { background: var(--bg-hover); border-color: var(--primary); transform: translateX(5px); }
        .table-card-icon { width: 40px; height: 40px; background: rgba(229, 9, 20, 0.1); border-radius: 10px; display: flex; align-items: center; justify-content: center; color: var(--primary); font-size: 1rem; }
        .table-card-info { flex: 1; }
        .table-card-name { font-weight: 600; color: var(--text-white); font-size: 0.9rem; }
        .table-card-count { font-size: 0.75rem; color: var(--text-gray); }
        .table-card-arrow { color: var(--text-gray); transition: all 0.3s ease; }
        .table-card:hover .table-card-arrow { color: var(--primary); transform: translateX(5px); }
        
        .table-container { background: var(--bg-card); border-radius: var(--radius-lg); border: 1px solid var(--border-color); overflow: hidden; }
        .table-header { padding: 20px 25px; border-bottom: 1px solid var(--border-color); display: flex; justify-content: space-between; align-items: center; background: linear-gradient(90deg, rgba(229, 9, 20, 0.05) 0%, transparent 100%); }
        .table-header span { color: var(--text-gray); font-size: 0.9rem; }
        .table-wrapper { overflow-x: auto; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 14px 20px; text-align: left; border-bottom: 1px solid var(--border-color); }
        th { background: rgba(255, 255, 255, 0.03); font-weight: 600; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1px; color: var(--text-gray); white-space: nowrap; }
        td { font-size: 0.85rem; color: var(--text-light); }
        tr:hover td { background: rgba(229, 9, 20, 0.03); }
        .actions-cell { display: flex; gap: 8px; }
        
        .modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0, 0, 0, 0.85); backdrop-filter: blur(5px); z-index: 2000; justify-content: center; align-items: center; padding: 20px; }
        .modal.active { display: flex; }
        .modal-content { background: var(--bg-card); border-radius: var(--radius-lg); width: 100%; max-width: 550px; max-height: 90vh; overflow: hidden; border: 1px solid var(--border-color); box-shadow: 0 25px 50px rgba(0, 0, 0, 0.5); }
        .modal-small { max-width: 420px; }
        .modal-header { display: flex; justify-content: space-between; align-items: center; padding: 25px 30px; border-bottom: 1px solid var(--border-color); background: linear-gradient(90deg, rgba(229, 9, 20, 0.1) 0%, transparent 100%); }
        .modal-header h2 { font-size: 1.2rem; font-weight: 600; color: var(--text-white); }
        .close-btn { width: 35px; height: 35px; background: var(--bg-input); border: none; border-radius: 50%; color: var(--text-gray); font-size: 1.2rem; cursor: pointer; transition: all 0.3s ease; display: flex; align-items: center; justify-content: center; }
        .close-btn:hover { background: var(--danger); color: white; }
        .modal-body { padding: 30px; max-height: calc(90vh - 160px); overflow-y: auto; }
        .modal-footer { display: flex; justify-content: flex-end; gap: 12px; padding: 20px 30px; border-top: 1px solid var(--border-color); background: rgba(0, 0, 0, 0.2); }
        
        .form-group { margin-bottom: 20px; }
        .form-group label { display: block; margin-bottom: 8px; font-weight: 500; font-size: 0.85rem; color: var(--text-light); }
        .form-group .required { color: var(--primary); margin-left: 3px; }
        .form-group input, .form-group select { width: 100%; padding: 12px 16px; background: var(--bg-input); border: 1px solid var(--border-color); border-radius: var(--radius); color: var(--text-white); font-size: 0.9rem; font-family: 'Poppins', sans-serif; transition: all 0.3s ease; }
        .form-group input:focus, .form-group select:focus { outline: none; border-color: var(--primary); box-shadow: 0 0 0 3px rgba(229, 9, 20, 0.2); }
        .form-group input:disabled { opacity: 0.6; cursor: not-allowed; }
        
        .toast { position: fixed; bottom: 30px; right: 30px; background: var(--bg-card); border: 1px solid var(--border-color); border-radius: var(--radius); padding: 18px 25px; display: flex; align-items: center; gap: 15px; transform: translateY(100px); opacity: 0; transition: all 0.4s ease; z-index: 3000; box-shadow: var(--shadow); max-width: 400px; }
        .toast.show { transform: translateY(0); opacity: 1; }
        .toast.success { border-left: 4px solid var(--success); }
        .toast.success .toast-icon { color: var(--success); }
        .toast.error { border-left: 4px solid var(--danger); }
        .toast.error .toast-icon { color: var(--danger); }
        .toast-icon { font-size: 1.3rem; }
        .toast-message { font-size: 0.85rem; color: var(--text-light); }
        
        .loading { display: flex; justify-content: center; padding: 60px; }
        .spinner { width: 45px; height: 45px; border: 4px solid var(--border-color); border-top-color: var(--primary); border-radius: 50%; animation: spin 0.8s linear infinite; }
        @keyframes spin { to { transform: rotate(360deg); } }
        
        .empty-state { text-align: center; padding: 60px; color: var(--text-gray); }
        .empty-state i { font-size: 4rem; margin-bottom: 20px; color: var(--border-color); }
        .empty-state p { font-size: 1.1rem; }
        
        .menu-toggle { display: none; background: none; border: none; color: var(--text-white); font-size: 1.3rem; cursor: pointer; margin-right: 20px; }
        
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
        <aside class="sidebar" id="sidebar">
            <div class="logo">
                <div class="logo-icon"><i class="fas fa-film"></i></div>
                <span class="logo-text">CineplexxDB</span>
            </div>
            <div class="nav-section">
                <div class="nav-section-title">Main Menu</div>
                <a href="#" class="nav-item active" data-view="dashboard"><i class="fas fa-th-large"></i><span>Dashboard</span></a>
            </div>
            <div class="nav-section">
                <div class="nav-section-title">Locations</div>
                <a href="#" class="nav-item" data-table="cinema"><i class="fas fa-building-columns"></i><span>Cinemas</span></a>
                <a href="#" class="nav-item" data-table="hall"><i class="fas fa-door-open"></i><span>Halls</span></a>
                <a href="#" class="nav-item" data-table="seat"><i class="fas fa-chair"></i><span>Seats</span></a>
            </div>
            <div class="nav-section">
                <div class="nav-section-title">Movies & Shows</div>
                <a href="#" class="nav-item" data-table="movie"><i class="fas fa-film"></i><span>Movies</span></a>
                <a href="#" class="nav-item" data-table="genre"><i class="fas fa-tags"></i><span>Genres</span></a>
                <a href="#" class="nav-item" data-table="movie_genre"><i class="fas fa-link"></i><span>Movie Genres</span></a>
                <a href="#" class="nav-item" data-table="showtime"><i class="fas fa-clock"></i><span>Showtimes</span></a>
            </div>
            <div class="nav-section">
                <div class="nav-section-title">Customers & Bookings</div>
                <a href="#" class="nav-item" data-table="customer"><i class="fas fa-users"></i><span>Customers</span></a>
                <a href="#" class="nav-item" data-table="booking"><i class="fas fa-calendar-check"></i><span>Bookings</span></a>
                <a href="#" class="nav-item" data-table="ticket"><i class="fas fa-ticket"></i><span>Tickets</span></a>
            </div>
            <div class="nav-section">
                <div class="nav-section-title">Concessions</div>
                <a href="#" class="nav-item" data-table="food"><i class="fas fa-utensils"></i><span>Food Menu</span></a>
                <a href="#" class="nav-item" data-table="food_order"><i class="fas fa-receipt"></i><span>Orders</span></a>
                <a href="#" class="nav-item" data-table="order_food"><i class="fas fa-list"></i><span>Order Items</span></a>
            </div>
            <div class="nav-section">
                <div class="nav-section-title">Payments</div>
                <a href="#" class="nav-item" data-table="payment"><i class="fas fa-credit-card"></i><span>All Payments</span></a>
                <a href="#" class="nav-item" data-table="card_payment"><i class="fas fa-credit-card"></i><span>Card Payments</span></a>
                <a href="#" class="nav-item" data-table="cash_payment"><i class="fas fa-money-bill-wave"></i><span>Cash Payments</span></a>
            </div>
            <div class="nav-section">
                <div class="nav-section-title">Staff Management</div>
                <a href="#" class="nav-item" data-table="employee"><i class="fas fa-id-badge"></i><span>Employees</span></a>
                <a href="#" class="nav-item" data-table="department"><i class="fas fa-sitemap"></i><span>Departments</span></a>
                <a href="#" class="nav-item" data-table="manager"><i class="fas fa-user-tie"></i><span>Managers</span></a>
                <a href="#" class="nav-item" data-table="cashier"><i class="fas fa-cash-register"></i><span>Cashiers</span></a>
                <a href="#" class="nav-item" data-table="cleaner"><i class="fas fa-broom"></i><span>Cleaners</span></a>
                <a href="#" class="nav-item" data-table="showtime_supervisor"><i class="fas fa-user-shield"></i><span>Supervisors</span></a>
            </div>
        </aside>

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
                        <i class="fas fa-plus"></i><span>Add New</span>
                    </button>
                </div>
            </header>

            <div class="content" id="dashboardView">
                <div class="stats-grid">
                    <div class="stat-card"><div class="stat-icon teal"><i class="fas fa-building-columns"></i></div><div class="stat-info"><span class="stat-value" id="statCinemas">-</span><span class="stat-label">Cinemas</span></div></div>
                    <div class="stat-card"><div class="stat-icon red"><i class="fas fa-film"></i></div><div class="stat-info"><span class="stat-value" id="statMovies">-</span><span class="stat-label">Movies</span></div></div>
                    <div class="stat-card"><div class="stat-icon gold"><i class="fas fa-users"></i></div><div class="stat-info"><span class="stat-value" id="statCustomers">-</span><span class="stat-label">Customers</span></div></div>
                    <div class="stat-card"><div class="stat-icon green"><i class="fas fa-ticket"></i></div><div class="stat-info"><span class="stat-value" id="statTickets">-</span><span class="stat-label">Tickets Sold</span></div></div>
                    <div class="stat-card"><div class="stat-icon blue"><i class="fas fa-calendar-check"></i></div><div class="stat-info"><span class="stat-value" id="statBookings">-</span><span class="stat-label">Bookings</span></div></div>
                    <div class="stat-card"><div class="stat-icon purple"><i class="fas fa-credit-card"></i></div><div class="stat-info"><span class="stat-value" id="statPayments">-</span><span class="stat-label">Payments</span></div></div>
                    <div class="stat-card"><div class="stat-icon orange"><i class="fas fa-id-badge"></i></div><div class="stat-info"><span class="stat-value" id="statEmployees">-</span><span class="stat-label">Employees</span></div></div>
                </div>
                <h2 class="section-title">All Tables</h2>
                <div class="tables-grid" id="allTablesGrid"></div>
            </div>

            <div class="content" id="tableView" style="display: none;">
                <div class="table-container">
                    <div class="table-header"><span id="recordCount">0 records</span></div>
                    <div class="table-wrapper">
                        <table id="dataTable"><thead id="tableHead"></thead><tbody id="tableBody"></tbody></table>
                    </div>
                </div>
            </div>
        </main>
    </div>

    <div class="modal" id="recordModal">
        <div class="modal-content">
            <div class="modal-header"><h2 id="modalTitle">Add New Record</h2><button class="close-btn" id="closeModal"><i class="fas fa-times"></i></button></div>
            <div class="modal-body"><form id="recordForm"></form></div>
            <div class="modal-footer"><button class="btn btn-secondary" id="cancelBtn">Cancel</button><button class="btn btn-primary" id="saveBtn"><i class="fas fa-save"></i> Save</button></div>
        </div>
    </div>

    <div class="modal" id="deleteModal">
        <div class="modal-content modal-small">
            <div class="modal-header"><h2>Confirm Delete</h2><button class="close-btn" id="closeDeleteModal"><i class="fas fa-times"></i></button></div>
            <div class="modal-body"><p style="text-align: center; font-size: 1rem;"><i class="fas fa-exclamation-triangle" style="font-size: 3rem; color: var(--danger); display: block; margin-bottom: 15px;"></i>Are you sure you want to delete this record?<br><span style="color: var(--text-gray); font-size: 0.85rem;">This action cannot be undone.</span></p></div>
            <div class="modal-footer"><button class="btn btn-secondary" id="cancelDeleteBtn">Cancel</button><button class="btn btn-danger" id="confirmDeleteBtn"><i class="fas fa-trash"></i> Delete</button></div>
        </div>
    </div>

    <div class="toast" id="toast"><i class="toast-icon"></i><span class="toast-message"></span></div>

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
                    document.getElementById('statCinemas').textContent = stats.cinema || 0;
                    document.getElementById('statMovies').textContent = stats.movie || 0;
                    document.getElementById('statCustomers').textContent = stats.customer || 0;
                    document.getElementById('statTickets').textContent = stats.ticket || 0;
                    document.getElementById('statBookings').textContent = stats.booking || 0;
                    document.getElementById('statPayments').textContent = stats.payment || 0;
                    document.getElementById('statEmployees').textContent = stats.employee || 0;
                }
            } catch (error) { console.error('Stats error:', error); }
        }

        function buildAllTablesGrid() {
            const grid = document.getElementById('allTablesGrid');
            grid.innerHTML = '';
            for (const [tableName, schema] of Object.entries(tableSchemas)) {
                const card = document.createElement('div');
                card.className = 'table-card';
                card.innerHTML = `<div class="table-card-icon"><i class="fas ${schema.icon || 'fa-table'}"></i></div><div class="table-card-info"><div class="table-card-name">${schema.display_name}</div><div class="table-card-count">${schema.columns.length} columns</div></div><i class="fas fa-chevron-right table-card-arrow"></i>`;
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
            document.getElementById('menuToggle').addEventListener('click', () => { document.getElementById('sidebar').classList.toggle('open'); });
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
                tbody.innerHTML = data.map(row => `<tr>${columns.map(col => `<td>${formatValue(row[col])}</td>`).join('')}<td class="actions-cell"><button class="btn btn-sm btn-icon btn-edit" onclick="editRecord('${getPKValue(row, schema.pk)}')"><i class="fas fa-pen"></i></button><button class="btn btn-sm btn-icon btn-delete" onclick="confirmDelete('${getPKValue(row, schema.pk)}')"><i class="fas fa-trash"></i></button></td></tr>`).join('');
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
                formHtml += `<div class="form-group"><label>${formatColumnName(col)}${isRequired ? '<span class="required">*</span>' : ''}</label>${buildInputField(col, type, value, isPK && mode === 'edit')}</div>`;
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
            const selectFields = { 'gender': ['Male', 'Female', 'Other'], 'shift_type': ['Morning', 'Afternoon', 'Night'], 'employment_status': ['Active', 'Inactive', 'On Leave'], 'payment_method': ['Card', 'Cash'], 'status': ['Completed', 'Failed'], 'card_type': ['Visa', 'Mastercard', 'Amex', 'Discover'], 'seat_type': ['Regular', 'VIP'], 'contract_type': ['Full-time', 'Part-time', 'Contract'] };
            if (selectFields[name]) { return `<select name="${name}" ${extraAttrs}><option value="">Select...</option>${selectFields[name].map(opt => `<option value="${opt}" ${value === opt ? 'selected' : ''}>${opt}</option>`).join('')}</select>`; }
            return `<input type="${inputType}" name="${name}" value="${value || ''}" ${extraAttrs}>`;
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
                if (editingPK) { response = await fetch(`/api/${currentTable}/${editingPK}`, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) }); }
                else { response = await fetch(`/api/${currentTable}`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) }); }
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

        function debounce(func, wait) { let timeout; return function(...args) { clearTimeout(timeout); timeout = setTimeout(() => func(...args), wait); }; }
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
        cursor.execute(f'SELECT * FROM "{table}"')
        columns = [desc[0] for desc in cursor.description]
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
        placeholders = ', '.join(['%s' for _ in insert_cols])
        col_names = ', '.join([f'"{col}"' for col in insert_cols])
        cursor.execute(f'INSERT INTO "{table}" ({col_names}) VALUES ({placeholders})', values)
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
        where_clause = ' AND '.join([f'"{col}" = %s' for col in pk_cols])
        cursor.execute(f'SELECT * FROM "{table}" WHERE {where_clause}', pk_vals)
        columns = [desc[0] for desc in cursor.description]
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
        set_clause = ', '.join([f'"{col}" = %s' for col in update_cols])
        where_clause = ' AND '.join([f'"{col}" = %s' for col in pk_cols])
        cursor.execute(f'UPDATE "{table}" SET {set_clause} WHERE {where_clause}', values + pk_vals)
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
        where_clause = ' AND '.join([f'"{col}" = %s' for col in pk_cols])
        cursor.execute(f'DELETE FROM "{table}" WHERE {where_clause}', pk_vals)
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
            cursor.execute(f'SELECT COUNT(*) FROM "{table}"')
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
        conditions = ' OR '.join([f'"{col}" ILIKE %s' for col in search_cols])
        search_values = [f'%{query}%' for _ in search_cols]
        cursor.execute(f'SELECT * FROM "{table}" WHERE {conditions}', search_values)
        columns = [desc[0] for desc in cursor.description]
        rows = [serialize_row(row, columns) for row in cursor.fetchall()]
        conn.close()
        return jsonify({'data': rows, 'columns': columns})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================
# INITIALIZE DATABASE WITH SAMPLE DATA
# ============================================
def init_db():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cinema (
                cinema_id INT PRIMARY KEY,
                location VARCHAR(50) NOT NULL,
                name VARCHAR(50) NOT NULL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS department (
                department_id INT PRIMARY KEY,
                department_name VARCHAR(50) NOT NULL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS customer (
                customer_id INT PRIMARY KEY,
                full_name VARCHAR(100) NOT NULL,
                phone_number VARCHAR(20) UNIQUE,
                email VARCHAR(100) UNIQUE NOT NULL,
                date_of_birth DATE NOT NULL,
                gender VARCHAR(10) NOT NULL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS genre (
                genre_id INT PRIMARY KEY,
                genre_name VARCHAR(30) NOT NULL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS hall (
                hall_id INT PRIMARY KEY,
                hall_name VARCHAR(50) NOT NULL,
                capacity INT NOT NULL CHECK (capacity > 0),
                cinema_id INT NOT NULL REFERENCES cinema(cinema_id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS food (
                food_id INT PRIMARY KEY,
                food_name VARCHAR(50) NOT NULL,
                price DECIMAL(6,2) NOT NULL CHECK (price > 0)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS movie (
                movie_id INT PRIMARY KEY,
                title VARCHAR(100) NOT NULL,
                duration INT NOT NULL CHECK (duration > 0),
                release_date DATE NOT NULL,
                language VARCHAR(30) NOT NULL,
                age_rating INT NOT NULL CHECK (age_rating >= 0),
                adult_price DECIMAL(8,2) NOT NULL,
                kids_price DECIMAL(8,2) NOT NULL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS employee (
                employee_id INT PRIMARY KEY,
                full_name VARCHAR(100) NOT NULL,
                role VARCHAR(30) NOT NULL,
                phone_number VARCHAR(20) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                date_of_birth DATE NOT NULL,
                department_id INT NOT NULL REFERENCES department(department_id),
                cinema_id INT NOT NULL REFERENCES cinema(cinema_id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS seat (
                hall_id INT NOT NULL,
                seat_number INT NOT NULL,
                seat_row VARCHAR(5) NOT NULL,
                seat_type VARCHAR(10) NOT NULL CHECK (seat_type IN ('Regular', 'VIP')),
                PRIMARY KEY (hall_id, seat_number, seat_row),
                FOREIGN KEY (hall_id) REFERENCES hall(hall_id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS movie_genre (
                movie_id INT NOT NULL,
                genre_id INT NOT NULL,
                PRIMARY KEY (movie_id, genre_id),
                FOREIGN KEY (movie_id) REFERENCES movie(movie_id),
                FOREIGN KEY (genre_id) REFERENCES genre(genre_id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS showtime (
                showtime_id INT PRIMARY KEY,
                movie_id INT NOT NULL REFERENCES movie(movie_id),
                hall_id INT NOT NULL REFERENCES hall(hall_id),
                show_date DATE NOT NULL,
                start_time TIME NOT NULL,
                end_time TIME NOT NULL,
                CHECK (end_time > start_time)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS booking (
                booking_id INT PRIMARY KEY,
                customer_id INT NOT NULL REFERENCES customer(customer_id),
                showtime_id INT NOT NULL REFERENCES showtime(showtime_id),
                booking_date DATE NOT NULL,
                adult_seat INT NOT NULL CHECK (adult_seat >= 0),
                child_seat INT NOT NULL CHECK (child_seat >= 0)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ticket (
                ticket_id INT PRIMARY KEY,
                booking_id INT NOT NULL REFERENCES booking(booking_id),
                showtime_id INT NOT NULL REFERENCES showtime(showtime_id),
                hall_id INT NOT NULL,
                seat_number INT NOT NULL,
                seat_row VARCHAR(5) NOT NULL,
                ticket_price DECIMAL(8,2) NOT NULL CHECK (ticket_price > 0),
                FOREIGN KEY (hall_id, seat_number, seat_row) REFERENCES seat(hall_id, seat_number, seat_row)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS manager (
                employee_id INT PRIMARY KEY REFERENCES employee(employee_id),
                management_level INT NOT NULL,
                contract_type VARCHAR(30) NOT NULL,
                hire_date DATE NOT NULL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cashier (
                employee_id INT PRIMARY KEY REFERENCES employee(employee_id),
                shift_type VARCHAR(20) NOT NULL,
                hire_date DATE NOT NULL,
                employment_status VARCHAR(10)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cleaner (
                employee_id INT PRIMARY KEY REFERENCES employee(employee_id),
                shift_type VARCHAR(20) NOT NULL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS showtime_supervisor (
                employee_id INT PRIMARY KEY REFERENCES employee(employee_id),
                shift_type VARCHAR(20) NOT NULL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS food_order (
                order_id INT PRIMARY KEY,
                customer_id INT NOT NULL REFERENCES customer(customer_id),
                order_date DATE NOT NULL,
                order_time TIME NOT NULL,
                order_amount DECIMAL(8,2) CHECK (order_amount > 0)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS order_food (
                order_id INT NOT NULL REFERENCES food_order(order_id),
                food_id INT NOT NULL REFERENCES food(food_id),
                quantity INT NOT NULL CHECK (quantity > 0),
                PRIMARY KEY (order_id, food_id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS payment (
                payment_id INT PRIMARY KEY,
                booking_id INT REFERENCES booking(booking_id),
                order_id INT REFERENCES food_order(order_id),
                payment_date DATE NOT NULL,
                payment_time TIME NOT NULL,
                amount DECIMAL(8,2) NOT NULL CHECK (amount > 0),
                status VARCHAR(15) NOT NULL CHECK (status IN ('Completed', 'Failed')),
                payment_method VARCHAR(10) NOT NULL CHECK (payment_method IN ('Cash', 'Card'))
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cash_payment (
                payment_id INT PRIMARY KEY REFERENCES payment(payment_id),
                change_amount DECIMAL(6,2) NOT NULL CHECK (change_amount >= 0)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS card_payment (
                payment_id INT PRIMARY KEY REFERENCES payment(payment_id),
                card_number VARCHAR(20) NOT NULL,
                card_type VARCHAR(20) NOT NULL,
                expiry_date DATE NOT NULL,
                cardholder_name VARCHAR(100) NOT NULL
            )
        ''')
        
        conn.commit()
        
        # Check if data exists
        cursor.execute('SELECT COUNT(*) FROM cinema')
        if cursor.fetchone()[0] == 0:
            # Insert sample data
            print("Loading sample data...")
            
            # Cinema
            cursor.execute('''INSERT INTO cinema (cinema_id, location, name) VALUES 
                (1, 'Tirana', 'Cineplexx TEG'),
                (2, 'Tirana', 'Cineplexx City Park'),
                (3, 'Durres', 'Cineplexx Durres')''')
            
            # Department
            cursor.execute('''INSERT INTO department (department_id, department_name) VALUES 
                (1, 'Management'), (2, 'Box Office'), (3, 'Concessions'),
                (4, 'Projection'), (5, 'Maintenance'), (6, 'Security')''')
            
            # Customer
            cursor.execute('''INSERT INTO customer (customer_id, full_name, phone_number, email, date_of_birth, gender) VALUES 
                (1, 'Arben Hoxha', '+355691234567', 'arben.hoxha@email.com', '1990-05-15', 'Male'),
                (2, 'Maria Koci', '+355692345678', 'maria.koci@email.com', '1985-08-22', 'Female'),
                (3, 'Dritan Leka', '+355693456789', 'dritan.leka@email.com', '1992-03-10', 'Male'),
                (4, 'Elena Brahimi', '+355694567890', 'elena.brahimi@email.com', '1988-12-01', 'Female'),
                (5, 'Besnik Shehu', '+355695678901', 'besnik.shehu@email.com', '1995-07-25', 'Male')''')
            
            # Genre
            cursor.execute('''INSERT INTO genre (genre_id, genre_name) VALUES 
                (1, 'Action'), (2, 'Comedy'), (3, 'Drama'), (4, 'Horror'), (5, 'Science Fiction'),
                (6, 'Romance'), (7, 'Thriller'), (8, 'Animation'), (9, 'Adventure'), (10, 'Fantasy')''')
            
            # Hall
            cursor.execute('''INSERT INTO hall (hall_id, hall_name, capacity, cinema_id) VALUES 
                (1, 'Hall A - IMAX', 200, 1),
                (2, 'Hall B - Premium', 150, 1),
                (3, 'Hall C - Standard', 120, 1),
                (4, 'Hall D - Standard', 120, 2),
                (5, 'Hall E - VIP', 50, 2)''')
            
            # Food
            cursor.execute('''INSERT INTO food (food_id, food_name, price) VALUES 
                (1, 'Small Popcorn', 350.00), (2, 'Medium Popcorn', 500.00), (3, 'Large Popcorn', 650.00),
                (4, 'Small Soda', 200.00), (5, 'Medium Soda', 300.00), (6, 'Large Soda', 400.00),
                (7, 'Hot Dog', 450.00), (8, 'Nachos', 550.00)''')
            
            # Movie
            cursor.execute('''INSERT INTO movie (movie_id, title, duration, release_date, language, age_rating, adult_price, kids_price) VALUES 
                (1, 'The Dark Knight Returns', 152, '2025-06-15', 'English', 13, 800.00, 500.00),
                (2, 'Love in Paris', 118, '2025-07-20', 'English', 12, 700.00, 450.00),
                (3, 'Alien Invasion 3', 135, '2025-08-10', 'English', 16, 850.00, 550.00),
                (4, 'Comedy Night', 95, '2025-09-01', 'English', 7, 600.00, 400.00),
                (5, 'Frozen Dreams', 105, '2025-10-01', 'English', 0, 650.00, 450.00)''')
            
            # Employee
            cursor.execute('''INSERT INTO employee (employee_id, full_name, role, phone_number, email, date_of_birth, department_id, cinema_id) VALUES 
                (1, 'Robert Pasha', 'General Manager', '+355681111111', 'robert.p@cineplexx.al', '1975-03-15', 1, 1),
                (2, 'Sara Kelmendi', 'Operations Manager', '+355682222222', 'sara.k@cineplexx.al', '1980-07-22', 1, 1),
                (3, 'Tom Berisha', 'Floor Manager', '+355683333333', 'tom.b@cineplexx.al', '1985-11-10', 1, 2),
                (4, 'Alba Hoti', 'Senior Cashier', '+355684444444', 'alba.h@cineplexx.al', '1992-05-18', 2, 1),
                (5, 'Bujar Duka', 'Cashier', '+355685555555', 'bujar.d@cineplexx.al', '1995-08-25', 2, 1)''')
            
            # Seat
            cursor.execute('''INSERT INTO seat (hall_id, seat_number, seat_row, seat_type) VALUES 
                (1, 1, 'A', 'Regular'), (1, 2, 'A', 'Regular'), (1, 3, 'A', 'Regular'), (1, 4, 'A', 'Regular'), (1, 5, 'A', 'Regular'),
                (1, 1, 'B', 'Regular'), (1, 2, 'B', 'Regular'), (1, 3, 'B', 'Regular'), (1, 4, 'B', 'Regular'), (1, 5, 'B', 'Regular'),
                (1, 1, 'C', 'VIP'), (1, 2, 'C', 'VIP'), (1, 3, 'C', 'VIP'), (1, 4, 'C', 'VIP'), (1, 5, 'C', 'VIP'),
                (2, 1, 'A', 'VIP'), (2, 2, 'A', 'VIP'), (2, 3, 'A', 'VIP'), (2, 4, 'A', 'VIP'), (2, 5, 'A', 'VIP')''')
            
            # Movie Genre
            cursor.execute('''INSERT INTO movie_genre (movie_id, genre_id) VALUES 
                (1, 1), (1, 7), (2, 6), (2, 2), (3, 5), (3, 1), (4, 2), (5, 8), (5, 10)''')
            
            # Showtime
            cursor.execute('''INSERT INTO showtime (showtime_id, movie_id, hall_id, show_date, start_time, end_time) VALUES 
                (1, 1, 1, '2026-03-01', '10:00:00', '12:32:00'),
                (2, 1, 1, '2026-03-01', '14:00:00', '16:32:00'),
                (3, 2, 2, '2026-03-01', '11:00:00', '12:58:00'),
                (4, 3, 1, '2026-03-02', '18:00:00', '20:15:00')''')
            
            # Manager
            cursor.execute('''INSERT INTO manager (employee_id, management_level, contract_type, hire_date) VALUES 
                (1, 1, 'Full-time', '2015-01-10'),
                (2, 2, 'Full-time', '2017-03-15'),
                (3, 3, 'Full-time', '2019-06-20')''')
            
            # Cashier
            cursor.execute('''INSERT INTO cashier (employee_id, shift_type, hire_date, employment_status) VALUES 
                (4, 'Morning', '2020-02-01', 'Active'),
                (5, 'Afternoon', '2021-05-15', 'Active')''')
            
            # Booking
            cursor.execute('''INSERT INTO booking (booking_id, customer_id, showtime_id, booking_date, adult_seat, child_seat) VALUES 
                (1, 1, 1, '2026-02-28', 2, 0),
                (2, 2, 3, '2026-02-28', 2, 1)''')
            
            # Ticket
            cursor.execute('''INSERT INTO ticket (ticket_id, booking_id, showtime_id, hall_id, seat_number, seat_row, ticket_price) VALUES 
                (1, 1, 1, 1, 1, 'A', 800.00),
                (2, 1, 1, 1, 2, 'A', 800.00),
                (3, 2, 3, 2, 1, 'A', 700.00),
                (4, 2, 3, 2, 2, 'A', 700.00),
                (5, 2, 3, 2, 3, 'A', 450.00)''')
            
            # Food Order
            cursor.execute('''INSERT INTO food_order (order_id, customer_id, order_date, order_time, order_amount) VALUES 
                (1, 1, '2026-03-01', '09:45:00', 1200.00),
                (2, 2, '2026-03-01', '10:30:00', 950.00)''')
            
            # Order Food
            cursor.execute('''INSERT INTO order_food (order_id, food_id, quantity) VALUES 
                (1, 3, 1), (1, 6, 2), (2, 2, 1), (2, 5, 1)''')
            
            # Payment
            cursor.execute('''INSERT INTO payment (payment_id, booking_id, order_id, payment_date, payment_time, amount, status, payment_method) VALUES 
                (1, 1, 1, '2026-03-01', '09:50:00', 2800.00, 'Completed', 'Card'),
                (2, 2, 2, '2026-03-01', '10:35:00', 2800.00, 'Completed', 'Cash')''')
            
            # Card Payment
            cursor.execute('''INSERT INTO card_payment (payment_id, card_number, card_type, expiry_date, cardholder_name) VALUES 
                (1, '4532XXXXXXXX1234', 'Visa', '2028-05-01', 'Arben Hoxha')''')
            
            # Cash Payment
            cursor.execute('''INSERT INTO cash_payment (payment_id, change_amount) VALUES (2, 200.00)''')
            
            conn.commit()
            print("Sample data loaded successfully!")
        
        conn.close()
        print("Database initialized successfully!")
    except Exception as e:
        print(f"Database initialization error: {e}")

# ============================================
# RUN THE APP
# ============================================
if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=False, host='0.0.0.0', port=port)
