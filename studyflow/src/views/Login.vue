<template>
  <div class="login-page">
    
    <!-- Component mạng nơ-ron chồng lên -->
    <NeuralNetworkBg />

    <!-- Content chính -->
    <div class="content">
      <h1 style="font-size: 3.5em;">StudyFlow</h1>

      <!-- Khung đăng nhập -->
        <div class="auth-form">
          <h2 id="loginTitle">Đăng nhập</h2>
          <form @submit.prevent="handleLogin">
            <div class="form-group">
              <label for="username" id="usernameLabel">Tên đăng nhập:</label>
              <input type="text" v-model="username" id="usernamePlaceholder" :placeholder="'Nhập tên đăng nhập.....'" />
              <p v-if="errors.username" class="error-message">{{ errors.username }}</p>
            </div>
            <div class="form-group">
              <label for="password" id="passwordLabel">Mật khẩu:</label>
              <input type="password" v-model="password" id="passwordPlaceholder" :placeholder= "'Nhập mật khẩu.....'" />
              <p v-if="errors.password" class="error-message">{{ errors.password }}</p>
            </div>
            <button class="btn-login" id="loginButton"> Đăng nhập</button> 
            <p>Hoặc đăng nhập bằng:</p>         
            <div class="social-login">
              <button type="button" class="btn-login"  @click="loginWithGoogle" ><i class='bx bxl-google'></i>&nbsp;&nbsp;Đăng nhập với Google</button>
              <p v-if="errors.google" class="error-message">{{ errors.google }}</p>
            </div>
          </form>
      
          <p class="signup-link">
            Bạn chưa có tài khoản?
            <button class="btn-signup" @click="goToRegister">Đăng ký</button>
          </p>

        </div>
      <!-- Kết thúc khung đăng nhập -->
    </div>
  </div>
</template>

<script setup>
import NeuralNetworkBg from '@/components/NeuralNetworkBg.vue';
import { useRouter } from 'vue-router';
import { ref, reactive } from 'vue';
import axios from "axios";
import { getAuth, signInWithPopup, GoogleAuthProvider } from "firebase/auth";

const router = useRouter();

const goToRegister = () => {
  router.push('/register');
}

// Đăng nhập Google với Firebase
const auth = getAuth();
const provider = new GoogleAuthProvider();
const errors = reactive({});

const loginWithGoogle = async () => {
  try {
    // 1. Đăng nhập bằng popup Google
    const result = await signInWithPopup(auth, provider)
    const user = result.user
    
    // 2. Lấy ID token
    const idToken = await user.getIdToken()
    console.log("Google ID Token:", idToken) // Debug token

    // 3. Gửi token lên backend
    const response = await axios.post("/api/auth/google-login", {
      token: idToken  
    }, {
      headers: {
        'Content-Type': 'application/json'
      }
    })

    // 4. Xử lý kết quả
    if (response.data.success) {
      console.log("Đăng nhập thành công:", response.data)
      localStorage.setItem('token', response.data.token)
      router.push('/home') // Chuyển hướng sau khi đăng nhập
    } else {
      errors.google = response.data.message || "Đăng nhập thất bại"
    }
    
  } catch (error) {
    console.error("Lỗi đăng nhập Google:", error)
    
    // Phân loại lỗi chi tiết
    if (error.response) {
      // Lỗi từ phía server
      errors.google = error.response.data.detail || "Lỗi server"
    } else if (error.code === 'auth/popup-closed-by-user') {
      errors.google = "Bạn đã đóng cửa sổ đăng nhập"
    } else {
      errors.google = "Lỗi hệ thống, vui lòng thử lại"
    }
  }
}

// Biến lưu tên đăng nhập và mật khẩu
const username = ref("");
const password = ref("");

// Xử lý đăng nhập
const handleLogin = async () => {
  errors.username = username.value ? "" : "Tên đăng nhập không được để trống.";
  errors.password = password.value ? "" : "Mật khẩu không được để trống.";

  if (!username.value || !password.value) {
    alert("⚠️ Vui lòng nhập đầy đủ thông tin!");
    return;
  }

  try {
    const response = await axios.post("/api/auth/login", {
      username: username.value,
      password: password.value
    });

    const { token, user } = response.data;

    localStorage.setItem("token", token);
    localStorage.setItem("user", JSON.stringify(user));

    alert("🎉 Đăng nhập thành công!");

    // ➤ Phân quyền chuyển hướng
    if (user.role === "admin") {
      router.push("/admin"); // Chuyển đến trang admin
    } else {
      router.push("/home"); // Người dùng thường
    }

  } catch (error) {
    console.error("Lỗi:", error);
    if (error.response) {
      alert("⚠️ " + error.response.data.detail);
    } else {
      alert("❌ Lỗi kết nối server");
    }
  }
};


</script>

<style scoped>
.login-page {
  position: relative;
  height: 100vh;
  overflow: hidden;
  background-color: #000;
}

.content {
  position: relative;
  z-index: 1;  /* Nằm trên cùng */
  color: white;
  text-align: left;
  padding-top: 10px;
  margin-left: 20px;
}

.auth-form {
      background-color: rgba(255, 255, 255, 0.1); /* Nền trắng trong suốt */
      border-radius: 10px;
      padding: 20px;
      margin: 20px auto;
      width: 700px; /* Chiều rộng khung đăng nhập */
      box-shadow: 0 4px 10px rgba(0, 0, 0, 0.5);
}
  
.form-group {
  margin-bottom: 15px;
}

.auth-options {
  display: flex;
  align-items: center;
  gap: 10px;
}

label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}
  
input {
  width: 100%;
  padding: 10px;
  border-radius: 5px;
  border: 1px solid #ccc;
}
  
.btn-login {
  width: 100%;
  padding: 10px;
  background-color: #f50057; /* Màu nút đăng nhập */
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}
  
.btn-login:hover {
  background-color: #c51162; /* Màu nền khi hover */
}

.btn-signup {
  background: none;
  color: #007bff;
  text-decoration: underline;
  cursor: pointer;
}

.signup-link {
  margin-top: 10px;
}

h2 {
  text-align: center;
}
</style>