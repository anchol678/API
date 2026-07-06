/**
 * Vue3 Composition API 应用
 * 功能：用户注册/登录/退出、文章CRUD、WebSocket实时通知
 */

const API_BASE = 'http://127.0.0.1:8000/api/v1';
const WS_BASE = 'ws://127.0.0.1:8000/ws';

// Axios 实例：自动携带 JWT Token
const api = axios.create({ baseURL: API_BASE });
api.interceptors.request.use(config => {
    const token = localStorage.getItem('access_token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});
// 响应拦截：401 自动清除 token
api.interceptors.response.use(
    res => res,
    error => {
        if (error.response?.status === 401) {
            localStorage.removeItem('access_token');
            localStorage.removeItem('user');
        }
        return Promise.reject(error);
    }
);

const { createApp, ref, reactive, computed, onMounted, onUnmounted, watch, nextTick } = Vue;

const app = createApp({
    setup() {
        // ========== 认证状态 ==========
        const currentUser = ref(JSON.parse(localStorage.getItem('user') || 'null'));
        const showModal = ref(null);           // 'login' | 'register' | null
        const authForm = reactive({ username: '', email: '', password: '' });
        const authError = ref('');
        const authLoading = ref(false);

        // ========== 文章状态 ==========
        const items = ref([]);
        const totalItems = ref(0);
        const editing = ref(null);           // null | { id?, title?, content? }
        const form = reactive({ title: '', content: '' });

        // ========== WebSocket 状态 ==========
        const wsConnected = ref(false);
        const wsMessage = ref('');
        let ws = null;
        let wsTimer = null;

        // ========== 方法：认证 ==========
        async function handleAuth() {
            authError.value = '';
            authLoading.value = true;
            try {
                const endpoint = showModal.value === 'login' ? '/users/login' : '/users/register';
                const payload = showModal.value === 'login'
                    ? { username: authForm.username, password: authForm.password }
                    : { username: authForm.username, email: authForm.email, password: authForm.password };

                const res = await api.post(endpoint, payload);
                const { access_token, user } = res.data;

                localStorage.setItem('access_token', access_token);
                localStorage.setItem('user', JSON.stringify(user));
                currentUser.value = user;
                showModal.value = null;
                authForm.username = '';
                authForm.email = '';
                authForm.password = '';

                fetchItems();
                connectWebSocket();
            } catch (e) {
                authError.value = e.response?.data?.detail || '请求失败，请检查网络';
            } finally {
                authLoading.value = false;
            }
        }

        function logout() {
            localStorage.removeItem('access_token');
            localStorage.removeItem('user');
            currentUser.value = null;
            items.value = [];
            totalItems.value = 0;
            disconnectWebSocket();
        }

        // ========== 方法：文章 CRUD ==========
        async function fetchItems() {
            try {
                const res = await api.get('/items');
                items.value = res.data.items;
                totalItems.value = res.data.total;
            } catch (e) {
                console.error('获取文章列表失败:', e);
            }
        }

        function openCreateForm() {
            editing.value = {};
            form.title = '';
            form.content = '';
        }

        function editItem(item) {
            editing.value = item;
            form.title = item.title;
            form.content = item.content;
        }

        function cancelEdit() {
            editing.value = null;
            form.title = '';
            form.content = '';
        }

        async function saveItem() {
            if (!form.title.trim()) {
                alert('标题不能为空');
                return;
            }
            try {
                if (editing.value.id) {
                    await api.put(`/items/${editing.value.id}`, {
                        title: form.title,
                        content: form.content,
                    });
                } else {
                    await api.post('/items', {
                        title: form.title,
                        content: form.content,
                    });
                }
                cancelEdit();
                await fetchItems();
            } catch (e) {
                alert(e.response?.data?.detail || '操作失败');
            }
        }

        async function deleteItem(id) {
            if (!confirm('确定删除这篇文章？')) return;
            try {
                await api.delete(`/items/${id}`);
                await fetchItems();
            } catch (e) {
                alert(e.response?.data?.detail || '删除失败');
            }
        }

        // ========== 方法：WebSocket ==========
        function connectWebSocket() {
            if (!currentUser.value) return;
            const token = localStorage.getItem('access_token');
            if (!token) return;

            disconnectWebSocket();

            ws = new WebSocket(`${WS_BASE}/${currentUser.value.id}?token=${token}`);

            ws.onopen = () => {
                wsConnected.value = true;
            };

            ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    wsMessage.value = data.message || event.data;
                    // 3秒后自动清除通知
                    clearTimeout(wsTimer);
                    wsTimer = setTimeout(() => { wsMessage.value = ''; }, 3000);
                } catch {
                    wsMessage.value = event.data;
                }
            };

            ws.onclose = () => {
                wsConnected.value = false;
            };

            ws.onerror = () => {
                wsConnected.value = false;
            };
        }

        function disconnectWebSocket() {
            if (ws) {
                ws.close();
                ws = null;
            }
            wsConnected.value = false;
            clearTimeout(wsTimer);
        }

        // ========== 工具方法 ==========
        function formatDate(dateStr) {
            if (!dateStr) return '';
            return new Date(dateStr).toLocaleString('zh-CN');
        }

        // ========== 生命周期 ==========
        onMounted(() => {
            if (currentUser.value) {
                fetchItems();
                connectWebSocket();
            }
        });

        onUnmounted(() => {
            disconnectWebSocket();
        });

        return {
            currentUser, showModal, authForm, authError, authLoading,
            items, totalItems, editing, form,
            wsConnected, wsMessage,
            handleAuth, logout,
            fetchItems, openCreateForm, editItem, cancelEdit, saveItem, deleteItem,
            formatDate,
        };
    }
});

app.mount('#app');
