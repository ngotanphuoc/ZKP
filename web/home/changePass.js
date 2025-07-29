document.addEventListener('DOMContentLoaded', function () {
    const changePassForm = document.getElementById('changePassForm');
    if (changePassForm) {
      changePassForm.addEventListener('submit', async function (e) {
        e.preventDefault();

        // Lấy email và role từ localStorage
        const email = localStorage.getItem('zk_email');
        if (!email) {
          alert('Không tìm thấy email đăng nhập!');
          return false;
        }
        const role = extractRoleFromEmail(email); // Hàm này bạn đã có ở client

        // Lấy giá trị các trường
        const oldSecret = this.querySelector('input[name="old_secret"]').value;
        const newSecret = this.querySelector('input[name="new_secret"]').value;
        const confirmSecret = this.querySelector('input[name="confirm_secret"]').value;

        // Kiểm tra mật khẩu mới và xác nhận
        if (newSecret !== confirmSecret) {
          alert('Mật khẩu mới và xác nhận không khớp!');
          return false;
        }

        // Kiểm tra mật khẩu mới có khác mật khẩu cũ không
         if (newSecret === oldSecret) {
          alert('Mật khẩu mới không được trùng với mật khẩu hiện tại!');
          return false;
        }

        // 1. Sinh proof xác thực mật khẩu cũ
        let proof, publicSignals, index;
        try {
          ({ proof, publicSignals , index } = await generateProof(email, oldSecret, role));
          alert('Sinh proof thành công!');
        } catch (err) {
          alert('Lỗi khi sinh proof xác thực mật khẩu cũ: ' + err);
          return false;
        }

        //2. Gửi proof lên server để xác thực mật khẩu cũ
        try {
          const res = await fetch('/verify_login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ proof, publicSignals })
          });
          const result = await res.json();
          if (!result.success) {
            alert('Mật khẩu hiện tại không đúng!');
            return false;
          }else{
            alert('Xác thực mật khẩu cũ thành công! có index = ' + String(index));
            // Gửi request cập nhật secret lên server
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
                alert('Cập nhật mật khẩu mới trong employees thành công!');
              } else {
                alert('Cập nhật employees thất bại: ' + updateResult.message);
              }
            } catch (err) {
              alert('Lỗi khi cập nhật employees: ' + err);
            }
            // Lưu index để gửi lên server
            localStorage.setItem('zk_index', index);
          }
        } catch (err) {
          alert('Lỗi xác thực mật khẩu cũ: ' + err);
          return false;
        }

       // 3. Tính hash Poseidon của email + mật khẩu mới (giả sử bạn có hàm poseidonHashLeafJS)
        let newLeaf;
        try {
          newLeaf = await hashLeaf(email, newSecret); // Hàm này bạn cần định nghĩa ở client
        } catch (err) {
          alert('Lỗi khi hash mật khẩu mới: ' + err);
          return false;
        }

        // 4. Gửi hash mới, index, role lên server để đổi leaf
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
            alert('Đổi mật khẩu thành công!');
            window.location.href = "/";
          } else {
            alert(result.message || 'Đổi mật khẩu thất bại!');
          }
        } catch (err) {
          alert('Lỗi server: ' + err);
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