<template>
  <el-card class="user-management-card">
    <template #header>
      <div class="card-header">
        <span>用户管理</span>
      </div>
    </template>
    <el-form :model="userForm" label-width="80px">
      <el-row>
        <el-col :span="12">
          <el-form-item label="头像">
            <el-upload
              class="avatar-uploader"
              action="https://jsonplaceholder.typicode.com/posts/"
              :show-file-list="false"
              :on-success="handleAvatarSuccess"
              :before-upload="beforeAvatarUpload"
            >
              <img v-if="userForm.avatar" :src="userForm.avatar" class="avatar" />
              <el-icon v-else class="avatar-uploader-icon"><Plus /></el-icon>
            </el-upload>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="账号">
            <el-input v-model="userForm.account" placeholder="请输入账号"></el-input>
          </el-form-item>
        </el-col>
      </el-row>
      <el-row>
        <el-col :span="12">
          <el-form-item label="密码">
            <el-input v-model="userForm.password" type="password" placeholder="请输入密码"></el-input>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="昵称">
            <el-input v-model="userForm.nickname" placeholder="请输入昵称"></el-input>
          </el-form-item>
        </el-col>
      </el-row>
      <el-row>
        <el-col :span="12">
          <el-form-item label="邮箱">
            <el-input v-model="userForm.email" placeholder="请输入邮箱"></el-input>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="状态">
            <el-select v-model="userForm.status" placeholder="请选择状态">
              <el-option label="可用" value="active"></el-option>
              <el-option label="禁用" value="inactive"></el-option>
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>
      <el-row>
        <el-col :span="12">
          <el-form-item label="教师工号">
            <el-input v-model="userForm.teacherId" placeholder="请输入教师工号"></el-input>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="教师姓名">
            <el-input v-model="userForm.teacherName" placeholder="请输入教师姓名"></el-input>
          </el-form-item>
        </el-col>
      </el-row>
      <el-form-item>
        <el-button type="primary" @click="onSubmit">提交</el-button>
        <el-button @click="onCancel">取消</el-button>
      </el-form-item>
    </el-form>
  </el-card>
</template>

<script setup>
import { ref, reactive } from 'vue';
import { ElMessage } from 'element-plus';
import { Plus } from '@element-plus/icons-vue';

const userForm = reactive({
  avatar: '',
  account: '',
  password: '',
  nickname: '',
  email: '',
  status: 'active',
  teacherId: '',
  teacherName: '',
});

const handleAvatarSuccess = (response, uploadFile) => {
  userForm.avatar = URL.createObjectURL(uploadFile.raw);
};

const beforeAvatarUpload = (rawFile) => {
  if (rawFile.type !== 'image/jpeg' && rawFile.type !== 'image/png') {
    ElMessage.error('Avatar picture must be JPG/PNG format!');
    return false;
  } else if (rawFile.size / 1024 / 1024 > 2) {
    ElMessage.error('Avatar picture size can not exceed 2MB!');
    return false;
  }
  return true;
};

const onSubmit = () => {
  console.log('submit!', userForm);
  // Here you would typically send the data to your backend API
};

const onCancel = () => {
  console.log('cancel!');
  // Reset form or navigate away
};
</script>

<style scoped>
.user-management-card {
  margin: 20px;
}
.avatar-uploader .avatar {
  width: 178px;
  height: 178px;
  display: block;
}
.avatar-uploader .el-upload {
  border: 1px dashed var(--el-border-color-dark);
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: var(--el-transition-duration-fast);
}
.avatar-uploader .el-upload:hover {
  border-color: var(--el-color-primary);
}
.el-icon.avatar-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 178px;
  height: 178px;
  text-align: center;
}
</style>