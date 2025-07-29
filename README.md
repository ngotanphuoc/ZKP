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

## �️ Công nghệ

- **ZK-SNARKs**: Tạo và verify proof
- **Merkle Trees**: Lưu trữ dữ liệu nhân viên
- **Poseidon Hash**: Hash function cho ZK circuits
- **Python Flask**: Backend API
- **JavaScript**: Frontend logic

## � Chạy Demo

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

---

**🎯 Zero-Knowledge Demo với Merkle Tree Operations**

### Đăng ký nhân viên mới
1. Vào `/register`
2. Chọn phòng ban
3. Nhập email: `name@phongban.company.com`
4. Nhập mật khẩu
5. Nhấn đăng ký

### Đăng nhập
1. Vào trang chủ `/`
2. Nhập email và mật khẩu
3. Hệ thống tự động tạo ZK proof
4. Chuyển đến dashboard của phòng ban

### Xóa nhân viên
1. Vào `/delete`
2. Chọn phòng ban
3. Chọn nhân viên cần xóa
4. Xác nhận xóa

## � Cấu trúc file

```
├── circuits/           # ZK Circuit
├── web/               # Web app
│   ├── prover/        # Trang đăng nhập
│   ├── Register/      # Trang đăng ký
│   ├── Delete/        # Trang xóa
│   └── home/          # Dashboard
├── employees/         # Dữ liệu nhân viên
├── roots/            # Merkle tree data
└── outputs/          # ZK keys và circuits
```

## � Bảo mật

### Zero-Knowledge Properties
- **Hoàn chỉnh**: Proof đúng luôn được chấp nhận
- **Âm thanh**: Proof sai luôn bị từ chối
- **Zero-Knowledge**: Không tiết lộ thông tin bí mật

### Phân quyền
- Mỗi phòng ban có dữ liệu riêng biệt
- Email phải đúng format: `name@phongban.company.com`
- Không duplicate email trong cùng phòng ban

## 🛡️ API Endpoints

### Xác thực
- `POST /verify_login` - Verify ZK proof
- `GET /` - Trang đăng nhập

### Quản lý nhân viên
- `POST /register` - Đăng ký nhân viên mới
- `POST /check_email` - Kiểm tra email có tồn tại
- `POST /change_password` - Đổi mật khẩu
- `POST /delete_leaves` - Xóa nhân viên

## 🐛 Xử lý lỗi

### Lỗi thường gặp

**1. Không tạo được proof**
- Kiểm tra email và mật khẩu
- Đảm bảo đã đăng ký trước

**2. Server lỗi**
- Kiểm tra đường dẫn file
- Kiểm tra format JSON
- Restart server

**3. Hash không khớp**
- Đảm bảo encoding UTF-8
- Kiểm tra Poseidon implementation

## 📈 Hiệu năng

- **Tạo Proof**: 2-5 giây
- **Verify Proof**: <100ms
- **Cập nhật Merkle**: <50ms
- **Hỗ trợ**: 8 nhân viên/phòng ban

## 📞 Liên hệ

- **Email**: contact@zkrbac.com
- **GitHub**: [Repository Link]

---

**⚡ Xây dựng với ❤️ sử dụng Zero-Knowledge Cryptography**
   - Tạo ZK proof
   - Verify proof trên server
   - Chuyển hướng đến dashboard tương ứng

### Xóa nhân viên
1. Truy cập `/delete`
2. Chọn phòng ban
3. Chọn nhân viên cần xóa
4. Xác nhận xóa
5. Hệ thống sẽ:
   - Xóa khỏi tất cả file lưu trữ
   - Cập nhật lại Merkle tree
   - Dịch chuyển leaves còn lại

## 📁 Cấu trúc dữ liệu

### File `roots/{role}.json`
```json
{
  "root": "merkle_root_hash",
  "leaves": ["leaf1", "leaf2", "0", "0"],
  "emails": ["email_hash1", "email_hash2"]
}
```

### File `employees/employees_{role}.json`
```json
[
  {"email": "user@it.company.com", "secret": "password123"},
  {"email": "admin@hr.company.com", "secret": "secret456"}
]
```

## 🔐 Bảo mật

### Zero-Knowledge Properties
- **Completeness**: Proof hợp lệ luôn được chấp nhận
- **Soundness**: Proof không hợp lệ luôn bị từ chối  
- **Zero-Knowledge**: Không tiết lộ thông tin ngoài validity

### Hash Functions
- **Poseidon**: Optimized cho ZK circuits
- **Merkle Tree**: Đảm bảo data integrity
- **Role Separation**: Mỗi role có tree riêng biệt

### Access Control
- **Role-based**: 4 levels: IT, HR, Sales, Finance
- **Email Format Validation**: `name@role.company.com`
- **Unique Constraints**: Không duplicate email

## 🛡️ API Endpoints

### Authentication
- `POST /verify_login` - Verify ZK proof
- `GET /` - Main login page

### Employee Management  
- `POST /register` - Register new employee
- `POST /check_email` - Check email existence
- `POST /add_employee` - Add to employees file
- `POST /change_password` - Update password
- `POST /update_employee_secret` - Update raw secret

### Employee Deletion
- `POST /get_leaves` - Get leaves by role
- `POST /delete_leaves` - Delete selected employees
- `GET /delete` - Deletion interface

### File Serving
- `GET /register` - Registration page
- `GET /home/{filename}` - Dashboard files
- `GET /roots/{filename}` - Merkle data
- `GET /outputs/{filename}` - Circuit artifacts

## 🐛 Troubleshooting

### Common Issues

**1. Circuit compilation errors**
```bash
# Ensure Circom is installed
circom --version

# Check circuit syntax
circom circuits/merkle_proof.circom --r1cs --wasm --sym
```

**2. Proof generation fails**
- Kiểm tra witness generation
- Verify input format
- Check circuit constraints

**3. Server errors**
- Kiểm tra file paths trong `server.py`
- Verify JSON file format
- Check Python dependencies

**4. Hash mismatch**
- Ensure consistent Poseidon implementation
- Verify input encoding (UTF-8)
- Check Node.js script execution

## 📈 Hiệu năng

### Benchmarks (Local)
- **Proof Generation**: ~2-5 seconds
- **Proof Verification**: <100ms  
- **Merkle Update**: <50ms
- **Tree Size**: Support up to 8 leaves per role

### Optimization
- Pre-compiled WASM circuits
- Cached verification keys
- Optimized Poseidon parameters

## 🤝 Đóng góp

1. Fork repository
2. Tạo feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Tạo Pull Request

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

## 👥 Team

- **Lead Developer**: [Your Name]
- **ZK Consultant**: [Consultant Name]  
- **UI/UX Designer**: [Designer Name]

## 📞 Liên hệ

- **Email**: contact@zkrbac.com
- **GitHub**: [Repository Link]
- **Documentation**: [Docs Link]

## 🙏 Acknowledgments

- [Circom Team](https://github.com/iden3/circom) - ZK circuit framework
- [SnarkJS](https://github.com/iden3/snarkjs) - JavaScript SNARK toolkit  
- [Poseidon Hash](https://github.com/iden3/circomlib) - ZK-friendly hash function
- [Tailwind CSS](https://tailwindcss.com) - Utility-first CSS framework

---

## 📚 Additional Resources

### Learning ZK
- [Zero Knowledge Proofs: An Illustrated Primer](https://blog.cryptographyengineering.com/2014/11/27/zero-knowledge-proofs-illustrated-primer/)
- [Circom Documentation](https://docs.circom.io/)
- [ZK Learning Resources](https://zkp.science/)

### Cryptography
- [Poseidon Hash Paper](https://eprint.iacr.org/2019/458.pdf)
- [Merkle Tree Specification](https://tools.ietf.org/html/rfc6962)
- [Groth16 Paper](https://eprint.iacr.org/2016/260.pdf)

---

**⚡ Built with ❤️ using Zero-Knowledge Cryptography**
