<template>
  <div class="change-password-container">
    <el-card class="change-password-card">
      <template #header>
        <div class="card-header">
          <span>修改密码</span>
        </div>
      </template>
      <el-form
        ref="passwordFormRef"
        :model="passwordForm"
        :rules="passwordRules"
        label-width="100px"
        class="password-form"
      >
        <el-form-item label="旧密码" prop="oldPassword">
          <el-input v-model="passwordForm.oldPassword" type="password" show-password></el-input>
        </el-form-item>
        <el-form-item label="新密码" prop="newPassword">
          <el-input v-model="passwordForm.newPassword" type="password" show-password></el-input>
        </el-form-item>
        <el-form-item label="确认新密码" prop="confirmPassword">
          <el-input v-model="passwordForm.confirmPassword" type="password" show-password></el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="submitForm">提交</el-button>
          <el-button @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import { ElCard, ElForm, ElFormItem, ElInput, ElButton, ElMessage } from 'element-plus';
import axios from 'axios';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

const router = useRouter();
const backendUrl = 'http://127.0.0.1:8001';
const authStore = useAuthStore();

const username = ref(authStore.userInfo?.username || '');
const passwordForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: '',
});

// Removed duplicate declaration: const router = useRouter();

const validatePass = (rule, value, callback) => {
if (value === '') {
    callback(new Error('请输入新密码(密码至少8个字符，包含大小写字母和数字)'));
  } else if (value.length < 8) { 
    callback(new Error('密码长度不能少于 8 位'));
  } else if (!/\d/.test(value)) { 
    callback(new Error('密码必须包含数字'));
  } else if (!/[a-z]/.test(value)) { 
    callback(new Error('密码必须包含小写字母'));
  } else if (!/[A-Z]/.test(value)) { 
    callback(new Error('密码必须包含大写字母'));
  } else if (value === passwordForm.oldPassword) {
    callback(new Error('新密码不能与旧密码相同!'));
  } else {
    if (passwordForm.confirmPassword !== '') {
      if (!passwordFormRef.value) return;
      passwordFormRef.value.validateField('confirmPassword');
    }
    callback();
  }
};

const validatePass2 = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('请再次输入新密码'));
  } else if (value !== passwordForm.newPassword) {
    callback(new Error('两次输入密码不一致!'));
  } else {
    callback();
  }
};

const passwordRules = reactive({
  oldPassword: [
    { required: true, message: '请输入旧密码', trigger: 'blur' },
  ],
  newPassword: [
    { required: true, validator: validatePass, trigger: 'blur' },
  ],
  confirmPassword: [
    { required: true, validator: validatePass2, trigger: 'blur' },
  ],
});

const submitForm = () => {
  if (!passwordFormRef.value) return;
  passwordFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        // Assuming username is stored in localStorage or a global state after login
        const username = localStorage.getItem('username'); // Or from your Pinia store
        if (!username) {
          ElMessage.error('未找到用户信息，请重新登录');
          router.push('/login');
          return;
        }

        const response = await axios.post('http://127.0.0.1:8001/api/user/change_password/', {
          username: username,
          oldPassword: passwordForm.oldPassword,
          newPassword: passwordForm.newPassword,
        });

        if (response.data.code === 200) {
          ElMessage.success(response.data.message);
          resetForm();
          router.push('/login');
        } else {
          ElMessage.error(response.data.message);
        }
      } catch (error) {
        console.error('密码修改失败:', error.response?.data);
        let errorMsg = '密码修改失败，请稍后再试';
        if (error.response?.data?.message) {
            errorMsg = error.response.data.message;
        } else if (error.response?.data?.newPassword) {
            errorMsg = error.response.data.newPassword[0];
        }
        ElMessage.error(errorMsg);
      }
    } else {
      ElMessage.error('请检查输入项');
      return false;
    }
  });
};

const resetForm = () => {
  if (!passwordFormRef.value) return;
  passwordFormRef.value.resetFields();
};

// 获取认证头
const getAuthHeaders = () => {
    if (authStore.token) {
        return { Authorization: `Bearer ${authStore.token}` };
    }
    return null;
};

// 处理未授权响应
const handleUnauthorized = () => {
    ElMessage.error('登录已过期或无效，请重新登录');
    authStore.clearAuthInfo();
    router.push('/login');
};
</script>

<style scoped>
.change-password-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  background-color: #f0f2f5;
}

.change-password-card {
  width: 500px;
  max-width: 90%;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.card-header {
  font-size: 18px;
  font-weight: bold;
  text-align: center;
}

.password-form {
  padding: 20px;
}
</style>