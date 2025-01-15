import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import mysql.connector
import traceback

# MySQL 설정 정보를 코드 내부에 포함
MYSQL_CONFIG = {
    "MYSQL_HOST": "localhost",
    "MYSQL_USER": "root",
    "MYSQL_PASSWORD": "password",
    "MYSQL_DATABASE": "db"
}

# Function to update the rank field based on PCB barcode input
def update_rank(event=None):
    pcb_barcode = pn_entry.get()
    if len(pcb_barcode) >= 18:
        rank_value = pcb_barcode[12:18]  # 13~18번째 문자 추출
        rank_label_var.set(rank_value)
    else:
        rank_label_var.set("")

# Function to log data into MySQL database
def log_data():
    if not worker_entry.get() or not solder_lot_entry.get() or not material_entry.get() or not pn_entry.get() or not ln_entry.get() or not qty_entry.get():
        messagebox.showerror("Error", "모든 필드가 채워져야 합니다.")
        return

    try:

        # Validate P/N and L/N length
        if len(pn_entry.get()) != 29:
            messagebox.showerror("Error", "PCB 바코드는 29자리를 입력해야 됩니다.")
            return
        if len(ln_entry.get()) != 8:
            messagebox.showerror("Error", "제품 바코드는 8자리를 입력해야 됩니다.")
            return
        
        # Validate date format (YYYY-MM-DD)
        try:
            input_date = datetime.strptime(date_entry.get(), "%Y-%m-%d").date()
        except ValueError:
            messagebox.showerror("Error", "날짜는 YYYY-MM-DD 형식을 사용해주세요.")
            return
        
        # 데이터 확인 팝업창 생성
        worker = worker_entry.get()
        pn = pn_entry.get()
        ln = ln_entry.get()
        rank = rank_label_var.get()  # Get rank value
        qty = int(qty_entry.get())  # Convert QTY to integer

        confirm_message = (
            f"다음 데이터를 확인해주세요.\n\n"
            f"작업자: {worker}\n"
            f"PCB 바코드: {pn}\n"
            f"제품 바코드: {ln}\n"
            f"랭크: {rank}\n"
            f"개수: {qty}\n\n"
            "입력 내용이 맞습니까?"
        )

        # "예"와 "아니오" 버튼 추가
        confirm = messagebox.askyesno("확인", confirm_message)
        if not confirm:  # 사용자가 "아니오"를 누른 경우 필드 초기화
            worker_entry.delete(0, tk.END)
            pn_entry.delete(0, tk.END)
            ln_entry.delete(0, tk.END)
            rank_label_var.set("")  # 랭크 초기화
            qty_entry.delete(0, tk.END)
            return

        # Use values from the MYSQL_CONFIG dictionary for MySQL connection
        db_connection = mysql.connector.connect(
            host=MYSQL_CONFIG["MYSQL_HOST"],
            user=MYSQL_CONFIG["MYSQL_USER"],
            password=MYSQL_CONFIG["MYSQL_PASSWORD"],
            database=MYSQL_CONFIG["MYSQL_DATABASE"]
        )
        cursor = db_connection.cursor()

        # Get additional inputs
        solder_lot = solder_lot_entry.get()
        material = material_entry.get()
        input_date = date_entry.get()  # Get the date input as string
        input_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Insert data into MySQL table
        insert_query = """
        INSERT INTO store_db (입출고, 자재종류, 날짜, 작업자, pn, ln, 랭크, 수량, 입력시간)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
        """
        cursor.execute(insert_query, (solder_lot, material, input_date, worker, pn, ln, rank, qty))
        db_connection.commit()  # Commit the transaction

        # Update the log box with the new entry
        log_box.insert(tk.END, f"입/출고: {solder_lot}\n자재 종류: {material}\n날짜: {input_date}\n작업자: {worker}\nPCB 바코드: {pn}\n제품 바코드: {ln}\n개수: {qty}\n입력 시간: {input_time}\n\n")
        log_box.yview(tk.END)  # Scroll to the end of the log box

        messagebox.showinfo("Success", "데이터 입력 성공")

        # Clear inputs for P/N, L/N, QTY after successful log
        worker_entry.delete(0, tk.END)
        pn_entry.delete(0, tk.END)
        ln_entry.delete(0, tk.END)
        rank_label_var.set("")
        qty_entry.delete(0, tk.END)

        # Focus the P/N entry box for the next input
        worker_entry.focus()

        # Close the cursor and connection
        cursor.close()
        db_connection.close()
        
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"An error occurred: {err}")
        print(f"Error: {e}")
        raise
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
        print("An error occurred:", e)
        print(traceback.format_exc())

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

# Solder_lot entry
tk.Label(root, font=("Helvetica", 20), text="입/출고:").place(x=85, y=30)
solder_lot_entry = tk.Entry(root, width=15, font=("Helvetica",20))
solder_lot_entry.place(x=200, y=30)
solder_lot_entry.bind("<Return>", focus_next)  # Bind Enter key

# Material entry
tk.Label(root, font=("Helvetica", 20), text="자재 종류:").place(x=59, y=90)
material_entry = tk.Entry(root, width=15, font=("Helvetica", 20))
material_entry.place(x=200, y=95)
material_entry.bind("<Return>", focus_next)  # Bind Enter key

# Input_date entry
tk.Label(root, font=("Helvetica", 20), text="날짜:").place(x=120, y=140)
date_entry = tk.Entry(root, width=15, font=("Helvetica", 20))
date_entry.place(x=200, y=140)
date_entry.bind("<Return>", focus_next)  # Bind Enter key

# Worker entry
tk.Label(root, font=("Helvetica", 20), text="작업자:").place(x=93, y=250)
worker_entry = tk.Entry(root, width=15, font=("Helvetica", 20))
worker_entry.place(x=200, y=250)
worker_entry.bind("<Return>", focus_next)  # Bind Enter key

tk.Label(root, font=("Helvetica", 20), text="PCB 바코드:").place(x=29, y=300)
pn_entry = tk.Entry(root, width=15, font=("Helvetica", 20))
pn_entry.place(x=200, y=300)
pn_entry.bind("<KeyRelease>", update_rank)  # 키 릴리스 이벤트 바인딩
pn_entry.bind("<Return>", focus_next)  # Bind Enter key

tk.Label(root, font=("Helvetica", 20), text="제품 바코드:").place(x=29, y=350)
ln_entry = tk.Entry(root, width=15, font=("Helvetica", 20))
ln_entry.place(x=200, y=350)
ln_entry.bind("<Return>", focus_next)  # Bind Enter key

# 랭크 field
tk.Label(root, font=("Helvetica", 20), text="랭크:").place(x=118, y=400)
rank_label_var = tk.StringVar()
rank_label = tk.Label(root, width=15, font=("Helvetica", 20), textvariable=rank_label_var, relief="sunken")
rank_label.place(x=200, y=400)

tk.Label(root, font=("Helvetica", 20), text="개수:").place(x=117, y=450)
qty_entry = tk.Entry(root, width=15, font=("Helvetica", 20))
qty_entry.place(x=200, y=450)
qty_entry.bind("<Return>", focus_next)  # Bind Enter key

# Enter button to log data with blue background and white font
enter_button = tk.Button(root, text="Enter", font=("Helvetica", 15), width=10, command=log_data, bg="blue", fg="white")
enter_button.place(x=475, y=520)

# Delete buttons for each entry field
tk.Button(root, text="삭제", font=("Helvetica", 15), command=lambda: clear_entry(solder_lot_entry)).place(x=440, y=30)
tk.Button(root, text="삭제", font=("Helvetica", 15), command=lambda: clear_entry(material_entry)).place(x=440, y=90)
tk.Button(root, text="삭제", font=("Helvetica", 15), command=lambda: clear_entry(date_entry)).place(x=440, y=140)
tk.Button(root, text="삭제", font=("Helvetica", 15), command=lambda: clear_entry(worker_entry)).place(x=440, y=250)
tk.Button(root, text="삭제", font=("Helvetica", 15), command=lambda: clear_entry(pn_entry)).place(x=440, y=300)
tk.Button(root, text="삭제", font=("Helvetica", 15), command=lambda: clear_entry(ln_entry)).place(x=440, y=350)
tk.Button(root, text="삭제", font=("Helvetica", 15), command=lambda: clear_entry(qty_entry)).place(x=440, y=450)

# Log box to display logged entries with a specific font size
log_box = tk.Text(root, height=27, width=60, font=("Helvetica", 11))
log_box.place(x=550, y=30)

root.mainloop()