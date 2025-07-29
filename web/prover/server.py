from flask import Flask, request, render_template_string, redirect, send_from_directory
from flask import jsonify
from flask import Flask, jsonify, abort
from flask import send_file
import subprocess
import os
import sys
import json


def extract_role_from_email(email):
    # Giả sử email có dạng: user@role.company.com
    try:
        return email.split("@")[1].split(".")[0]
    except Exception:
        return None

# Đảm bảo terminal hiển thị đúng UTF-8
sys.stdout.reconfigure(encoding='utf-8')

app = Flask(__name__)


def poseidon_hash(inputs):
    """Gọi Node.js script để hash Poseidon 2 input."""
    if len(inputs) != 2:
        raise ValueError("Poseidon hash requires exactly 2 inputs.")
    js_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../merkle/poseidon_hash.js"))
    result = subprocess.run(
        ["node", js_path, str(inputs[0]), str(inputs[1])],
        capture_output=True,
        text=True,
        check=True
    )
    return int(result.stdout.strip())

# Load HTML template
html_path = os.path.join(os.path.dirname(__file__), "index.html")
with open(html_path, "r", encoding="utf-8") as f:
    html_template = f.read()

# function to generate Merkle root
def build_merkle_root(leaves):
    # Chuyển leaves thành int nếu cần
    nodes = [int(x) for x in leaves]
    while len(nodes) > 1:
        next_level = []
        for i in range(0, len(nodes), 2):
            left = nodes[i]
            right = nodes[i+1] if i+1 < len(nodes) else left
            # Gọi hàm poseidon_hash 2 input (giống backend bạn đang dùng)
            h = poseidon_hash([left, right])
            next_level.append(h)
        nodes = next_level
    return str(nodes[0])

# Hàm để verify proof từ client
def verify_proof_from_client(proof, public_signals):
    # Đường dẫn tới zkey và verification key
    vkey_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../outputs/verification_key.json"))

    # Lưu proof và public signals tạm thời
    with open("proof.json", "w", encoding="utf-8") as f:
        json.dump(proof, f)
    with open("public.json", "w", encoding="utf-8") as f:
        json.dump(public_signals, f)

    # Gọi snarkjs để verify
    try:
        result = subprocess.run([
            "snarkjs.cmd", "groth16", "verify",
            vkey_path, "public.json", "proof.json"
        ], capture_output=True, text=True, check=True)
        # Kiểm tra isValid trong public_signals
        is_valid = str(public_signals[-1])  # isValid thường là phần tử cuối
        if is_valid != "1":
            return False, "isValid signal != 1 (proof không hợp lệ)"
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

# Route chính để xử lý đăng nhập
@app.route("/", methods=["GET", "POST"])
def zk_process():
    return render_template_string(html_template)

#xử lí sk khi người dùng gửi proof và public signals lên 
@app.route('/verify_login', methods=['POST'])
def verify_login_route():
    data = request.get_json()
    proof = data['proof']
    public_signals = data['publicSignals']

    ok, msg = verify_proof_from_client(proof, public_signals)
    if ok:
        return jsonify({"success": True, "message": "Proof hợp lệ!", "log": msg})
    else:
        return jsonify({"success": False, "message": "Proof không hợp lệ!", "log": msg})

#=====================================  đăng kí tai khoản mới =========================================
#check email exist   
@app.route('/check_email', methods=['POST'])
def check_email():
    data = request.get_json()
    email_hash = str(data['email_hash'])
    role = data['role']
    roots_path = os.path.abspath(os.path.join(os.path.dirname(__file__), f"../../roots/{role}.json"))
    if not os.path.exists(roots_path):
        return jsonify({"success": False, "message": "Role không tồn tại!"})

    with open(roots_path, 'r', encoding='utf-8') as f:
        roots = json.load(f)
    emails = roots.get('emails', [])
    # Kiểm tra trùng email
    if email_hash in emails:
        return jsonify({"success": False, "message": "Email đã tồn tại!"})
    return jsonify({"success": True, "message": "Email chưa tồn tại, có thể đăng ký."})

# Đăng ký tài khoản mới
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email_hash = str(data['email_hash'])
    leaf_hash = str(data['leaf_hash'])
    role = data['role']
    roots_path = os.path.abspath(os.path.join(os.path.dirname(__file__), f"../../roots/{role}.json"))
    if not os.path.exists(roots_path):
        return jsonify({"success": False, "message": "Role không tồn tại!"})
    with open(roots_path, 'r', encoding='utf-8') as f:
        roots = json.load(f)
    leaves = roots.get('leaves', [])
    emails = roots.get('emails', [])
    try:
        idx = leaves.index("0")
    except ValueError:
        return jsonify({"success": False, "message": "Hết slot đăng ký!"})
    leaves[idx] = leaf_hash
    if len(emails) < len(leaves):
        emails.append(email_hash)
    else:
        emails[idx] = email_hash
    roots['leaves'] = leaves
    roots['emails'] = emails
    roots['root'] = build_merkle_root(leaves)
    with open(roots_path, 'w', encoding='utf-8') as f:
        json.dump(roots, f, ensure_ascii=False, indent=2)
    return jsonify({"success": True, "message": "Đăng ký thành công!"})

#thêm email và secret vào file trong folder employees (Bước thử nghiệm)
@app.route('/add_employee', methods=['POST'])
def add_employee():
    data = request.get_json()
    email = data['email']
    secret = data['secret']
    role = data['role']
    employees_path = os.path.abspath(os.path.join(os.path.dirname(__file__), f"../../employees/employees_{role}.json"))
    try:
        if os.path.exists(employees_path):
            with open(employees_path, 'r', encoding='utf-8') as f:
                employees = json.load(f)
        else:
            employees = []
        employees.append({"email": email, "secret": secret})
        with open(employees_path, 'w', encoding='utf-8') as f:
            json.dump(employees, f, ensure_ascii=False, indent=2)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})
    
#====================================================================================================

#======================================== Đổi mật khẩu ========================================

@app.route('/change_password', methods=['POST'])
def change_password():
    try:
        data = request.get_json()
        new_leaf = str(data['new_leaf'])
        index = int(data['index'])
        role = data['role']
        roots_path = os.path.abspath(os.path.join(os.path.dirname(__file__), f"../../roots/{role}.json"))
        if not os.path.exists(roots_path):
            return jsonify({"success": False, "message": f"Không tìm thấy file {roots_path}"}), 400

        with open(roots_path, 'r', encoding='utf-8') as f:
            roots = json.load(f)

        # Kiểm tra index hợp lệ
        if not (0 <= index < len(roots['leaves'])):
            return jsonify({"success": False, "message": "Index không hợp lệ!"}), 400

        roots['leaves'][index] = new_leaf
        roots['root'] = build_merkle_root(roots['leaves'])


        with open(roots_path, 'w', encoding='utf-8') as f:
            json.dump(roots, f, ensure_ascii=False, indent=2)

        return jsonify({"success": True, "message": "Đổi mật khẩu thành công!"})
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"success": False, "message": f"Lỗi server: {e}"}), 500

#====================================================================================================

#========================================= Các chức năng chuyển hướng và lấy file json =========================================

# Chuyển hướng dashboard theo role
@app.route("/home/<path:filename>")
def serve_home(filename):
    # Lấy đường dẫn thư mục home cùng cấp với prover
    home_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../home"))
    return send_from_directory(home_dir, filename)

# Server the register page
@app.route('/register')
def serve_register():
    html_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../Register/register.html"))
    return send_file(html_path)

#để cập nhật lại mật khẩu lúc chưa hash
@app.route('/update_employee_secret', methods=['POST'])
def update_employee_secret():
    data = request.get_json()
    email = data['email']
    role = data['role']
    new_secret = data['new_secret']
    # Đường dẫn tuyệt đối tới file employees
    employees_path = os.path.abspath(os.path.join(os.path.dirname(__file__), f"../../employees/employees_{role}.json"))
    try:
        with open(employees_path, 'r', encoding='utf-8') as f:
            employees = json.load(f)
        # Cập nhật theo email
        for emp in employees:
            if emp['email'] == email:
                emp['secret'] = new_secret
                break
        with open(employees_path, 'w', encoding='utf-8') as f:
            json.dump(employees, f, ensure_ascii=False, indent=2)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})
    
@app.route('/roots/<path:filename>')
def serve_myfile(filename):
    # Đường dẫn tuyệt đối hoặc tương đối tới thư mục chứa file
    file_path = f"../../roots/{filename}"
    return send_file(file_path)

@app.route('/outputs/merkle_proof_js/<filename>')
def serve_wasm(filename):
    wasm_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../outputs/merkle_proof_js"))
    file_path = os.path.join(wasm_dir, filename)
    if not os.path.exists(file_path):
        abort(404)
    return send_file(file_path)

@app.route('/outputs/<filename>')
def serve_zkey(filename):
    outputs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../outputs"))
    file_path = os.path.join(outputs_dir, filename)
    if not os.path.exists(file_path):
        abort(404)
    return send_file(file_path)

#====================================================================================================

if __name__ == "__main__":
    app.run(debug=True, port=5001)