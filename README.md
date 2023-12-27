Hướng dẫn sử dụng:
Ứng dụng cho phép nhận diện biển số xe qua cả webcam và qua file ảnh có sẵn trong máy tính.
Khi nhấn nút "Nhận diện" thì sẽ nhận diện biển số xe qua webcam, và khi nhấn nút"Nhận diện từ ảnh" thì sẽ nhận diện biển số xe qua file ảnh từ trong máy tính.
Nếu nhận diện được biển số xe thì hiển thị lên giao diện biển số xe đã nhận diện được. Nếu không nhận diện được biển số xe thì sẽ hiện lên thông báo.
Nếu có biển số xe thì khi nhấn nút "Lưu" thì xe lưu biển số xe và ngày, giờ lưu vào trong cơ sở dữ liệu. Nếu không có biển số xe thì khi ấn nút "Lưu" sẽ hiện lên thông báo.
Biển số xe sẽ được lưu với ý nghĩa là xe vào bãi đỗ và biến "Số xe đã vào" sẽ tăng lên 1 và biến số "Tổng số xe còn lại" sẽ tăng lên 1.
Ấn nút "Xem cơ sở dữ liệu" để mở tệp dư liệu để quan sát.
Khi ấn nút "Lưu file" thì dữ liệu ở trong cơ sở dữ liệu sẽ được xuất ra trong một file text.
Khi ấn nút "Xe ra về" thì sẽ nhận diện lại biển số xe qua webcam hoặc qua file ảnh. Nếu biển số xe nhận diện được có tồn tại trong cơ sở dữ liệu, thì sẽ xóa nó đi và hiện thống báo "Đã ra khỏi bãi đỗ".
Đồng thời biến số "Số xe đã ra" sẽ tăng lên 1 và biến số "Tổng số xe còn lại" sẽ giảm đi 1.
Biến số "Tổng số tiền đã thu" sẽ tăng lên 3000 đồng sau mỗi lượt xe ra khỏi bãi thành công.
Khi ấn nút "Vẽ biểu đồ" sẽ thực hiện vẽ biểu đồ cột dựa trên các thông số "Số xe vào", "Số xe ra" và "Tổng số xe còn lại".
Khi nhấn nút "Xóa cơ sở dữ liệu" thì sẽ thực hiện xóa hết các dữ liệu ở trong cơ sở dữ liệu.

Link github ban đầu: 
https://github.com/process-python/OpenCV-Python/blob/main/Code_MNM.py
