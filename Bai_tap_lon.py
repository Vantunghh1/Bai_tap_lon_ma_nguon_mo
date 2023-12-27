import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk
import cv2
import easyocr
import sqlite3
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class LicensePlateRecognitionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Ứng dụng nhận diện biển số xe")

        self.dem_xe_vao = 0
        self.dem_xe_ra = 0
        self.so_xe_con_lai = 0

        # Biến lưu ảnh từ webcam
        self.webcam = cv2.VideoCapture(0)

        # Biến lưu ảnh chụp được
        self.captured_image = None

        # Biến lưu trạng thái của hệ thống (True nếu xe ra về, False nếu xe vào)
        self.system_status = False


        # Tạo và đặt vị trí các thành phần trên giao diện
        self.label_image = tk.Label(root)
        self.label_image.pack(pady=10)

        self.btn_nhan_dien = tk.Button(root, text="Nhận diện", command=self.capture_and_recognize_license_plate)
        self.btn_nhan_dien.pack(pady=5)

        self.label_hien_thi = tk.Label(root, text="Biển số xe: ")
        self.label_hien_thi.pack(pady=10)

        # Tạo frame để đặt nút "Xem Cơ sở dữ liệu" và "Xóa Tất Cả Dữ Liệu" trên cùng một dòng
        self.frame_buttons = tk.Frame(root)
        self.frame_buttons.pack()

        # Đặt nút "Lưu" trong frame này
        self.btn_save = tk.Button(self.frame_buttons, text="Lưu", command=self.save_to_database, width=14, height=1)
        self.btn_save.grid(row=0, column=1, padx=5)

        # Nút để vẽ biểu đồ
        self.btn_draw_chart = tk.Button(self.frame_buttons, text="Vẽ Biểu Đồ", command=self.draw_chart, width=14, height=1)
        self.btn_draw_chart.grid(row=0, column=2, padx=5)

        # Đặt nút "Xem Cơ sở dữ liệu" trong frame này
        self.btn_view_database = tk.Button(self.frame_buttons, text="Xem Cơ sở dữ liệu", command=self.view_database, width=14, height=1)
        self.btn_view_database.grid(row=1, column=1, padx=5)

        # Đặt nút "Xóa Tất Cả Dữ Liệu" trong frame này
        self.btn_delete_all = tk.Button(self.frame_buttons, text="Xóa Tất Cả Dữ Liệu", command=self.delete_all_data, width=14, height=1)
        self.btn_delete_all.grid(row=1, column=2, padx=5)

        self.btn_xoa_xe_ra = tk.Button(self.frame_buttons, text="Xe Ra Về", command=self.process_vehicle_exit, width=14, height=1)
        self.btn_xoa_xe_ra.grid(row=2, column=1, padx=5)

        # Đặt nút "Lưu Dữ Liệu Xuống File" và điều chỉnh kích thước
        self.btn_save_to_file = tk.Button(self.frame_buttons, text="Lưu File",
                                          command=self.save_to_text_file, width=14, height=1)
        self.btn_save_to_file.grid(row=2, column=2, padx=5)

        # Nút để chọn và nhận diện biển số từ ảnh
        self.btn_recognize_image = tk.Button(self.frame_buttons, text="Nhận diện từ ảnh",
                                             command=self.nhan_dien_qua_anh)
        self.btn_recognize_image.grid(row=3, column=2, padx=5)

        # Tổng số tiền đã thu
        self.tong_tien_thu = 0

        # Tạo hộp đóng để chứa nhãn số xe vào, số xe ra, số xe còn lại, và tổng số tiền đã thu
        self.frame_labels = tk.Frame(root)
        self.frame_labels.pack()

        # Nhãn số xe vào
        self.label_so_xe_vao = tk.Label(self.frame_labels, text="Số xe đã vào: 0")
        self.label_so_xe_vao.grid(row=0, column=0, padx=5)

        # Nhãn số xe ra
        self.label_so_xe_ra = tk.Label(self.frame_labels, text="Số xe đã ra: 0")
        self.label_so_xe_ra.grid(row=0, column=1, padx=5)

        # Nhãn số xe còn lại
        self.label_so_xe_con_lai = tk.Label(self.frame_labels, text="Tổng số xe còn lại: 0")
        self.label_so_xe_con_lai.grid(row=0, column=2, padx=5)

        # Nhãn tổng số tiền đã thu
        self.label_tong_tien = tk.Label(self.frame_labels, text="Tổng số tiền đã thu: 0 đồng")
        self.label_tong_tien.grid(row=0, column=3, padx=5)

        # Khởi tạo mô hình nhận diện biển số xe
        self.reader = easyocr.Reader(['en'])

        # Kết nối đến cơ sở dữ liệu SQLite
        self.conn = sqlite3.connect('license_plate_database.db')
        self.create_table()

        # Bắt đầu hiển thị hình ảnh từ webcam
        self.update_webcam()
        # Biến để lưu biển số từ webcam
        self.detected_license_plate = ""

        # Biến để lưu biển số từ ảnh
        self.detected_license_plate_from_image = ""
        # cờ
        self.flag = 0

    def create_table(self):
        # Tạo bảng trong cơ sở dữ liệu nếu chưa tồn tại
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS license_plates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    plate_number TEXT,
                    capture_time TEXT
                )
            ''')

    def nhan_dien_qua_anh(self):
        # Mở hộp thoại để chọn tệp ảnh
        file_path = filedialog.askopenfilename(title="Chọn ảnh",
                                               filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")])

        if file_path:
            # Đọc ảnh từ đường dẫn đã chọn
            image = cv2.imread(file_path)

            # Hiển thị ảnh trên giao diện
            self.display_image(image)

            # Chuyển đổi ảnh sang đen trắng
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # Thực hiện OCR trên ảnh đen trắng để nhận diện biển số xe
            results = self.reader.readtext(gray)

            # Hiển thị ảnh trên giao diện
            self.display_image(image)

            if results:
                # Kết hợp kết quả nhận diện trên hai hàng chữ
                license_plate_number = ' '.join([result[-2] for result in results])

                # Hiển thị biển số trên giao diện
                self.label_hien_thi.config(text=f"Biển số xe: {license_plate_number}")
                # Lưu biển số từ ảnh vào biến
                self.detected_license_plate_from_image = license_plate_number
                self.flag = 1

            else:
                self.label_hien_thi.config(text="Không nhận diện được biển số xe")

    def display_image(self, image):
        # Hiển thị ảnh từ webcam
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(image)
        self.tk_image = ImageTk.PhotoImage(image)
        self.label_image.config(image=self.tk_image)
    def save_to_text_file(self):
        # Kết nối đến cơ sở dữ liệu SQLite
        conn = sqlite3.connect('license_plate_database.db')

        # Mở tệp văn bản để ghi dữ liệu
        with open("database_to_text.txt", "w", encoding="utf-8") as file:
            # Truy vấn cơ sở dữ liệu và ghi dữ liệu vào tệp
            with conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM license_plates")
                rows = cursor.fetchall()
                for row in rows:
                    # Chuyển định dạng thời gian sang str trước khi ghi vào tệp
                    formatted_time = datetime.strptime(row[2], '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
                    file.write(f"ID: {row[0]}, Biển số xe: {row[1]}, Thời gian: {formatted_time}\n")

       # print("Dữ liệu đã được lưu vào file: database_to_text.txt")
        self.label_hien_thi.config(text="Dữ liệu đã được lưu vào file: database_to_text.txt")
    def save_to_database(self):
        if not self.flag and not self.detected_license_plate:
            # Nếu không có biển số từ ảnh và không có biển số từ webcam
            self.label_hien_thi.config(text="Vui lòng nhận diện biển số xe trước khi lưu")
            return

        if self.flag:
            # Nếu biển số từ ảnh đã được nhận diện, sử dụng nó để lưu vào cơ sở dữ liệu
            plate_to_save = self.detected_license_plate_from_image
        elif self.detected_license_plate:
            # Nếu không, sử dụng biển số từ webcam để lưu vào cơ sở dữ liệu
            plate_to_save = self.detected_license_plate

            # Reset giá trị AUTOINCREMENT
        self.reset_autoincrement()

        # Lưu vào cơ sở dữ liệu
        self.save_plate_to_database(plate_to_save)

        # Cập nhật số xe đã vào và tổng số xe còn lại
        self.dem_xe_vao += 1
        self.so_xe_con_lai += 1

        # Hiển thị thông tin trên giao diện
        self.label_so_xe_vao.config(text=f"Số xe đã vào: {self.dem_xe_vao}")
        self.label_so_xe_con_lai.config(text=f"Tổng số xe còn lại: {self.so_xe_con_lai}")

        # Hiển thị thông báo lên giao diện
        self.label_hien_thi.config(text=f"Biển số xe: {plate_to_save} đã được lưu")

        # Reset biến detected_license_plate và detected_license_plate_from_image sau khi lưu
        self.detected_license_plate = ""
        self.detected_license_plate_from_image = ""
        self.flag = 0

    def save_plate_to_database(self, plate_number):
        # Lưu biển số và thời gian vào cơ sở dữ liệu
        capture_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute('INSERT INTO license_plates (plate_number, capture_time) VALUES (?, ?)', (plate_number, capture_time))

    def delete_all_data(self):
        # Xóa tất cả dữ liệu từ cơ sở dữ liệu
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute('DELETE FROM license_plates')

        # Reset giá trị AUTOINCREMENT
        self.reset_autoincrement()
        self.dem_xe_vao = 0
        self.dem_xe_ra = 0
        self.so_xe_con_lai = 0
        self.tong_tien_thu = 0

        # Hiển thị thông tin trên giao diện
        self.label_so_xe_vao.config(text=f"Số xe đã vào: {self.dem_xe_vao}")
        self.label_so_xe_ra.config(text=f"Số xe đã ra: {self.dem_xe_ra}")
        self.label_so_xe_con_lai.config(text=f"Tổng số xe còn lại: {self.so_xe_con_lai}")
        self.label_tong_tien.config(text="Tổng số tiền đã thu: 0 đồng")
        # Hiển thị thông báo lên giao diện
        self.label_hien_thi.config(text="Đã xóa tất cả dữ liệu trong cơ sở dữ liệu")
    def capture_and_recognize_license_plate(self):
        if self.captured_image is not None:
            # Chuyển đổi ảnh sang đen trắng
            gray = cv2.cvtColor(self.captured_image, cv2.COLOR_BGR2GRAY)

            # Thực hiện OCR trên ảnh đen trắng để nhận diện biển số xe
            results = self.reader.readtext(gray)

            if results:
                # Kết hợp kết quả nhận diện trên hai hàng chữ
                license_plate_number = ' '.join([result[-2] for result in results])
                # Lưu biển số vào biến
                self.detected_license_plate = license_plate_number
                # Hiển thị biển số trên giao diện
                self.label_hien_thi.config(text=f"Biển số xe: {license_plate_number}")

            else:
                self.label_hien_thi.config(text="Không nhận diện được biển số xe")
        else:
            self.label_hien_thi.config(text="Vui lòng nhận diện biển số xe trước khi lưu")

    def update_webcam(self):
        # Đọc frame từ webcam
        ret, frame = self.webcam.read()

        # Hiển thị frame từ webcam
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(frame)
        image = ImageTk.PhotoImage(image)
        self.label_image.config(image=image)
        self.label_image.image = image

        # Lặp lại hàm update_webcam sau một khoảng thời gian nhất định (ở đây là 10ms)
        self.root.after(10, self.update_webcam)

        # Lưu ảnh chụp được
        self.captured_image = frame

    def process_vehicle_exit(self):
        if self.flag:
            # Nếu biển số từ ảnh đã được nhận diện, sử dụng nó để xử lý xe ra về
            plate_to_process = self.detected_license_plate_from_image
        elif self.captured_image is not None:
            # Nếu không, sử dụng biển số từ webcam để xử lý xe ra về
            # Chuyển đổi ảnh sang đen trắng
            gray = cv2.cvtColor(self.captured_image, cv2.COLOR_BGR2GRAY)

            # Thực hiện OCR trên ảnh đen trắng để nhận diện biển số xe
            results = self.reader.readtext(gray)

            if results:
                # Kết hợp kết quả nhận diện trên hai hàng chữ
                plate_to_process = ' '.join([result[-2] for result in results])
            else:
                self.label_hien_thi.config(text="Không nhận diện được biển số xe")
                return
        else:
            self.label_hien_thi.config(text="Vui lòng nhận diện biển số xe trước khi xử lý xe ra về")
            return

            # Kiểm tra xem biển số có trong cơ sở dữ liệu không
        if self.check_plate_in_database(plate_to_process):
            # Nếu có, hiển thị thông báo
            self.label_hien_thi.config(text=f"Biển số xe: {plate_to_process} đã ra khỏi bãi đỗ")
            # Sau đó, xóa biển số từ cơ sở dữ liệu
            self.remove_plate(plate_to_process)
            # Reset giá trị AUTOINCREMENT
            self.reset_autoincrement()
            # Cập nhật số xe đã ra và tổng số xe còn lại
            self.dem_xe_ra += 1
            self.so_xe_con_lai -= 1

            # Hiển thị thông tin trên giao diện
            self.label_so_xe_ra.config(text=f"Số xe đã ra: {self.dem_xe_ra}")
            self.label_so_xe_con_lai.config(text=f"Tổng số xe còn lại: {self.so_xe_con_lai}")

            # Xác định giá tiền cho mỗi xe ra
            gia_tien = 3000

            # Cập nhật tổng số tiền và hiển thị trên nhãn
            self.tong_tien_thu += gia_tien
            self.label_tong_tien.config(text=f"Tổng số tiền đã thu: {self.tong_tien_thu} đồng")
        else:
            self.label_hien_thi.config(text=f"Biển số xe: {plate_to_process} không có trong cơ sở dữ liệu")

            # Reset biến detected_license_plate và detected_license_plate_from_image sau khi xử lý xe ra về
        self.detected_license_plate = ""
        self.detected_license_plate_from_image = ""
        self.flag = 0

    def check_plate_in_database(self, plate_number):
        # Kiểm tra xem biển số có trong cơ sở dữ liệu không
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM license_plates WHERE plate_number = ?', (plate_number,))
            return cursor.fetchone() is not None

    def reset_autoincrement(self):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute('DELETE FROM sqlite_sequence WHERE name="license_plates"')

    def remove_plate(self, plate_number):
        # Xóa biển số từ cơ sở dữ liệu
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute('DELETE FROM license_plates WHERE plate_number = ?', (plate_number,))




    def view_database(self):
        # Tạo cửa sổ mới để hiển thị cơ sở dữ liệu
        database_window = tk.Toplevel(self.root)
        database_window.title("Cơ sở dữ liệu biển số xe")

        # Tạo cây để hiển thị dữ liệu từ cơ sở dữ liệu
        tree = ttk.Treeview(database_window)
        tree["columns"] = ("ID", "Biển số xe", "Thời gian")

        # Đặt độ rộng cho từng cột
        tree.column("#0", width=0, stretch=tk.NO)
        tree.column("ID", anchor=tk.CENTER, width=50)
        tree.column("Biển số xe", anchor=tk.CENTER, width=150)
        tree.column("Thời gian", anchor=tk.CENTER, width=150)

        # Đặt tiêu đề cho từng cột
        tree.heading("#0", text="", anchor=tk.CENTER)
        tree.heading("ID", text="ID", anchor=tk.CENTER)
        tree.heading("Biển số xe", text="Biển số xe", anchor=tk.CENTER)
        tree.heading("Thời gian", text="Thời gian", anchor=tk.CENTER)

        # Truy vấn cơ sở dữ liệu và hiển thị dữ liệu trong cây
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM license_plates")
            rows = cursor.fetchall()
            for row in rows:
                tree.insert("", tk.END, values=row)

        tree.pack(expand=tk.YES, fill=tk.BOTH)

    def draw_chart(self):
        # Tạo biểu đồ
        fig, ax = plt.subplots()
        labels = ['Số xe vào', 'Số xe ra', 'Tổng số xe còn lại']
        data = [self.dem_xe_vao, self.dem_xe_ra, self.so_xe_con_lai]

        # Vẽ biểu đồ cột
        ax.bar(labels, data)

        # Hiển thị giá trị trên cột
        for i, v in enumerate(data):
            ax.text(i, v + 0.1, str(v), color='black', ha='center')

        # Thêm tiêu đề và nhãn cho biểu đồ
        ax.set_title('Biểu Đồ Số Xe')
        ax.set_ylabel('Số lượng xe')

        # Hiển thị biểu đồ trong giao diện
        chart_window = tk.Toplevel(self.root)
        chart_window.title("Biểu Đồ Số Xe")
        canvas = FigureCanvasTkAgg(fig, master=chart_window)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

if __name__ == "__main__":
    root = tk.Tk()
    app = LicensePlateRecognitionApp(root)
    root.mainloop()
