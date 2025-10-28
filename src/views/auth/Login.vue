<template>
  <div class="login-container">
    <el-card class="login-card">
      <h2>实验室危化品管理系统</h2>
      <el-form ref="loginFormRef" :model="loginForm" :rules="loginRules" class="login-form">
        <el-form-item prop="username">
          <el-input v-model="loginForm.username" placeholder="用户名" prefix-icon="User" />
        </el-form-item>
        <el-form-item prop="password">
          <el-input v-model="loginForm.password" type="password" placeholder="密码" prefix-icon="Lock" show-password />
        </el-form-item>
        <el-form-item prop="captcha">
          <div class="captcha-wrapper">
            <el-input v-model="loginForm.captcha" placeholder="验证码" prefix-icon="Picture" class="captcha-input" />
            <img :src="captchaUrl" @click="refreshCaptcha" alt="验证码" class="captcha-image" />
          </div>
        </el-form-item>
        <el-form-item class="login-options">
          <el-checkbox v-model="loginForm.rememberPassword">记住密码</el-checkbox>
          <el-link type="primary" @click="goToForgotPassword">忘记密码?</el-link>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="loading" @click="submitForm(loginFormRef)" class="login-button">登录</el-button>
        </el-form-item>
        <el-form-item class="social-login">
          <el-divider>其他登录方式</el-divider>
          <div class="social-icons">
            <el-button type="info" circle @click="socialLogin('qq')">QQ</el-button>
            <el-button type="success" circle @click="socialLogin('wechat')">微信</el-button>
            <el-button type="danger" circle @click="socialLogin('weibo')">微博</el-button>
          </div>
        </el-form-item>
        <el-form-item class="register-link">
          <el-link type="primary" @click="goToRegister">新用户注册</el-link>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import axios from 'axios'
import { useRouter } from 'vue-router'
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { User, Lock, Picture } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth';
import { jwtDecode } from 'jwt-decode';
const router = useRouter()
const authStore = useAuthStore();
const loginFormRef = ref(null)
const loginForm = reactive({
  username: '',
  password: '',
  captcha: '',
  rememberPassword: false,
})

const loginRules = reactive({
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 15, message: '用户名长度在 3 到 15 个字符', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度在 6 到 20 个字符', trigger: 'blur' },
  ],
})

const loading = ref(false)
const captchaUrl = ref('/api/captcha') // 假设后端提供验证码接口

const refreshCaptcha = () => {
  captchaUrl.value = `/api/captcha?t=${Date.now()}`
}

const goToForgotPassword = () => {
  router.push('/forgot-password');
};

const goToRegister = () => {
  router.push('/register');
};

const submitForm = (formEl) => {
  if (!formEl) return
  formEl.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        await login(loginForm.username, loginForm.password, loginForm.captcha)
      } finally {
        loading.value = false
      }
          } else {
      ElMessage.error('请检查输入信息')
      return false
    }
  })
}

// src/views/Login.vue

const login = async (username, password) => {
  try {
    const res = await axios.post('http://127.0.0.1:8001/api/user/login/', {
      username: username,
      password: password,
    });

    if (res.data.code === 200) {
      ElMessage.success('登录成功！');

      // 从响应或 Token 中提取用户信息
      // 注意：从 Access Token 解码 user_id 可能不是最佳实践，最好后端直接返回必要信息
      // 但如果后端只返回了 username 和 role，我们可以这样构造
       let userInfo = {
           username: res.data.username,
           role: res.data.role,
           id: null // 如果后端不返回 ID，可以先设为 null
       };
       // 尝试从 token 解码 user_id (如果 SIMPLE_JWT 配置了包含 user_id)
       try {
           const decoded = jwtDecode(res.data.token);
           if (decoded.user_id) {
               userInfo.id = decoded.user_id;
           }
       } catch (decodeError) {
           console.error("无法从 token 解码 user_id:", decodeError);
       }


      // 调用 store action 保存认证信息
      authStore.setAuthInfo(res.data.token, userInfo, loginForm.rememberPassword);

      console.log("准备跳转到 /dashboard..."); // 可以保留调试
      router.push('/dashboard');
      console.log("router.push 已调用"); // 可以保留调试

    } else {
      ElMessage.error(res.data.message || '登录失败');
    }

  } catch (error) {
    if (error.response && error.response.status === 401) {
      ElMessage.error('用户名或密码错误');
    } else {
      ElMessage.error('登录请求失败，请检查网络');
      console.error(error);
    }
  }
};
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f0f2f5;
}

.login-card {
  width: 400px;
  padding: 40px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  border-radius: 8px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .login-card {
    width: 90%; /* 在小屏幕上宽度占90% */
    padding: 20px;
  }

  .login-card h2 {
    font-size: 20px;
    margin-bottom: 20px;
  }

  .login-form .el-input {
    height: 36px;
  }

  .captcha-image {
    width: 80px;
    height: 36px;
  }

  .login-button {
    height: 40px;
    font-size: 14px;
  }

  .social-icons .el-button {
    margin: 0 5px;
  }
}

@media (max-width: 480px) {
  .login-card {
    width: 95%; /* 在更小屏幕上宽度占95% */
    padding: 15px;
  }

  .login-card h2 {
    font-size: 18px;
    margin-bottom: 15px;
  }

  .social-icons {
    flex-direction: column; /* 垂直排列社交登录按钮 */
  }

  .social-icons .el-button {
    margin: 5px 0; /* 调整垂直间距 */
    width: 100%;
  }
}

.login-card h2 {
  text-align: center;
  margin-bottom: 30px;
  color: #333;
}

.login-form .el-input {
  height: 40px;
}

.captcha-wrapper {
  display: flex;
  align-items: center;
}

.captcha-input {
  flex: 1;
  margin-right: 10px;
}

.captcha-image {
  width: 100px;
  height: 40px;
  cursor: pointer;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
}

.login-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.login-button {
  width: 100%;
  height: 45px;
  font-size: 16px;
}

.social-login {
  text-align: center;
  margin-top: 20px;
}

.social-icons .el-button {
  margin: 0 10px;
}

.register-link {
  text-align: center;
  margin-top: 20px;
}

</style>
