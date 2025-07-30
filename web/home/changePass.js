document.addEventListener('DOMContentLoaded', function () {
    const changePassForm = document.getElementById('changePassForm');
    if (changePassForm) {
      changePassForm.addEventListener('submit', async function (e) {
        e.preventDefault();

        // Lấy nút submit và lưu trạng thái ban đầu
        const submitBtn = this.querySelector('button[type="submit"]');
        const originalHTML = submitBtn.innerHTML;
        
        // Chuyển nút thành trạng thái "Đang xác nhận..."
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin finance-icon"></i> Đang xác nhận...';
        submitBtn.disabled = true;

        try {
          // Lấy email và role từ localStorage
          const email = localStorage.getItem('zk_email');
          if (!email) {
            alert('Login email not found!');
            return;
          }
          const role = extractRoleFromEmail(email); // Hàm này bạn đã có ở client

          // Lấy giá trị các trường
          const oldSecret = this.querySelector('input[name="old_secret"]').value;
          const newSecret = this.querySelector('input[name="new_secret"]').value;
          const confirmSecret = this.querySelector('input[name="confirm_secret"]').value;

          // Check if new password matches confirmation
          if (newSecret !== confirmSecret) {
            alert('New password and confirmation do not match!');
            return;
          }

          // Check if new password is different from current password
          if (newSecret === oldSecret) {
            alert('New password cannot be the same as current password!');
            return;
          }

          // 1. Generate proof to verify old password
          let proof, publicSignals, index;
          try {
            ({ proof, publicSignals , index } = await generateProof(email, oldSecret, role));
            alert('Proof generated successfully!');
          } catch (err) {
            alert('Error generating old password verification proof: ' + err);
            return;
          }

          //2. Send proof to server to verify old password
          try {
            const res = await fetch('/verify_old_password', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ proof, publicSignals })
            });
            const result = await res.json();
            if (!result.success) {
              alert('Current password is incorrect!');
              return;
            }else{
              alert('Old password verification successful! Index = ' + String(index));
              // Send request to update secret on server
              try {
                const updateRes = await fetch('/update_employee_secret', {
                  method: 'POST',
                  headers: { 'Content-Type': 'application/json' },
                  body: JSON.stringify({
                    email: email,
                    role: role,
                    new_secret: newSecret
                  })
                });
                const updateResult = await updateRes.json();
                if (updateResult.success) {
                  alert('New password updated in employees successfully!');
                } else {
                  alert('Employee update failed: ' + updateResult.message);
                }
              } catch (err) {
                alert('Error updating employees: ' + err);
              }
              // Save index to send to server
              localStorage.setItem('zk_index', index);
            }
          } catch (err) {
            alert('Old password verification error: ' + err);
            return;
          }

          // 3. Calculate Poseidon hash of email + new password (assuming you have poseidonHashLeafJS function)
          let newLeaf;
          try {
            newLeaf = await hashLeaf(email, newSecret); // This function needs to be defined on client
          } catch (err) {
            alert('Error hashing new password: ' + err);
            return;
          }

          // 4. Send new hash, index, role to server to change leaf
          try {
            const res = await fetch('/change_password', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                new_leaf: newLeaf,
                index: index,
                role: role
              })
            });
            const result = await res.json();
            if (result.success) {
              alert('Password changed successfully!');
              window.location.href = "/";
            } else {
              alert(result.message || 'Password change failed!');
            }
          } catch (err) {
            alert('Server error: ' + err);
          }
        } catch (error) {
          alert('Unknown error: ' + error);
        } finally {
          // Restore original button state
          submitBtn.innerHTML = originalHTML;
          submitBtn.disabled = false;
        }
      });
    }

    // Hiện/ẩn mật khẩu
    const showPassword = document.getElementById('showPassword');
    showPassword.addEventListener('change', function () {
      const fields = [
        document.getElementById('oldSecret'),
        document.getElementById('newSecret'),
        document.getElementById('confirmSecret')
      ];
      fields.forEach(field => {
        if (field) field.type = this.checked ? 'text' : 'password';
      });
    });
  });