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
        <li class="nav-item"><a class="nav-link active" aria-current="page" href="#" @click="goToAdminStats">Thống kê</a></li>
        <li class="nav-item"><a class="nav-link" href="#" @click="goToAdminReminder">Cài đặt</a></li>
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


      <!-- Phần thống kê hệ thống -->
      <div class="stats-container">
        <h2 class="stats-title">Thống kê hệ thống</h2>
        
        <div class="stats-grid">
          <!-- Tổng số người dùng -->
          <div class="stat-card">
            <div class="stat-value">{{ formatNumber(stats.total_users) }}</div>
            <div class="stat-label">Tổng người dùng</div>
          </div>
          
          <!-- Tổng số giờ học -->
          <div class="stat-card">
            <div class="stat-value">{{ formatHours(stats.total_hours) }}</div>
            <div class="stat-label">Tổng giờ học</div>
          </div>
          
          <!-- Bài học hoàn thành -->
          <div class="stat-card">
            <div class="stat-value">{{ formatNumber(stats.total_completed_lessons) }}</div>
            <div class="stat-label">Bài học hoàn thành</div>
          </div>
          
          <!-- Mức độ hoạt động -->
          <div class="stat-card">
            <div class="stat-value">{{ stats.active_level.daily_avg }} <small>/ngày</small></div>
            <div class="stat-label">Hoạt động trung bình</div>
            <div class="stat-subvalue">{{ stats.active_level.weekly_avg }} <small>/tuần</small></div>
          </div>
        </div>
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
const stats = ref({
  total_users: 0,
  total_hours: 0,
  total_completed_lessons: 0,
  active_level: {
    daily_avg: 0,
    weekly_avg: 0
  }
});

const dropdownOpen = ref(false)
function toggleDropdown() {
  dropdownOpen.value = !dropdownOpen.value
}

// Thông tin admin
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
    router.push("/login"); // Nếu lỗi, quay về login
  }
};


// Hàm lấy thống kê từ API
const fetchStatistics = async () => {
  try {
    const token = localStorage.getItem("token");
    if (!token) throw new Error("Token không tồn tại");

    // Tổng số người dùng
    const usersRes = await fetch("/api/admin/statistics/users", {
      headers: { Authorization: `Bearer ${token}` }
    });
    const usersData = await usersRes.json();
    
    // Tổng số giờ học
    const hoursRes = await fetch("/api/admin/statistics/hours", {
      headers: { Authorization: `Bearer ${token}` }
    });
    const hoursData = await hoursRes.json();
    
    // Tổng số bài học hoàn thành
    const lessonsRes = await fetch("/api/admin/statistics/lessons", {
      headers: { Authorization: `Bearer ${token}` }
    });
    const lessonsData = await lessonsRes.json();
    
    // Mức độ hoạt động
    const activityRes = await fetch("/api/admin/statistics/active-level", {
      headers: { Authorization: `Bearer ${token}` }
    });
    const activityData = await activityRes.json();

    // Cập nhật dữ liệu thống kê
    stats.value = {
      total_users: usersData.total_users || 0,
      total_hours: hoursData.total_hours || 0,
      total_completed_lessons: lessonsData.total_completed_lessons || 0,
      active_level: activityData || { daily_avg: 0, weekly_avg: 0 }
    };

  } catch (error) {
    console.error("Lỗi khi lấy thống kê:", error);
    alert("Không thể tải dữ liệu thống kê");
  }
};

// Định dạng số
const formatNumber = (num) => {
  return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
};

// Định dạng giờ
const formatHours = (hours) => {
  const h = Math.floor(hours);
  const m = Math.floor((hours - h) * 60);
  return `${h}h ${m}m`;
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
    await fetchStatistics();

  } catch (error) {
    console.error("Lỗi khi khởi tạo:", error);
    router.push("/login");
  }
});


// Chuyển trang Quản lý người dùng
const goToAdminUserList = () => {
  router.push('/adminuserlist');
}

//Chuyển trang Cài đặt
const goToAdminReminder = () => {
  router.push('/adminreminders');
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
  z-index: 1;  
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
  padding-right: 40px; 
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


.stats-container {
  position: absolute;
  padding: 100px;
  top: 100px;
  color: white;
  align-items: center;
  justify-content: center;
  min-height: 50vh;
  box-sizing: border-box;
  flex-direction: column;
  display: flex;
}

.stats-title {
  text-align: center;
  margin-bottom: 40px;
  font-size: 2.5rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
}

.stat-card {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 15px;
  padding: 20px;
  text-align: center;
  transition: transform 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-5px);
  background: rgba(255, 255, 255, 0.15);
}

.stat-value {
  font-size: 2.5rem;
  font-weight: bold;
  margin-bottom: 10px;
}

.stat-value small {
  font-size: 1rem;
  opacity: 0.8;
}

.stat-label {
  font-size: 1.5rem;
  opacity: 0.9;
}

.stat-subvalue {
  margin-top: 10px;
  font-size: 1.2rem;
  opacity: 0.8;
}
</style>