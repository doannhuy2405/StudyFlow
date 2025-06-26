<template>
  <div class="addtopic-page">
    
    <!-- Component mạng nơ-ron chồng lên -->
    <NeuralNetworkBg />

    <!-- Content chính -->
    <div class="content">
        <div class="header-bar">
            <!-- Bên trái -->
            <div class="left">
                <img src="../assets//image/icon.png" alt="logo" class="logo" />
                <h1 style="font-size: 4em;">StudyFlow</h1>
            </div>

            <!-- Giữa -->
            <ul class="nav nav-tabs center-nav">
                <li class="nav-item"><a class="nav-link" href="#" @click="goToHome">Trang chủ</a></li>
                <li class="nav-item"><a class="nav-link" href="#" @click="goToUserStats">Thống kê</a></li>
                <li class="nav-item"><a class="nav-link" href="#" @click="goToTimetable">Thời khóa biểu</a></li>
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


      <div class="topic-container">
        <div class="topic-form">
            <h2 class="form-title">Thêm Chủ Đề Học</h2>

            <!-- Form nhập tên & mô tả -->
            <div class="form-group">
            <label class="form-label">Tên chủ đề</label>
            <input 
                v-model="topic.name" 
                class="form-control" 
                placeholder="VD: Lập trình Python" 
            />
            </div>

            <div class="form-group">
            <label class="form-label">Mô tả chủ đề</label>
            <textarea 
                v-model="topic.description" 
                class="form-control" 
                placeholder="VD: Những kiến thức cơ bản về Python..."
                rows="3"
            ></textarea>
            </div>

            <!-- Form danh sách bài học -->
            <h5 class="lessons-title">Danh sách bài học</h5>
            <div 
            v-for="(lesson, index) in topic.lessons" 
            :key="index" 
            class="lesson-item"
            >
            <input
                v-model="lesson.name"
                class="form-control lesson-input"
                placeholder="Tên bài học"
            />
            <button class="remove-btn" @click="removeLesson(index)">
                <i class="fas fa-times"></i>
            </button>
            </div>

            <button class="add-lesson-btn" @click="addLesson">
            <i class="fas fa-plus"></i> Thêm bài học
            </button>

            <button class="submit-btn" @click="submitTopic">
            Tạo chủ đề
            </button>
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

const dropdownOpen = ref(false)
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

const topic = ref({
  name: '',
  description: '',
  user_id: '',       
  lessons: [],
});


const user_id = JSON.parse(localStorage.getItem("user"))?.id;

// Thêm một bài học mới
const addLesson = () => {
  topic.value.lessons.push({
    name: '',
    note: '',
    due_date: '',
    status: 'Chưa hoàn thành',
  });
};


// Xóa một bài học theo index
const removeLesson = (index) => {
  topic.value.lessons.splice(index, 1);
};

// Gửi dữ liệu lên backend
const submitTopic = async () => {
  const currentUser = JSON.parse(localStorage.getItem("user"));
  const user_id = currentUser?.id;

  if (!user_id) {
    alert("Không tìm thấy thông tin người dùng.");
    return;
  }

  if (!topic.value.name.trim()) {
    alert("Vui lòng nhập tên chủ đề");
    return;
  }

  if (topic.value.lessons.length === 0 || topic.value.lessons.some(l => !l.name.trim())) {
    alert("Vui lòng nhập đầy đủ tên các bài học");
    return;
  }

  const payload = {
    user_id,
    name: topic.value.name,
    description: topic.value.description,
    lessons: topic.value.lessons,
  };

  const res = await fetch("/api/topics", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${localStorage.getItem("token")}`
    },
    body: JSON.stringify(payload),
  });


  if (res.ok) {
    alert("Tạo chủ đề thành công!");
    router.push("/home");
  } else {
    const err = await res.json();
    alert(`Lỗi khi tạo chủ đề: ${err.detail || "Không rõ"}`);
  }
};



onMounted(async () => {
  const userData = await fetchUserProfile();
  if (userData) {
    user.value = userData;
    topic.value.user_id = userData.id; 
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

//Chuyển trang Thống kê
const goToUserStats = () => {
  router.push('/userstats');
}

// Đăng xuất
const logout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    router.push("/");
};

</script>

<style scoped>
.addtopic-page {
  position: relative;
  min-height: 100vh;
  overflow-x: hidden;
  background-color: #000;
}

.content {
  position: relative;
  z-index: 1;  
  color: white;
  align-items: center;
  display: flex;
  justify-content: space-between;
  gap: 30px;
  flex-direction: column;
}

.header-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  padding: 10px 40px;
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
  background-color: rgba(255,255,255,0.1);
  border-radius: 8px;
}

.left {
  display: flex;
  align-items: center;
  gap: 15px;
}

.center-nav {
  display: flex;
  gap: 5px;
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

.topic-container {
  position: relative;
  z-index: 0;
  display: flex;
  justify-content: center;
  padding: 40px 20px;
  width: 900px;
  flex-direction: column;
  margin: 0 auto;
}

.topic-form {
  width: 100%;
  max-width: 800px;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 15px;
  padding: 30px;
  box-shadow: 0 4px 20px rgba(255, 255, 255, 0.1);
}

.form-title {
  color: white;
  text-align: center;
  margin-bottom: 25px;
  font-size: 1.8rem;
}

.form-group {
  margin-bottom: 20px;
}

.form-label {
  display: block;

  margin-bottom: 8px;
  font-weight: 500;
}

.form-control {
  width: 100%;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  padding: 12px 15px;
  font-size: 1rem;
  transition: all 0.3s ease;
}

.form-control:focus {
  outline: none;
  border-color: #4ecca3;
  box-shadow: 0 0 0 2px rgba(78, 204, 163, 0.2);
}

textarea.form-control {
  min-height: 100px;
  resize: vertical;
}

.lessons-title {
  color: white;
  margin: 25px 0 15px;
  font-size: 1.2rem;
}

.lesson-item {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.lesson-input {
  flex: 1;
}

.remove-btn {
  background: rgba(255, 99, 71, 0.2);
  border: none;
  color: tomato;
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.remove-btn:hover {
  background: rgba(255, 99, 71, 0.3);
}

.add-lesson-btn {
  background: rgba(78, 204, 163, 0.2);
  border: 1px dashed rgba(78, 204, 163, 0.5);
  color: #4ecca3;
  width: 100%;
  padding: 10px;
  border-radius: 8px;
  margin-top: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.add-lesson-btn:hover {
  background: rgba(78, 204, 163, 0.3);
}

.submit-btn {
  background: #4ecca3;
  color: white;
  border: none;
  width: 100%;
  padding: 12px;
  border-radius: 8px;
  margin-top: 25px;
  font-weight: bold;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.submit-btn:hover {
  background: #3db389;
  transform: translateY(-2px);
}


@media (max-width: 768px) {
  .topic-form {
    padding: 20px;
  }
  
  .form-title {
    font-size: 1.5rem;
  }
}

</style>