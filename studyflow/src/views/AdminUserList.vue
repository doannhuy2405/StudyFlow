<template>
  <div class="home-page">
    <!-- Component mạng nơ-ron chồng lên -->
    <NeuralNetworkBg />

    <!-- Content chính -->
    <div class="content">
      <!-- Bên trái -->
      <div class="left">
        <img src="../assets/image/icon.png" alt="logo" class="logo" />
        <h1 style="font-size: 4em;">StudyFlow</h1>
      </div>

      <!-- Giữa -->
      <ul class="nav nav-tabs center-nav">
        <li class="nav-item"><a class="nav-link active" aria-current="page" @click="goToAdminUserList" href="#">Quản lý người dùng</a></li>
        <li class="nav-item"><a class="nav-link" @click="goToAdminStats" href="#" >Thống kê</a></li>
        <li class="nav-item"><a class="nav-link" @click="goToAdminReminder" href="#" >Cài đặt</a></li>
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
            <img :src="user?.photo || defaultAvatar" alt="avatar" class="avatar" />
            <!-- Tên hiển thị -->
            <span class="username">{{ user?.fullname }}</span>
          </button>

          <!-- Dropdown nội dung -->
          <div class="dropdown-menu dropdown-menu-end p-2" style="width: 220px;">
            <div class="card border-0 text-center bg-dark text-white">
              <img
                :src="user?.photo || defaultAvatar"
                class="card-img-top rounded-circle mx-auto mt-2"
                style="width: 60px; height: 60px; object-fit: cover;"
                alt="avatar"
              />
              <div class="card-body p-2">
                <h6 class="card-title mb-1">{{ user?.fullname }}</h6>
                <p class="card-text" style="font-size: 0.8em;">{{ user?.email }}</p>
                <a href="#" class="btn btn-sm btn-outline-danger w-100" @click="logout">Đăng xuất</a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Phần quản lý người dùng -->
    <div class="user-management-container">
      <div class="user-management-header">
        <h2>Danh sách người dùng</h2>
        <button class="add-user-btn" @click="showAddUserModal = true">
          <i class="bi bi-plus-circle"></i> Thêm người dùng
        </button>
      </div>

      <div class="user-management-toolbar">
        <div class="search-box">
          <i class="bi bi-search"></i>
          <input 
            v-model="searchQuery" 
            type="text" 
            placeholder="Tìm kiếm người dùng..."
          >
        </div>
        <select v-model="statusFilter" class="status-filter">
          <option value="all">Tất cả trạng thái</option>
          <option value="active">Đang hoạt động</option>
          <option value="locked">Đã khóa</option>
        </select>
      </div>

      <div class="user-table-container">
        <table class="user-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Thông tin</th>
              <th>Tên đăng nhập</th>
              <th>Trạng thái</th>
              <th>Hành động</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in filteredUsers" :key="user._id">
              <td class="user-id">{{ user._id }}</td>
              <td class="user-info">
                <img :src="user.photo || defaultAvatar" class="user-avatar">
                <div class="user-details">
                  <div class="user-name">{{ user.fullname }}</div>
                  <div class="user-email">{{ user.email }}</div>
                </div>
              </td>
              <td class="user-username">@{{ user.username }}</td>
              <td>
                <span :class="['status-badge', user.locked ? 'locked' : 'active']">
                  {{ user.locked ? 'Đã khóa' : 'Hoạt động' }}
                </span>
              </td>
              <td class="user-actions">
                <button 
                  v-if="user.locked" 
                  @click="unlockUser(user._id)" 
                  class="action-btn unlock-btn"
                  title="Mở khóa tài khoản"
                >
                  <i class="bi bi-unlock"></i>
                </button>
                <button 
                  v-else 
                  @click="lockUser(user._id)" 
                  class="action-btn lock-btn"
                  title="Khóa tài khoản"
                >
                  <i class="bi bi-lock"></i>
                </button>
                <button 
                  @click="confirmDelete(user._id)" 
                  class="action-btn delete-btn"
                  title="Xóa người dùng"
                >
                  <i class="bi bi-trash"></i>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Modal thêm người dùng -->
      <div v-if="showAddUserModal" class="user-modal">
        <div class="modal-content">
          <div class="modal-header">
            <h3>Thêm người dùng mới</h3>
            <button @click="showAddUserModal = false" class="close-btn">
              <i class="bi bi-x"></i>
            </button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="addUser">
              <div class="form-group">
                <label>Tên đầy đủ</label>
                <input v-model="newUser.fullname" type="text" required>
              </div>
              <div class="form-group">
                <label>Email</label>
                <input v-model="newUser.email" type="email" required>
              </div>
              <div class="form-group">
                <label>Username</label>
                <input v-model="newUser.username" type="text" required>
              </div>
              <div class="form-group">
                <label>Mật khẩu</label>
                <input v-model="newUser.password" type="password" required>
              </div>
              <div class="modal-footer">
                <button type="button" @click="showAddUserModal = false" class="btn-cancel">
                  Hủy bỏ
                </button>
                <button type="submit" class="btn-submit">
                  Thêm người dùng
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>

      <!-- Modal xác nhận xóa -->
      <div v-if="showDeleteModal" class="user-modal">
        <div class="modal-content confirm-modal">
          <div class="modal-header">
            <h3>Xác nhận xóa</h3>
            <button @click="showDeleteModal = false" class="close-btn">
              <i class="bi bi-x"></i>
            </button>
          </div>
          <div class="modal-body">
            <p>Bạn có chắc chắn muốn xóa người dùng này?</p>
            <p class="warning-text">Hành động này không thể hoàn tác!</p>
          </div>
          <div class="modal-footer">
            <button @click="showDeleteModal = false" class="btn-cancel">
              Hủy bỏ
            </button>
            <button @click="deleteUser" class="btn-delete">
              Xác nhận xóa
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import NeuralNetworkBg from '@/components/NeuralNetworkBg.vue';
import defaultAvatar from '@/assets/image/Logo_app.png';

const router = useRouter();
const users = ref ([])
const user = ref(null);
const dropdownOpen = ref(false);

const lockUser = (userId) => toggleUserLock(userId, true);
const unlockUser = (userId) => toggleUserLock(userId, false);


// Data cho quản lý người dùng
const searchQuery = ref('')
const statusFilter = ref('all')
const showAddUserModal = ref(false)
const showDeleteModal = ref(false)
const selectedUserId = ref(null)

const newUser = ref({
  fullname: '',
  email: '',
  username: '',
  password: ''
});

// Computed
const filteredUsers = computed(() => {
  let result = users.value;
  
  if (statusFilter.value !== 'all') {
    result = result.filter(user => 
      statusFilter.value === 'active' ? !user.locked : user.locked
    );
  }
  
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase();
    result = result.filter(user => 
      user.fullname.toLowerCase().includes(query) || 
      user.email.toLowerCase().includes(query) ||
      user.username.toLowerCase().includes(query)
    );
  }
  
  return result;
});

// Hàm cho admin
const toggleDropdown = () => {
  dropdownOpen.value = !dropdownOpen.value;
};

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
    return data; // ✅ thêm dòng này
  } catch (error) {
    console.error("Error fetching admin profile:", error);
    router.push("/login"); // Nếu lỗi, quay về login
  }
};


// Hàm lấy thông tin người dùng
const fetchUsers = async () => {
  try {
    const token = localStorage.getItem('token');
    console.log("Token:", token); // Debug token

    if (!token) {
      alert("Token không tồn tại. Vui lòng đăng nhập lại.");
      return;
    }

    const response = await fetch('/api/admin/users', {  // Sửa URL
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,  // Đảm bảo đúng định dạng Bearer
        'Content-Type': 'application/json'
      }
    });

    console.log("Response status:", response.status); // Debug status

    if (!response.ok) {
      const errorText = await response.text();
      console.error("Error response:", errorText); // Log toàn bộ response
      throw new Error(errorText || 'Request failed');
    }

    const data = await response.json();
    console.log("Data received:", data); // Debug data
    users.value = data;

  } catch (error) {
    console.error("Full error:", error);
    alert(`Lỗi: ${error.message}`);
  }
};


// Hàm thêm người dùng thủ công
const addUser = async () => {
  try {
    const token = localStorage.getItem('token');
    const response = await fetch('/api/admin/users', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(newUser.value)
    });
    
    if (!response.ok) throw new Error('Thêm người dùng thất bại');
    
    showAddUserModal.value = false;
    newUser.value = { fullname: '', email: '', username: '', password: '' };
    await fetchUsers();
  } catch (error) {
    console.error('Lỗi khi thêm người dùng:', error);
    alert(error.message);
  }
};

const confirmDelete = (userId) => {
  selectedUserId.value = userId;
  showDeleteModal.value = true;
};

// Hàm xóa người dùng
const deleteUser = async () => {
  try {
    const token = localStorage.getItem('token');
    const response = await fetch(`/api/admin/users/${selectedUserId.value}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });

    if (!response.ok) throw new Error('Xóa người dùng thất bại');

    showDeleteModal.value = false;
    await fetchUsers();
  } catch (error) {
    console.error('Lỗi khi xóa người dùng:', error);
    alert(error.message);
  }
};


const toggleUserLock = async (userId, shouldLock) => {
  try {
    const token = localStorage.getItem('token');
    const endpoint = shouldLock ? 'lock' : 'unlock';
    const response = await fetch(`/api/admin/users/${userId}/${endpoint}`, {
      method: 'PATCH',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    if (!response.ok) throw new Error(shouldLock ? 'Khóa tài khoản thất bại' : 'Mở khóa tài khoản thất bại');
    
    await fetchUsers();
  } catch (error) {
    console.error('Lỗi khi thay đổi trạng thái tài khoản:', error);
    alert(error.message);
  }
};

// Chuyển trang Quản lý người dùng
const goToAdminUserList = () => {
  router.push('/adminuserlist');
}

//Chuyển trang Thống kê
const goToAdminStats = () => {
  router.push('/adminstats');
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
    await fetchUsers();
  } catch (error) {
    console.error("Lỗi khi khởi tạo:", error);
    router.push("/login");
  }
});


</script>

<style scoped>
/* Giữ nguyên các style hiện có */
.home-page {
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
  z-index: 1;
  border-radius: 10px;
  overflow: hidden;
}

/* Style mới cho phần quản lý người dùng */
.user-management-container {
  position: absolute;
  top: 120px;
  left: 0;
  right: 0;
  bottom: 0;
  padding: 20px;
  overflow-y: auto;
  z-index: 0;
}

.user-management-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 0 20px;
}

.user-management-header h2 {
  color: white;
  margin: 0;
}

.add-user-btn {
  background: linear-gradient(135deg, #6e8efb, #a777e3);
  border: none;
  color: white;
  padding: 10px 20px;
  border-radius: 50px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.add-user-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(167, 119, 227, 0.3);
}

.user-management-toolbar {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
  padding: 0 20px;
}

.search-box {
  position: relative;
  width: 300px;
}

.search-box i {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #a6b0cf;
}

.search-box input {
  width: 100%;
  padding: 10px 15px 10px 40px;
  background-color: #1a2035;
  border: 1px solid #2d3653;
  border-radius: 50px;
  color: white;
  outline: none;
}

.status-filter {
  background-color: #1a2035;
  border: 1px solid #2d3653;
  color: white;
  border-radius: 50px;
  padding: 10px 15px;
  min-width: 200px;
}

.user-table-container {
  background-color: #1a2035;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  margin: 0 20px;
}

.user-table {
  width: 100%;
  border-collapse: collapse;
}

.user-table th {
  background-color: #252d47;
  padding: 15px;
  text-align: left;
  font-weight: 600;
  color: #a6b0cf;
}

.user-table td {
  padding: 15px;
  border-bottom: 1px solid #2d3653;
}

.user-table tr:last-child td {
  border-bottom: none;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-avatar {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid #3a4568;
}

.user-details {
  display: flex;
  flex-direction: column;
}

.user-name {
  font-weight: 600;
  margin-bottom: 5px;
}

.user-email {
  font-size: 0.85rem;
  color: #a6b0cf;
}

.user-id {
  color: #a6b0cf;
  font-family: monospace;
  font-size: 0.85rem;
}

.user-username {
  font-weight: 500;
  color: #6e8efb;
}

.status-badge {
  display: inline-block;
  padding: 5px 12px;
  border-radius: 50px;
  font-size: 0.85rem;
  font-weight: 500;
}

.status-badge.active {
  background-color: rgba(46, 204, 113, 0.2);
  color: #2ecc71;
}

.status-badge.locked {
  background-color: rgba(231, 76, 60, 0.2);
  color: #e74c3c;
}

.user-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
}

.action-btn:hover {
  transform: scale(1.1);
}

.action-btn i {
  font-size: 1rem;
}

.lock-btn {
  background-color: rgba(241, 196, 15, 0.2);
  color: #f1c40f;
}

.unlock-btn {
  background-color: rgba(46, 204, 113, 0.2);
  color: #2ecc71;
}

.delete-btn {
  background-color: rgba(231, 76, 60, 0.2);
  color: #e74c3c;
}

/* Modal styles */
.user-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background-color: #1a2035;
  border-radius: 12px;
  width: 100%;
  max-width: 500px;
  overflow: hidden;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

.modal-header {
  padding: 20px;
  border-bottom: 1px solid #2d3653;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.25rem;
}

.close-btn {
  background: none;
  border: none;
  color: #a6b0cf;
  font-size: 1.5rem;
  cursor: pointer;
  padding: 5px;
}

.modal-body {
  padding: 20px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: #a6b0cf;
  font-size: 0.9rem;
}

.form-group input {
  width: 100%;
  padding: 10px 15px;
  background-color: #252d47;
  border: 1px solid #2d3653;
  border-radius: 8px;
  color: white;
  outline: none;
}

.modal-footer {
  padding: 20px;
  border-top: 1px solid #2d3653;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.btn-cancel {
  background-color: #252d47;
  border: none;
  color: white;
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-cancel:hover {
  background-color: #2d3653;
}

.btn-submit {
  background: linear-gradient(135deg, #6e8efb, #a777e3);
  border: none;
  color: white;
  padding: 10px 20px;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
}

.btn-delete {
  background: linear-gradient(135deg, #ff6b6b, #ff4757);
  border: none;
  color: white;
  padding: 10px 20px;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
}

.confirm-modal .modal-body {
  text-align: center;
}

.warning-text {
  color: #ff6b6b;
  font-weight: 500;
  margin-top: 15px;
}
</style>