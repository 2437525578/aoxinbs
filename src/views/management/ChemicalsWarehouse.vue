<template>
  <div class="app-container"> 

    <el-card class="search-card" shadow="never">
      <el-form :model="queryParams" ref="queryFormRef" :inline="true" label-width="68px">
        <el-form-item label="关键字" prop="search">
          <el-input
            v-model="queryParams.search"
            placeholder="名称/CAS/位置/批号"
            clearable
            style="width: 240px"
            @keyup.enter="handleQuery"
          />
        </el-form-item>
        <el-form-item label="存放位置" prop="location">
          <el-input
            v-model="queryParams.location"
            placeholder="请输入存放位置"
            clearable
            style="width: 240px"
            @keyup.enter="handleQuery"
          />
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
            v-if="hasPermission('inventory:add')"
          >新增</el-button>
        </el-col>
        <el-col :span="1.5">
          <el-button
            type="success"
            plain
            :icon="EditPen"
            :disabled="singleSelected"
            @click="handleUpdate"
             v-if="hasPermission('inventory:edit')"
          >修改</el-button>
        </el-col>
        <el-col :span="1.5">
          <el-button
            type="danger"
            plain
            :icon="Delete"
            :disabled="multipleSelected"
            @click="handleBulkDelete"
             v-if="hasPermission('inventory:delete')"
          >删除</el-button>
        </el-col>
      </el-row>
      <el-table
        :data="inventoryItems"
        v-loading="loading"
        @selection-change="handleSelectionChange"
        @sort-change="handleSortChange"
        row-key="id"
      >
        <el-table-column type="selection" width="55" align="center" />
        <el-table-column prop="chemical_details.nameCn" label="化学品名称" sortable="custom" :show-overflow-tooltip="true" min-width="180" />
        <el-table-column prop="chemical_details.casNo" label="CAS号" width="140" />
        <el-table-column prop="location" label="存放位置" width="150" sortable="custom" :show-overflow-tooltip="true"/>
        <el-table-column prop="quantity" label="当前数量" align="right" width="120" sortable="custom">
            <template #default="scope">
                {{ scope.row.quantity }} {{ scope.row.unit }}
            </template>
        </el-table-column>
        <el-table-column prop="unit" label="单位" align="center" width="80" />
        <el-table-column prop="batch_number" label="批号" width="150" :show-overflow-tooltip="true"/>
        <el-table-column prop="expiry_date" label="有效期至" align="center" width="120" sortable="custom">
             <template #default="scope">
                <span>{{ formatDate(scope.row.expiry_date) }}</span>
            </template>
        </el-table-column>
        <el-table-column prop="last_updated" label="最后更新" align="center" width="160" sortable="custom">
             <template #default="scope">
                <span>{{ formatDateTime(scope.row.last_updated) }}</span>
            </template>
        </el-table-column>
        <el-table-column prop="added_by_username" label="添加人" align="center" width="100" />
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
      <el-empty v-if="!loading && inventoryItems.length === 0" description="暂无库存记录" />

    </el-card>

    <el-dialog :title="dialogTitle" v-model="dialogVisible" width="700px" append-to-body @close="handleDialogClose">
       <el-form :model="itemForm" :rules="itemRules" ref="itemFormRef" label-width="100px">
         <el-form-item label="化学品" prop="chemical">
           <el-select
             v-model="itemForm.chemical"
             filterable remote clearable reserve-keyword
             placeholder="搜索化学品名称或CAS号"
             :remote-method="searchChemicals"
             :loading="chemicalSearchLoading"
             style="width: 100%;" value-key="id"
            >
              <el-option
                v-for="item in chemicalOptions"
                :key="item.id"
                :label="`${item.nameCn} (${item.casNo})`"
                :value="item.id"
              />
            </el-select>
        </el-form-item>
        <el-form-item label="存放位置" prop="location">
          <el-input v-model="itemForm.location" placeholder="例如：储藏柜A-1"></el-input>
        </el-form-item>
         <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="数量" prop="quantity">
              <el-input-number v-model="itemForm.quantity" :precision="2" :step="0.1" :min="0" controls-position="right" style="width: 100%;"/>
            </el-form-item>
           </el-col>
           <el-col :span="12">
            <el-form-item label="单位" prop="unit">
              <el-input v-model="itemForm.unit" placeholder="例如：ml, g, L, kg, 瓶"></el-input>
            </el-form-item>
           </el-col>
         </el-row>
        <el-form-item label="批号" prop="batch_number">
          <el-input v-model="itemForm.batch_number"></el-input>
        </el-form-item>
         <el-row :gutter="20">
           <el-col :span="12">
            <el-form-item label="采购日期" prop="purchase_date">
                <el-date-picker v-model="itemForm.purchase_date" type="date" placeholder="选择日期" value-format="YYYY-MM-DD" style="width: 100%;"/>
            </el-form-item>
           </el-col>
           <el-col :span="12">
            <el-form-item label="有效期至" prop="expiry_date">
                <el-date-picker v-model="itemForm.expiry_date" type="date" placeholder="选择日期" value-format="YYYY-MM-DD" style="width: 100%;"/>
            </el-form-item>
           </el-col>
         </el-row>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="cancel">取 消</el-button>
          <el-button type="primary" @click="submitItemForm" :loading="submitLoading">确 定</el-button>
        </div>
      </template>
    </el-dialog>

  </div>
</template>

<script setup name="ChemicalsWarehouse">
import { ref, reactive, onMounted, nextTick } from 'vue';
import { ElCard, ElButton, ElTable, ElTableColumn, ElPagination, ElDialog, ElForm, ElFormItem,
  ElInput, ElInputNumber, ElSelect, ElOption, ElDatePicker, ElRow, ElCol, ElMessage, ElEmpty,
  ElPopconfirm, ElMessageBox } from 'element-plus';
import { Search, Refresh, Plus, EditPen, Delete, Download, Upload } from '@element-plus/icons-vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

const router = useRouter();
const backendUrl = 'http://127.0.0.1:8001';
const authStore = useAuthStore();

// --- (状态变量定义保持不变) ---
const loading = ref(true);
const inventoryItems = ref([]);
const totalItems = ref(0);
const queryParams = reactive({ pageNum: 1, pageSize: 10, search: '', location: '', orderByColumn: 'chemical__name_cn', isAsc: 'ascending', });
const selectedIds = ref([]); // 存储选中的 ID 列表
const singleSelected = ref(true); // 是否只选中了一个 (用于修改按钮)
const multipleSelected = ref(true); // 是否选中了至少一个 (用于删除按钮) - 注意：这个变量名现在有点误导，但逻辑是正确的
const dialogVisible = ref(false);
const dialogTitle = ref('');
const itemFormRef = ref(null);
const submitLoading = ref(false);
const isEditMode = ref(false);
const itemForm = reactive({ id: null, chemical: null, location: '', quantity: 0.00, unit: '', batch_number: '', purchase_date: null, expiry_date: null, });
const itemRules = reactive({ chemical: [{ required: true, message: '请选择化学品', trigger: 'change' }], quantity: [{ required: true, message: '请输入数量', trigger: 'blur' }, { type: 'number', min: 0, message: '数量不能为负数', trigger: 'blur'}], unit: [{ required: true, message: '请输入单位', trigger: 'blur' }], location: [{ required: true, message: '请输入存放位置', trigger: 'blur' }], });
const chemicalSearchLoading = ref(false);
const chemicalOptions = ref([]);
const hasPermission = (perm) => { return true; }; // 权限模拟

// --- (获取 Token 和处理 401 保持不变) ---
const getAuthHeaders = () => { /* ... */
    if (authStore.token) { return { Authorization: `Bearer ${authStore.token}` }; }
    return null;
};
const handleUnauthorized = () => { /* ... */
    ElMessage.error('登录已过期或无效，请重新登录');
    authStore.clearAuthInfo();
    router.push('/login');
};

// --- (API 调用: fetchInventory, searchChemicals 保持不变) ---
const fetchInventory = async (page = queryParams.pageNum) => { /* ... */
  loading.value = true; const headers = getAuthHeaders(); if (!headers) { handleUnauthorized(); loading.value = false; return; }
  try { let ordering = ''; if (queryParams.orderByColumn) { ordering = (queryParams.isAsc === 'descending' ? '-' : '') + queryParams.orderByColumn; }
    const response = await axios.get(`${backendUrl}/api/inventory/`, { params: { page: page, page_size: queryParams.pageSize, search: queryParams.search || undefined, location: queryParams.location || undefined, ordering: ordering || undefined, }, headers: headers });
    inventoryItems.value = response.data.results.map(item => { if (item.chemical_details && item.chemical_details.image && !item.chemical_details.image.startsWith('http')) { item.chemical_details.image = `${backendUrl}${item.chemical_details.image}`; } return item; });
    totalItems.value = response.data.count; queryParams.pageNum = page;
  } catch (error) { if (error.response && error.response.status === 401) { handleUnauthorized(); } else { console.error("获取库存列表失败:", error.response?.data); ElMessage.error(error.response?.data?.detail || "获取库存列表失败"); inventoryItems.value = []; totalItems.value = 0; }
  } finally { loading.value = false; }
};
let searchTimeout = null;
const searchChemicals = async (query) => { /* ... */
  clearTimeout(searchTimeout); const headers = getAuthHeaders(); if (!headers) { handleUnauthorized(); return; }
  if (query) { chemicalSearchLoading.value = true; searchTimeout = setTimeout(async () => { try { const response = await axios.get(`${backendUrl}/api/chemical/`, { params: { search: query, page_size: 50 }, headers: headers }); chemicalOptions.value = response.data.results || response.data; } catch (error) { if (error.response && error.response.status === 401) { handleUnauthorized(); } else { console.error("搜索化学品失败:", error); chemicalOptions.value = []; } } finally { chemicalSearchLoading.value = false; } }, 300);
  } else { chemicalOptions.value = []; }
};

// --- (事件处理: handleQuery, resetQuery, handleSortChange, handleSizeChange, handlePageChange, resetForm, handleDialogClose, cancel, handleAdd, handleUpdate, submitItemForm 保持不变) ---
const handleQuery = () => { queryParams.pageNum = 1; fetchInventory(); };
const resetQuery = () => { queryParams.search = ''; queryParams.location = ''; queryParams.pageNum = 1; queryParams.orderByColumn = 'chemical__name_cn'; queryParams.isAsc = 'ascending'; handleQuery(); };
const handleSortChange = ({ prop, order }) => { queryParams.orderByColumn = prop; queryParams.isAsc = order; handleQuery(); };
const handleSizeChange = (newSize) => { queryParams.pageSize = newSize; queryParams.pageNum = 1; fetchInventory(); };
const handlePageChange = (newPage) => { fetchInventory(newPage); };
const resetForm = () => { itemForm.id = null; itemForm.chemical = null; itemForm.location = ''; itemForm.quantity = 0.00; itemForm.unit = ''; itemForm.batch_number = ''; itemForm.purchase_date = null; itemForm.expiry_date = null; chemicalOptions.value = []; nextTick(() => { itemFormRef.value?.resetFields(); }); };
const handleDialogClose = () => { resetForm(); };
const cancel = () => { dialogVisible.value = false; };
const handleAdd = () => { resetForm(); isEditMode.value = false; dialogTitle.value = '添加入库记录'; dialogVisible.value = true; };
const handleUpdate = () => {
    resetForm();
    const targetRow = inventoryItems.value.find(item => item.id === selectedIds.value[0]);
    if (!targetRow) {
        ElMessage.warning('请选择一条数据进行修改');
        return;
    }
    isEditMode.value = true;
    dialogTitle.value = '编辑库存记录';
    itemForm.id = targetRow.id;
    itemForm.chemical = targetRow.chemical; // chemical ID
    itemForm.location = targetRow.location;
    itemForm.quantity = parseFloat(targetRow.quantity) || 0.00;
    itemForm.unit = targetRow.unit;
    itemForm.batch_number = targetRow.batch_number;
    itemForm.purchase_date = targetRow.purchase_date; // 确保日期格式正确
    itemForm.expiry_date = targetRow.expiry_date;     // 确保日期格式正确

    // 确保 chemicalOptions 包含当前选中的化学品，以便 el-select 正确显示
    if (targetRow.chemical_details) {
        chemicalOptions.value = [{ 
            id: targetRow.chemical_details.id,
            nameCn: targetRow.chemical_details.nameCn,
            casNo: targetRow.chemical_details.casNo
        }];
    } else {
        chemicalOptions.value = [];
    }
    dialogVisible.value = true;
};
const submitItemForm = () => { /* ... (之前的 submitItemForm 代码) ... */
    if (!itemFormRef.value) return; const headers = getAuthHeaders(); if (!headers) { handleUnauthorized(); return; }
    itemFormRef.value.validate(async (valid) => { if (valid) { submitLoading.value = true; const url = isEditMode.value ? `${backendUrl}/api/inventory/${itemForm.id}/` : `${backendUrl}/api/inventory/`; const method = isEditMode.value ? 'put' : 'post'; const dataToSend = { chemical: itemForm.chemical, location: itemForm.location, quantity: itemForm.quantity, unit: itemForm.unit, batch_number: itemForm.batch_number || null, purchase_date: itemForm.purchase_date || null, expiry_date: itemForm.expiry_date || null, };
            try { await axios[method](url, dataToSend, { headers: headers }); ElMessage.success(isEditMode.value ? '修改成功！' : '添加成功！'); dialogVisible.value = false; fetchInventory(isEditMode.value ? queryParams.pageNum : 1); } catch (error) { if (error.response && error.response.status === 401) { handleUnauthorized(); } else { console.error("保存失败:", error.response?.data); let errorMsg = error.response?.data?.detail || (isEditMode.value ? '修改失败！' : '添加失败！'); if (error.response && typeof error.response.data === 'object' && error.response.status !== 401 && error.response.status !== 403) { const fieldErrors = Object.entries(error.response.data).map(([field, messages]) => `${field}: ${Array.isArray(messages) ? messages.join(', ') : messages}`).join('; '); if (fieldErrors) errorMsg = fieldErrors; } ElMessage.error(errorMsg); } } finally { submitLoading.value = false; }
        } else { ElMessage.error('请检查表单填写是否完整和正确。'); return false; } });
};

// 表格多选 (!!! 修改 multipleSelected 的逻辑 !!!)
const handleSelectionChange = (selection) => {
    selectedIds.value = selection.map(item => item.id);
    singleSelected.value = selection.length !== 1; // 修改按钮：仅在选中一项时启用
    multipleSelected.value = selection.length === 0; // 删除按钮：只要选中了至少一项就启用 (所以是 length === 0 时禁用)
};


// --- V V V V V V 修改 handleBulkDelete 函数 V V V V V V ---
const handleBulkDelete = async () => {
    const idsToDelete = selectedIds.value; // 获取当前选中的 ID 列表
    if (idsToDelete.length === 0) {
        ElMessage.warning('请先选择要删除的数据');
        return;
    }
    const headers = getAuthHeaders();
    if (!headers) { handleUnauthorized(); return; }

    const isSingleDelete = idsToDelete.length === 1; // 判断是单个删除还是批量删除
    const confirmMessage = `确认删除选中的 ${idsToDelete.length} 条数据吗？`;

     ElMessageBox.confirm(confirmMessage, '警告', {
        confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning',
      }).then(async () => {
            loading.value = true;
            try {
                if (isSingleDelete) {
                    // --- 调用单个删除 API ---
                    const singleId = idsToDelete[0];
                    await axios.delete(`${backendUrl}/api/inventory/${singleId}/`, { headers: headers });
                } else {
                    // --- 调用批量删除 API ---
                    await axios.post(`${backendUrl}/api/inventory/bulk-delete/`,
                      { ids: idsToDelete },
                      { headers: headers }
                    );
                }

                ElMessage.success('删除成功！');
                // 检查删除后是否需要跳转到前一页
                 if (inventoryItems.value.length === idsToDelete.length && queryParams.pageNum > 1) {
                     queryParams.pageNum--;
                 }
                fetchInventory(); // 重新加载数据
            } catch (error) {
                 if (error.response && error.response.status === 401) { handleUnauthorized(); }
                 else {
                    console.error("删除失败:", error.response?.data);
                    ElMessage.error(error.response?.data?.detail || '删除失败，请重试');
                }
            } finally {
                 loading.value = false;
                 // 清空选项会在 fetchInventory 之后或 selection-change 事件中自动处理
                 // selectedIds.value = []; multipleSelected.value = true; // 不需要手动清
            }
        }).catch(() => {
             ElMessage.info('已取消删除');
        });
};
// --- (辅助函数: formatDate, formatDateTime 保持不变) ---
const formatDate = (dateString) => { if (!dateString) return ''; try { return dateString.split('T')[0]; } catch (e) { return dateString; } };
const formatDateTime = (dateString) => { if (!dateString) return ''; try { const date = new Date(dateString); return date.toLocaleString('zh-CN', { hour12: false }); } catch (e) { return dateString; } };

// --- 初始化加载 ---
onMounted(() => {
  fetchInventory();
});
</script>

<style scoped>
/* (样式保持不变) */
.app-container { padding: 20px; }
.search-card { margin-bottom: 10px; }
.action-buttons { margin-bottom: 10px; }
.el-input-number { width: 100%; }
.el-table .el-table__cell { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
</style>