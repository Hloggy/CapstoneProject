document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const loginForm = document.getElementById('login-form');
    const userInfo = document.getElementById('user-info');
    const displayUsername = document.getElementById('display-username');
    const loginBtn = document.getElementById('login-btn');
    const registerBtn = document.getElementById('register-btn');
    const logoutBtn = document.getElementById('logout-btn');
    const authMessage = document.getElementById('auth-message');
    
    const inventorySection = document.getElementById('inventory-section');
    const historySection = document.getElementById('history-section');
    
    const addItemBtn = document.getElementById('add-item-btn');
    const itemForm = document.getElementById('item-form');
    const saveItemBtn = document.getElementById('save-item-btn');
    const cancelItemBtn = document.getElementById('cancel-item-btn');
    const searchItems = document.getElementById('search-items');
    const categoryFilter = document.getElementById('category-filter');
    const lowStockBtn = document.getElementById('low-stock-btn');
    
    const inventoryTable = document.getElementById('inventory-items');
    const historyTable = document.getElementById('history-items');
    
    const prevPageBtn = document.getElementById('prev-page');
    const nextPageBtn = document.getElementById('next-page');
    const pageInfo = document.getElementById('page-info');
    
    // Global variables
    let currentUser = null;
    let token = null;
    let currentPage = 1;
    let totalPages = 1;
    let isEditing = false;
    let currentItemId = null;
    
    // API Base URL
    const API_BASE = '/api';
    
    // Initialize the application
    init();
    
    function init() {
        // Check if user is already logged in
        const storedToken = localStorage.getItem('inventory_token');
        const storedUser = localStorage.getItem('inventory_user');
        
        if (storedToken && storedUser) {
            token = storedToken;
            currentUser = JSON.parse(storedUser);
            updateUIAfterLogin();
            loadInventoryItems();
            loadCategories();
        }
        
        // Event listeners
        loginBtn.addEventListener('click', handleLogin);
        registerBtn.addEventListener('click', handleRegister);
        logoutBtn.addEventListener('click', handleLogout);
        
        addItemBtn.addEventListener('click', showItemForm);
        saveItemBtn.addEventListener('click', saveItem);
        cancelItemBtn.addEventListener('click', hideItemForm);
        
        searchItems.addEventListener('input', debounce(loadInventoryItems, 300));
        categoryFilter.addEventListener('change', loadInventoryItems);
        lowStockBtn.addEventListener('click', toggleLowStockFilter);
        
        prevPageBtn.addEventListener('click', goToPrevPage);
        nextPageBtn.addEventListener('click', goToNextPage);
    }
    
    // Authentication functions
    async function handleLogin() {
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        
        if (!username || !password) {
            showAuthMessage('Please enter both username and password');
            return;
        }
        
        try {
            const response = await fetch(`${API_BASE}/auth/login/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    username,
                    password
                })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                token = data.access;
                currentUser = {
                    username: username,
                    is_staff: data.is_staff || false
                };
                
                // Store token and user in localStorage
                localStorage.setItem('inventory_token', token);
                localStorage.setItem('inventory_user', JSON.stringify(currentUser));
                
                updateUIAfterLogin();
                loadInventoryItems();
                loadCategories();
                showAuthMessage('');
            } else {
                showAuthMessage(data.detail || 'Login failed');
            }
        } catch (error) {
            showAuthMessage('An error occurred during login');
            console.error('Login error:', error);
        }
    }
    
    async function handleRegister() {
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        
        if (!username || !password) {
            showAuthMessage('Please enter both username and password');
            return;
        }
        
        try {
            const response = await fetch(`${API_BASE}/users/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    username,
                    password,
                    email: `${username}@example.com` // Simple email generation
                })
            });
            
            if (response.ok) {
                showAuthMessage('Registration successful. Please login.');
            } else {
                const data = await response.json();
                showAuthMessage(data.username || data.password || 'Registration failed');
            }
        } catch (error) {
            showAuthMessage('An error occurred during registration');
            console.error('Registration error:', error);
        }
    }
    
    function handleLogout() {
        localStorage.removeItem('inventory_token');
        localStorage.removeItem('inventory_user');
        token = null;
        currentUser = null;
        
        loginForm.style.display = 'flex';
        userInfo.style.display = 'none';
        inventorySection.style.display = 'none';
        historySection.style.display = 'none';
        
        // Clear form fields
        document.getElementById('username').value = '';
        document.getElementById('password').value = '';
        showAuthMessage('');
    }
    
    function updateUIAfterLogin() {
        loginForm.style.display = 'none';
        userInfo.style.display = 'block';
        inventorySection.style.display = 'block';
        displayUsername.textContent = currentUser.username;
    }
    
    function showAuthMessage(message) {
        authMessage.textContent = message;
    }
    
    // Inventory Item functions
    async function loadInventoryItems() {
        if (!token) return;
        
        try {
            let url = `${API_BASE}/items/?page=${currentPage}`;
            
            // Add search filter
            if (searchItems.value) {
                url += `&search=${encodeURIComponent(searchItems.value)}`;
            }
            
            // Add category filter
            if (categoryFilter.value) {
                url += `&category=${categoryFilter.value}`;
            }
            
            const response = await fetch(url, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                renderInventoryItems(data.results);
                
                // Update pagination info
                if (data.count) {
                    totalPages = Math.ceil(data.count / 10); // Assuming page size of 10
                    updatePaginationUI();
                }
            } else {
                console.error('Failed to load inventory items');
            }
        } catch (error) {
            console.error('Error loading inventory items:', error);
        }
    }
    
    function renderInventoryItems(items) {
        inventoryTable.innerHTML = '';
        
        if (items.length === 0) {
            inventoryTable.innerHTML = '<tr><td colspan="6">No items found</td></tr>';
            return;
        }
        
        items.forEach(item => {
            const row = document.createElement('tr');
            if (item.quantity < 5) { // Low stock threshold
                row.classList.add('low-stock');
            }
            
            row.innerHTML = `
                <td>${item.name}</td>
                <td>${item.description || ''}</td>
                <td>${item.quantity}</td>
                <td>$${item.price.toFixed(2)}</td>
                <td>${item.category ? item.category.name : ''}</td>
                <td>
                    <button class="action-btn edit-btn" data-id="${item.id}">Edit</button>
                    <button class="action-btn delete-btn" data-id="${item.id}">Delete</button>
                    <button class="action-btn adjust-btn" data-id="${item.id}">Adjust</button>
                    <button class="action-btn history-btn" data-id="${item.id}">History</button>
                </td>
            `;
            
            inventoryTable.appendChild(row);
        });
        
        // Add event listeners to action buttons
        document.querySelectorAll('.edit-btn').forEach(btn => {
            btn.addEventListener('click', (e) => editItem(e.target.dataset.id));
        });
        
        document.querySelectorAll('.delete-btn').forEach(btn => {
            btn.addEventListener('click', (e) => deleteItem(e.target.dataset.id));
        });
        
        document.querySelectorAll('.adjust-btn').forEach(btn => {
            btn.addEventListener('click', (e) => adjustStock(e.target.dataset.id));
        });
        
        document.querySelectorAll('.history-btn').forEach(btn => {
            btn.addEventListener('click', (e) => showItemHistory(e.target.dataset.id));
        });
    }
    
    function showItemForm() {
        isEditing = false;
        currentItemId = null;
        
        // Reset form
        document.getElementById('item-id').value = '';
        document.getElementById('item-name').value = '';
        document.getElementById('item-description').value = '';
        document.getElementById('item-quantity').value = '';
        document.getElementById('item-price').value = '';
        document.getElementById('item-category').value = '';
        
        itemForm.style.display = 'block';
    }
    
    function hideItemForm() {
        itemForm.style.display = 'none';
    }
    
    async function editItem(itemId) {
        try {
            const response = await fetch(`${API_BASE}/items/${itemId}/`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            
            if (response.ok) {
                const item = await response.json();
                
                // Fill the form
                document.getElementById('item-id').value = item.id;
                document.getElementById('item-name').value = item.name;
                document.getElementById('item-description').value = item.description || '';
                document.getElementById('item-quantity').value = item.quantity;
                document.getElementById('item-price').value = item.price;
                document.getElementById('item-category').value = item.category ? item.category.id : '';
                
                isEditing = true;
                currentItemId = item.id;
                itemForm.style.display = 'block';
            }
        } catch (error) {
            console.error('Error editing item:', error);
        }
    }
    
    async function saveItem() {
        const itemId = document.getElementById('item-id').value;
        const name = document.getElementById('item-name').value;
        const description = document.getElementById('item-description').value;
        const quantity = document.getElementById('item-quantity').value;
        const price = document.getElementById('item-price').value;
        const categoryId = document.getElementById('item-category').value;
        
        if (!name || !quantity || !price) {
            alert('Please fill in all required fields');
            return;
        }
        
        const itemData = {
            name,
            description,
            quantity: parseInt(quantity),
            price: parseFloat(price),
            category_id: categoryId || null
        };
        
        try {
            const url = isEditing ? `${API_BASE}/items/${itemId}/` : `${API_BASE}/items/`;
            const method = isEditing ? 'PUT' : 'POST';
            
            const response = await fetch(url, {
                method,
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(itemData)
            });
            
            if (response.ok) {
                hideItemForm();
                loadInventoryItems();
            } else {
                const errorData = await response.json();
                alert(`Error: ${JSON.stringify(errorData)}`);
            }
        } catch (error) {
            console.error('Error saving item:', error);
            alert('An error occurred while saving the item');
        }
    }
    
    async function deleteItem(itemId) {
        if (!confirm('Are you sure you want to delete this item?')) return;
        
        try {
            const response = await fetch(`${API_BASE}/items/${itemId}/`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            
            if (response.ok) {
                loadInventoryItems();
            }
        } catch (error) {
            console.error('Error deleting item:', error);
        }
    }
    
    async function adjustStock(itemId) {
        const change = prompt('Enter quantity change (positive for stock in, negative for stock out):');
        if (change === null) return;
        
        const notes = prompt('Enter notes for this adjustment:') || '';
        
        try {
            const response = await fetch(`${API_BASE}/items/${itemId}/adjust_stock/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    change: parseInt(change),
                    notes
                })
            });
            
            if (response.ok) {
                loadInventoryItems();
            } else {
                const errorData = await response.json();
                alert(`Error: ${JSON.stringify(errorData)}`);
            }
        } catch (error) {
            console.error('Error adjusting stock:', error);
        }
    }
    
    // Category functions
    async function loadCategories() {
        if (!token) return;
        
        try {
            const response = await fetch(`${API_BASE}/categories/`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                renderCategoryOptions(data);
            }
        } catch (error) {
            console.error('Error loading categories:', error);
        }
    }
    
    function renderCategoryOptions(categories) {
        categoryFilter.innerHTML = '<option value="">All Categories</option>';
        const itemCategorySelect = document.getElementById('item-category');
        itemCategorySelect.innerHTML = '<option value="">No Category</option>';
        
        categories.forEach(category => {
            const option1 = document.createElement('option');
            option1.value = category.id;
            option1.textContent = category.name;
            categoryFilter.appendChild(option1);
            
            const option2 = document.createElement('option');
            option2.value = category.id;
            option2.textContent = category.name;
            itemCategorySelect.appendChild(option2);
        });
    }
    
    // History functions
    async function showItemHistory(itemId) {
        try {
            const response = await fetch(`${API_BASE}/history/?item=${itemId}`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            
            if (response.ok) {
                const history = await response.json();
                renderHistory(history);
                inventorySection.style.display = 'none';
                historySection.style.display = 'block';
            }
        } catch (error) {
            console.error('Error loading history:', error);
        }
    }
    
    function renderHistory(history) {
        historyTable.innerHTML = '';
        
        if (history.length === 0) {
            historyTable.innerHTML = '<tr><td colspan="7">No history found</td></tr>';
            return;
        }
        
        history.forEach(entry => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${entry.item}</td>
                <td>${entry.action}</td>
                <td>${entry.quantity_change}</td>
                <td>${entry.previous_quantity}</td>
                <td>${entry.new_quantity}</td>
                <td>${new Date(entry.timestamp).toLocaleString()}</td>
                <td>${entry.notes || ''}</td>
            `;
            historyTable.appendChild(row);
        });
    }
    
    function toggleLowStockFilter() {
        if (lowStockBtn.textContent.includes('Show')) {
            lowStockBtn.textContent = 'Show All Items';
            searchItems.value = '';
            categoryFilter.value = '';
            currentPage = 1;
            loadInventoryItems('?quantity__lt=5'); // Show items with quantity less than 5
        } else {
            lowStockBtn.textContent = 'Show Low Stock';
            searchItems.value = '';
            categoryFilter.value = '';
            currentPage = 1;
            loadInventoryItems();
        }
    }
    
    // Pagination functions
    function updatePaginationUI() {
        pageInfo.textContent = `Page ${currentPage} of ${totalPages}`;
        prevPageBtn.disabled = currentPage === 1;
        nextPageBtn.disabled = currentPage === totalPages;
    }
    
    function goToPrevPage() {
        if (currentPage > 1) {
            currentPage--;
            loadInventoryItems();
        }
    }
    
    function goToNextPage() {
        if (currentPage < totalPages) {
            currentPage++;
            loadInventoryItems();
        }
    }
    
    // Utility functions
    function debounce(func, wait) {
        let timeout;
        return function() {
            const context = this;
            const args = arguments;
            clearTimeout(timeout);
            timeout = setTimeout(() => {
                func.apply(context, args);
            }, wait);
        };
    }
});

