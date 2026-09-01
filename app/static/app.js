// Tab 切换功能
document.addEventListener('DOMContentLoaded', function() {
    const tabButtons = document.querySelectorAll('.tab-btn');
    const panels = document.querySelectorAll('.panel');

    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const tabId = button.getAttribute('data-tab');

            // 更新活动标签
            tabButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');

            // 显示对应面板
            panels.forEach(panel => {
                panel.classList.remove('active');
                if (panel.id === `${tabId}-panel`) {
                    panel.classList.add('active');
                }
            });
        });
    });

    // 知识问答功能
    const chatInput = document.getElementById('chat-input');
    const chatSendBtn = document.getElementById('chat-send');
    const chatContainer = document.querySelector('#chat-panel .chat-container');

    function sendChat() {
        const question = chatInput.value.trim();
        if (!question) return;

        // 添加用户消息
        addMessage(chatContainer, 'user', question);
        chatInput.value = '';

        // 禁用按钮并显示加载状态
        chatSendBtn.disabled = true;
        chatSendBtn.textContent = '思考中...';

        fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                question: question,
                top_k: 5
            })
        })
        .then(response => response.json())
        .then(data => {
            // 添加AI回答
            addMessage(chatContainer, 'ai', data.answer, 'RAG · 知识问答');

            // 添加sources表格
            if (data.sources && data.sources.length > 0) {
                const sourcesTable = document.createElement('table');
                sourcesTable.className = 'sources-table';
                sourcesTable.innerHTML = `
                    <thead>
                        <tr>
                            <th>Rank</th>
                            <th>Chunk ID</th>
                            <th>Source</th>
                            <th>Vector Score</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${data.sources.map(source => `
                            <tr>
                                <td>${source.rank}</td>
                                <td>${source.chunk_id}</td>
                                <td>${source.source}</td>
                                <td>${source.vector_score}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                `;
                chatContainer.appendChild(sourcesTable);
            }

            // 添加cached标签
            if (data.cached) {
                const cachedTag = document.createElement('span');
                cachedTag.className = 'cached-tag';
                cachedTag.textContent = 'Cached';
                chatContainer.appendChild(cachedTag);
            }

            // 滚动到底部
            chatContainer.scrollTop = chatContainer.scrollHeight;
        })
        .catch(error => {
            console.error('Error:', error);
            addMessage(chatContainer, 'ai', '抱歉，出现了错误。请重试。', 'RAG · 知识问答');
        })
        .finally(() => {
            // 恢复按钮
            chatSendBtn.disabled = false;
            chatSendBtn.textContent = '发送';
        });
    }

    chatSendBtn.addEventListener('click', sendChat);

    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendChat();
        }
    });

    // Agent 对话功能
    const agentInput = document.getElementById('agent-input');
    const agentSendBtn = document.getElementById('agent-send');
    const agentContainer = document.querySelector('#agent-panel .chat-container');

    function sendAgent() {
        const message = agentInput.value.trim();
        if (!message) return;

        // 添加用户消息
        addMessage(agentContainer, 'user', message);
        agentInput.value = '';

        // 禁用按钮并显示加载状态
        agentSendBtn.disabled = true;
        agentSendBtn.textContent = '思考中...';

        fetch('/agent', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message
            })
        })
        .then(response => response.json())
        .then(data => {
            // 添加AI回答
            addMessage(agentContainer, 'ai', data.answer, 'Agent · 智能助手');

            // 滚动到底部
            agentContainer.scrollTop = agentContainer.scrollHeight;
        })
        .catch(error => {
            console.error('Error:', error);
            addMessage(agentContainer, 'ai', '抱歉，出现了错误。请重试。', 'Agent · 智能助手');
        })
        .finally(() => {
            // 恢复按钮
            agentSendBtn.disabled = false;
            agentSendBtn.textContent = '发送';
        });
    }

    agentSendBtn.addEventListener('click', sendAgent);

    agentInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendAgent();
        }
    });

    // 文档上传功能
    const documentUpload = document.getElementById('document-upload');
    const uploadBtn = document.getElementById('upload-btn');
    const uploadResult = document.getElementById('upload-result');

    uploadBtn.addEventListener('click', () => {
        const file = documentUpload.files[0];
        if (!file) {
            alert('请选择一个文件');
            return;
        }

        const formData = new FormData();
        formData.append('file', file);

        fetch('/documents/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            uploadResult.innerHTML = `
                <div>
                    <p><strong>文档ID:</strong> ${data.document_id}</p>
                    <p><strong>块数量:</strong> ${data.chunk_count}</p>
                </div>
            `;
        })
        .catch(error => {
            console.error('Error:', error);
            uploadResult.innerHTML = '<p style="color: red;">上传失败，请重试。</p>';
        });
    });

    // 工单创建功能
    const ticketTitle = document.getElementById('ticket-title');
    const ticketDescription = document.getElementById('ticket-description');
    const createTicketBtn = document.getElementById('create-ticket');
    const ticketResult = document.getElementById('ticket-result');

    createTicketBtn.addEventListener('click', () => {
        const title = ticketTitle.value.trim();
        const description = ticketDescription.value.trim();

        if (!title || !description) {
            alert('请填写完整信息');
            return;
        }

        fetch('/tickets', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                title: title,
                description: description
            })
        })
        .then(response => response.json())
        .then(data => {
            ticketResult.innerHTML = `
                <div>
                    <p><strong>工单ID:</strong> ${data.ticket_id}</p>
                    <p><strong>状态:</strong> ${data.status}</p>
                </div>
            `;
        })
        .catch(error => {
            console.error('Error:', error);
            ticketResult.innerHTML = '<p style="color: red;">创建失败，请重试。</p>';
        });
    });

    // 工单查询功能
    const ticketIdInput = document.getElementById('ticket-id');
    const queryTicketBtn = document.getElementById('query-ticket');

    queryTicketBtn.addEventListener('click', () => {
        const ticketId = ticketIdInput.value.trim();
        if (!ticketId) {
            alert('请输入工单ID');
            return;
        }

        fetch(`/tickets/${ticketId}`)
        .then(response => response.json())
        .then(data => {
            ticketResult.innerHTML = `
                <div>
                    <p><strong>工单ID:</strong> ${data.ticket_id}</p>
                    <p><strong>标题:</strong> ${data.title}</p>
                    <p><strong>描述:</strong> ${data.description}</p>
                    <p><strong>状态:</strong> ${data.status}</p>
                </div>
            `;
        })
        .catch(error => {
            console.error('Error:', error);
            ticketResult.innerHTML = '<p style="color: red;">查询失败，请重试。</p>';
        });
    });

    // 辅助函数：添加消息到指定聊天容器
    // tagText 为来源标识（如 "RAG · 知识问答" / "Agent · 智能助手"），
    // 正文始终使用 textContent 渲染，避免 innerHTML 引入 XSS 风险。
    function addMessage(container, type, content, tagText) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}-message`;

        if (tagText) {
            const tag = document.createElement('span');
            tag.className = 'msg-tag';
            tag.textContent = tagText;
            messageDiv.appendChild(tag);
        }

        const contentNode = document.createElement('div');
        contentNode.className = 'msg-content';
        contentNode.textContent = content;
        messageDiv.appendChild(contentNode);

        container.appendChild(messageDiv);
    }

    // 清空记录：清空指定容器并恢复欢迎语
    function clearChatContainer(container, welcomeText) {
        while (container.firstChild) {
            container.removeChild(container.firstChild);
        }
        const welcome = document.createElement('div');
        welcome.className = 'message user-message';
        welcome.textContent = welcomeText;
        container.appendChild(welcome);
    }

    document.getElementById('chat-clear').addEventListener('click', () => {
        clearChatContainer(chatContainer, '欢迎使用知识问答系统！请输入您的问题。');
    });

    document.getElementById('agent-clear').addEventListener('click', () => {
        clearChatContainer(agentContainer, '欢迎使用 Agent 对话系统！请输入您的消息。');
    });
});