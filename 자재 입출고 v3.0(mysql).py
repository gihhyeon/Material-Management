import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime
import mysql.connector
import os
import config # config.py 파일 임포트
import time


# Function to log data into MySQL database
def log_data():
    if not worker_entry.get() or not solder_lot_entry.get() or not material_entry.get() or not pn_entry.get() or not ln_entry.get() or not qty_entry.get():
        messagebox.showerror("Error", "All fields must be filled!")
        return

    try:
        
         # Validate P/N and L/N length
        if len(pn_entry.get()) != 29:
            messagebox.showerror("Error", "P/N must be exactly 29 characters!")
            return
        if len(ln_entry.get()) != 8:
            messagebox.showerror("Error", "L/N must be exactly 8 characters!")
            return
        
         # MySQL 연결 시작 시간 기록
        start_time = time.time()

         # Use values from the config.py file for MySQL connection
        db_connection = mysql.connector.connect(
            host=config.MYSQL_HOST,  # MySQL 서버 주소
            user=config.MYSQL_USER,  # MySQL 사용자명
            password=config.MYSQL_PASSWORD,  # MySQL 비밀번호
            database=config.MYSQL_DATABASE  # 사용할 데이터베이스 이름
        )
        cursor = db_connection.cursor()

        # Get data from input fields and input time
        worker = worker_entry.get()
        solder_lot = solder_lot_entry.get()
        material = material_entry.get()
        pn = pn_entry.get()
        ln = ln_entry.get()
        qty = int(qty_entry.get())  # Convert QTY to integer
        input_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Insert data into MySQL table
        insert_query = """
        INSERT INTO test (작업자, 입출고, 자재종류, pn, ln, 수량, 입력시간)
        VALUES (%s, %s, %s, %s, %s, %s, NOW())
        """
        cursor.execute(insert_query, (worker, solder_lot, material, pn, ln, qty))
        db_connection.commit()  # Commit the transaction

        # 데이터 저장 완료 시간 기록
        end_time = time.time()

        # 데이터 저장 소요 시간 계산
        elapsed_time = end_time - start_time

        # Update the log box with the new entry
        log_box.insert(tk.END, f"작업자: {worker}\n입/출고: {solder_lot}\n자재 종류: {material}\nP/N: {pn}\nL/N: {ln}\nQTY: {qty}\n입력 시간: {input_time}\n\n")
        log_box.yview(tk.END)  # Scroll to the end of the log box

        messagebox.showinfo("Success", f"Data logged successfully! (소요 시간: {elapsed_time:.4f}초)")

        messagebox.showinfo("Success", "Data logged successfully!")

        # Clear inputs for P/N, L/N, QTY after successful log
        pn_entry.delete(0, tk.END)
        ln_entry.delete(0, tk.END)
        qty_entry.delete(0, tk.END)

        # Focus the P/N entry box for the next input
        pn_entry.focus()

        # Close the cursor and connection
        cursor.close()
        db_connection.close()
        
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"An error occurred: {err}")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

# Function to clear the input of a specific entry
def clear_entry(entry):
    entry.delete(0, tk.END)

# Function to move focus to the next entry field
def focus_next(event):
    event.widget.tk_focusNext().focus()
    return "break"  # Prevent the default behavior of the Enter key

# GUI setup
root = tk.Tk()
root.title("자재 입출고")
root.geometry("1050x600")  # Increase window size to accommodate larger elements

# Worker entry
tk.Label(root, font=("Helvetica", 20), text="작업자:").place(x=50, y=30)
worker_entry = tk.Entry(root, width=15, font=("Helvetica",20))
worker_entry.place(x=200, y=30)
worker_entry.bind("<Return>", focus_next)  # Bind Enter key

# Solder lot No entry
tk.Label(root, font=("Helvetica", 20), text="입/출고:").place(x=50, y=90)
solder_lot_entry = tk.Entry(root, width=15, font=("Helvetica", 20))
solder_lot_entry.place(x=200, y=95)
solder_lot_entry.bind("<Return>", focus_next)  # Bind Enter key

# Material entry
tk.Label(root, font=("Helvetica", 20), text="자재:").place(x=50, y=140)
material_entry = tk.Entry(root, width=15, font=("Helvetica", 20))
material_entry.place(x=200, y=140)
material_entry.bind("<Return>", focus_next)  # Bind Enter key

# New entries: P/N, L/N, QTY, positioned below "No file selected" label
tk.Label(root, font=("Helvetica", 20), text="P/N:").place(x=120, y=350)
pn_entry = tk.Entry(root, width=15, font=("Helvetica", 20))
pn_entry.place(x=200, y=350)
pn_entry.bind("<Return>", focus_next)  # Bind Enter key

tk.Label(root, font=("Helvetica", 20), text="L/N:").place(x=120, y=400)
ln_entry = tk.Entry(root, width=15, font=("Helvetica", 20))
ln_entry.place(x=200, y=400)
ln_entry.bind("<Return>", focus_next)  # Bind Enter key

tk.Label(root, font=("Helvetica", 20), text="QTY:").place(x=120, y=450)
qty_entry = tk.Entry(root, width=15, font=("Helvetica", 20))
qty_entry.place(x=200, y=450)
qty_entry.bind("<Return>", focus_next)  # Bind Enter key

# Enter button to log data with blue background and white font
enter_button = tk.Button(root, text="Enter", font=("Helvetica", 15), width=10, command=log_data, bg="blue", fg="white")
enter_button.place(x=475, y=520)

# Delete buttons for each entry field
tk.Button(root, text="삭제", font=("Helvetica", 15), command=lambda: clear_entry(worker_entry)).place(x=440, y=30)
tk.Button(root, text="삭제", font=("Helvetica", 15), command=lambda: clear_entry(solder_lot_entry)).place(x=440, y=90)
tk.Button(root, text="삭제", font=("Helvetica", 15), command=lambda: clear_entry(material_entry)).place(x=440, y=140)
tk.Button(root, text="삭제", font=("Helvetica", 15), command=lambda: clear_entry(pn_entry)).place(x=440, y=350)
tk.Button(root, text="삭제", font=("Helvetica", 15), command=lambda: clear_entry(ln_entry)).place(x=440, y=400)
tk.Button(root, text="삭제", font=("Helvetica", 15), command=lambda: clear_entry(qty_entry)).place(x=440, y=450)

# Log box to display logged entries with a specific font size
log_box = tk.Text(root, height=27, width=60, font=("Helvetica", 11))
log_box.place(x=550, y=30)

root.mainloop()
