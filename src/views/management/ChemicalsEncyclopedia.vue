<template>
  <div class="app-container">
    <el-card class="search-card" shadow="never">
      <el-form :model="queryParams" ref="queryFormRef" :inline="true" label-width="68px">
        <el-form-item label="关键字" prop="search">
          <el-input
            v-model="queryParams.search"
            placeholder="名称/CAS号"
            clearable
            style="width: 240px"
            @keyup.enter="handleQuery"
          />
        </el-form-item>
        <el-form-item label="形态" prop="formState">
          <el-select v-model="queryParams.formState" placeholder="请选择形态" clearable style="width: 240px">
            <el-option label="固体" value="固体"></el-option>
            <el-option label="液体" value="液体"></el-option>
            <el-option label="气体" value="气体"></el-option>
            <el-option label="其他" value="其他"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="handleQuery">搜索</el-button>
          <el-button :icon="Refresh" @click="resetQuery">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="table-card" shadow="never">
      <el-row :gutter="10" class="action-buttons">
        <el-col :span="1.5">
          <el-button
            type="primary"
            plain
            :icon="Plus"
            @click="handleAdd"
            v-if="hasPermission('chemical:add')"
          >新增</el-button>
        </el-col>
        <el-col :span="1.5">
          <el-button
            type="success"
            plain
            :icon="EditPen"
            :disabled="singleSelected"
            @click="handleUpdate"
            v-if="hasPermission('chemical:edit')"
          >修改</el-button>
        </el-col>
        <el-col :span="1.5">
          <el-button
            type="danger"
            plain
            :icon="Delete"
            :disabled="multipleSelected"
            @click="handleBulkDelete"
            v-if="hasPermission('chemical:delete')"
          >删除</el-button>
        </el-col>
      </el-row>
      <el-table
        :data="chemicals"
        v-loading="loading"
        @selection-change="handleSelectionChange"
        @sort-change="handleSortChange"
        row-key="id"
      >
        <el-table-column type="selection" width="55" align="center" />
        <el-table-column prop="nameCn" label="化学品中文名称" sortable="custom" :show-overflow-tooltip="true" min-width="180" />
        <el-table-column label="图片" width="100">
          <template #default="scope">
            <el-image
              v-if="scope.row.image"
              :src="scope.row.image"
              :preview-src-list="[scope.row.image]"
              style="width: 50px; height: 50px; object-fit: cover;"
              fit="cover"
              lazy
            />
            <span v-else>无图片</span>
          </template>
        </el-table-column>
        <el-table-column prop="casNo" label="CAS 号" width="140" sortable="custom" />
        <el-table-column prop="specification" label="规格型号" width="150" :show-overflow-tooltip="true" />
        <el-table-column prop="formState" label="形态" width="100" sortable="custom" />
        <el-table-column label="危险类别" width="180">
          <template #default="scope">
            {{ Array.isArray(scope.row.hazardClasses) ? scope.row.hazardClasses.join(', ') : '' }}
          </template>
        </el-table-column>
        <el-table-column prop="signalWord" label="等级" width="100" sortable="custom" />
      </el-table>
      <el-pagination
        v-show="totalItems > 0"
        style="margin-top: 20px;"
        :total="totalItems"
        v-model:current-page="queryParams.pageNum"
        v-model:page-size="queryParams.pageSize"
        layout="total, sizes, prev, pager, next, jumper"
        :page-sizes="[10, 20, 50, 100]"
        @size-change="handleSizeChange"
        @current-change="handlePageChange"
      />
      <el-empty v-if="!loading && chemicals.length === 0" description="暂无化学品记录" />
    </el-card>

    <el-dialog :title="dialogTitle" v-model="dialogVisible" width="700px" append-to-body @close="handleDialogClose">
      <el-form :model="itemForm" :rules="itemRules" ref="itemFormRef" label-width="150px">
        <el-divider content-position="left">关键信息</el-divider>
        <el-form-item label="化学品中文名称" prop="nameCn">
          <el-input v-model="itemForm.nameCn"></el-input>
        </el-form-item>
        <el-form-item label="CAS 号" prop="casNo">
          <el-input v-model="itemForm.casNo"></el-input>
        </el-form-item>
        <el-form-item label="图片" prop="image">
          <el-upload
            ref="editUploadRef"
            :auto-upload="false"
            :limit="1"
            :on-change="handleEditFileChange"
            :on-exceed="handleEditFileExceed"
            list-type="picture-card"
            :file-list="imageFileList"
            :on-remove="handleImageRemove"
          >
            <el-icon><Plus /></el-icon>
            <template #tip>
              <div class="el-upload__tip">
              </div>
            </template>
          </el-upload>
        </el-form-item>
        <el-form-item label="规格型号" prop="specification">
          <el-input v-model="itemForm.specification"></el-input>
        </el-form-item>
        <el-form-item label="形态" prop="formState">
          <el-select v-model="itemForm.formState" placeholder="请选择形态">
            <el-option label="固体" value="固体"></el-option>
            <el-option label="液体" value="液体"></el-option>
            <el-option label="气体" value="气体"></el-option>
            <el-option label="其他" value="其他"></el-option>
          </el-select>
        </el-form-item>
        <el-divider content-position="left">危险性信息</el-divider>
        <el-form-item label="危险类别" prop="hazardClasses">
          <el-checkbox-group v-model="itemForm.hazardClasses">
            <el-checkbox label="易燃液体" name="hazardClasses"></el-checkbox>
            <el-checkbox label="腐蚀品" name="hazardClasses"></el-checkbox>
            <el-checkbox label="毒性物质" name="hazardClasses"></el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        <el-form-item label="等级" prop="signalWord">
          <el-radio-group v-model="itemForm.signalWord">
            <el-radio label="危险"></el-radio>
            <el-radio label="警告"></el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="cancel">取 消</el-button>
          <el-button type="primary" @click="submitItemForm">
            保存
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup name="ChemicalsEncyclopedia">
import { ref, reactive, onMounted, nextTick } from 'vue'
import { ElCard, ElButton, ElTable, ElTableColumn, ElPagination, ElDialog, ElForm, ElFormItem,
  ElInput, ElInputNumber, ElSelect, ElOption, ElDatePicker, ElRow, ElCol, ElMessage, ElEmpty,
  ElPopconfirm, ElMessageBox, ElCheckboxGroup, ElCheckbox, ElRadioGroup, ElRadio, ElDivider, ElImage, ElUpload, ElIcon } from 'element-plus'
import { Search, Refresh, Plus, EditPen, Delete } from '@element-plus/icons-vue'
import axios from 'axios'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth';

const router = useRouter()
const backendUrl = 'http://127.0.0.1:8001'
const authStore = useAuthStore();

// --- 状态变量定义 ---
const loading = ref(true)
const chemicals = ref([])
const totalItems = ref(0)
const queryParams = reactive({ pageNum: 1, pageSize: 10, search: '', formState: '', orderByColumn: 'name_cn', isAsc: 'ascending' })
const selectedIds = ref([]) // 存储选中的 ID 列表
const singleSelected = ref(true) // 是否只选中了一个 (用于修改按钮)
const multipleSelected = ref(true) // 是否选中了至少一个 (用于删除按钮)
const dialogVisible = ref(false)
const dialogTitle = ref('')
const itemFormRef = ref(null)
const submitLoading = ref(false)
const isEditMode = ref(false)
const editUploadRef = ref(null)
const currentEditImage = ref('')
const newImageFile = ref(null)
const imageFileList = ref([])
const itemForm = reactive({
  id: null,
  nameCn: '',
  casNo: '',
  specification: '',
  formState: '',
  hazardClasses: [],
  signalWord: '',
  image: null,
})
const itemRules = reactive({
  nameCn: [{ required: true, message: '请输入化学品中文名称', trigger: 'blur' }],
  casNo: [{ required: true, message: '请输入CAS号', trigger: 'blur' }],
  formState: [{ required: true, message: '请选择形态', trigger: 'change' }],
  hazardClasses: [{ type: 'array', required: true, message: '请至少选择一个危险类别', trigger: 'change' }],
  signalWord: [{ required: true, message: '请选择等级', trigger: 'change' }],
})

const hasPermission = (perm) => { return true } // 权限模拟

// --- 获取 Token 和处理 401 ---
const getAuthHeaders = () => {
  if (authStore.token) {
    return { Authorization: `Bearer ${authStore.token}` }
  }
  return null
}

const handleUnauthorized = () => {
  ElMessage.error('登录已过期或无效，请重新登录')
  authStore.clearAuthInfo();
  router.push('/login')
}

// --- API 调用: fetchChemicals ---
const fetchChemicals = async (page = queryParams.pageNum) => {
  loading.value = true
  const headers = getAuthHeaders()
  if (!headers) {
    handleUnauthorized()
    loading.value = false
    return
  }

  try {
    let ordering = ''
    if (queryParams.orderByColumn) {
      console.log('fetchChemicals - queryParams.orderByColumn:', queryParams.orderByColumn, 'queryParams.isAsc:', queryParams.isAsc);
      ordering = (queryParams.isAsc === 'descending' ? '-' : '') + queryParams.orderByColumn
    }
    console.log('fetchChemicals - Final ordering string:', ordering);
    const response = await axios.get(`${backendUrl}/api/chemical/`, {
      params: {
        page: page,
        page_size: queryParams.pageSize,
        search: queryParams.search || undefined,
        form_state: queryParams.formState || undefined,
        ordering: ordering || undefined,
      },
      headers: headers,
    })
    chemicals.value = response.data.results.map((item) => {
      if (item.image && !item.image.startsWith('http')) {
        item.image = `${backendUrl}${item.image}`
      }
      if (typeof item.hazardClasses === 'string') {
        item.hazardClasses = item.hazardClasses.split(',').filter(Boolean)
      } else if (!Array.isArray(item.hazardClasses)) {
        item.hazardClasses = []
      }
      return item
    })
    totalItems.value = response.data.count
    queryParams.pageNum = page
  } catch (error) {
    if (error.response && error.response.status === 401) {
      handleUnauthorized()
    } else {
      console.error('获取化学品列表失败:', error.response?.data)
      ElMessage.error(error.response?.data?.detail || '获取化学品列表失败')
      chemicals.value = []
      totalItems.value = 0
    }
  } finally {
    loading.value = false
  }
}

// --- 事件处理 ---
const handleQuery = () => {
  queryParams.pageNum = 1
  fetchChemicals()
}

const resetQuery = () => {
  queryParams.search = ''
  queryParams.formState = ''
  queryParams.pageNum = 1
  queryParams.orderByColumn = 'name_cn'
  queryParams.isAsc = 'ascending'
  handleQuery()
}

const handleSortChange = ({ prop, order }) => {
  console.log('handleSortChange - Original prop:', prop, 'order:', order);
  const sortMap = {
    nameCn: 'name_cn',
    casNo: 'cas_no',
    formState: 'form_state',
    signalWord: 'signal_word',
    last_updated: 'last_updated',
  };
  queryParams.orderByColumn = sortMap[prop] || prop;
  queryParams.isAsc = order;
  console.log('handleSortChange - Mapped orderByColumn:', queryParams.orderByColumn, 'isAsc:', queryParams.isAsc);
  handleQuery();
};

const handleSizeChange = (newSize) => {
  queryParams.pageSize = newSize
  queryParams.pageNum = 1
  fetchChemicals()
}

const handlePageChange = (newPage) => {
  fetchChemicals(newPage)
}

const resetForm = () => {
  itemForm.id = null
  itemForm.nameCn = ''
  itemForm.casNo = ''
  itemForm.specification = ''
  itemForm.formState = ''
  itemForm.hazardClasses = []
  itemForm.signalWord = ''
  itemForm.image = null
  currentEditImage.value = ''
  newImageFile.value = null
  imageFileList.value = [] // 清空文件列表
  editUploadRef.value?.clearFiles()
  nextTick(() => {
    itemFormRef.value?.resetFields()
  })
}

const handleDialogClose = () => {
  resetForm()
}

const cancel = () => {
  dialogVisible.value = false
}

const handleAdd = () => {
  resetForm()
  isEditMode.value = false
  dialogTitle.value = '新增危化品'
  dialogVisible.value = true
}

const handleUpdate = () => {
  resetForm()
  const targetRow = chemicals.value.find((item) => item.id === selectedIds.value[0])
  if (!targetRow) {
    ElMessage.warning('请选择一条数据进行修改')
    return
  }
  isEditMode.value = true
  dialogTitle.value = '编辑危化品'
  Object.assign(itemForm, targetRow)
  currentEditImage.value = targetRow.image || ''
  newImageFile.value = null
  // 如果有图片，将其添加到文件列表
  if (targetRow.image) {
    imageFileList.value = [{ name: 'image', url: targetRow.image, uid: Date.now() }]
  } else {
    imageFileList.value = []
  }
  editUploadRef.value?.clearFiles()
  dialogVisible.value = true
}

const handleEditFileChange = (uploadFile) => {
  newImageFile.value = uploadFile.raw
  // 更新文件列表以显示新选择的图片
  imageFileList.value = [{ name: uploadFile.name, url: URL.createObjectURL(uploadFile.raw), uid: uploadFile.uid }]
}

const handleEditFileExceed = (files) => {
  editUploadRef.value?.clearFiles()
  const file = files[0]
  editUploadRef.value?.handleStart(file)
  newImageFile.value = file
  // 更新文件列表以显示新选择的图片
  imageFileList.value = [{ name: file.name, url: URL.createObjectURL(file), uid: file.uid }]
}

const handleImageRemove = (file) => {
  // 当图片被移除时，清空 newImageFile 和 imageFileList
  newImageFile.value = null
  imageFileList.value = []
  // 如果是编辑模式且移除了原有图片，需要将 itemForm.image 置空
  if (isEditMode.value && itemForm.image === file.url) {
    itemForm.image = null
  }
}
const submitItemForm = () => {
  if (!itemFormRef.value) return
  const headers = getAuthHeaders()
  if (!headers) {
    handleUnauthorized()
    return
  }

  itemFormRef.value.validate(async (valid) => {
    if (valid) {
      submitLoading.value = true
      const postData = new FormData()
      postData.append('nameCn', itemForm.nameCn)
      postData.append('casNo', itemForm.casNo)
      postData.append('specification', itemForm.specification)
      postData.append('formState', itemForm.formState)
      postData.append('signalWord', itemForm.signalWord)

      if (Array.isArray(itemForm.hazardClasses)) {
        itemForm.hazardClasses.forEach((item) => {
          postData.append('hazardClasses', item)
        })
      }
      if (newImageFile.value) {
        postData.append('image', newImageFile.value)
      }

      const url = isEditMode.value ? `${backendUrl}/api/chemical/${itemForm.id}/` : `${backendUrl}/api/chemical/`
      const method = isEditMode.value ? 'put' : 'post'

      try {
        await axios[method](url, postData, { headers: headers })
        ElMessage.success(isEditMode.value ? '修改成功！' : '添加成功！')
        dialogVisible.value = false
        fetchChemicals(isEditMode.value ? queryParams.pageNum : 1)
      } catch (error) {
        if (error.response && error.response.status === 401) {
          handleUnauthorized()
        } else {
          console.error('保存失败:', error.response?.data)
          let errorMsg = (isEditMode.value ? '修改失败！' : '添加失败！')

          if (error.response?.data?.error && typeof error.response.data.error === 'string' && error.response.data.error.includes('Duplicate entry') && error.response.data.error.includes('cas_no')) {
            errorMsg = 'CAS号已存在，请检查！'
          } else if (error.response?.data?.detail) {
            errorMsg = error.response.data.detail
          } else if (error.response && typeof error.response.data === 'object' && error.response.status !== 401 && error.response.status !== 403) {
            const fieldErrors = Object.entries(error.response.data).map(([field, messages]) => `${field}: ${Array.isArray(messages) ? messages.join(', ') : messages}`).join('; ')
            if (fieldErrors) errorMsg = fieldErrors
          }
          ElMessage.error({
            message: errorMsg,
            duration: 3000 // 3秒后自动消失
          })
        }
      } finally {
        submitLoading.value = false
      }
    } else {
      ElMessage.error('请检查表单填写是否完整和正确。')
      return false
    }
  })
}

const handleSelectionChange = (selection) => {
  selectedIds.value = selection.map((item) => item.id)
  singleSelected.value = selection.length !== 1
  multipleSelected.value = selection.length === 0
}

const handleBulkDelete = async () => {
  const idsToDelete = selectedIds.value;
  if (idsToDelete.length === 0) {
    ElMessage.warning('请先选择要删除的数据');
    return;
  }
  const headers = getAuthHeaders();
  if (!headers) { handleUnauthorized(); return; }

  const isSingleDelete = idsToDelete.length === 1;
  const confirmMessage = `确认删除选中的 ${idsToDelete.length} 条数据吗？`;

  ElMessageBox.confirm(confirmMessage, '警告', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(async () => {
    loading.value = true;
    try {
      if (isSingleDelete) {
        await axios.delete(`${backendUrl}/api/chemical/${idsToDelete[0]}/`, { headers });
      } else {
        await axios.post(
          `${backendUrl}/api/chemical/bulk-delete/`,
          { ids: idsToDelete },
          { headers }
        );
      }
      ElMessage.success('删除成功！');
      if (chemicals.value.length === idsToDelete.length && queryParams.pageNum > 1) {
        queryParams.pageNum--;
      }
      fetchChemicals();
    } catch (error) {
      if (error.response?.status === 401) handleUnauthorized();
      else {
        console.error('删除失败:', error.response?.data);
        ElMessage.error(error.response?.data?.detail || '删除失败，请重试');
      }
    } finally {
      loading.value = false;
    }
  }).catch(() => {
    ElMessage.info('已取消删除');
  });
};

// --- 辅助函数 ---
const formatDateTime = (dateString) => {
  if (!dateString) return ''
  try {
    const date = new Date(dateString)
    return date.toLocaleString('zh-CN', { hour12: false })
  } catch (e) {
    return dateString
  }
}

// --- 初始化加载 ---
onMounted(() => {
  fetchChemicals()
})
</script>

<style scoped>
</style>