<template>
  <div class="forgot-password-container">
    <el-card class="forgot-password-card">
      <h2>忘记密码</h2>
      <el-form ref="forgotPasswordFormRef" :model="forgotPasswordForm" :rules="forgotPasswordRules" class="forgot-password-form">
        <el-form-item prop="email">
          <el-input v-model="forgotPasswordForm.email" placeholder="请输入您的注册邮箱" prefix-icon="Message" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="loading" @click="submitForm(forgotPasswordFormRef)" class="submit-button">发送重置链接</el-button>
        </el-form-item>
        <el-form-item class="back-to-login">
          <el-link type="primary" :underline="false" @click="goToLogin">返回登录</el-link>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const router = useRouter()

const forgotPasswordFormRef = ref(null)
const forgotPasswordForm = reactive({
  email: '',
})

const forgotPasswordRules = reactive({
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱地址', trigger: ['blur', 'change'] },
  ],
})

const loading = ref(false)

const submitForm = (formEl) => {
  if (!formEl) return
  formEl.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        const res = await axios.post('http://127.0.0.1:8001/api/user/reset-password/request/', {
          email: forgotPasswordForm.email,
        })
        if (res.data.code === 200) {
          ElMessage.success('密码重置链接已发送至您的邮箱，请查收！')
          router.push('/login')
        } else {
          ElMessage.error(res.data.message)
        }
      } catch (error) {
        const errorMsg = error.response?.data?.message || '发送失败，请稍后再试';
        ElMessage.error(errorMsg);
      } finally {
        loading.value = false
      }
    } else {
      ElMessage.error('请检查输入信息')
      return false
    }
  })
}

const goToLogin = () => {
  router.push('/login')
}
</script>

<style scoped>
.forgot-password-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f0f2f5;
}

.forgot-password-card {
  width: 400px;
  padding: 40px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  border-radius: 8px;
}

.forgot-password-card h2 {
  text-align: center;
  margin-bottom: 30px;
  color: #333;
}

.forgot-password-form .el-input {
  height: 40px;
}

.submit-button {
  width: 100%;
  height: 45px;
  font-size: 16px;
}

.back-to-login {
  text-align: center;
  margin-top: 20px;
}
</style>