from flask import Flask, render_template, request, redirect, url_for
import sqlite3

import sqlite3 as sql

conn = sqlite3.connect('database.db')
conn.execute('''CREATE TABLE IF NOT EXISTS users (
                    name TEXT,
                    email TEXT,
                    password TEXT
                )''')
conn.execute('''CREATE TABLE IF NOT EXISTS questions (
             name TEXT,
             question TEXT,
             uanswer TEXT    
        )
             ''')
conn.close()