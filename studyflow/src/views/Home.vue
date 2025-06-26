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
          <li class="nav-item"><a class="nav-link active" aria-current="page" href="#">Trang chủ</a></li>
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
                  <a href="#" class="btn btn-sm btn-outline-danger w-100 logout-btn" @click="logout">Đăng xuất</a>
                </div>
              </div>
            </div>
          </div>
        </div>
    </div>

    <!-- Phần thêm chủ đề và danh sách chủ đề -->
    <div class="topic-section">
      <div class="add-topic-container">
        <button class="add-topic-btn" @click="addNewTopic">
          <i class="fas fa-plus-circle"></i> Thêm chủ đề học mới
        </button>

        <button class="add-topic-btn" @click="goToClock">
          <i class="fas fa-plus-circle"></i> Đồng hồ
        </button>
      </div>

      <h2 class="topic-list-title">Danh sách Chủ đề học</h2>

      <div v-if="topics.length === 0" class="empty-topic-message">
        <p>Bạn vẫn chưa có chủ đề học nào! Hãy tạo chủ đề và cùng tôi học nhé!</p>
      </div>

      <div v-for="topic in topics" :key="topic._id" class="accordion-item bg-dark text-white border-0 mb-4 rounded-lg shadow-md overflow-hidden">
        <div class="accordion-header bg-primary px-4 py-3 cursor-pointer d-flex justify-content-between align-items-center" @click="toggleTopic(topic._id)">
          <h5 class="mb-0 text-white">{{ topic.name }}</h5>
          <span class="text-white">{{ activeTopic === topic._id ? '▲' : '▼' }}</span>
        </div>

        <div v-show="activeTopic === topic._id" class="accordion-body bg-dark p-4" style="color: white;">
          <p style="color: white;">{{ topic.description }}</p>

          <div class="d-flex gap-2 mb-3">
            <button class="btn btn-sm btn-outline-info" @click="editTopic(topic)">Sửa</button>
            <button class="btn btn-sm btn-outline-danger" @click="confirmDeleteTopic(topic.id)">Xóa</button>
            <button class="btn btn-sm btn-outline-success" @click="addLesson(topic.id)">Thêm bài học</button>
          </div>

          <ul class="list-group">
            <li v-for="lesson in lessonsMap[topic._id]" :key="lesson._id" class="lesson-card">
              <div>
                <strong>{{ lesson.name }}</strong>
                <p>{{ lesson.note }}</p>
                <span class="badge" :class="lesson.status === 'done' ? 'bg-success' : 'bg-warning text-dark'">
                  {{ lesson.status === 'done' ? 'Đã hoàn thành' : 'Chưa hoàn thành' }}
                </span>
              </div>
              <div class="lesson-actions">
                <div class="btn-group">
                  <button type="button" class="btn btn-outline-success dropdown-toggle" data-bs-toggle="dropdown">
                    Trạng thái
                  </button>
                  <ul class="dropdown-menu">
                    <li><a class="dropdown-item" href="#" @click.prevent="changeStatus(lesson, 'done')">Đã hoàn thành</a></li>
                    <li><a class="dropdown-item" href="#" @click.prevent="changeStatus(lesson, 'chưa hoàn thành')">Chưa hoàn thành</a></li>
                  </ul>
                </div>
                <button class="btn btn-outline-info" @click="editLesson(lesson)">Sửa</button>
                <button class="btn btn-outline-danger" @click="deleteLesson(lesson.id, lesson.topic_id)">Xóa</button>
              </div>
            </li>
          </ul>

          <!-- Form thêm bài học -->
          <div v-if="showAddLessonForm === topic._id" class="bg-secondary p-3 rounded mt-3">
            <div class="mb-2">
              <label class="form-label text-white">Tên bài học:</label>
              <input v-model="newLesson.name" type="text" class="form-control" />
            </div>
            <div class="mb-2">
              <label class="form-label">Ghi chú:</label>
              <input v-model="newLesson.note" type="text" class="form-control" />
            </div>
            <div class="mb-3">
              <label class="form-label text-white">Ngày học dự kiến:</label>
              <input v-model="newLesson.due_date" type="date" class="form-control" />
            </div>
            <div class="d-flex gap-2">
              <button class="btn btn-success btn-sm" @click="submitNewLesson(topic._id)">Lưu</button>
              <button class="btn btn-secondary btn-sm" @click="cancelAddLesson">Hủy</button>
            </div>
          </div>

          <div v-if="!lessonsMap[topic._id]?.length" class=" mt-3" style="color: white;">Không có bài học nào trong chủ đề này.</div>
        </div>
      </div>
    </div>

    
  </div>
</template>

<script setup>
import NeuralNetworkBg from '@/components/NeuralNetworkBg.vue';
import { ref, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';


// Import avatar mặc đinh hệ thống
import defaultAvatar from '../assets/image/Logo_app.png';

const router = useRouter();
const user = ref(null)
const topics = ref([])
const lessonsMap = ref({})
const activeTopic = ref(null)
const loadingTopics = ref(false)
const loadingLessons = ref({})

const showAddLessonForm = ref(null)
const newLesson = ref({
  name: '',
  note: '',
  due_date: ''
})

const addLesson = (topicId) => {
  showAddLessonForm.value = topicId
  newLesson.value = {
    name: '',
    note: '',
    due_date: ''
  }
}

const cancelAddLesson = () => {
  showAddLessonForm.value = null
}

const submitNewLesson = async (topicId) => {
  if (!newLesson.value.name || !newLesson.value.due_date) {
    alert("Vui lòng điền tên và ngày học!");
    return;
  }

  try {
    const res = await fetch(`/api/topics/${topicId}/lessons`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem("token")}`
      },
      body: JSON.stringify({
        name: newLesson.value.name,
        note: newLesson.value.note,
        due_date: newLesson.value.due_date,
        status: 'chưa hoàn thành'
      })
    });

    if (!res.ok) throw new Error("Lỗi khi thêm bài học!");

    await loadLessons(topicId);
    showAddLessonForm.value = null;
    alert("Đã thêm bài học thành công!");

  } catch (err) {
    console.error("❌ Lỗi thêm bài học:", err);
    alert("Thêm bài học thất bại.");
  }
}


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

// Kiểm tra chủ đề đã hoàn thành
const isTopicComplete = (topicId) => {
  const lessons = lessonsMap.value[topicId]
  if (!lessons || !lessons.length) return false
  return lessons.every(lesson => lesson.status === 'done')
}

// Toggle mở/đóng chủ đề
const toggleTopic = async (topicId) => {
  if (activeTopic.value === topicId) {
    activeTopic.value = null
  } else {
    activeTopic.value = topicId
    await fetchLessons(topicId)
  }
}

// Lấy danh sách chủ đề từ API
const fetchTopics = async () => {
  loadingTopics.value = true
  try {
    const token = localStorage.getItem('token')
    const res = await fetch('/api/topics', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    
    if (!res.ok) throw new Error('Lỗi khi lấy danh sách chủ đề')
    const data = await res.json()

    topics.value = data.map(topic => ({
      ...topic,
      id: topic._id  
    }))

  } catch (error) {
    console.error('Error fetching topics:', error)
    toast.error('Lỗi khi tải danh sách chủ đề')
    topics.value = []
  } finally {
    loadingTopics.value = false
  }
}

// Xác nhận xóa chủ đề
const confirmDeleteTopic = async (topicId) => {
  if (confirm('Bạn có chắc muốn xóa chủ đề này? Tất cả bài học trong chủ đề cũng sẽ bị xóa.')) {
    try {
      const token = localStorage.getItem('token')
      const res = await fetch(`/api/topics/${topicId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (!res.ok) throw new Error('Failed to delete topic')
      
      // Cập nhật UI
      topics.value = topics.value.filter(t => t.id !== topicId)
      delete lessonsMap.value[topicId]
      
      if (activeTopic.value === topicId) {
        activeTopic.value = null
      }
      
      toast.success('Đã xóa chủ đề thành công')
    } catch (error) {
      console.error('Error deleting topic:', error)
      toast.error('Có lỗi khi xóa chủ đề')
    }
  }
}

// Sửa chủ đề
const editTopic = async (topic) => {
  const newName = prompt('Nhập tên mới:', topic.name);
  const newDescription = prompt('Nhập mô tả mới:', topic.description);
  if (newName !== null && newDescription !== null) {
    await fetch(`/api/topics/${topic._id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: newName,
        description: newDescription,
        user_id: topic.user_id, 
      }),
    });
    await fetchTopics();
    lessonsMap.value = {};  

  }
};

// Lấy danh sách bài học của từng topic
const fetchLessons = async (topicId) => {
  if (lessonsMap.value[topicId]) return
  
  loadingLessons.value[topicId] = true
  try {
    const token = localStorage.getItem('token')
    const res = await fetch(`/api/topics/${topicId}/lessons`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    
    if (!res.ok) throw new Error(`Failed to fetch lessons for topic ${topicId}`)
    
    const lessons = await res.json()
    lessonsMap.value = {
      ...lessonsMap.value,
      [topicId]: lessons
    }
  } catch (error) {
    console.error(`Error fetching lessons for topic ${topicId}:`, error)
    toast.error('Lỗi khi tải bài học')
    lessonsMap.value[topicId] = []
  } finally {
    loadingLessons.value[topicId] = false
  }
}


// Gọi khi accordion mở ra
watch(topics, () => {
  topics.value.forEach(topic => {
    fetchLessons(topic._id);
  });
});

// Load bài học
const loadLessons = async (topicId) => {
  try {
    const token = localStorage.getItem("token"); // <== THÊM
    const res = await fetch(`/api/topics/${topicId}/lessons`, {
      headers: {
        Authorization: `Bearer ${token}` // <== THÊM
      }
    });

    if (res.ok) {
      const lessons = await res.json();
      lessonsMap.value[topicId] = lessons;
    } else {
      console.error("Không thể tải bài học:", await res.text());
    }
  } catch (err) {
    console.error("Lỗi khi load bài học:", err);
  }
};


// Sửa thông tin bài học
const editLesson = async (lesson) => {
  const newName = prompt("Tên mới:", lesson.name);
  const newNote = prompt("Ghi chú mới:", lesson.note);
  const newDate = prompt("Ngày học dự kiến mới (YYYY-MM-DD):", lesson.due_date);  

  // Tạo object chỉ chứa field thay đổi
  const updateData = {};

  if (newName !== null && newName !== lesson.name) {
    updateData.name = newName.trim();
  }
  if (newNote !== null && newNote !== lesson.note) {
    updateData.note = newNote.trim();
  }
  if (newDate !== null && newDate !== lesson.due_date) {
    updateData.due_date = newDate.trim();
  }

  // Nếu không có gì thay đổi thì bỏ qua
  if (Object.keys(updateData).length === 0) {
    alert("Không có thay đổi nào để cập nhật.");
    return;
  }

  try {
    const response = await fetch(`/api/lessons/${lesson.id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(updateData),
    });

    if (!response.ok) {
      const data = await response.json();
      alert(`Lỗi cập nhật: ${data.detail}`);
    } else {
      alert("Đã cập nhật bài học.");
      await loadLessons(lesson.topic_id);
    }
  } catch (error) {
    console.error("Lỗi khi cập nhật bài học:", error);
    alert("Có lỗi xảy ra khi gửi yêu cầu.");
  }
};

// Xóa bài học
const deleteLesson = async (id, topicId) => {
  if (!id || id === 'undefined') {
    alert("ID bài học không hợp lệ!");
    return;
  }

  if (!topicId || topicId === 'undefined') {
    alert("Chủ đề không hợp lệ!");
    return;
  }

  if (confirm("Xóa bài học này?")) {
    try {
      const res = await fetch(`/api/lessons/${id}`, {
        method: 'DELETE'
      });

      if (!res.ok) {
        const error = await res.json();
        alert("Lỗi: " + error.detail);
      } else {
        await loadLessons(topicId);
        alert("Xóa bài học thành công!");
      }

    } catch (err) {
      console.error("Lỗi khi xóa bài học:", err);
      alert("Xóa bài học thất bại.");
    }
  }
};


// Trạng thái bài học
async function toggleStatus(lesson) {
  const newStatus = lesson.status === "Chưa hoàn thành" ? "Đã hoàn thành" : "Chưa hoàn thành"

  const res = await fetch(`/api/lessons/${lesson.id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ status: newStatus }),
  })

  const result = await res.json()
  if (res.ok) {
    lesson.status = newStatus
  } else {
    alert("Lỗi cập nhật: " + result.detail)
  }
}

const changeStatus = async (lesson, newStatus) => {
  if (lesson.status === newStatus) return; // Không cần cập nhật nếu không thay đổi

  try {
    const response = await fetch(`/api/lessons/${lesson.id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: newStatus }),
    });

    if (response.ok) {
      alert("Cập nhật trạng thái thành công.");
      await loadLessons(lesson.topic_id);  // Cập nhật lại danh sách
    } else {
      const data = await response.json();
      alert(`Lỗi cập nhật trạng thái: ${data.detail}`);
    }
  } catch (err) {
    console.error("Lỗi khi cập nhật trạng thái:", err);
    alert("Có lỗi xảy ra khi cập nhật trạng thái.");
  }
};


onMounted(async () => {
  const userData = await fetchUserProfile();
  if (userData) {
    user.value = userData;
    await fetchTopics(); 
  }
});

// Chuyển trang Thông tin tài khoản
const goToAccountInformation = () => {
  router.push('/accountinformation');
}

// Chuyển trang Thời khóa biểu
const goToTimetable = () => {
  router.push('/timetable');
}

//Chuyển trang Thông báo
const goToNotifications = () => {
  router.push('/notifications');
}

//Chuyển trang Thống kê
const goToUserStats = () => {
  router.push('/userstats');
}

//Chuyển trang Thêm chủ đề
const addNewTopic = () => {
  router.push('/addtopic');
}

// Chuyển trang Đồng hồ
const goToClock = () => {
  router.push('/clock'); 
};


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
  padding-right: 5px; 
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

/* Phần topic section mới */
.topic-section {
  position: relative;
  z-index: 0;
  margin-top: 30px;
  padding: 0 40px;
  width: 95%;
}

.add-topic-container {
  margin-bottom: 20px;
  display: flex;
  justify-content: flex-start;
  padding-left: 0;
  gap: 30px;
}

.add-topic-btn {
  background-color: rgba(255, 255, 255, 0.08);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 30px;
  font-size: 1.1rem;
  font-weight: bold;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 10px;
  transition: all 0.3s ease;
  border: 1px solid white;
}

.add-topic-btn:hover {
  background-color: rgba(255, 255, 255, 0.8);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(112, 112, 112, 0.186)
}

.add-topic-btn i {
  font-size: 1.3rem;
}

.topic-list-title {
  color: white;
  font-size: 1.3em;
  margin-bottom: 20px;
  text-align: left;
  padding-left: 10px;
}


.empty-topic-message {
  text-align: center;
  color: white;
  font-size: 1.2rem;
  padding: 40px;
  background-color: rgba(255, 255, 255, 0.8);
  border-radius: 10px;
  margin-left: -5px; 
  margin-right: -5px;
}


.topic-section {
  width: 100%;
  padding: 10px 40px;
  margin-top: 30px;
  margin-left: 0;
  margin-right: 0;
}

.topic-list-title {
  color: #fff;
  margin: 1.5rem 0;
  font-size: 1.8rem;
  text-align: center;
}


.accordion-header {
  background-color: #1a1f3c;
  cursor: pointer;
  transition: background 0.3s ease;
  border-radius: 8px 8px 0 0;
}

.accordion-header:hover {
  background-color: rgba(255, 255, 255, 0.08);
}

.accordion-body {
  background-color: #20283e;
  border-radius: 0 0 8px 8px;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-5px); }
  to { opacity: 1; transform: translateY(0); }
}

.lesson-card {
  background-color: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  padding: 10px 15px;
  margin-bottom: 10px;
  color: #fff;
}

.lesson-actions {
  display: flex;
  gap: 10px;
  margin-top: 10px;
  flex-wrap: wrap;
}

.bg-primary {
  --bs-bg-opacity: 1;
  background-color: rgba(255, 255, 255, 0.1) !important;
}

</style>