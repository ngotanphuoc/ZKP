# ZK-RBAC: Zero-Knowledge Role-Based Access Control

## 🎯 Tổng quan

Hệ thống xác thực dựa trên Zero-Knowledge Proof và Merkle Tree, cho phép người dùng chứng minh quyền truy cập mà không tiết lộ thông tin nhạy cảm.

## 🔑 Tính năng chính

- **🔐 ZK Authentication**: Đăng nhập mà không tiết lộ mật khẩu
- **🌳 Merkle Tree Management**: Quản lý danh sách nhân viên theo phòng ban
- **👥 Role-Based Access**: Phân quyền theo 4 phòng ban (IT, HR, Sales, Finance)
- **🛡️ Cryptographic Security**: Sử dụng ZK-SNARKs và Poseidon hash

## 🏗️ Kiến trúc hệ thống

### Frontend (Browser)
- **Proof Generation**: Tạo ZK proof từ email + secret
- **Merkle Path**: Tính toán đường đi trong cây Merkle
- **Privacy**: Secret không bao giờ rời khỏi browser

### Backend (Server)  
- **Proof Verification**: Verify ZK proof bằng snarkjs
- **Role Management**: Quản lý root hash cho từng phòng ban
- **Access Control**: Chuyển hướng dựa trên verified root

### Cryptographic Components
- **ZK-SNARKs**: Groth16 proving system
- **Poseidon Hash**: ZK-friendly hash function
- **Merkle Trees**: Efficient membership proof

## 🚀 Cài đặt và chạy

### 1. Yêu cầu hệ thống
```bash
# Node.js để compile Circom
node --version  # >= 16.0.0

# Python để chạy server
python --version  # >= 3.8

# Circom toolchain (nếu cần compile lại circuit)
npm install -g circom snarkjs
```

### 2. Khởi động server
```bash
cd web/prover
python server.py
```

### 3. Truy cập ứng dụng
- **Login**: http://localhost:5001/
- **Register**: http://localhost:5001/register
- **Admin**: http://localhost:5001/delete

## � Hướng dẫn sử dụng

### Đăng ký nhân viên mới
1. Truy cập `/register`
2. Chọn phòng ban: `it`, `hr`, `sales`, `finance`
3. Nhập email: `alice@it.company.com`
4. Nhập secret: `mypassword123`
5. Hệ thống tạo leaf hash và cập nhật Merkle tree

### Đăng nhập ZK Proof
1. Truy cập `/`
2. Nhập email và secret đã đăng ký
3. Browser tạo ZK proof (2-5 giây)
4. Server verify proof và chuyển hướng đến dashboard tương ứng

### Quản lý nhân viên
1. Truy cập `/delete`
2. Chọn phòng ban
3. Xem danh sách leaves hiện có
4. Xóa nhân viên không cần thiết

## � Cấu trúc dữ liệu

### Merkle Tree Files (`roots/{role}.json`)
```json
{
  "root": "1234567890...",
  "leaves": [
    "9876543210...",  // hash(email1, secret1)
    "1111111111...",  // hash(email2, secret2)
    "0",              // empty slot
    "0"               // empty slot
  ],
  "emails": [
    "hash_of_email1",
    "hash_of_email2"
  ]
}
```

### Employee Data (`employees/employees_{role}.json`)
```json
[
  {
    "email": "alice@it.company.com",
    "secret": "mypassword123"
  }
]
```

## � Bảo mật và Privacy

### Zero-Knowledge Properties
- **Completeness**: User hợp lệ luôn tạo được proof
- **Soundness**: User không hợp lệ không thể fake proof  
- **Zero-Knowledge**: Server không biết secret của user

### Security Features
- ✅ **Client-side proof generation**: Secret không rời browser
- ✅ **Server-side verification**: Đảm bảo proof hợp lệ
- ✅ **Role-based redirect**: Server kiểm soát quyền truy cập
- ✅ **Merkle membership**: Chứng minh thuộc danh sách mà không tiết lộ vị trí

## ⚡ Performance

| Operation | Time | Note |
|-----------|------|------|
| Proof Generation | 2-5s | Client-side, depends on device |
| Proof Verification | <100ms | Server-side with snarkjs |
| Tree Update | <50ms | Add/remove employees |
| Max Capacity | 8 employees/dept | Configurable in circuit |

## 🔧 Cấu hình nâng cao

### Thay đổi số lượng employee tối đa
1. Sửa file `circuits/merkle_proof.circom`
2. Thay đổi parameter `levels`
3. Recompile circuit và generate setup

### Thêm phòng ban mới
1. Tạo file `roots/newdept.json`
2. Tạo file `employees/employees_newdept.json`
3. Cập nhật logic trong server.py

## 🐛 Troubleshooting

### Lỗi thường gặp

**"Không tìm thấy file wasm"**
- Đảm bảo đã compile circuit thành công
- Check file `outputs/merkle_proof_js/merkle_proof.wasm`

**"Proof generation failed"**
- Kiểm tra email/secret có trong danh sách không
- Verify Merkle tree structure trong `roots/{role}.json`

**"Proof verification failed"**
- Đảm bảo `verification_key.json` đúng version
- Check log server để xem chi tiết lỗi

## 📚 Tài liệu kỹ thuật

### Circuit Logic
```
Input:
- leaf: hash(email, secret)
- path_elements: [sibling1, sibling2, ...]
- path_index: [0/1, 0/1, ...] (direction bits)
- root: expected Merkle root

Output:
- isValid: 1 if proof valid, 0 otherwise
- verified_root: computed root from path
```

### API Endpoints
- `POST /verify_login`: Verify ZK proof và redirect
- `POST /register`: Đăng ký nhân viên mới
- `POST /delete_leaves`: Xóa nhân viên khỏi tree
- `GET /roots/{role}.json`: Lấy Merkle data cho role

## 🤝 Contribute

1. Fork repository
2. Tạo feature branch
3. Implement và test
4. Submit pull request

## 📄 License

MIT License - Xem file LICENSE để biết chi tiết

---

**🎯 Zero-Knowledge Authentication với Merkle Tree Management**
