<template>
  <div class="admin-page">
    
    <!-- Component mạng nơ-ron chồng lên -->
    <NeuralNetworkBg />

    <!-- Content chính -->
    <div class="content">
      <!-- Bên trái -->
      <div class="left">
        <img src="../assets//image/icon.png" alt="logo" class="logo" />
        <h1 style="font-size: 4em;">StudyFlow</h1>
      </div>

      <!-- Giữa -->
      <ul class="nav nav-tabs center-nav">
        <li class="nav-item"><a class="nav-link" href="#" @click="goToAdminUserList">Quản lý người dùng</a></li>
        <li class="nav-item"><a class="nav-link" href="#" @click="goToAdminStats">Thống kê</a></li>
        <li class="nav-item"><a class="nav-link active" aria-current="page" href="#" @click="goToAdminReminder">Cài đặt</a></li>
      </ul>
      
      <!-- Phải -->
       <div class="right">
        <div class="dropdown text-end">
          <button
            class="btn p-0 border-0 bg-transparent d-flex align-items-center gap-2"
            type="button"
            data-bs-toggle="dropdown"
            aria-expanded="false"
          >
            <!-- Avatar -->
            <img :src= "user?.photo || defaultAvatar" alt="avatar" class="avatar" />
            <!-- Tên hiển thị -->
            <span class="username">{{ user?.fullname }}</span>
          </button>

          <!-- Dropdown nội dung -->
          <div class="dropdown-menu dropdown-menu-end p-2" style="width: 220px;">
            <div class="card border-0 text-center bg-dark text-white">
              <img
                :src= "user?.photo || defaultAvatar"
                class="card-img-top rounded-circle mx-auto mt-2"
                style="width: 60px; height: 60px; object-fit: cover;"
                alt="avatar"
              />
              <div class="card-body p-2">
                <h6 class="card-title mb-1">{{user?.fullname}}</h6>
                <p class="card-text" style="font-size: 0.8em;">{{ user?.email }}</p>
                <a href="#" class="btn btn-sm btn-outline-danger w-100" @click="logout">Đăng xuất</a>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="reminder-box">
        <h2 class="reminder-title">⏰ Cài đặt giờ nhắc mặc định</h2>

        <div class="form-group">
          <label for="reminder-time">Chọn giờ nhắc:</label>
          <input
            id="reminder-time"
            type="time"
            v-model="reminderTime"
            class="form-control time-input"
          />
        </div>

        <button class="btn btn-outline-light mt-3" @click="saveReminder">Lưu cài đặt</button>

        <p v-if="successMsg" class="text-success mt-3">{{ successMsg }}</p>
        <p v-if="errorMsg" class="text-danger mt-3">{{ errorMsg }}</p>
      </div>

    </div>
  </div>
</template>

<script setup>
import NeuralNetworkBg from '@/components/NeuralNetworkBg.vue';
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';

// Import avatar mặc đinh hệ thống
import defaultAvatar from '../assets/image/Logo_app.png';

const router = useRouter();
const user = ref(null);
const reminderTime = ref('');
const successMsg = ref('');
const errorMsg = ref('');


// Lấy thông tin admin
const fetchAdminProfile = async () => {
  try {
    const token = localStorage.getItem("token");
    const response = await fetch("/api/auth/admin/profile", {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data; 
  } catch (error) {
    console.error("Error fetching admin profile:", error);
    router.push("/login"); 
  }
};

const saveReminder = async () => {
  successMsg.value = '';
  errorMsg.value = '';

  const token = localStorage.getItem("token"); 

  try {
    const res = await fetch('/api/admin/reminder/default', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}` 
      },
      body: JSON.stringify({ time: reminderTime.value })
    });

    const result = await res.json();

    if (res.ok) {
      successMsg.value = '✅ Cập nhật giờ nhắc thành công!';
    } else {
      errorMsg.value = result?.msg || '❌ Lỗi khi cập nhật.';
    }
  } catch (error) {
    console.error("❌ Lỗi khi gửi request:", error);
    errorMsg.value = '❌ Gặp lỗi khi gửi dữ liệu.';
  }
};


// Khởi tạo
onMounted(async () => {
  const token = localStorage.getItem("token");
  if (!token) {
    router.push("/login");
    return;
  }
  try {
    const adminData = await fetchAdminProfile();

    if (!adminData) {
      router.push("/login");
      return;
    }
    user.value = adminData;
    try {
      const res = await fetch('/api/admin/reminder/default', {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      const data = await res.json();
      if (data?.time) {
        reminderTime.value = data.time;
      }
    // eslint-disable-next-line no-unused-vars
    } catch (error) {
      errorMsg.value = 'Không thể tải giờ nhắc.';
    }
  } catch (error) {
    console.error("Lỗi khi khởi tạo:", error);
  }
});


// Chuyển trang Quản lý người dùng
const goToAdminUserList = () => {
  router.push('/adminuserlist');
}

//Chuyển trang Thống kê
const goToAdminStats = () => {
  router.push('/adminstats');
}

// Đăng xuất
const logout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    router.push("/");
};

</script>

<style scoped>
.admin-page {
  position: relative;
  height: 100vh;
  overflow: hidden;
  background-color: #000;
}

.content {
  position: relative;
  z-index: 1;  /* Nằm trên cùng */
  color: white;
  align-items: center;
  padding-top: 5px;
  display: flex;
  justify-content: space-between;
  gap: 30px;
}


.logo-title {
  display: flex;
  align-items: center;
  gap: 20px;
}

.logo-title h1 {
  margin: 0px;

}

.logo {
  height: 120px;
}


.nav-tabs {
  display: flex;
  gap: 20px;
  margin-bottom: 0;
  padding-left: 0;
  list-style: none;
}

.nav-link {
  color: white;
  font-weight: bold;
  font-size: 1.1em;
  text-decoration: none;
}

.nav-link:hover {
  background-color: rgba(208, 204, 204, 0.844);
  border-radius: 8px;
}

.left {
  display: flex;
  align-items: center;
  gap: 15px;
}

.center-nav {
  display: flex;
  gap: 25px;
  list-style: none;
  padding: 0;
  margin: 0;
}

.right {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  flex: 1;
  padding-right: 40px; /* canh khoảng cách với mép phải */
}

 .avatar {
  height: 50px;
  width: 50px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid white;
}

.username {
  font-weight: bold;
  color: white;
  font-size: 1rem;
}

.dropdown-menu {
  z-index: 1000;
  border-radius: 10px;
  overflow: hidden;
}

.reminder-box {
  margin: 0 auto;
  left: 50%;
  margin-top: 900px;
  transform: translate(-50%, -50%);
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(10px);
  padding: 50px;
  border-radius: 20px;
  width: 400px;
  text-align: center;
  color: white;
  position: absolute;
  box-shadow: 0 0 15px rgba(255, 255, 255, 0.2);
  z-index: 1;
}

.reminder-title {
  font-size: 1.8em;
  margin-bottom: 20px;
}

.time-input {
  padding: 10px;
  font-size: 1em;
  border-radius: 10px;
  width: 100%;
  border: none;
  background-color: rgba(255, 255, 255, 0.2);
  color: white;
}

</style>