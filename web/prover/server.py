from flask import Flask, request, render_template_string, redirect, send_from_directory, session
from flask import jsonify
from flask import Flask, jsonify, abort
from flask import send_file
import subprocess
import os
import sys
import json


def extract_role_from_email(email):
    # Assume email format: user@role.company.com
    try:
        return email.split("@")[1].split(".")[0]
    except Exception:
        return None

def find_role_by_root(target_root):
    #Find role corresponding to root by checking all files in roots
    roles = ["finance", "hr", "it", "sales"]  # List of available roles
    
    for role in roles:
        roots_path = os.path.abspath(os.path.join(os.path.dirname(__file__), f"../../roots/{role}.json"))
        try:
            if os.path.exists(roots_path):
                with open(roots_path, 'r', encoding='utf-8') as f:
                    root_data = json.load(f)
                    stored_root = str(root_data.get('root', ''))
                    
                    if stored_root == str(target_root):
                        return role
            else:
                print(f"[DEBUG] File does not exist: {roots_path}")
        except Exception as e:
            print(f"Error reading {roots_path}: {e}")
            continue
    
    return None  # No role found

# Ensure terminal displays UTF-8 correctly
sys.stdout.reconfigure(encoding='utf-8')

app = Flask(__name__)
app.secret_key = 'zk_rbac_2025_super_secure_key_f8a9b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2'


def poseidon_hash(inputs):
    #Call Node.js script to hash Poseidon with 2 inputs.
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
    # Convert leaves to int if needed
    nodes = [int(x) for x in leaves]
    while len(nodes) > 1:
        next_level = []
        for i in range(0, len(nodes), 2):
            left = nodes[i]
            right = nodes[i+1] if i+1 < len(nodes) else left
            # Call poseidon_hash with 2 inputs (same as backend you're using)
            h = poseidon_hash([left, right])
            next_level.append(h)
        nodes = next_level
    return str(nodes[0])

# Function to verify proof from client
def verify_proof_from_client(proof, public_signals):
    # Path to zkey and verification key
    vkey_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../outputs/verification_key.json"))

    # Path to outputs directory to save temporary files
    outputs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../outputs"))
    proof_path = os.path.join(outputs_dir, "proof.json")
    public_path = os.path.join(outputs_dir, "public.json")

    # Save proof and public signals temporarily to outputs directory
    with open(proof_path, "w", encoding="utf-8") as f:
        json.dump(proof, f)
    with open(public_path, "w", encoding="utf-8") as f:
        json.dump(public_signals, f)

    # Call snarkjs to verify
    try:
        result = subprocess.run([
            "snarkjs.cmd", "groth16", "verify",
            vkey_path, public_path, proof_path
        ], capture_output=True, text=True, check=True)
        
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

# Main route to handle login
@app.route("/", methods=["GET", "POST"])
def zk_process():
    return render_template_string(html_template)

# Handle when user sends proof and public signals
@app.route('/verify_login', methods=['POST'])
def verify_login_route():
    data = request.get_json()
    proof = data['proof']
    public_signals = data['publicSignals']

    ok, msg = verify_proof_from_client(proof, public_signals)
    if ok:
        if len(public_signals) >= 2:
            # verified_root from public signals
            verified_root = str(public_signals[1])
            
            # Find role corresponding to verified_root
            role = find_role_by_root(verified_root)
            if role:
                # Lưu role vào session
                session['user_role'] = role
                
                # Return URL for client to redirect (still safe because server has verified)
                return jsonify({
                    "success": True, 
                    "message": "Login successful!", 
                    "role": role,
                    "redirect_url": f"/home/{role}-dashboard.html"
                })
            else:
                return jsonify({
                    "success": False, 
                    "message": "Root has been tampered with or does not exist in the system!",
                    "verified_root": verified_root
                })
        else:
            return jsonify({
                "success": False, 
                "message": "Public signals incomplete!", 
                "log": msg
            })
    else:
        return jsonify({"success": False, "message": "Proof is invalid!", "log": msg})

# Separate endpoint for verifying old password during password change
@app.route('/verify_old_password', methods=['POST'])
def verify_old_password_route():
    print("Verifying old password...")
    data = request.get_json()
    proof = data['proof']
    public_signals = data['publicSignals']

    ok, msg = verify_proof_from_client(proof, public_signals)
    if ok:
        if len(public_signals) >= 2:
            # verified_root from public signals
            verified_root = str(public_signals[1])
            
            # Find role corresponding to verified_root
            role = find_role_by_root(verified_root)
            if role:
                # Don't set session for password verification, just return success
                return jsonify({
                    "success": True, 
                    "message": "Old password verification successful!", 
                    "role": role
                })
            else:
                return jsonify({
                    "success": False, 
                    "message": "Root has been tampered with or does not exist in the system!",
                    "verified_root": verified_root
                })
        else:
            return jsonify({
                "success": False, 
                "message": "Public signals incomplete!", 
                "log": msg
            })
    else:
        return jsonify({"success": False, "message": "Proof is invalid!", "log": msg})

#=====================================  Register new account =========================================
# Check email exists   
@app.route('/check_email', methods=['POST'])
def check_email():
    data = request.get_json()
    email_hash = str(data['email_hash'])
    role = data['role']
    roots_path = os.path.abspath(os.path.join(os.path.dirname(__file__), f"../../roots/{role}.json"))
    if not os.path.exists(roots_path):
        return jsonify({"success": False, "message": "Role does not exist!"})

    with open(roots_path, 'r', encoding='utf-8') as f:
        roots = json.load(f)
    emails = roots.get('emails', [])
    # Check duplicate email
    if email_hash in emails:
        return jsonify({"success": False, "message": "Email already exists!"})
    return jsonify({"success": True, "message": "Email does not exist, can register."})

# Register new account
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email_hash = str(data['email_hash'])
    leaf_hash = str(data['leaf_hash'])
    role = data['role']
    roots_path = os.path.abspath(os.path.join(os.path.dirname(__file__), f"../../roots/{role}.json"))
    if not os.path.exists(roots_path):
        return jsonify({"success": False, "message": "Role does not exist!"})
    with open(roots_path, 'r', encoding='utf-8') as f:
        roots = json.load(f)
    leaves = roots.get('leaves', [])
    emails = roots.get('emails', [])
    try:
        idx = leaves.index("0")
    except ValueError:
        return jsonify({"success": False, "message": "No registration slots available!"})
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
    return jsonify({"success": True, "message": "Registration successful!"})

# Add email and secret to file in employees folder (Trial step)
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

#======================================== Change Password ========================================

@app.route('/change_password', methods=['POST'])
def change_password():
    try:
        data = request.get_json()
        new_leaf = str(data['new_leaf'])
        index = int(data['index'])
        role = data['role']
        roots_path = os.path.abspath(os.path.join(os.path.dirname(__file__), f"../../roots/{role}.json"))
        if not os.path.exists(roots_path):
            return jsonify({"success": False, "message": f"File {roots_path} not found"}), 400

        with open(roots_path, 'r', encoding='utf-8') as f:
            roots = json.load(f)

        # Check valid index
        if not (0 <= index < len(roots['leaves'])):
            return jsonify({"success": False, "message": "Invalid index!"}), 400

        roots['leaves'][index] = new_leaf
        roots['root'] = build_merkle_root(roots['leaves'])


        with open(roots_path, 'w', encoding='utf-8') as f:
            json.dump(roots, f, ensure_ascii=False, indent=2)
        session.clear()
        return jsonify({"success": True, "message": "Password changed successfully!"})
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"success": False, "message": f"Server error: {e}"}), 500

#====================================================================================================

#========================================= Delete leaves function =========================================

# Get list of leaves by role
@app.route('/get_leaves', methods=['POST'])
def get_leaves():
    try:
        data = request.get_json()
        role = data['role']
        
        roots_path = os.path.abspath(os.path.join(os.path.dirname(__file__), f"../../roots/{role}.json"))
        if not os.path.exists(roots_path):
            return jsonify({"success": False, "message": f"Role {role} does not exist!"})

        with open(roots_path, 'r', encoding='utf-8') as f:
            roots = json.load(f)

        leaves = roots.get('leaves', [])
        return jsonify({"success": True, "leaves": leaves})
    except Exception as e:
        return jsonify({"success": False, "message": f"Server error: {e}"})

# Delete leaves by indices
@app.route('/delete_leaves', methods=['POST'])
def delete_leaves():
    try:
        data = request.get_json()
        role = data['role']
        indices = data['indices']  # List of indices to delete
        
        roots_path = os.path.abspath(os.path.join(os.path.dirname(__file__), f"../../roots/{role}.json"))
        if not os.path.exists(roots_path):
            return jsonify({"success": False, "message": f"Role {role} does not exist!"})

        with open(roots_path, 'r', encoding='utf-8') as f:
            roots = json.load(f)

        leaves = roots.get('leaves', [])
        emails = roots.get('emails', [])
        
        # Check valid indices
        for idx in indices:
            if not (0 <= idx < len(leaves)):
                return jsonify({"success": False, "message": f"Index {idx} is invalid!"})
            if leaves[idx] == '0':
                return jsonify({"success": False, "message": f"Index {idx} is already empty!"})

        # Read employees file to delete corresponding email and secret
        employees_path = os.path.abspath(os.path.join(os.path.dirname(__file__), f"../../employees/employees_{role}.json"))
        employees = []
        if os.path.exists(employees_path):
            with open(employees_path, 'r', encoding='utf-8') as f:
                employees = json.load(f)

        # Sort indices in descending order to delete from end to beginning
        sorted_indices = sorted(indices, reverse=True)
        
        # Delete leaves, emails and employees by indices
        for idx in sorted_indices:
            # Delete leaf
            leaves[idx] = '0'
            # Delete corresponding email directly from array
            if idx < len(emails):
                emails.pop(idx)
            # Delete corresponding employee from employees file
            if idx < len(employees):
                employees.pop(idx)

        # Move non-zero leaves to the front
        non_zero_leaves = [leaf for leaf in leaves if leaf != '0']
        zero_count = len(leaves) - len(non_zero_leaves)
        leaves = non_zero_leaves + ['0'] * zero_count

        # Emails only contain actual emails, not '0'
        # No need to add '0' to emails

        # Update root
        roots['leaves'] = leaves
        roots['emails'] = emails
        roots['root'] = build_merkle_root(leaves)

        # Save roots file
        with open(roots_path, 'w', encoding='utf-8') as f:
            json.dump(roots, f, ensure_ascii=False, indent=2)

        # Save updated employees file
        if os.path.exists(employees_path):
            with open(employees_path, 'w', encoding='utf-8') as f:
                json.dump(employees, f, ensure_ascii=False, indent=2)

        return jsonify({"success": True, "message": f"Successfully deleted {len(indices)} leaves and corresponding employees!"})
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"success": False, "message": f"Server error: {e}"})

#====================================================================================================

#========================================= Redirect and JSON file functions =========================================

# Redirect dashboard by role - kiểm tra session và role
@app.route("/home/<path:filename>")
def serve_home(filename):
    # Chỉ kiểm tra đã đăng nhập chưa
    if 'user_role' not in session:
        return redirect('/')
    
    # Lấy role từ filename (vd: "finance-dashboard.html" -> "finance")
    requested_role = filename.split('-')[0] if '-' in filename else None
    user_role = session.get('user_role')
    
    # Kiểm tra role có khớp không - chỉ redirect nếu khác role
    if requested_role and requested_role != user_role:
        # Redirect về dashboard đúng của user
        return redirect(f"/home/{user_role}-dashboard.html")
    
    # Get path to home directory at same level as prover
    home_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../home"))
    return send_from_directory(home_dir, filename)


# Server the register page
@app.route('/register')
def serve_register():
    html_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../Register/register.html"))
    return send_file(html_path)

# Server the delete page
@app.route('/delete')
def serve_delete():
    html_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../Delete/Delete.html"))
    return send_file(html_path)

# To update password when not yet hashed
@app.route('/update_employee_secret', methods=['POST'])
def update_employee_secret():
    data = request.get_json()
    email = data['email']
    role = data['role']
    new_secret = data['new_secret']
    # Absolute path to employees file
    employees_path = os.path.abspath(os.path.join(os.path.dirname(__file__), f"../../employees/employees_{role}.json"))
    try:
        with open(employees_path, 'r', encoding='utf-8') as f:
            employees = json.load(f)
        # Update by email
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
    # Absolute or relative path to directory containing file
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