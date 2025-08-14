<template>
  <div class="home-page">
    
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
        <li class="nav-item"><a class="nav-link" href="#" @click="goToHome">Trang chủ</a></li>
        <li class="nav-item"><a class="nav-link active" aria-current="page" href="#">Thống kê</a></li>
        <li class="nav-item"><a class="nav-link " href="#" @click="goToTimetable">Thời khóa biểu</a></li>
        <li class="nav-item"><a class="nav-link" href="#" @click="goToNotifications">Thông báo</a></li>
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
                <a href="#" class="btn btn-sm btn-primary w-100 mb-1" @click="goToAccountInformation">Thông tin tài khoản</a>
                <a href="#" class="btn btn-sm btn-outline-danger w-100" @click="logout">Đăng xuất</a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="statistics-container mt-5 px-5" style="color: white;">
      <h2>Thống kê học tập</h2>

      <div class="row mt-4">
        <div class="col-md-3">
          <div class="card bg-dark text-white p-3">
            <h5>Tổng giờ học</h5>
            <p class="fs-4">{{ summary?.total_hours ?? '—' }} giờ</p>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card bg-dark text-white p-3">
            <h5>Số bài học đã hoàn thành</h5>
            <p class="fs-4">{{ summary?.completed_lessons ?? '—' }}</p>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card bg-dark text-white p-3">
            <h5>Chủ đề đã hoàn thành</h5>
            <p class="fs-4">{{ summary?.completed_topics ?? '—' }}</p>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card bg-dark text-white p-3">
            <h5>Chuỗi streak</h5>
            <p class="fs-4">{{ summary?.streak ?? '—' }} ngày</p>
          </div>
        </div>
      </div>

      <div class="card mt-4 bg-dark p-4">
        <h5 class="text-white">Biểu đồ thời gian học</h5>
        <Line :data="chartData" :options="{ responsive: true, plugins: { legend: { display: true } } }" />
      </div>
    </div>
  </div>
</template>

<script setup>
import NeuralNetworkBg from '@/components/NeuralNetworkBg.vue';
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { Line } from 'vue-chartjs';
import {
  Chart as ChartJS, Title, Tooltip, Legend, LineElement, CategoryScale, LinearScale, PointElement
} from 'chart.js';

// Import avatar mặc đinh hệ thống
import defaultAvatar from '../assets/image/Logo_app.png';

ChartJS.register(Title, Tooltip, Legend, LineElement, CategoryScale, LinearScale, PointElement);

const user = ref(null);
const summary = ref(null);
const graphData = ref([]);
const router = useRouter();

const dropdownOpen = ref(false)
// eslint-disable-next-line no-unused-vars
function toggleDropdown() {
  dropdownOpen.value = !dropdownOpen.value
}

// Lấy thông tin người dùng
const fetchUserProfile = async () => {
  try {
    const token = localStorage.getItem("token"); // Lấy token từ localStorage
    if (!token) {
      throw new Error("Token không tồn tại");
    }

    const response = await fetch("/api/auth/profile", {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`, // Gửi token trong header
      },
    });

    console.log("Response từ API:", response); // Debug

    if (!response.ok) {
      throw new Error(`Lỗi HTTP: ${response.status}`);
    }

    const data = await response.json();
    console.log("Thông tin người dùng:", data);
    return data;
  } catch (error) {
    console.error("Lỗi khi lấy thông tin người dùng:", error);
    return null;
  }
};


const fetchStatisticsSummary = async () => {
  const token = localStorage.getItem("token");
  const res = await fetch("/api/statistics/user/summary", {
    headers: { Authorization: `Bearer ${token}` }
  });
  summary.value = await res.json();
};

const fetchStatisticsGraph = async () => {
  const token = localStorage.getItem("token");
  const res = await fetch("/api/statistics/user/graph", {
    headers: { Authorization: `Bearer ${token}` }
  });
  graphData.value = await res.json();
};

const chartData = computed(() => ({
  labels: graphData.value.map(item => item.date),
  datasets: [{
    label: 'Phút học mỗi ngày',
    data: graphData.value.map(item => item.minutes),
    borderColor: 'rgba(75, 192, 192, 1)',
    backgroundColor: 'rgba(75, 192, 192, 0.2)',
    tension: 0.3
  }]
}));


onMounted(async () => {
  const userData = await fetchUserProfile();
  if (userData) {
    user.value = userData;
    await fetchStatisticsSummary();
    await fetchStatisticsGraph();
  }
});


//Chuyển trang Thông báo
const goToNotifications = () => {
  router.push('/notifications');
}

// Chuyển trang Thông tin tài khoản
const goToAccountInformation = () => {
  router.push('/accountinformation');
}

// Chuyển trang Trang chủ
const goToHome = () => {
  router.push('/home');
}

//Chuyển trang Thời khóa biểu
const goToTimetable = () => {
  router.push('/timetable');
}

// Đăng xuất
const logout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    router.push("/");
  };
</script>

<style scoped>
.home-page {
  position: relative;
  height: 100vh;
  overflow-x: hidden;
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
  gap: 15px;
  list-style: none;
  padding: 0;
  margin: 0;
}

.right {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  flex: 1;
  padding-right: 5px; /* canh khoảng cách với mép phải */
  gap: 15px;
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

</style>