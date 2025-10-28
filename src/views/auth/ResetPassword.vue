<template>
  <div class="reset-password-container">
    <el-card class="reset-password-card">
      <h2>重置密码</h2>
      <el-form ref="resetPasswordFormRef" :model="resetPasswordForm" :rules="resetPasswordRules" class="reset-password-form">
        <el-form-item label="新密码" prop="new_password">
          <el-input v-model="resetPasswordForm.new_password" type="password" placeholder="请输入新密码" show-password />
        </el-form-item>
        <el-form-item label="确认新密码" prop="confirm_password">
          <el-input v-model="resetPasswordForm.confirm_password" type="password" placeholder="请再次输入新密码" show-password />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="loading" @click="submitForm(resetPasswordFormRef)" class="submit-button">提交新密码</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const router = useRouter()
const route = useRoute()

const resetPasswordFormRef = ref(null)
const resetPasswordForm = reactive({
  new_password: '',
  confirm_password: '',
})

const uid = ref(null)
const token = ref(null)

const loading = ref(false)

onMounted(() => {
  uid.value = route.query.uid;
  token.value = route.query.token; 
  if (!uid.value || !token.value) { 
    ElMessage.error('无效的重置链接！')
    router.push('/login')
  }
})

const validatePass2 = (rule, value, callback) => {
  if (value === '') { callback(new Error('请再次输入新密码')); }
  else if (value !== resetPasswordForm.new_password) { callback(new Error('两次输入密码不一致!')); }
  else { callback(); }
};
const resetPasswordRules = reactive({
  new_password: [ { required: true, message: '请输入新密码(密码至少8个字符，包含大小写字母和数字)', trigger: 'blur' }, { min: 8, message: '密码必须至少8个字符，包含大小写字母和数字', trigger: 'blur' }, ],
  confirm_password: [ { required: true, validator: validatePass2, trigger: 'blur' }, ],
})

const submitForm = (formEl) => {
  if (!formEl) return
  formEl.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        const res = await axios.post(`http://127.0.0.1:8001/api/user/reset-password/confirm/`, 
          { 
            new_password: resetPasswordForm.new_password,
          },
          { 
            params: {
              uid: uid.value,
              token: token.value
            }
          }
        )
        
        if (res.data.code === 200) {
          ElMessage.success('密码重置成功！即将跳转到登录页...')
          setTimeout(() => {
            router.push('/login')
          }, 2000)
        } else {
          ElMessage.error(res.data.message)
        }
      } catch (error) {
        ElMessage.error(error.response?.data?.message || '重置失败，链接可能已过期')
      } finally {
        loading.value = false
      }
    }
  })
}
</script>

<style scoped>
.reset-password-container { display: flex; justify-content: center; align-items: center; min-height: 100vh; background-color: #f0f2f5; }
.reset-password-card { width: 400px; padding: 40px; }
.submit-button { width: 100%; }
</style>