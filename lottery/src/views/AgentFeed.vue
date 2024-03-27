<template>
    <div class="right-content">
        <div class="sidebar">
            <div class="menu-container">
                <div class="search-box">
                    <Input placeholder="Search..." v-model="searchQuery" @on-press-enter="handleSearch">
                        <Icon type="ios-search" slot="append" @click="handleSearch" />
                    </Input>
                </div>
                <Menu :active-name="activeMenuName" mode="vertical" theme="dark" accordion @on-select="handleMenuSelect">
                    <MenuItem 
                        :name="'assistant_' + index" v-for="(item, index) in assistants"
                        >
                        <div>
                            <span>{{item.name}}</span>
                            <Button type="error" size="small" class="delete-btn" @click.stop="handleDeleteAssistant(item)">X </Button>
                        </div>
                    </MenuItem>
                    <MenuGroup title=""> <!-- 空标题，用作视觉上的分割 -->
                        <!-- 你可以不放置任何内容，只是为了分隔 -->
                        <hr/>
                    </MenuGroup>
                    <MenuItem 
                        :name="'thread_' + index" v-for="(item, index) in currentAssistantThreads"
                        >
                        <div>
                            <span>{{item.name}}</span>
                            <Button type="error" size="small" class="delete-btn" @click.stop="handleDeleteAssistant(item)">X </Button>
                        </div>
                    </MenuItem>
                    <!-- 添加更多 Submenu 和 MenuItem 以匹配您的数据 -->
                </Menu>
            </div>
            <div class="button-container">
                <Button type="primary" @click="showCreateModal = true">创建代理</Button>
            </div>
        </div>        
        <div class="chat-container" ref="chatContainer">
            <div class="switch-container" v-if="!currentThread">
                学习模式：<i-switch v-model="islearning" size="large"> </i-switch>
            </div>
            <div class="chat-history" ref="chatHistory">
                    <div v-for="(message, index) in messages" :key="index">
                    <div>
                        <B>{{ message.name }} says: </B>
                    </div>
                    <!-- Display text content directly; for images and other file types, you might want to handle differently -->
                    <div v-if="message.type === 'text'">{{ message.content }}</div>
                    <img v-if="message.type === 'image'" :src="message.content" class="chat-image"/>
                    <!-- Add other types as needed -->
                </div>
            </div>
            <div class="resize-handle" ref="resizeHandle"></div>
            <div class="chat-input" ref="chatInput">
                <div
                    class="editable-area"
                    contenteditable="true"
                    @paste="handlePaste"
                    @input="handleInput"
                    placeholder="Paste text, images, or files here"
                    ref="editableArea"
                ></div>
                <div class="attachments-area">
                    <!-- 显示图片缩略图 -->
                    <div v-for="(image, index) in images" :key="`image-${index}`" class="attachment-thumbnail">
                        <img :src="image" class="thumbnail-image">
                        <span class="delete-icon" @click="removeImage(index)">X</span>
                    </div>
                    <!-- 显示文件信息 -->
                    <div v-for="(file, index) in files" :key="`file-${index}`" class="attachment-file">
                        <div style="font-size: 20px; padding: 2px; margin: 0; line-height: 10px"><i class="fas fa-paperclip"></i></div>
                        <div  style="font-size: 10px; padding: 2px;  margin: 0; line-height: 10px">{{ file.name }} <BR/> {{ file.size }} Bytes</div>
                        <span class="delete-icon" @click="removeFile(index)">X</span>
                    </div>
                </div>

                <i-button id="send-button" class="chat-button" type="primary" @click="sendMessage"><i class="fas fa-paper-plane"></i></i-button>
                <i-button id="attach-button" class="chat-button" @click="addAttachment"><i class="fas fa-paperclip"></i></i-button>

                <!-- 在模板的底部添加，但在<script>标签之外 -->
                <input type="file" ref="fileInput" style="display: none" @change="handleFileChange" multiple>
            </div>
        </div>
        <!-- 创建模态框 -->
        <Modal v-model="showCreateModal" title="Create" @on-ok="handleCreate" @on-cancel="handleCancel">
        <div style="margin-bottom: 20px;">
            <div><strong>Name:</strong></div>
            <Input v-model="newItemName" placeholder="Enter name"></Input>
        </div>
        <div>
            <div><strong>Instruction:</strong></div>
            <Input type="textarea" v-model="newItemInstruction" placeholder="Enter instruction"></Input>
        </div>
        </Modal>
    </div>
  </template>

  <script>
    import { postFormData, postData, fetchData } from '../api/agentfeed';

    export default {
        data() {
            return {
                messages: [], // Messages fetched from the server
                newMessage: '', // New message to send (text part)
                images: [],  // Array for storing image URLs
                files: [],  // Array for storing file information
                islearning: false, 
                searchQuery: '', 
                showCreateModal: false,
                newItemName: '', // 新项目的名称绑定
                newItemInstruction: '', // 新项目的说明绑定
                assistants: [], 
                currentAssistant: null,
                currentThread: null, 
                activeMenuName: '', 
                currentAssistantThreads: [], 
                menus: [], 
            };
        },
        mounted() {
            this.initializeResizableChatInput();
            this.getAssistants();
        },
        methods: {
            scrollToBottom() {
                this.$nextTick(() => {
                    const chatHistory = this.$refs.chatHistory;
                    if(chatHistory) {
                        chatHistory.scrollTop = chatHistory.scrollHeight;
                    }
                });
            },
            buildMenu: function() {
                this.menus = []
                for (let i = 0; i < this.assistants.length; i++) {
                    this.menus.push({
                        prefix: '',
                        menuname: "assistant_" + i, 
                        name: this.assistants[i].name,
                        id: this.assistants[i].assistant_id,
                        idx: i
                    })
                    if (this.currentAssistant 
                            && this.currentAssistantThreads 
                            && this.assistants[i].assistant_id == this.currentAssistant.assistant_id) {
                        for (let j = 0; j < this.currentAssistantThreads.length; j++) {
                            this.menus.push({
                                prefix: ' - ',
                                menuname: "thread_" + j, 
                                name: " - " + this.currentAssistantThreads[j].name,
                                id: this.currentAssistantThreads[j].thread_id, 
                                idx: j
                            })
                        }
                    }
                }
            }, 
            handleMenuSelect: async function(name) {
                // 选中某个submenu，复位当前选择的assistant，如果直接输出对话，则创建一个新的thread，
                // 同时要判断一下当前是否是learning模式，如果是learning模式则不创建thread
                if (this.activeMenuName == name) {
                    return
                }

                this.activeMenuName = name
                let ind = name.split("_")[1]
                if (name.indexOf("assistant_") == 0) {
                    // 选中某个assistant
                    this.currentAssistant = this.assistants[ind]
                    this.currentThread = null
                    this.currentAssistantThreads = await fetchData("chat?assistant=" + this.currentAssistant.assistant_id)
                    console.log(this.currentAssistantThreads)
                    
                } else {
                    this.currentThread = this.currentAssistantThreads[ind]
                }
                this.messages = []
            }, 
            getAssistants: async function() {
                let response = await fetchData("agent")
                console.log(response)
                this.assistants = response

                this.currentAssistant = (this.assistants && this.assistants.length > 0) ? this.assistants[0] : null
                this.currentAssistantThreads = null
                this.$nextTick(async () =>  {
                    this.activeMenuName = "assistant_0"
                    if (this.currentAssistant) {
                        this.currentAssistantThreads = await fetchData("chat?assistant=" + this.currentAssistant.assistant_id)
                    }
                })
            }, 
            handleDeleteAssistant: async function(id) {

            },
            handleSearch() {
                // 实现搜索逻辑，或在这里处理搜索相关的动作
                console.log('Searching for', this.searchQuery);
            },
            initializeResizableChatInput() {
                const chatInput = this.$refs.chatInput;
                const resizeHandle = this.$refs.resizeHandle;
                const editableArea = this.$refs.editableArea;
                let startY, startHeight, inputStartHeight;

                if (resizeHandle) {
                    resizeHandle.addEventListener('mousedown', (e) => {
                        startY = e.clientY;
                        startHeight = chatInput.offsetHeight;
                        inputStartHeight = editableArea.offsetHeight;
                        document.addEventListener('mousemove', doDrag, false);
                        document.addEventListener('mouseup', stopDrag, false);
                    });

                    const doDrag = (e) => {
                        const newHeight = startHeight - (e.clientY - startY);
                        const newEditHeight = inputStartHeight - (e.clientY - startY);
                        chatInput.style.height = `${Math.max(newHeight, 20)}px`; // 设置最小高度为20px
                        editableArea.style.height = `${Math.max(newEditHeight, 20)}px`; // 设置最小高度为20px
                    };

                    const stopDrag = () => {
                        document.removeEventListener('mousemove', doDrag, false);
                        document.removeEventListener('mouseup', stopDrag, false);
                    };
                }
            },
            fetchMessages() {

            },
            updateSendProgress: function(progressEvent) {
                const progress = parseInt(Math.round((progressEvent.loaded * 100) / progressEvent.total));
                console.log(progress)
            }, 
            sendMessage: async function() {
                // Here you should form the data including text, images and files to send
                // This example just sends a plain text message
                let assistant_id = this.currentAssistant? this.currentAssistant.assistant_id : null
                let thread_id = this.currentThread? this.currentThread.thread_id : null
                if (assistant_id == null) {
                    return
                }
                let response = null
                this.messages.push({
                    role: 'user', 
                    name: 'me', 
                    type: 'text', 
                    content: this.newMessage
                })
                
                let newMessage = this.newMessage
                let files = this.files
                let images = this.images
                this.clearInput()
                if (this.islearning && thread_id == null) {
                    response = await postFormData('learn', assistant_id, thread_id, newMessage, files, images, this.updateSendProgress)
                } else {
                    response = await postFormData('chat', assistant_id, thread_id, newMessage, files, images, this.updateSendProgress)
                }
                
                if (response) {
                    if (this.currentThread == null && !this.islearning) {
                        this.currentAssistantThreads = await fetchData("chat?assistant=" + this.currentAssistant.assistant_id)
                        for (let i = 0; i < this.currentAssistantThreads.length; i++) {
                            if (this.currentAssistantThreads[i].thread_id == response.thread_id) {
                                this.activeMenuName = 'thread_' + i
                                this.currentThread = this.currentAssistantThreads[i]
                                break
                            }
                        }
                    }
                    
                    response = response.messages
                    
                    if (response && response.data) {
                        for (let i = 0; i < response.data.length; i++) {
                            for (let j = 0; j < response.data[i].content.length; j++) {
                                if (response.data[i].content[j].type == 'text') {
                                    this.messages.push({
                                        role: 'bot', 
                                        name: this.currentAssistant.name, 
                                        type: 'text', 
                                        content: response.data[i].content[j].text.value
                                    })
                                }
                            }
                        }
                    }
                }
                this.scrollToBottom()
            },
            clearInput() {
                this.newMessage = ''; // Clear text
                this.images = []; // Clear images
                this.files = []; // Clear other files
                this.$refs.editableArea.innerHTML = ''; // Clear editable area content
            },
            handleInput(e) {
                this.newMessage = e.target.innerText;
                this.adjustHeight(e.target);
            },
            handlePaste(e) {
                const items = (e.clipboardData || e.originalEvent.clipboardData).items;
                for (const item of items) {
                    if (item.kind === 'string') {
                        item.getAsString(pastedText => {
                            const selection = window.getSelection();
                            if (!selection.rangeCount) return;
                            const range = selection.getRangeAt(0);
                            range.deleteContents();
                            range.insertNode(document.createTextNode(pastedText));
                            this.adjustHeight(e.target);
                            this.newMessage = e.target.innerText;  // Update the text model
                            console.log(e.target.innerText)
                        });
                    } else if (item.kind === 'file') {
                        const blob = item.getAsFile();
                        if (blob.type.startsWith('image/')) {
                            const reader = new FileReader();
                            reader.onload = (event) => {
                                // 将图片DataURL加入到images数组
                                this.images.push(event.target.result);
                            };
                            reader.readAsDataURL(blob);
                        } else {
                            // 将非图片文件信息加入到files数组
                            const file = blob;
                            this.files.push(file);
                        }
                    }
                }
                e.preventDefault(); // 阻止默认粘贴行为
            },
            removeImage(index) {
                this.images.splice(index, 1);
            },
            removeFile(index) {
                this.files.splice(index, 1);
            },
            adjustHeight(target) {
                target.style.height = 'auto';
                target.style.height = target.scrollHeight + 'px';
            }, 
            addAttachment() {
                this.$refs.fileInput.click(); // 触发文件输入元素的点击事件
            },
            handleFileChange(e) {
                const files = e.target.files;
                for (let i = 0; i < files.length; i++) {
                    const file = files[i];
                    if (file.type.startsWith('image/')) {
                        const reader = new FileReader();
                        reader.onload = (event) => {
                            // 将图片DataURL加入到images数组
                            this.images.push(event.target.result);
                        };
                        reader.readAsDataURL(file);
                    } else {
                        // 将非图片文件信息加入到files数组
                        const fileInfo = file;
                        this.files.push(fileInfo);
                    }
                }
                e.target.value = ''; // 重置文件输入，以便再次选择相同文件
            },
            handleCreate: async function () {
                // 这里实现创建项的逻辑
                if (!this.newItemName || !this.newItemInstruction) {
                    return;
                }
                response = await postData('agent', {
                    name: this.newItemName, 
                    desc: this.newItemInstruction
                })
                console.log("Created:", this.newItemName, this.newItemInstruction);
                // 清空输入并关闭模态框
                this.newItemName = '';
                this.newItemInstruction = '';
                this.showCreateModal = false;
            },
            handleCancel() {
                // 清空输入并关闭模态框
                this.newItemName = '';
                this.newItemInstruction = '';
                this.showCreateModal = false;
            }
        }
    };


  </script>
  
  <style scoped>
    .right-content {
        flex: 1; /* 充满剩余空间 */
        padding: 0;
        color: #000;
        display: flex;
        height: 100vh; /* 使布局顶天立地 */
        text-align: left;
    }
    .sidebar {
        width: 30%; /* 占容器的30%宽度 */
        background-color: #334455;
        display: flex;
        flex-direction: column; /* 使内容垂直堆叠 */
        height: 100vh; /* 使侧边栏填满整个视窗高度 */
    }
    .sidebar .ivu-menu {
        width: 100% !important; /* 占满 .sidebar 的宽度 */
    }
    ::v-deep .ivu-menu-submenu > .ivu-menu-submenu-title .ivu-icon {
        display: none !important;
    }
    .delete-btn {
        position: absolute;
        right: 10px; /* 根据需要调整 */
        top: 50%;
        transform: translateY(-50%);
        opacity: 0.1; /* 默认不显示 */
        transition: opacity 0.2s; /* 平滑过渡效果 */
        cursor: pointer;
    }

    .ivu-menu-submenu:hover .delete-btn {
        opacity: 1; /* 鼠标悬停时显示 */
    }
    .menu-container {
        flex: 1; /* 使菜单填满除按钮外的所有可用空间 */
        overflow-y: auto; /* 超出内容可以滚动 */
    }
    .active-submenu {
        background-color: #3399ff; /* 选中状态的背景颜色 */
        color: white; /* 选中状态的文本颜色 */
    }

    .button-container {
        padding: 10px; /* 在按钮周围添加一些间距 */
        background-color: #334455; /* 使其背景与侧边栏一致，可根据需要调整 */
    }

    .demo-spin-container{
        display: inline-block;
        width: 100%;
        height: 100px;
        position: relative;
    }
    .preview-container {
        margin-top: 10px;
    }
    .search-box {
        margin-bottom: 20px; /* 在搜索框和菜单项之间添加一些空间 */
    }
    .image-container, .file-container {
        margin-bottom: 10px;
    }

    .image-preview {
        width: 100%; /* Adjust based on your needs */
        max-width: 100%; /* Ensure it fits in the container */
        cursor: pointer; /* Indicates it can be clicked */
    }

    .file-preview {
        cursor: pointer; /* Indicates it can be clicked */
    }
    .chat-container {
        position: relative;
        display: flex;
        flex-direction: column;
        height: 100vh; /* 设置容器高度为视口高度 */
        justify-content: space-between; /* 确保子元素分布在容器的两端 */
        margin-bottom: 20px; /* 保留底部空间 */
        width: 70%; /* 占容器的70%宽度 */
        padding: 20px;
        overflow-y: auto; /* 内容超出时可滚动 */
    }

    .chat-history {
        flex-grow: 1;
        overflow-y: auto; /* 允许聊天历史滚动 */
        padding: 30px 10px;
    }
    .chat-input {
        /* 输入区域的样式 */
        position: relative; /* 使得内部的绝对定位元素相对于此容器定位 */
        min-height: 200px; /* 或根据需要设置适当的高度 */
        padding-bottom: 40px; /* 留出足够的空间给按钮 */
        border: 1px solid #ccc;
    }
    .attachments-area {
        position: absolute;
        bottom: 10px;
        left: 60px;
        right: 60px;
        display: flex;
        flex-direction: row; /* 确保附件水平排列 */
        align-items: center;
        overflow-x: auto; /* 允许水平滚动 */
        overflow-y: hidden;
        white-space: nowrap;
        max-height: 100px; /* 限制附件区域的最大高度 */
    }

    .attachment-thumbnail {
        width: 100px; /* 缩略图宽度 */
        height: 50px; /* 缩略图高度 */
        object-fit: cover; /* 确保图片不失真 */
        margin-right: 8px; /* 缩略图之间的间距 */
        border-radius: 4px; /* 轻微的圆角效果 */
        background-color: #e4e6e8; /* 背景颜色 */
        display: flex;
        justify-content: center;
        align-items: center;
        overflow: hidden; /* 隐藏溢出内容 */
        position: relative; /* 使子元素的绝对定位相对于此容器 */
    }

    .attachment-file {
        width: 100px; /* 缩略图宽度 */
        height: 50px; /* 缩略图高度 */
        margin-right: 8px; /* 缩略图之间的间距 */
        border-radius: 4px; /* 轻微的圆角效果 */
        justify-content: center;
        align-items: center;
        overflow: hidden; /* 隐藏溢出内容 */
        position: relative; /* 使子元素的绝对定位相对于此容器 */
    }

    .thumbnail-image {
        max-width: 100%;  /* 确保图片不超过其容器的宽度 */
        max-height: 100%; /* 确保图片不超过其容器的高度 */
        object-fit: cover; /* 保证图片完全覆盖容器区域，可能会被裁切以适应容器 */
    }

    .delete-icon {
        position: absolute;
        top: 0; /* 放置在容器的顶部 */
        right: 0; /* 放置在容器的右侧 */
        cursor: pointer; /* 显示为可点击状态 */
        background-color: #f44336; /* 背景颜色 */
        color: white; /* 字体颜色 */
        font-size: 12px; /* 字体大小 */
        width: 16px; /* 宽度 */
        height: 16px; /* 高度 */
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 50%; /* 圆形 */
        box-shadow: 0 0 2px #000; /* 轻微的阴影效果，可选 */
    }
    .editable-area {
        height: 200%; /* 充满整个 .chat-input 容器 */
        padding: 10px;
        border: 0px;
        margin-right: 10px;
        flex-grow: 1;
        text-align: left;
        line-height: normal;
    }
    .chat-button {
        position: absolute;
        bottom: 10px; /* 根据需要调整距离底部的距离 */
    }
    #send-button {
        right: 10px; /* 发送按钮位于右下角 */
    }

    #attach-button {
        left: 10px; /* 添加附件按钮位于左下角 */
        border: 0;
        background: none;
    }
    .chat-image {
        max-width: 100%; /* Ensure images do not overflow */
    }
    .file-icon {
        display: inline-flex;
        align-items: center;
        padding: 5px;
        margin-right: 10px;
        background-color: #f0f0f0;
        border-radius: 4px;
    }
    .file-icon i.fa-file {
        margin-right: 5px;
        color: #606266;
    }
    .resize-handle {
        height: 5px;
        background-color: #ccc;
        cursor: ns-resize;
    }
    .editable-area:focus {
        outline: none;
    }
    .switch-container {
        position: absolute; /* 使用固定定位 */
        top: 20px; /* 距离页面顶部20像素 */
        left: 20px; /* 距离页面左侧20像素 */
        z-index: 1000; /* 确保开关显示在其他内容之上 */
    }
  </style>
    