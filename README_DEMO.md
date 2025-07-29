# ZK-RBAC Demo System

## 🎯 Demo Zero-Knowledge Proof với Merkle Tree

Project demo các chức năng cơ bản:
- **Thêm leaves** vào Merkle tree (đăng ký nhân viên)
- **Xóa leaves** khỏi Merkle tree (xóa nhân viên) 
- **Đăng nhập** bằng ZK proof mà không tiết lộ mật khẩu

## ✨ Chức năng Demo

- **➕ Thêm**: Đăng ký nhân viên mới vào cây Merkle
- **➖ Xóa**: Xóa nhân viên và cập nhật cây Merkle
- **🔐 Đăng nhập**: Xác thực bằng ZK proof
- **👥 Phân nhóm**: 4 phòng ban riêng biệt (IT, HR, Sales, Finance)

## 🛠️ Công nghệ

- **ZK-SNARKs**: Tạo và verify proof
- **Merkle Trees**: Lưu trữ dữ liệu nhân viên
- **Poseidon Hash**: Hash function cho ZK circuits
- **Python Flask**: Backend API
- **JavaScript**: Frontend logic

## 🚀 Chạy Demo

### 1. Cài đặt
```bash
git clone <repository-url>
cd zk_rbac_proof
pip install flask
npm install circomlib snarkjs
```

### 2. Khởi động
```bash
cd web/prover
python server.py
```

### 3. Demo URLs
- **Đăng nhập**: http://localhost:5001/
- **Đăng ký (Thêm)**: http://localhost:5001/register  
- **Xóa nhân viên**: http://localhost:5001/delete

## 💡 Demo Workflow

### 1. Thêm Leaves (Đăng ký)
1. Vào `/register`
2. Chọn phòng ban
3. Nhập email: `name@phongban.company.com`
4. Nhập mật khẩu
5. ✅ **Leaf mới được thêm vào Merkle tree**

### 2. Đăng nhập ZK Proof
1. Vào `/`
2. Nhập thông tin đã đăng ký
3. ✅ **Tạo ZK proof để chứng minh biết mật khẩu mà không tiết lộ**
4. Chuyển đến dashboard

### 3. Xóa Leaves 
1. Vào `/delete`
2. Chọn phòng ban
3. Chọn nhân viên cần xóa
4. ✅ **Leaves bị xóa và cây Merkle được cập nhật**

## 📁 Dữ liệu Demo

### Merkle Tree Structure
```
roots/{role}.json - Chứa cây Merkle của mỗi phòng ban
├── root: hash gốc của cây
├── leaves: [leaf1, leaf2, "0", "0"] 
└── emails: [email_hash1, email_hash2]
```

### Raw Data
```
employees/employees_{role}.json - Dữ liệu thô để demo
[
  {"email": "user@it.company.com", "secret": "password123"}
]
```

## 🔍 Demo Features

### ✅ Thêm Leaves
- Hash email + secret thành leaf
- Tìm slot trống (giá trị "0")  
- Thêm leaf vào vị trí trống
- Cập nhật root hash

### ✅ Xóa Leaves
- Chọn multiple leaves để xóa
- Set leaves về "0"
- Dịch chuyển leaves còn lại lên đầu
- Cập nhật root hash

### ✅ ZK Login
- Client tạo Merkle proof
- Tạo ZK-SNARK proof 
- Server verify mà không biết mật khẩu
- Redirect theo phòng ban

## 🎮 Demo Tips

- **Tối đa 8 nhân viên/phòng ban**
- **Email format**: `name@{it|hr|sales|finance}.company.com`
- **Mỗi phòng ban có cây Merkle riêng**
- **ZK proof mất 2-5 giây để tạo**

## 🔐 Security Features

- **Zero-Knowledge**: Server không bao giờ thấy mật khẩu
- **Merkle Proof**: Chứng minh membership mà không tiết lộ dữ liệu khác
- **Role Separation**: Mỗi phòng ban có cây riêng biệt
- **Cryptographic Hash**: Sử dụng Poseidon hash cho ZK circuits

## 📊 Demo Performance

- **Proof Generation**: 2-5 giây
- **Proof Verification**: <100ms
- **Tree Update**: <50ms
- **Max Employees**: 8 per department

---

**🎯 Zero-Knowledge Demo với Merkle Tree Operations**
