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

# Load HTML template
html_path = os.path.join(os.path.dirname(__file__), "index.html")
with open(html_path, "r", encoding="utf-8") as f:
    html_template = f.read()

# def generate_proof(email, secret):
#     """Sinh proof cho email + secret. Trả về True nếu thành công, False nếu lỗi."""
#     script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../merkle/generate_input_json.py"))
#     script_dir = os.path.dirname(script_path)
#     try:
#         result = subprocess.run(
#             ["python", script_path, "--email", email, "--secret", secret],
#             cwd=script_dir,
#             capture_output=True,
#             text=True,
#             encoding="utf-8",
#             errors="ignore",
#             check=True
#         )
#         print("✅ generate_input_json.py success")
#         print("STDOUT:", result.stdout)
#     except subprocess.CalledProcessError as e:
#         print("❌ Error calling generate_input_json.py")
#         print("Return code:", e.returncode)
#         print("STDOUT:", e.stdout)
#         print("STDERR:", e.stderr)
#         return False

#     # Generate witness
#     try:
#         wasm_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../outputs/merkle_proof_js/merkle_proof.wasm"))
#         input_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../inputs/input.json"))
#         witness_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../outputs/witness.wtns"))
#         subprocess.run([
#             "snarkjs.cmd", "wtns", "calculate",
#             "--wasm", wasm_path,
#             "--input", input_path,
#             "--witness", witness_path
#         ], check=True, text=True, encoding="utf-8", errors="ignore")
#         # Generate proof
#         zkey_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../outputs/merkle_proof_final.zkey"))
#         proof_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../outputs/proof.json"))
#         public_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../outputs/public.json"))
#         subprocess.run([
#             "snarkjs.cmd", "groth16", "prove",
#             zkey_path,
#             witness_path,
#             proof_path,
#             public_path
#         ], check=True, text=True, encoding="utf-8", errors="ignore")
#         return True
#     except subprocess.CalledProcessError as e:
#         print("❌ Error during witness/proof generation")
#         print("Return code:", e.returncode)
#         print("STDOUT:", e.stdout)
#         print("STDERR:", e.stderr)
#         return False

# def verify_proof():
#     """Xác thực proof đã sinh. Trả về True nếu hợp lệ, False nếu không."""
#     try:
#         proof_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../outputs/proof.json"))
#         public_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../outputs/public.json"))
#         vkey_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../outputs/verification_key.json"))
#         subprocess.check_call([
#             "snarkjs.cmd", "groth16", "verify",
#             vkey_path, public_path, proof_path
#         ])
#         return True
#     except subprocess.CalledProcessError:
#         return False

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
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

@app.route("/", methods=["GET", "POST"])
def zk_process():
    if request.method == "GET":
        return render_template_string(html_template)

    email = request.form.get("email")
    secret = request.form.get("secret")
    role = extract_role_from_email(email)

    if not email or '@' not in email:
        return render_template_string(html_template + "<script>alert('Sai format email!');</script>")

    # if not generate_proof(email, secret):
    #     return render_template_string(html_template + "<script>alert('❌ Tài khoản hoặc mật khẩu không đúng!');</script>")

    if verify_proof():
        print("role là : " + str(role))
        return redirect(f"/home/{role}-dashboard.html")
    else:
        return render_template_string(html_template + "<script>alert('❌ Tài khoản hoặc mật khẩu không đúng!');</script>")

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
    
# Chuyển hướng dashboard theo role
@app.route("/home/<path:filename>")
def serve_home(filename):
    # Lấy đường dẫn thư mục home cùng cấp với prover
    home_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../home"))
    return send_from_directory(home_dir, filename)

import subprocess

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

        # TODO: build lại Merkle root ở đây nếu bạn có hàm build_merkle_root
        # roots['root'] = build_merkle_root(roots['leaves'])

        with open(roots_path, 'w', encoding='utf-8') as f:
            json.dump(roots, f, ensure_ascii=False, indent=2)

        return jsonify({"success": True, "message": "Đổi mật khẩu thành công!"})
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"success": False, "message": f"Lỗi server: {e}"}), 500

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

if __name__ == "__main__":
    app.run(debug=True, port=5001)